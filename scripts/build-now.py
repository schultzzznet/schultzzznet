#!/usr/bin/env python3
"""The Now board: one data file, docs/_data/now.yml, drawn on the site (docs/now.md) and in the profile README.

The board says what is moving this week: what was done in the last few days, what runs now, what waits on the owner, and
what comes next, under a few headline figures. It is kept by hand on every change of state (a merge, an apply, a drill, a
decision), so it is checked the way a hand-kept, fast-moving thing needs:

  build-now.py --write       write the README block between <!-- now:start --> and <!-- now:end --> from now.yml
  build-now.py --stdout      print that block instead
  build-now.py --check       what the guard runs, from the root of the tree it checks: fails when
     1. now.yml has the wrong shape: a list too long or empty, an item that is not one plain sentence, a stray key;
     2. as_of is in the future or more than MAX_AGE_DAYS old, or a done item is dated after as_of or more than
        DONE_MAX_AGE_DAYS before it, or the done items are not newest first;
     3. a headline figure disagrees with docs/_data/progress.yml dated after as_of, or with docs/_data/stats.yml
        measured after as_of (a newer source wins, so the board must be read again);
     4. README.md does not hold exactly one now block, or the block is not what this script writes from now.yml.
  build-now.py --self-test   plant each fault above in a scratch copy and require a refusal

Standard library only: the guard runs with python3 and nothing installed. now.yml is read with build-progress.py's reader
(whole numbers and double-quoted strings, two levels at most), so the two hand-kept files share one format.
"""
import datetime as dt
import importlib.util
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = "docs/_data/now.yml"
PROGRESS = "docs/_data/progress.yml"
STATS = "docs/_data/stats.yml"
README = "README.md"
SITE = "https://schultzzznet.github.io/schultzzznet/"
START, END = "<!-- now:start -->", "<!-- now:end -->"

# A live board is updated on every change of state, and in this work something changes most days. A week with no
# update means the board was forgotten or the work stopped; either way a reader should not be told it is "now".
# The weekly guard run (Monday) turns CI red within a week of passing the limit, with no commit needed.
MAX_AGE_DAYS = 7
DONE_MAX_AGE_DAYS = 14   # "done recently" means the last few days; two weeks is the outer edge
MAX_TEXT = 300           # one plain sentence; the full account lives on the page it links to
LISTS = {"done_recently": (1, 8), "running": (1, 6), "waiting_on_owner": (0, 6), "next": (1, 6)}
FIELDS = {"headline": {"label", "figure", "value", "of", "also"}, "done_recently": {"date", "text"},
          "running": {"text"}, "waiting_on_owner": {"text"}, "next": {"text"}}
TITLES = {"running": "Running now", "waiting_on_owner": "Waiting on the owner", "next": "Next, in order"}
AS_OF = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}) UTC$")


