#!/usr/bin/env python3
"""Fail when a page has no fast-reader summary, or when its prose has not been re-read lately.

The site is long and honest and, for a fast reader, buried. Every page therefore carries an "In short" block rendered from its own
front matter (docs/_includes/in-short.html). A block that is allowed to go stale is worse than none: it is the one thing a reader
trusts without reading the rest. So this check, run by the leak guard and CI:

  * every docs/*.md has `reread: YYYY-MM-DD` and a `summary:` list of 3 to 6 items, each short, and includes the block;
  * `reread` (the summary was checked against the system) is not in the future and not older than MAX_AGE_DAYS; the optional
    `body_read` (the whole body was read in full) is not later than `reread`, not in the future, and not older than
    MAX_BODY_AGE_DAYS. Moving a date is a claim: read the page against the system first;
  * docs/_data/recently.yml (the landing page's dated "what changed" list) has well-formed, newest-first entries and its newest
    entry is not older than RECENT_MAX_AGE_DAYS, so the list cannot quietly stop being a list of recent things.

Standard library only (a small YAML subset reader: scalars and one list of scalars or one-level maps), because the guard must run
anywhere with python3 and nothing installed.
Usage: scripts/check-summaries.py [--docs DIR] [--today YYYY-MM-DD]
"""
import argparse
import datetime as dt
import glob
import os
import re
import sys

MAX_AGE_DAYS = 45          # a summary older than this has not been re-checked; the stats guard allows 21 for measurements
MAX_BODY_AGE_DAYS = 60     # the body is longer than the summary, so it is allowed to go longer between full reads
RECENT_MAX_AGE_DAYS = 45
MIN_ITEMS, MAX_ITEMS, MAX_ITEM_CHARS = 3, 6, 420
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1), text[m.end():]) if m else ("", text)


def parse_front(fm):
    """The subset the pages use: `key: scalar` and `key:` followed by `  - item` lines (items may be quoted or folded with >-)."""
    out, key, items, folding = {}, None, None, None
    for raw in fm.split("\n"):
        if folding is not None and (raw.startswith("    ") or not raw.strip()):
            folding.append(raw.strip())
            continue
        if folding is not None:
            items[-1] = " ".join(x for x in folding if x)
            folding = None
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if m and not raw.startswith(" "):
            key, val = m.group(1), m.group(2).strip()
            if val == "":
                out[key] = items = []
            else:
                out[key] = val.strip("\"'")
                items = None
            continue
        m = re.match(r"^\s+-\s*(.*)$", raw)
        if m and items is not None:
            val = m.group(1).strip()
            if val in (">-", ">", "|", "|-"):
                items.append("")
                folding = []
            else:
                items.append(val.strip("\"'") if (val[:1] in "\"'" and val[-1:] == val[:1]) else val)
    if folding is not None:
        items[-1] = " ".join(x for x in folding if x)
    return out


def check_pages(docs, today, problems):
    for path in sorted(glob.glob(os.path.join(docs, "*.md"))):
        name = os.path.basename(path)
        text = open(path, encoding="utf-8").read()
        fm, body = front_matter(text)
        meta = parse_front(fm)
        if "include in-short.html" not in body:
            problems.append(f"{name}: does not include the block ({{% include in-short.html %}}) right under its first heading")
        d = meta.get("reread", "")
        if not DATE.match(d):
            problems.append(f"{name}: front matter has no `reread: YYYY-MM-DD`")
        else:
            age = (today - dt.date.fromisoformat(d)).days
            if age < 0:
                problems.append(f"{name}: reread {d} is in the future")
            elif age > MAX_AGE_DAYS:
                problems.append(f"{name}: reread {d} is {age} days old (limit {MAX_AGE_DAYS}): read the page against the system, then move the date")
        b = meta.get("body_read", "")
        if b:
            if not DATE.match(b):
                problems.append(f"{name}: `body_read` {b!r} is not YYYY-MM-DD")
            else:
                bage = (today - dt.date.fromisoformat(b)).days
                if bage < 0:
                    problems.append(f"{name}: body_read {b} is in the future")
                elif DATE.match(d) and b > d:
                    problems.append(f"{name}: body_read {b} is later than reread {d}: the body cannot have been read after the summary was checked")
                elif bage > MAX_BODY_AGE_DAYS:
                    problems.append(f"{name}: body_read {b} is {bage} days old (limit {MAX_BODY_AGE_DAYS}): read the page in full against the system")
        items = meta.get("summary")
        if not isinstance(items, list) or not (MIN_ITEMS <= len(items) <= MAX_ITEMS):
            problems.append(f"{name}: `summary:` must be a list of {MIN_ITEMS} to {MAX_ITEMS} items (found "
                            f"{len(items) if isinstance(items, list) else 'none'})")
        else:
            for i, it in enumerate(items, 1):
                if not it.strip():
                    problems.append(f"{name}: summary item {i} is empty")
                elif len(it) > MAX_ITEM_CHARS:
                    problems.append(f"{name}: summary item {i} is {len(it)} characters (limit {MAX_ITEM_CHARS}): a summary is short")
                elif "{{" in it or "{%" in it:
                    problems.append(f"{name}: summary item {i} contains Liquid; front matter is not rendered, type the fact with its date")


def check_recently(docs, today, problems):
    path = os.path.join(docs, "_data", "recently.yml")
    if not os.path.exists(path):
        problems.append("docs/_data/recently.yml is missing (the landing page's dated list of what changed)")
        return
    entries, cur = [], None
    for raw in open(path, encoding="utf-8").read().split("\n"):
        if raw.startswith("#") or not raw.strip():
            continue
        m = re.match(r"^-\s*date:\s*(\S+)\s*$", raw)
        if m:
            cur = {"date": m.group(1).strip("\"'")}
            entries.append(cur)
            continue
        m = re.match(r"^\s+(text|link):\s*(.*)$", raw)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip().strip("\"'")
    if not (3 <= len(entries) <= 12):
        problems.append(f"recently.yml: expected 3 to 12 entries, found {len(entries)}")
    dates = []
    for e in entries:
        if not DATE.match(e.get("date", "")):
            problems.append(f"recently.yml: bad date {e.get('date')!r}")
            continue
        dates.append(e["date"])
        if not e.get("text"):
            problems.append(f"recently.yml: {e['date']} has no text")
    if dates != sorted(dates, reverse=True):
        problems.append("recently.yml: entries must be newest first")
    if dates:
        newest = dt.date.fromisoformat(dates[0])
        if newest > today:
            problems.append(f"recently.yml: newest entry {dates[0]} is in the future")
        elif (today - newest).days > RECENT_MAX_AGE_DAYS:
            problems.append(f"recently.yml: newest entry is {(today - newest).days} days old: the list of what changed has stopped being recent")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--today", default=None, help="override today's date (tests)")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.now(dt.timezone.utc).date()
    problems = []
    check_pages(a.docs, today, problems)
    check_recently(a.docs, today, problems)
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
