#!/usr/bin/env python3
"""The Progress page's picture: write its data from docs/_data/progress.yml, and check that nothing is out of step.

docs/_data/progress.yml is copied by hand, on its as_of day, from the private platform repository's generated status page,
its plan and its run records. This script turns it into docs/assets/diagrams/progress-data.tex, which progress.tex draws, so
no number in the picture is typed into the drawing. The data digest goes into the built PDF (document info) and the PNG (a
tEXt chunk), so a picture drawn from older data can be told apart.

  build-progress.py                    write progress-data.tex
  build-progress.py --stdout           print it instead
  build-progress.py --stamp-png P D    copy the digest of PDF D into PNG P (the diagrams Makefile runs this)
  build-progress.py --check            what the guard runs, from the root of the tree it checks: fails when
     1. progress.yml has the wrong shape, its sums do not add up, or not exactly one phase is current;
     2. progress.yml is dated in the future or more than MAX_AGE_DAYS old;
     3. docs/_data/stats.yml was measured after progress.yml's day and disagrees with a figure both hold;
     4. progress-data.tex is not what this script writes now, or progress.pdf / progress.png carry another digest;
     5. a count typed in docs/progress.md's front matter ("N of M") is not a count of progress.yml.
  build-progress.py --self-test        plant each fault above in a scratch copy and require a refusal

Standard library only: the guard runs with python3 and nothing installed.
"""
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = "docs/_data/progress.yml"
STATS = "docs/_data/stats.yml"
OUT = "docs/assets/diagrams/progress-data.tex"
PDF = "docs/assets/diagrams/progress.pdf"
PNG = "docs/assets/diagrams/progress.png"
PAGE = "docs/progress.md"
MAX_AGE_DAYS = 21  # the same limit as stats.yml: a hand-copied count older than this misleads

STEP_STATES = ("done", "done-on-kind", "partly", "not-started", "gated")
PHASE_STATES = ("done", "partly", "current", "not-started")
GROUPS = ("build", "break", "upgrade")
WHERE = ("live", "simulated")
COUNTS = (("steps_total", "int"), ("steps_done", "int"), ("steps_done_on_kind", "int"), ("steps_partly", "int"),
          ("steps_not_started", "int"), ("steps_gated", "int"), ("rules_total", "int"), ("rules_built", "int"),
          ("rules_partly", "int"), ("rules_not_built", "int"), ("records", "int"), ("records_pass", "int"),
          ("records_fail", "int"), ("records_partial", "int"), ("records_note", "int"), ("records_latest", "date"),
          ("single_points", "int"), ("single_points_accepted", "int"), ("single_points_fixed", "int"),
          ("single_points_open", "int"))
LISTS = {
    "drills": (("kind", "str"), ("short", "str"), ("where", "str"), ("dates", "str"), ("run", "int"), ("passed", "int"),
               ("what", "str")),
    "phases": (("number", "int"), ("title", "str"), ("group", "str"), ("state", "str"), ("note", "str")),
    "steps": (("number", "int"), ("title", "str"), ("state", "str")),
    "objectives": (("name", "str"), ("rules", "int"), ("built", "int"), ("partly", "int")),
    "next": (("text", "str"),),
}
# The figures progress.yml shares with the generated stats.yml (progress key -> stats group.key).
SHARED = {"steps_total": "evidence.steps_total", "steps_done": "evidence.steps_done",
          "steps_done_on_kind": "evidence.steps_done_on_kind", "steps_partly": "evidence.steps_partly",
          "steps_not_started": "evidence.steps_not_started", "steps_gated": "evidence.steps_gated",
          "rules_total": "evidence.rules_total", "rules_built": "evidence.rules_built",
          "rules_partly": "evidence.rules_partly", "single_points_accepted": "evidence.single_points_accepted",
          "single_points_fixed": "evidence.single_points_fixed", "single_points_open": "evidence.single_points_open",
          "records": "repo.records", "records_pass": "repo.records_pass", "records_fail": "repo.records_fail",
          "records_partial": "repo.records_partial", "records_note": "repo.records_note"}