def _progress_module():
    spec = importlib.util.spec_from_file_location("build_progress", os.path.join(ROOT, "scripts", "build-progress.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bp = _progress_module()
Fail = bp.Fail


# The headline figures a board may show, each as (value, of) read from progress.yml, and the same pair in stats.yml
# where stats.yml holds it. A figure not listed here cannot be on the board: every headline number has a checked source.
def _live(d, key):
    return sum(x[key] for x in d["drills"] if x["where"] == "live")


FIGURES = {
    "steps_done": (lambda d: (d["counts"]["steps_done"], d["counts"]["steps_total"]), ("evidence.steps_done", "evidence.steps_total")),
    "rules_built": (lambda d: (d["counts"]["rules_built"], d["counts"]["rules_total"]), ("evidence.rules_built", "evidence.rules_total")),
    "rules_partly": (lambda d: (d["counts"]["rules_partly"], d["counts"]["rules_total"]), ("evidence.rules_partly", "evidence.rules_total")),
    "drills_home_passed": (lambda d: (_live(d, "passed"), _live(d, "run")), None),
    "single_points_fixed": (lambda d: (d["counts"]["single_points_fixed"], d["counts"]["single_points"]), None),
    "single_points_open": (lambda d: (d["counts"]["single_points_open"], d["counts"]["single_points"]), None),
    "records_pass": (lambda d: (d["counts"]["records_pass"], d["counts"]["records"]), ("repo.records_pass", "repo.records")),
}
# `also` adds a second figure to a headline line ("20 partly"); the word names which one, so it is checked too.
ALSO = {"partly": "rules_partly", "open": "single_points_open"}


# ------------------------------------------------------------------ reading and checking now.yml

def as_of_time(s):
    m = AS_OF.match(s) if isinstance(s, str) else None
    if not m or not bp.is_date(m.group(1)) or int(m.group(2)) > 23 or int(m.group(3)) > 59:
        return None
    return dt.datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}:{m.group(3)}:00+00:00")


def load(root):
    with open(os.path.join(root, DATA), encoding="utf-8") as fh:
        d = bp.parse(fh.read(), DATA)
    for k in LISTS:
        if k in d and d[k] is None:
            d[k] = []   # an empty list is written as the bare key
    return d


def text_problems(where, t):
    p = []
    if not isinstance(t, str) or not t.strip():
        return [f"{where}: text must be a non-empty double-quoted sentence"]
    if len(t) > MAX_TEXT:
        p.append(f"{where}: {len(t)} characters (limit {MAX_TEXT}): one plain sentence, the rest on the page it links to")
    if "{{" in t or "{%" in t:
        p.append(f"{where}: contains Liquid; the README cannot render it, type the fact")
    if "—" in t:
        p.append(f"{where}: contains an em dash; write two sentences or a comma")
    if not t.rstrip().endswith((".", ")")):
        p.append(f"{where}: does not end with a full stop; each item is one plain sentence")
    if re.search(r"\]\((?!https://|[a-z0-9-]+\.html(#[a-z0-9-]+)?\))", t):
        p.append(f"{where}: a link must name a site page (page.html or page.html#anchor) or a full https:// address")
    return p


def validate(d):
    p = []
    known = {"as_of", "headline", *LISTS}
    for k in d:
        if k not in known:
            p.append(f"{DATA}: '{k}' is not a key this board knows ({', '.join(sorted(known))})")
    when = as_of_time(d.get("as_of"))
    if when is None:
        p.append(f"{DATA}: as_of must be a quoted \"YYYY-MM-DD HH:MM UTC\"")
    h = d.get("headline")
    if not isinstance(h, list) or not 3 <= len(h) <= 5:
        p.append(f"{DATA}: headline must be a list of 3 to 5 figures")
        h = []
    for i, x in enumerate(h, 1):
        w = f"{DATA}: headline {i}"
        for k in x:
            if k not in FIELDS["headline"]:
                p.append(f"{w}: '{k}' is not a headline field")
        if not bp.kind_ok(x.get("label"), "str"):
            p.append(f"{w}: label must be a quoted phrase")
        if x.get("figure") not in FIGURES:
            p.append(f"{w}: figure {x.get('figure')!r} is not one of {', '.join(FIGURES)}; every headline number needs a checked source")
        if not (bp.kind_ok(x.get("value"), "int") and bp.kind_ok(x.get("of"), "int")) or x.get("value", 0) > x.get("of", 0):
            p.append(f"{w}: value and of must be whole numbers, value no more than of")
        if "also" in x:
            m = re.match(r"^(\d+) (\w+)$", str(x["also"]))
            if not m or m.group(2) not in ALSO:
                p.append(f"{w}: also must be \"N {'|'.join(ALSO)}\"")
    for k, (lo, hi) in LISTS.items():
        items = d.get(k)
        if not isinstance(items, list) or not lo <= len(items) <= hi:
            p.append(f"{DATA}: {k} must be a list of {lo} to {hi} items")
            continue
        for i, x in enumerate(items, 1):
            for f in x:
                if f not in FIELDS[k]:
                    p.append(f"{DATA}: {k} {i}: '{f}' is not a field of {k}")
            p += text_problems(f"{DATA}: {k} {i}", x.get("text"))
    done = d.get("done_recently") if isinstance(d.get("done_recently"), list) else []
    dates = [x.get("date") for x in done]
    for i, s in enumerate(dates, 1):
        if not bp.is_date(s):
            p.append(f"{DATA}: done_recently {i}: date must be a quoted \"YYYY-MM-DD\"")
        elif when is not None:
            age = (when.date() - dt.date.fromisoformat(s)).days
            if age < 0:
                p.append(f"{DATA}: done_recently {i}: {s} is after as_of")
            elif age > DONE_MAX_AGE_DAYS:
                p.append(f"{DATA}: done_recently {i}: {s} is {age} days before as_of (limit {DONE_MAX_AGE_DAYS}): "
                         "it is no longer recent, drop it (Recently on the landing page keeps the record)")
    if all(bp.is_date(s) for s in dates) and dates != sorted(dates, reverse=True):
        p.append(f"{DATA}: done_recently must be newest first")
    return p


def headline_pairs(x):
    """[(figure, value, of)] that one headline line claims."""
    out = [(x["figure"], x["value"], x["of"])]
    m = re.match(r"^(\d+) (\w+)$", str(x.get("also", "")))
    if m and m.group(2) in ALSO:
        out.append((ALSO[m.group(2)], int(m.group(1)), x["of"]))
    return out


def source_problems(root, d, when):
    """A source dated after the board's as_of has the last word: the board must be read again when one disagrees."""
    p = []
    try:
        prog = bp.load(root)
    except (Fail, FileNotFoundError):
        prog = None
    if prog and bp.is_date(prog.get("as_of")) and prog["as_of"] > when.date().isoformat():
        for x in d["headline"]:
            for fig, v, of in headline_pairs(x):
                want = FIGURES[fig][0](prog)
                if (v, of) != want:
                    p.append(f"{PROGRESS} (as of {prog['as_of']}, after the board's {d['as_of']}) has {fig} = {want[0]} of "
                             f"{want[1]}, the board says {v} of {of}. Read the board again and move as_of")
    stats = os.path.join(root, STATS)
    if os.path.isfile(stats):
        gen, figs = bp.read_stats(stats)
        try:
            measured = dt.datetime.fromisoformat(gen.replace("Z", "+00:00")) if gen else None
        except ValueError:
            measured = None
        if measured and measured > when:
            for x in d["headline"]:
                for fig, v, of in headline_pairs(x):
                    keys = FIGURES[fig][1]
                    if keys and all(k in figs for k in keys) and (str(v), str(of)) != (figs[keys[0]], figs[keys[1]]):
                        p.append(f"{STATS} (measured {gen}, after the board's {d['as_of']}) has {keys[0]} = {figs[keys[0]]} "
                                 f"of {figs[keys[1]]}, the board says {v} of {of}. Read the board again and move as_of")
    return p


# ------------------------------------------------------------------ the README block

def absolute(t):
    """A site-relative link (page.html) works on the site; in the README it must name the site."""
    return re.sub(r"\]\(([a-z0-9-]+\.html(?:#[a-z0-9-]+)?)\)", lambda m: f"]({SITE}{m.group(1)})", t)


def figure_text(x):
    s = f"**{x['value']} of {x['of']}** {x['label'][:1].lower()}{x['label'][1:]}"
    return s + (f" ({x['also']})" if x.get("also") else "")


def render(d):
    """The README block, markers included. Generated, so it is never edited by hand."""
    out = [START,
           "<!-- Written by scripts/build-now.py from docs/_data/now.yml; edit the data file and run it with --write. -->",
           "",
           f"*As of {d['as_of']}. Updated on every change of state; the full board, with what was done recently, is on "
           f"[Now]({SITE}now.html).*",
           "",
           "; ".join(figure_text(x) for x in d["headline"]) + ".",
           ""]
    for k in ("running", "waiting_on_owner", "next"):
        if not d[k]:
            continue
        out.append(f"**{TITLES[k]}:**")
        out.append("")
        for i, x in enumerate(d[k], 1):
            out.append(f"{i}. {absolute(x['text'])}" if k == "next" else f"- {absolute(x['text'])}")
        out.append("")
    out.append(END)
    return "\n".join(out)


def splice(readme_text, block):
    if readme_text.count(START) != 1 or readme_text.count(END) != 1 or readme_text.index(START) > readme_text.index(END):
        raise Fail(f"{README} must hold exactly one {START} ... {END} pair, in that order")
    a = readme_text.index(START)
    b = readme_text.index(END) + len(END)
    return readme_text[:a] + block + readme_text[b:]


# ------------------------------------------------------------------ the check

def check(root, now):
    try:
        d = load(root)
    except Fail as e:
        return [str(e)]
    except FileNotFoundError:
        return [f"{DATA} is missing"]
    problems = validate(d)
    if problems:
        return problems
    when = as_of_time(d["as_of"])
    if when > now + dt.timedelta(minutes=10):
        problems.append(f"{DATA}: as_of {d['as_of']} is in the future")
    elif now - when > dt.timedelta(days=MAX_AGE_DAYS):
        problems.append(f"{DATA}: as_of {d['as_of']} is {(now - when).days} days old (limit {MAX_AGE_DAYS}): the board says "
                        "'now'. Read the state again, update the lists and as_of, then python3 scripts/build-now.py --write")
    problems += source_problems(root, d, when)
    try:
        with open(os.path.join(root, README), encoding="utf-8") as fh:
            have = fh.read()
    except FileNotFoundError:
        return problems + [f"{README} is missing"]
    try:
        if splice(have, render(d)) != have:
            problems.append(f"{README}: the now block is not what the script writes from {DATA}. "
                            "Run: python3 scripts/build-now.py --write")
    except Fail as e:
        problems.append(str(e))
    return problems


# ------------------------------------------------------------------ self-test

def self_test():
    real = ROOT
    d = load(real)
    when = as_of_time(d["as_of"])
    base = check(real, when)
    if base:
        sys.exit("self-test: the real tree does not pass, so no planted fault can be judged:\n  " + "\n  ".join(base))
    n = 0

    def case(label, edit, want):
        nonlocal n
        with tempfile.TemporaryDirectory() as tmp:
            for rel in (DATA, PROGRESS, STATS, README, "scripts/build-progress.py"):
                os.makedirs(os.path.join(tmp, os.path.dirname(rel) or "."), exist_ok=True)
                shutil.copy(os.path.join(real, rel), os.path.join(tmp, rel))
            at = edit(tmp) or when
            got = check(tmp, at)
            if not any(want in g for g in got):
                sys.exit(f"self-test FAILED: '{label}' was not refused with '{want}'; got: {got}")
            n += 1

    def sub(rel, old, new, count=1):
        def edit(tmp):
            p = os.path.join(tmp, rel)
            with open(p, encoding="utf-8") as fh:
                t = fh.read()
            if old not in t:
                sys.exit(f"self-test: {old!r} is not in {rel}, the planted fault would change nothing")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(t.replace(old, new, count))
        return edit

    first = d["running"][0]["text"]
    h0 = d["headline"][0]
    case("a board older than the limit", lambda tmp: when + dt.timedelta(days=MAX_AGE_DAYS, minutes=1), "days old")
    case("a board dated in the future", lambda tmp: when - dt.timedelta(hours=1), "in the future")
    case("an as_of with no time", sub(DATA, f'as_of: "{d["as_of"]}"', f'as_of: "{when.date()}"'), "HH:MM UTC")
    case("a README block edited by hand", sub(README, first, first.replace(".", ", edited.", 1)), "is not what the script writes")
    case("a data change without --write", sub(DATA, first, first.replace(".", ", changed.", 1)), "is not what the script writes")
    case("a README without the block", sub(README, START, "<!-- no marker -->"), "exactly one")
    case("a README with two blocks", sub(README, END, END + "\n" + START + "\n" + END), "exactly one")
    case("a list item that is a wall of text", sub(DATA, first, "word " * 70 + "."), "characters (limit")
    case("Liquid in an item", sub(DATA, first, "{{ site.data.stats.cluster.nodes }} nodes."), "contains Liquid")
    case("an em dash in an item", sub(DATA, first, first.replace(" ", " — ", 1)), "em dash")
    case("an item that is not a sentence", sub(DATA, first, first.rstrip(".")), "full stop")
    case("a link to somewhere that is not a site page", sub(DATA, first, first[:-1] + " ([x](/etc/hosts))."), "a link must name")
    case("a stray key", sub(DATA, "running:\n", "owner_notes:\n  - text: \"x.\"\nrunning:\n"), "is not a key this board knows")
    case("an empty running list", sub(DATA, f'running:\n  - text: "{first}"', 'running:\n  - text: ""'), "non-empty")
    case("too many headline figures", sub(DATA, "headline:\n", "headline:\n" + (
        f'  - label: "x"\n    figure: "{h0["figure"]}"\n    value: {h0["value"]}\n    of: {h0["of"]}\n') * 3), "3 to 5 figures")
    case("a headline figure with no checked source", sub(DATA, f'figure: "{h0["figure"]}"', 'figure: "happiness"'), "checked source")
    case("a headline value above its total", sub(DATA, f"    value: {h0['value']}\n    of: {h0['of']}",
                                                 f"    value: {h0['of'] + 1}\n    of: {h0['of']}"), "no more than of")
    done = d["done_recently"]
    old = (when.date() - dt.timedelta(days=DONE_MAX_AGE_DAYS + 1)).isoformat()
    case("a done item no longer recent", sub(DATA, f'date: "{done[-1]["date"]}"', f'date: "{old}"'), "no longer recent")
    later = (when.date() + dt.timedelta(days=1)).isoformat()
    case("a done item dated after as_of", sub(DATA, f'date: "{done[0]["date"]}"', f'date: "{later}"'), "after as_of")
    if len(done) >= 2 and done[0]["date"] != done[-1]["date"]:
        # the oldest item moved to the top: its date is now older than the one after it
        def swap(tmp):
            p = os.path.join(tmp, DATA)
            with open(p, encoding="utf-8") as fh:
                t = fh.read()
            blocks = re.split(r"(?m)^(?=  - date:)", t.split("\nrunning:", 1)[0])
            head, items = blocks[0], blocks[1:]
            items[-1] = items[-1].rstrip("\n") + "\n"
            t = t.replace("".join(blocks).rstrip("\n"), (head + items[-1] + "".join(items[:-1])).rstrip("\n"), 1)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(t)
        case("done items out of order", swap, "newest first")

    def newer_progress(tmp):
        p = os.path.join(tmp, PROGRESS)
        with open(p, encoding="utf-8") as fh:
            t = fh.read()
        newer = (when.date() + dt.timedelta(days=1)).isoformat()
        t = re.sub(r'^as_of: "[^"]*"', f'as_of: "{newer}"', t, count=1, flags=re.M)
        t = re.sub(r"^  single_points_fixed: (\d+)$", lambda m: f"  single_points_fixed: {int(m.group(1)) + 1}", t, count=1, flags=re.M)
        t = re.sub(r"^  single_points_open: (\d+)$", lambda m: f"  single_points_open: {int(m.group(1)) - 1}", t, count=1, flags=re.M)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t)
        return when + dt.timedelta(days=1)
    if any(f == "single_points_fixed" for x in d["headline"] for f, _, _ in headline_pairs(x)):
        case("a newer progress.yml that disagrees", newer_progress, "has single_points_fixed")

    def newer_stats(tmp):
        # measured an hour after the board was read, and disagreeing with it: the board must be read again
        later = (when + dt.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        p = os.path.join(tmp, STATS)
        with open(p, encoding="utf-8") as fh:
            t = fh.read()
        t = re.sub(r'^generated_at: "[^"]*"', f'generated_at: "{later}"', t, count=1, flags=re.M)
        t = re.sub(r"^  steps_done: \d+$", "  steps_done: 11", t, count=1, flags=re.M)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t)
        return when + dt.timedelta(hours=2)
    if any(f == "steps_done" for x in d["headline"] for f, _, _ in headline_pairs(x)):
        case("a newer stats.yml that disagrees", newer_stats, "has evidence.steps_done = 11")
    # --write puts the block back between the markers and leaves the rest alone
    sample = f"# Title\nintro\n{START}\nOLD\n{END}\noutro\n"
    out = splice(sample, render(d))
    if "OLD" in out or not out.startswith("# Title\nintro\n") or not out.endswith("\noutro\n"):
        sys.exit("self-test FAILED: the README block was not spliced between the markers")
    print(f"ok: build-now.py self-test, {n} planted faults each refused, and the README block spliced between its markers")


def main(argv):
    try:
        if argv[:1] == ["--self-test"]:
            self_test()
            return 0
        if argv[:1] == ["--check"]:
            now = dt.datetime.now(dt.timezone.utc)
            if "--now" in argv:
                now = dt.datetime.fromisoformat(argv[argv.index("--now") + 1].replace("Z", "+00:00"))
            # Run from the root of the tree it checks, which may be a scratch copy (test-guard.sh).
            problems = check(os.getcwd(), now)
            if problems:
                print("\n".join(problems))
                return 1
            print(f"ok: {DATA} is fresh and well formed, and the README block is in step")
            return 0
        d = load(ROOT)
        p = validate(d)
        if p:
            sys.exit("build-now: " + "\n  ".join(p))
        block = render(d)
        if "--stdout" in argv:
            print(block)
            return 0
        if argv[:1] == ["--write"]:
            path = os.path.join(ROOT, README)
            with open(path, encoding="utf-8") as fh:
                have = fh.read()
            new = splice(have, block)
            if new != have:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
            print(f"{'wrote' if new != have else 'unchanged:'} the now block in {README}")
            return 0
        sys.exit(__doc__)
    except Fail as e:
        sys.exit(f"build-now: {e}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
