#!/usr/bin/env python3
"""Fail when a page names a stats figure that stats.yml does not have, or when a stats value is of a kind the site does not accept.

Why this exists. Jekyll renders a missing Liquid key as empty text and says nothing: "{{ site.data.stats.cluster.nodes }} nodes"
becomes " nodes" and the build is green. When the stats schema changes, every page that still names a removed key is silently
blanked. This check reads every page the way the pages name the data and fails with file:line.

Two checks, both read-only and standard library only:

  references  (default)  every Liquid reference to site.data.stats.GROUP.KEY, written in full or through an alias
                         ({% assign s = site.data.stats.cluster %} ... {{ s.nodes }}, chains of aliases, and a {% capture %} whose
                         whole body is one such reference) must name a group and key present in docs/_data/stats.yml. A key whose
                         value is 'not measured yet' is present, so it may be referenced.
  --values               every value in stats.yml is one of: a plain non-negative number (unquoted); the exact quoted string
                         'not measured yet'; a quoted date YYYY-MM-DD that is a real calendar day; a quoted UTC timestamp; or one of
                         the older quoted word, version and head shapes. Any other string where a number is expected is refused,
                         and so is a number written as a quoted string.

Usage: scripts/check-stats-refs.py [--docs DIR] [--readme FILE] [--stats FILE]
       scripts/check-stats-refs.py --values [--stats FILE]
       scripts/check-stats-refs.py --self-test
"""
import argparse
import datetime as dt
import glob
import math
import os
import re
import sys
import tempfile