DIGEST_LINE = re.compile(r"^\\newcommand\{\\ProgressDataDigest\}\{([0-9a-f]+)\}$", re.M)
MARK = re.compile(rb"progress-data ([0-9a-f]{16})")


class Fail(Exception):
    pass


# ------------------------------------------------------------------ reading progress.yml

def parse(text, name=DATA):
    """Read the subset progress.yml is written in: `key: scalar`, a group of `  key: scalar`, or a list of maps
    (`  - key: scalar` then `    key: scalar`). Scalars are JSON: whole numbers or double-quoted strings."""
    data, group, item = {}, None, None

    def val(s, n):
        try:
            v = json.loads(s)
        except ValueError:
            raise Fail(f"{name}:{n}: {s[:40]!r} is not a whole number or a double-quoted string") from None
        if not isinstance(v, (int, str)) or isinstance(v, bool):
            raise Fail(f"{name}:{n}: only whole numbers and double-quoted strings are accepted")
        return v

    def put(d, k, v, n):
        if k in d:
            raise Fail(f"{name}:{n}: the key '{k}' appears twice (the last one would silently win)")
        d[k] = v

    for n, raw in enumerate(text.split("\n"), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^([a-z0-9_]+):(?: (.*))?$", raw)
        if m:
            put(data, m.group(1), val(m.group(2), n) if m.group(2) else None, n)
            group = None if m.group(2) else m.group(1)
            item = None
            continue
        m = re.match(r"^  - ([a-z0-9_]+): (.*)$", raw)
        if m and group:
            if data[group] is None:
                data[group] = []
            if not isinstance(data[group], list):
                raise Fail(f"{name}:{n}: '{group}' mixes list items and keys")
            item = {}
            data[group].append(item)
            put(item, m.group(1), val(m.group(2), n), n)
            continue
        m = re.match(r"^    ([a-z0-9_]+): (.*)$", raw)
        if m and item is not None:
            put(item, m.group(1), val(m.group(2), n), n)
            continue
        m = re.match(r"^  ([a-z0-9_]+): (.*)$", raw)
        if m and group:
            if data[group] is None:
                data[group] = {}
            if not isinstance(data[group], dict):
                raise Fail(f"{name}:{n}: '{group}' mixes keys and list items")
            put(data[group], m.group(1), val(m.group(2), n), n)
            continue
        raise Fail(f"{name}:{n}: a line of an unexpected shape")
    return data


def is_date(s):
    if not isinstance(s, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return False
    try:
        dt.date.fromisoformat(s)
    except ValueError:
        return False
    return True


def kind_ok(v, kind):
    if kind == "int":
        return isinstance(v, int) and v >= 0
    if kind == "date":
        return is_date(v)
    return isinstance(v, str) and v.strip() != ""


def validate(d):
    """Every shape and sum problem, as a list of sentences."""
    p = []
    if not is_date(d.get("as_of")):
        p.append("as_of must be a quoted date, \"YYYY-MM-DD\"")
    if not kind_ok(d.get("now"), "str"):
        p.append("now must be a quoted sentence: what the current phase is doing")
    c = d.get("counts")
    if not isinstance(c, dict):
        return p + ["counts must be a group of figures"]
    for k, kind in COUNTS:
        if not kind_ok(c.get(k), kind):
            p.append(f"counts.{k} is missing or not a {'date' if kind == 'date' else 'whole number'}")
    for k in c:
        if k not in dict(COUNTS):
            p.append(f"counts.{k} is not a figure this script knows (add it to COUNTS or remove it)")
    for g, fields in LISTS.items():
        rows = d.get(g)
        if not isinstance(rows, list) or not rows:
            p.append(f"{g} must be a list with at least one item")
            continue
        for i, row in enumerate(rows):
            for k, kind in fields:
                if not kind_ok(row.get(k), kind):
                    p.append(f"{g}[{i}].{k} is missing or of the wrong kind")
            for k in row:
                if k not in dict(fields):
                    p.append(f"{g}[{i}].{k} is not a field of {g}")
    for k in d:
        if k not in ("as_of", "now", "counts", *LISTS):
            p.append(f"'{k}' is not a key of progress.yml")
    if p:
        return p

    def adds(label, total, parts):
        if sum(parts) != total:
            p.append(f"{label}: the parts add up to {sum(parts)}, not {total}")

    adds("steps", c["steps_total"], [c["steps_done"], c["steps_done_on_kind"], c["steps_partly"],
                                      c["steps_not_started"], c["steps_gated"]])
    adds("rules", c["rules_total"], [c["rules_built"], c["rules_partly"], c["rules_not_built"]])
    adds("records", c["records"], [c["records_pass"], c["records_fail"], c["records_partial"], c["records_note"]])
    adds("single points", c["single_points"], [c["single_points_accepted"], c["single_points_fixed"],
                                               c["single_points_open"]])
    if c["records_latest"] > d["as_of"]:
        p.append(f"counts.records_latest ({c['records_latest']}) is after as_of ({d['as_of']})")

    steps = d["steps"]
    if [s["number"] for s in steps] != list(range(len(steps))):
        p.append("steps must be numbered 0, 1, 2 ... in order")
    if len(steps) != c["steps_total"]:
        p.append(f"steps lists {len(steps)} steps, counts.steps_total says {c['steps_total']}")
    for s in steps:
        if s["state"] not in STEP_STATES:
            p.append(f"step {s['number']}: state '{s['state']}' is not one of {', '.join(STEP_STATES)}")
    for st, key in zip(STEP_STATES, ("steps_done", "steps_done_on_kind", "steps_partly", "steps_not_started", "steps_gated")):
        have = sum(1 for s in steps if s["state"] == st)
        if have != c[key]:
            p.append(f"steps: {have} in state {st}, counts.{key} says {c[key]}")

    phases = d["phases"]
    if [x["number"] for x in phases] != list(range(len(phases))):
        p.append("phases must be numbered 0, 1, 2 ... in order")
    for x in phases:
        if x["state"] not in PHASE_STATES:
            p.append(f"phase {x['number']}: state '{x['state']}' is not one of {', '.join(PHASE_STATES)}")
        if x["group"] not in GROUPS:
            p.append(f"phase {x['number']}: group '{x['group']}' is not one of {', '.join(GROUPS)}")
    order = [GROUPS.index(x["group"]) for x in phases if x["group"] in GROUPS]
    if order != sorted(order):
        p.append("phases must run build, then break, then upgrade")
    cur = [x["number"] for x in phases if x["state"] == "current"]
    if len(cur) != 1:
        p.append(f"exactly one phase must be current, found {len(cur)}")

    objs = d["objectives"]
    adds("objective rules", c["rules_total"], [o["rules"] for o in objs])
    adds("objective rules built", c["rules_built"], [o["built"] for o in objs])
    adds("objective rules partly built", c["rules_partly"], [o["partly"] for o in objs])
    for o in objs:
        if o["built"] + o["partly"] > o["rules"]:
            p.append(f"objective '{o['name']}': built and partly built exceed its {o['rules']} rules")

    for x in d["drills"]:
        if x["passed"] > x["run"]:
            p.append(f"drills '{x['kind']}': {x['passed']} passed of {x['run']} run")
        if x["where"] not in WHERE:
            p.append(f"drills '{x['kind']}': where must be one of {', '.join(WHERE)}")
    if not any(x["where"] == "live" for x in d["drills"]):
        p.append("drills: at least one kind must be live")
    return p


def load(root):
    try:
        with open(os.path.join(root, DATA), encoding="utf-8") as fh:
            d = parse(fh.read())
    except FileNotFoundError:
        raise Fail(f"{DATA} is missing") from None
    problems = validate(d)
    if problems:
        raise Fail(f"{DATA}: " + "; ".join(problems))
    return d


# ------------------------------------------------------------------ writing progress-data.tex

TEX_ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def tex(s):
    return "".join(TEX_ESC.get(ch, ch) for ch in str(s))


def tiles(d):
    c = d["counts"]
    live = [x for x in d["drills"] if x["where"] == "live"]
    sim = [x for x in d["drills"] if x["where"] == "simulated"]
    ran = ", ".join(f"{x['run']} {x['short']}" for x in live)
    extra = "".join(f"; and {x['passed']} of {x['run']} {x['short']} on a simulated cluster" for x in sim)
    return [
        (c["steps_done"], c["steps_total"], "steps of the build order done",
         f"{c['steps_done_on_kind']} more done on a test cluster only, {c['steps_partly']} partly, "
         f"{c['steps_not_started']} not started, {c['steps_gated']} waiting on its gate"),
        (c["rules_built"], c["rules_total"], "objective rules built",
         f"{c['rules_partly']} partly built, {c['rules_not_built']} not built. Built means a check enforces the rule"),
        (sum(x["passed"] for x in live), sum(x["run"] for x in live), "drills passed on the home site",
         f"{ran}{extra}"),
        (c["records_pass"], c["records"], "run records that pass",
         f"{c['records_fail']} fail, {c['records_partial']} partly pass, {c['records_note']} are notes. "
         f"The latest is dated {c['records_latest']}"),
        (c["single_points_fixed"], c["single_points"], "single points of failure fixed",
         f"{c['single_points_accepted']} accepted, {c['single_points_open']} open. Fixed needs a power-off that proves it"),
    ]


def render(d):
    """progress-data.tex as text. Deterministic: the same data gives the same bytes."""
    out = ["% Generated by scripts/build-progress.py from docs/_data/progress.yml. Do not edit: the guard fails when this",
           "% file is not what the script writes now. progress.tex draws it.", ""]
    out.append(rf"\newcommand{{\ProgressAsOf}}{{{d['as_of']}}}")
    out.append(r"\newcommand{\ProgressTiles}{%")
    for k, (v, of, label, sub) in enumerate(tiles(d)):
        out.append(rf"  \ProgressTile{{{k}}}{{{v}}}{{{of}}}{{{tex(label)}}}{{{tex(sub)}}}%")
    out.append("}")
    groups = []
    for x in d["phases"]:
        if groups and groups[-1][0] == x["group"]:
            groups[-1][2] = x["number"]
        else:
            groups.append([x["group"], x["number"], x["number"]])
    out.append(r"\newcommand{\ProgressGroups}{%")
    for g, a, b in groups:
        out.append(rf"  \ProgressGroup{{{g}}}{{{a}}}{{{b}}}%")
    out.append("}")
    out.append(r"\newcommand{\ProgressPhases}{%")
    for x in d["phases"]:
        out.append(rf"  \ProgressPhase{{{x['number']}}}{{{x['state']}}}{{{tex(x['title'])}}}{{{tex(x['note'])}}}%")
    out.append("}")
    out.append(rf"\newcommand{{\ProgressPhaseCount}}{{{len(d['phases'])}}}")
    now = next(x for x in d["phases"] if x["state"] == "current")
    out.append(rf"\newcommand{{\ProgressNowPhase}}{{{now['number']}}}")
    out.append(rf"\newcommand{{\ProgressNowTitle}}{{{tex(now['title'])}}}")
    out.append(rf"\newcommand{{\ProgressNow}}{{{tex(d['now'])}}}")
    out.append(r"\newcommand{\ProgressSteps}{%")
    for s in d["steps"]:
        out.append(rf"  \ProgressStep{{{s['number']}}}{{{s['state']}}}{{{tex(s['title'])}}}%")
    out.append("}")
    out.append(rf"\newcommand{{\ProgressStepCount}}{{{len(d['steps'])}}}")
    out.append(r"\newcommand{\ProgressDrills}{%")
    for k, x in enumerate(d["drills"]):
        out.append(rf"  \ProgressDrill{{{k}}}{{{tex(x['kind'])}}}{{{x['where']}}}{{{tex(x['dates'])}}}"
                   rf"{{{x['run']}}}{{{x['passed']}}}%")
    out.append("}")
    out.append(r"\newcommand{\ProgressRules}{%")
    for k, o in enumerate(d["objectives"]):
        out.append(rf"  \ProgressRule{{{k}}}{{{tex(o['name'])}}}{{{o['rules']}}}{{{o['built']}}}{{{o['partly']}}}"
                   rf"{{{o['rules'] - o['built'] - o['partly']}}}%")
    out.append("}")
    out.append(rf"\newcommand{{\ProgressObjectiveCount}}{{{len(d['objectives'])}}}")
    out.append(r"\newcommand{\ProgressNext}{%")
    for x in d["next"]:
        out.append(rf"  \item {tex(x['text'])}%")
    out.append("}")
    body = "\n".join(out) + "\n"
    return body + rf"\newcommand{{\ProgressDataDigest}}{{{digest(body)}}}" + "\n"


def digest(body):
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------ the digest in the built files

def digest_in_pdf(data):
    """The digest a PDF carries in its document info (/ProgressData), or None. xdvipdfmx may compress it."""
    m = MARK.search(data)
    if m:
        return m.group(1).decode()
    for s in re.finditer(rb"stream\r?\n", data):
        try:
            m = MARK.search(zlib.decompressobj().decompress(data[s.end():]))
        except zlib.error:
            continue
        if m:
            return m.group(1).decode()
    return None


def digest_in_png(data):
    pos = 8
    while pos + 8 <= len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind == b"tEXt":
            m = MARK.search(data[pos + 8:pos + 8 + n])
            if m:
                return m.group(1).decode()
        if kind == b"IEND":
            break
        pos += 12 + n
    return None


def stamp_png(png, digest_hex):
    """Insert (or replace) a tEXt chunk 'Comment' = 'progress-data <digest>' after the IHDR chunk."""
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise Fail("not a PNG")
    chunks, pos = [], 8
    while pos + 8 <= len(png):
        n, kind = struct.unpack(">I4s", png[pos:pos + 8])
        raw = png[pos:pos + 12 + n]
        if not (kind == b"tEXt" and MARK.search(raw)):
            chunks.append(raw)
        pos += 12 + n
        if kind == b"IEND":
            break
    text = b"Comment\x00progress-data " + digest_hex.encode()
    mine = struct.pack(">I", len(text)) + b"tEXt" + text + struct.pack(">I", zlib.crc32(b"tEXt" + text) & 0xFFFFFFFF)
    return png[:8] + chunks[0] + mine + b"".join(chunks[1:])


# ------------------------------------------------------------------ the check

def read_stats(path):
    """generated_at and the group.key figures of stats.yml (a flat, generated file: two levels)."""
    figures, group, gen = {}, None, None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.rstrip("\n")
            m = re.match(r"^([a-z0-9_]+):\s*(.*)$", raw)
            if m:
                group = m.group(1) if not m.group(2) else None
                if m.group(1) == "generated_at":
                    gen = m.group(2).strip().strip('"')
                continue
            m = re.match(r"^  ([a-z0-9_]+):\s*(.*)$", raw)
            if m and group:
                figures[f"{group}.{m.group(1)}"] = m.group(2).strip().strip('"')
    return gen, figures


def typed_pairs(d):
    c = d["counts"]
    live = [x for x in d["drills"] if x["where"] == "live"]
    pairs = {(c["steps_done"], c["steps_total"]), (c["rules_built"], c["rules_total"]),
             (c["records_pass"], c["records"]), (c["single_points_fixed"], c["single_points"]),
             (sum(x["passed"] for x in live), sum(x["run"] for x in live))}
    pairs |= {(x["passed"], x["run"]) for x in d["drills"]}
    return pairs


def check(root, today):
    problems = []
    try:
        d = load(root)
    except Fail as e:
        return [str(e)]
    as_of = dt.date.fromisoformat(d["as_of"])
    if as_of > today:
        problems.append(f"{DATA}: as_of {d['as_of']} is in the future")
    elif (today - as_of).days > MAX_AGE_DAYS:
        problems.append(f"{DATA}: as_of {d['as_of']} is {(today - as_of).days} days old (limit {MAX_AGE_DAYS}). Copy the "
                        "counts again from the private status page, its plan and its records, and move as_of")

    stats = os.path.join(root, STATS)
    if os.path.isfile(stats):
        gen, figures = read_stats(stats)
        if gen and is_date(gen[:10]) and gen[:10] > d["as_of"]:
            for k, sk in SHARED.items():
                if sk in figures and figures[sk] != str(d["counts"][k]):
                    problems.append(f"{STATS} (measured {gen[:10]}, after {DATA}'s {d['as_of']}) has {sk} = {figures[sk]}, "
                                    f"{DATA} has counts.{k} = {d['counts'][k]}. Copy the counts again and move as_of")

    want = render(d)
    try:
        with open(os.path.join(root, OUT), encoding="utf-8") as fh:
            have = fh.read()
    except FileNotFoundError:
        have = None
    if have != want:
        problems.append(f"{OUT} is not what the script writes from {DATA} now. Run: python3 scripts/build-progress.py && "
                        "make -C docs/assets/diagrams progress.png")
    dig = DIGEST_LINE.search(want).group(1)
    for path, read in ((PDF, digest_in_pdf), (PNG, digest_in_png)):
        try:
            with open(os.path.join(root, path), "rb") as fh:
                got = read(fh.read())
        except FileNotFoundError:
            problems.append(f"{path} is missing. Run: make -C docs/assets/diagrams progress.png")
            continue
        if got != dig:
            problems.append(f"{path} was drawn from progress data {got or '(no digest)'}, the data now is {dig}. "
                            "Run: make -C docs/assets/diagrams progress.png")

    try:
        with open(os.path.join(root, PAGE), encoding="utf-8") as fh:
            page = fh.read()
    except FileNotFoundError:
        problems.append(f"{PAGE} is missing")
        page = ""
    fm = re.match(r"^---\n(.*?)\n---\n", page, re.S)
    if page and not fm:
        problems.append(f"{PAGE} has no front matter")
    elif fm:
        pairs = typed_pairs(d)
        for m in re.finditer(r"\b(\d+) of (\d+)\b", fm.group(1)):
            if (int(m.group(1)), int(m.group(2))) not in pairs:
                problems.append(f"{PAGE}: the front matter says '{m.group(0)}', which is no count of {DATA}. Fix the sentence")
        if d["as_of"] not in fm.group(1):
            problems.append(f"{PAGE}: the front matter does not name the data's day, {d['as_of']}")
    return problems


# ------------------------------------------------------------------ self-test

def self_test():
    real = ROOT
    d = load(real)
    c = d["counts"]
    today = dt.date.fromisoformat(d["as_of"])
    base = check(real, today)
    if base:
        sys.exit("self-test: the real tree does not pass, so no planted fault can be judged:\n  " + "\n  ".join(base))
    n = 0

    def case(label, edit, want):
        nonlocal n
        with tempfile.TemporaryDirectory() as tmp:
            for rel in (DATA, STATS, OUT, PDF, PNG, PAGE):
                os.makedirs(os.path.join(tmp, os.path.dirname(rel)), exist_ok=True)
                shutil.copy(os.path.join(real, rel), os.path.join(tmp, rel))
            when = edit(tmp) or today
            got = check(tmp, when)
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

    # Plants are built from the data's own values, so a fresh copy of the counts does not break the self-test.
    case("a step count that no longer adds up",
         sub(DATA, f"steps_partly: {c['steps_partly']}", f"steps_partly: {c['steps_partly'] + 1}"), "the parts add up")
    case("a record count that no longer adds up",
         sub(DATA, f"records_pass: {c['records_pass']}", f"records_pass: {c['records_pass'] + 1}"), "records: the parts")
    case("objective rules that disagree with the total", sub(DATA, "    built: 1\n    partly: 3", "    built: 2\n    partly: 3"),
         "objective rules built")
    case("two current phases", sub(DATA, 'state: "partly"\n    note: "17', 'state: "current"\n    note: "17'),
         "exactly one phase must be current")
    case("a phase of no group", sub(DATA, 'group: "upgrade"', 'group: "later"'), "is not one of build")
    dr = d["drills"][0]
    case("more drills passed than run", sub(DATA, f"run: {dr['run']}\n    passed: {dr['passed']}",
                                            f"run: {dr['run']}\n    passed: {dr['run'] + 1}"), "passed of")
    case("a step state that is not known", sub(DATA, 'state: "gated"', 'state: "waiting"'), "is not one of done")
    case("an unquoted string", sub(DATA, 'as_of: "', "as_of: x"), "not a whole number or a double-quoted string")
    case("a stray key", sub(DATA, "counts:\n", "counts:\n  plan_items: 158\n"), "not a figure this script knows")
    case("data older than the limit", lambda tmp: today + dt.timedelta(days=MAX_AGE_DAYS + 1), "days old")
    case("data dated in the future", lambda tmp: today - dt.timedelta(days=1), "in the future")
    case("a newer stats.yml that disagrees",
         lambda tmp: (sub(STATS, 'generated_at: "', 'generated_at: "2099-01-01T00:00:00Z" #')(tmp),
                      sub(STATS, "  rules_built: ", "  rules_built: 9\n  rules_old: ")(tmp), None)[2],
         "has evidence.rules_built = 9")
    case("a picture data file edited by hand", sub(OUT, r"\ProgressTiles", r"\ProgressTilesX"), "is not what the script writes")
    case("a data change without a rebuild", sub(DATA, 'title: "The cutover"', 'title: "The cut-over"'),
         "was drawn from progress data")

    def stale_png(tmp):
        p = os.path.join(tmp, PNG)
        with open(p, "rb") as fh:
            b = fh.read()
        with open(p, "wb") as fh:
            fh.write(stamp_png(b, "0" * 16))
    case("a stale PNG", stale_png, f"{PNG} was drawn from progress data 0000")

    def stale_pdf(tmp):
        p = os.path.join(tmp, PDF)
        with open(p, "wb") as fh:
            fh.write(b"%PDF-1.5\n<< /ProgressData (progress-data " + b"0" * 16 + b") >>\n")
    case("a stale PDF", stale_pdf, f"{PDF} was drawn from progress data 0000")
    case("a typed count the data does not have",
         sub(PAGE, f"{c['steps_done']} of {c['steps_total']}", f"{c['steps_done'] + 1} of {c['steps_total']}"), "which is no count")
    day_before = (today - dt.timedelta(days=1)).isoformat()
    case("a page summary without the data's day", lambda tmp: (sub(PAGE, d["as_of"], day_before, count=99)(tmp), None)[1],
         "does not name the data's day")
    # the digest survives a compressed stream, as xdvipdfmx writes it
    blob = b"1 0 obj << /Filter /FlateDecode >> stream\n" + zlib.compress(b"/ProgressData (progress-data 0123456789abcdef)")
    if digest_in_pdf(blob) != "0123456789abcdef":
        sys.exit("self-test FAILED: a digest in a compressed stream was not read")
    print(f"ok: build-progress.py self-test, {n} planted faults each refused, and a compressed PDF digest read")


def main(argv):
    try:
        if argv[:1] == ["--self-test"]:
            self_test()
            return 0
        if argv[:1] == ["--check"]:
            today = dt.date.today()
            if "--today" in argv:
                today = dt.date.fromisoformat(argv[argv.index("--today") + 1])
            # The guard runs from the tree it checks, which may be a scratch copy (test-guard.sh), so the current
            # directory is the root here, as --data-dir docs/_data is for the other checks.
            root = os.getcwd()
            problems = check(root, today)
            if problems:
                print("\n".join(problems))
                return 1
            print(f"ok: {DATA} adds up and its picture is in step (progress-data {DIGEST_LINE.search(render(load(root))).group(1)})")
            return 0
        if argv[:1] == ["--stamp-png"]:
            if len(argv) != 3:
                sys.exit("usage: build-progress.py --stamp-png PNG PDF")
            with open(argv[2], "rb") as fh:
                dig = digest_in_pdf(fh.read())
            if not dig:
                sys.exit(f"{argv[2]} carries no progress-data digest; is progress.tex's docinfo line there?")
            with open(argv[1], "rb") as fh:
                png = fh.read()
            with open(argv[1], "wb") as fh:
                fh.write(stamp_png(png, dig))
            print(f"stamped {argv[1]} with progress-data {dig}")
            return 0
        text = render(load(ROOT))
    except Fail as e:
        sys.exit(f"build-progress: {e}")
    if "--stdout" in argv:
        sys.stdout.write(text)
        return 0
    with open(os.path.join(ROOT, OUT), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {OUT} (progress-data {DIGEST_LINE.search(text).group(1)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