NM = "not measured yet"
NUMBER = re.compile(r"^[0-9]+(\.[0-9]+)?$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
OLD_KINDS = {
    "ver": re.compile(r"^v?[0-9]+(\.[0-9]+){1,3}([+-][0-9A-Za-z.]+)?$"),
    "word": re.compile(r"^[a-z][a-z_-]{0,19}$"),
    "head": re.compile(r"^[0-9]+ commits, HEAD dated [0-9]{4}-[0-9]{2}-[0-9]{2}$"),
}
PROPERTIES = {"size"}  # Liquid properties that are valid on any hash, so they are not keys


# ------------------------------------------------------------------------------------------------ stats.yml
def scan_stats(path):
    """(groups, scalars, values): groups maps name -> {key: raw value}; scalars maps top-level name -> raw value."""
    groups, scalars, group = {}, {}, None
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
            if m:
                val = m.group(2).strip()
                if val == "" or val.startswith("#"):
                    group = m.group(1)
                    groups.setdefault(group, {})
                else:
                    scalars[m.group(1)] = (val, n)
                    group = None
                continue
            m = re.match(r"^\s+([A-Za-z0-9_]+):\s*(.*?)\s*$", line)
            if m and group is not None:
                groups[group][m.group(1)] = (m.group(2), n)
    return groups, scalars


def strip_comment(raw):
    if raw[:1] in "\"'":
        q = raw[0]
        end = raw.find(q, 1)
        return raw[: end + 1] if end > 0 else raw
    return re.sub(r"\s+#.*$", "", raw)


def value_problem(raw):
    """None if the raw YAML value is acceptable, else the reason."""
    raw = strip_comment(raw.strip())
    if raw == "":
        return "has no value"
    if raw[0] in "\"'":
        if len(raw) < 2 or raw[-1] != raw[0]:
            return f"{raw} is an unterminated string"
        s = raw[1:-1]
        if s == NM:
            return None
        if DATE.match(s):
            try:
                dt.date.fromisoformat(s)
                return None
            except ValueError:
                return f"{s!r} is not a real calendar date"
        if ISO.match(s):
            try:
                dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
                return None
            except ValueError:
                return f"{s!r} is not a real timestamp"
        if any(rx.match(s) for rx in OLD_KINDS.values()):
            return None
        if re.match(r"^[0-9]", s):
            return (f"{s!r} is a quoted string that looks like a number or a malformed date: "
                    f"write a number unquoted, a date as YYYY-MM-DD, or '{NM}'")
        return f"{s!r} is a string where a number, a date or '{NM}' is expected"
    if NUMBER.match(raw):
        return None if math.isfinite(float(raw)) else f"{raw} is not finite"
    if DATE.match(raw):
        return f"{raw} is an unquoted date: quote it, \"{raw}\""
    return f"{raw!r} is not a plain non-negative number; text must be quoted and one of an accepted kind"


# The monitoring tenant is not merged or live yet, so these figures cannot have been measured. Until it is, anything but the
# exact string is a leftover from the previous platform. When monitoring goes live, empty this set in the same change.
UNMEASURED_UNTIL_MONITORING = {
    ("observability", k)
    for k in ("scrape_targets", "alert_rules", "recording_rules", "dashboards", "metric_history_days", "alerts_reaching_a_person")
}


def check_values(stats_path):
    problems = []
    if not os.path.isfile(stats_path):
        return [f"{stats_path} is missing"]
    groups, scalars = scan_stats(stats_path)
    for g, keys in groups.items():
        for k, (raw, n) in keys.items():
            why = value_problem(raw)
            if why:
                problems.append(f"{stats_path}:{n}: {g}.{k}: {why}")
            elif (g, k) in UNMEASURED_UNTIL_MONITORING and strip_comment(raw.strip()).strip("\"'") != NM:
                problems.append(f"{stats_path}:{n}: {g}.{k}: monitoring is not live, so this must be '{NM}', not a carried-over number")
    for name, (raw, n) in scalars.items():
        why = value_problem(raw)
        if why:
            problems.append(f"{stats_path}:{n}: {name}: {why}")
    return problems


# ------------------------------------------------------------------------------------------------ references
LIQUID = re.compile(r"\{\{-?(.*?)-?\}\}|\{%-?(.*?)-?%\}", re.S)
RAW = re.compile(r"\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}", re.S)
TOKEN = re.compile(r"(?<![\w.\-])([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)")
ROOT = ("site", "data", "stats")


def blank_raw(text):
    return RAW.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def blank_strings(code):
    return re.sub(r"\"[^\"]*\"|'[^']*'", lambda m: " " * len(m.group(0)), code)


def resolve(parts, aliases):
    """The stats path (tuple below site.data.stats) a dotted token names, or None if it names something else."""
    if tuple(parts[:3]) == ROOT:
        return tuple(parts[3:])
    if parts[0] in aliases:
        return aliases[parts[0]] + tuple(parts[1:])
    return None


def path_problem(path, groups, scalars):
    if not path:
        return None
    g = path[0]
    if len(path) == 1:
        return None if (g in groups or g in scalars) else f"group '{g}' is not in stats.yml"
    if g in scalars:
        return None if path[1:] == ("size",) else f"'{g}' is a single value, it has no '{path[1]}'"
    if g not in groups:
        return f"group '{g}' is not in stats.yml"
    k = path[1]
    if k not in groups[g] and k not in PROPERTIES:
        return f"key '{g}.{k}' is not in stats.yml"
    if len(path) > 2 and not (len(path) == 3 and path[2] in PROPERTIES):
        return f"'{g}.{k}' is a single value, it has no '{path[2]}'"
    return None


def scan_file(path, text, groups, scalars):
    problems = []
    text = blank_raw(text)
    aliases = {}
    cap = None  # (name, body start)

    def line_of(pos):
        return text.count("\n", 0, pos) + 1

    def check_code(code, base_pos, shown_as=None):
        code = blank_strings(code)
        for m in TOKEN.finditer(code):
            parts = m.group(1).split(".")
            p = resolve(parts, aliases)
            if p is None:
                continue
            why = path_problem(p, groups, scalars)
            if why:
                ln = line_of(base_pos + m.start())
                problems.append(f"{path}:{ln}: Liquid reference `{m.group(1)}` -> stats {'.'.join(p) or '(root)'}: {why}")

    for m in LIQUID.finditer(text):
        code = m.group(1) if m.group(1) is not None else m.group(2)
        base = m.start(1) if m.group(1) is not None else m.start(2)
        is_tag = m.group(2) is not None
        stripped = code.strip()
        if is_tag:
            a = re.match(r"assign\s+([\w-]+)\s*=\s*(.*)$", stripped, re.S)
            if a:
                name, rhs = a.group(1), a.group(2)
                rhs_pos = base + code.index(rhs) if rhs in code else base
                check_code(rhs, rhs_pos)
                aliases.pop(name, None)
                pure = re.match(r"^([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)\s*$", blank_strings(rhs.strip()))
                if pure:
                    p = resolve(pure.group(1).split("."), aliases)
                    if p is not None and path_problem(p, groups, scalars) is None:
                        aliases[name] = p
                continue
            c = re.match(r"capture\s+([\w-]+)\s*$", stripped)
            if c:
                aliases.pop(c.group(1), None)
                cap = (c.group(1), m.end())
                continue
            if re.match(r"endcapture\b", stripped) and cap:
                body = text[cap[1]:m.start()].strip()
                one = re.match(r"^\{\{-?\s*([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)\s*-?\}\}$", body)
                if one:
                    p = resolve(one.group(1).split("."), aliases)
                    if p is not None and path_problem(p, groups, scalars) is None:
                        aliases[cap[0]] = p
                cap = None
                continue
            f = re.match(r"for\s+([\w-]+)\s+in\b", stripped)
            if f:
                aliases.pop(f.group(1), None)
        check_code(code, base)
    return problems


def check_refs(docs, readme, stats_path):
    if not os.path.isfile(stats_path):
        return [f"{stats_path} is missing, so no reference can be checked"]
    groups, scalars = scan_stats(stats_path)
    files = sorted(glob.glob(os.path.join(docs, "*.md")))
    for sub in ("_includes", "_layouts"):
        files += sorted(glob.glob(os.path.join(docs, sub, "*.html")))
    if readme and os.path.isfile(readme):
        files.append(readme)
    problems = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            problems += scan_file(f, fh.read(), groups, scalars)
    return problems


# ------------------------------------------------------------------------------------------------ self test
def self_test():
    ok = True

    def expect(label, got, want_substr=None, want_pass=False):
        nonlocal ok
        good = (not got) if want_pass else bool(got) and (want_substr is None or any(want_substr in g for g in got))
        print(f"  {'pass' if good else 'FAIL'}  {label}")
        if not good:
            ok = False
            for g in got:
                print("        " + g)

    with tempfile.TemporaryDirectory() as tmp:
        data = os.path.join(tmp, "docs", "_data")
        os.makedirs(data)
        stats = os.path.join(data, "stats.yml")
        with open(stats, "w") as fh:
            fh.write('generated_at: "2026-11-11T00:00:00Z"\ncluster:\n  nodes: 6\n  nodes_ready: 6\n  alerts: "not measured yet"\n'
                     '  drill_date: "2026-11-10"\n')
        page = os.path.join(tmp, "docs", "a.md")

        def refs(body):
            with open(page, "w") as fh:
                fh.write(body)
            return check_refs(os.path.join(tmp, "docs"), None, stats)

        expect("a full reference to an existing key passes", refs("has {{ site.data.stats.cluster.nodes }} nodes\n"), want_pass=True)
        expect("an alias chain and a capture alias pass",
               refs("{% assign st = site.data.stats %}{% assign c = st.cluster %}{{ c.nodes_ready }}\n"
                    "{% capture k %}{{ site.data.stats.cluster }}{% endcapture %}{{ k.nodes }}\n"), want_pass=True)
        expect("a nm key and a date key may be referenced", refs("{{ site.data.stats.cluster.alerts }} {{ site.data.stats.cluster.drill_date }}\n"), want_pass=True)
        expect("a missing key in a full reference fails with file:line",
               refs("one\ntwo {{ site.data.stats.cluster.gone }}\n"), "a.md:2:")
        expect("a missing key through an alias fails", refs("{% assign s = site.data.stats.cluster %}\n{% if s.gone %}x{% endif %}\n"), "a.md:2:")
        expect("a missing key through an alias chain fails",
               refs("{% assign a = site.data.stats %}{% assign b = a.cluster %}{{ b.gone | plus: 1 }}\n"), "gone")
        expect("a missing group fails", refs("{{ site.data.stats.storage.osds }}\n"), "group 'storage'")
        expect("a reference inside a raw block is not checked", refs("{% raw %}{{ site.data.stats.cluster.gone }}{% endraw %}\n"), want_pass=True)
        expect("unrelated Liquid is ignored", refs("{{ page.title }} {% for x in site.data.nav %}{{ x.gone }}{% endfor %}\n"), want_pass=True)
        expect("an alias reassigned to something else stops being checked",
               refs("{% assign s = site.data.stats.cluster %}{% assign s = page.other %}{{ s.gone }}\n"), want_pass=True)

        def vals(v):
            with open(stats, "w") as fh:
                fh.write(f'generated_at: "2026-11-11T00:00:00Z"\ncluster:\n  nodes: {v}\n')
            return check_values(stats)

        expect("a plain number is accepted", vals("6"), want_pass=True)
        expect("'not measured yet' is accepted", vals('"not measured yet"'), want_pass=True)
        expect("a quoted date is accepted", vals('"2026-11-10"'), want_pass=True)
        expect("another string where a number is expected is refused", vals('"about six"'), "string where a number")
        expect("a number written as a string is refused", vals('"12"'), "looks like a number")
        expect("a malformed date is refused", vals('"2026-13-45"'), "calendar date")
        expect("an unquoted date is refused", vals("2026-11-10"), "unquoted date")
        expect("a negative number is refused", vals("-3"), "non-negative")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--stats", default=None, help="default: DOCS/_data/stats.yml")
    ap.add_argument("--values", action="store_true", help="check the kinds of the values in stats.yml instead of the page references")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    stats = a.stats or os.path.join(a.docs, "_data", "stats.yml")
    problems = check_values(stats) if a.values else check_refs(a.docs, a.readme, stats)
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
