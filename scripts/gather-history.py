#!/usr/bin/env python3
"""Measure V1.0's history and write docs/_data/history.yml - the numbers behind docs/history.md.

V1.0 is the platform in the old private repository: first commit 2025-12-21, last commit
2026-11-05, torn down on 2026-11-10. V2.0 is its successor, in a new private repository from
2026-11-05, built on the same machines from 2026-11-10. V1.0 is dormant, so this file is FROZEN
rather than a snapshot: a second run against the same sources must give the same file (apart from
generated_at), and --check proves that it does. stats.yml's 21-day freshness rule does not apply.

What is measured, and on whose clock:
  * the V1.0 repository, by git (the committer's own clock, so the author could have set it):
    commits and days with a commit, per month; the first and last commit; numbered decision records;
  * GitHub's API for that repository (GitHub's clock): pull requests merged and Actions runs
    created, per month (UTC);
  * the V2.0 repository, by git: its first commit, and the dates of the run records of the V1.0
    teardown and the V2.0 bring-up;
  * THIS public repository, by git and GitHub's API, which anyone can repeat: commits per month,
    the first Pages deployment, the push time GitHub recorded for each public receipt, and the
    V1.0 figures the generated stats file carried before V2.0 existed.
The milestone lines are written by a person, here in MILESTONES, never copied from a private commit
message. Each says whether its evidence is public (a commit in this repository, with the push time
GitHub recorded) or private (my record, which a reader cannot check).

It publishes COUNTS, DATES AND THOSE LINES ONLY: never a repository name, host, address, path or a
private commit id. Four things enforce that: every value has a declared kind; text values are
refused if they look like an address, a dotted host name (name.local, name.net and the like), a
URL, a token or a commit id; public commit ids are written only after they are found in this
repository; and the file is run through the site's own leak guard (content patterns only), before
it is written and again by --verify. A BARE machine name (no dot) is caught only by that guard's
fixed list of real fleet names, so a new machine needs its name added there. A measurement that
fails writes nothing.

Usage:
  scripts/gather-history.py              measure, check, write docs/_data/history.yml
  scripts/gather-history.py --dry-run    measure and check, print the YAML, write nothing
  scripts/gather-history.py --check      measure again and fail if the committed file differs
                                         (generated_at aside): the frozen history is still what
                                         its sources say
  scripts/gather-history.py --verify [--data-dir DIR]
                                         offline, no repositories: kinds, sums, order, a method
                                         for every figure and the leak guard's content patterns
                                         (run by check-public-docs.sh)

Environment (measuring and --check only; no path is hard-coded here, see the Makefile):
  V1_REPO   REQUIRED: a checkout of the V1.0 platform repository (only its origin URL is used,
            never printed)
  V2_REPO   REQUIRED: a checkout of the V2.0 platform repository (likewise)
It also needs git, and the GitHub CLI (gh) logged in with read access to both repositories.
Each repository is read from a fresh, blob-less bare clone of its remote default branch, made
into a temporary directory and deleted again, so a local branch can never move a published number.

Standard library only.
"""
import argparse
import datetime as dt
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, "docs", "_data")
GUARD = os.path.join(SITE, "scripts", "check-public-docs.sh")
NAME = "history.yml"

V1_REPO = os.path.expanduser(os.environ.get("V1_REPO", ""))
V2_REPO = os.path.expanduser(os.environ.get("V2_REPO", ""))

# ------------------------------------------------------------------ facts written by a person
# Dates from the private V1.0 record that git cannot measure by itself. Both are already on the
# public site (choices.md, lessons.md); they are named here so the timeline can draw them.
SWARM_RETIRED = "2026-06-09"   # Docker Swarm decommissioned; everything on Kubernetes
K3S_STOOD_UP = "2026-04-04"    # a k3s cluster stood up beside Swarm, with the full stack

# (date, track, line, public commit in THIS repository or None)
# A line is generic on purpose: no machine, address, version or private commit message. A public
# commit is the evidence a reader can open; the push time GitHub recorded for it is measured.
MILESTONES = [
    ("2025-12-21", "v1", "The platform repository starts: a small Docker Swarm cluster with sign-in, metrics, logs and alerting from the first commit.", None),
    ("2025-12-22", "v1", "First CI workflows, a first release tag and a first mobile client.", None),
    ("2025-12-25", "v1", "First app live behind the sign-in: location sharing.", None),
    ("2026-01-01", "v1", "Second app: crowdsourced warnings on a map.", None),
    ("2026-01-03", "v1", "First software bill of materials and vulnerability scan of the images.", None),
    ("2026-02-09", "v1", "Three managers, so the cluster survives losing one; replicated databases, synthetic load tests and a public entrance followed by 2026-02-17.", None),
    ("2026-04-04", "v1", "A Kubernetes (k3s) cluster stood up beside Swarm, running the full stack.", None),
    ("2026-04-08", "v1", "Automated dependency updates. The same day, the first recorded outage: a file-server deadlock took a machine down.", None),
    ("2026-04-14", "v1", "A small local language model starts reading metrics, logs and alerts and posting to chat.", None),
    ("2026-04-18", "v1", "This public profile starts describing the running platform: Swarm and k3s side by side, the apps and the local operations agent.", "e74f8088779a464585d6b79f29f16f5ff0d98203"),
    ("2026-05-15", "v1", "Third app: chat.", None),
    ("2026-05-16", "v1", "Deploys move to a builder at home (a self-hosted CI runner).", None),
    ("2026-05-24", "v1", "Signed images with build provenance, a vulnerability tracker fed with bills of materials, and the numbered decision records that later ran to 0041.", None),
    ("2026-06-05", "v1", "A maturity baseline and scorecard, re-rated in June, July and September.", None),
    ("2026-06-09", "v1", "Swarm retired; everything runs on Kubernetes.", "0fa8334af67a72d254b73855fb14c4871c301577"),
    ("2026-07-02", "v1", "Scheduled database backups with a tested restore: about 2 minutes for a 13 MB database.", None),
    ("2026-07-11", "v1", "Security findings collected in one place.", None),
    ("2026-07-19", "v1", "The public entrance becomes default-deny; host patching, reboots and cluster upgrades are automated (from 2026-07-17).", None),
    ("2026-07-27", "v1", "Replicated block storage becomes the only default storage.", None),
    ("2026-07-30", "v1", "A pull-request gate on the main branch (the first gated merge on 2026-08-06) and an off-site uptime probe (2026-07-31).", None),
    ("2026-08-06", "v1", "First severity-1 incident: the replicated store filled, writes stopped, and sign-in and two apps went down.", None),
    ("2026-08-10", "v1", "A dated live-facts snapshot published here: 9 of 9 nodes Ready, 167 pods, 72 of 72 scrape targets, 8 Postgres clusters.", "97c72acf033e4e816240273aec97a3121d04975a"),
    ("2026-08-18", "v1", "The curated site is published on GitHub Pages; the first Pages deployment, of a placeholder page, was earlier the same day.", "f25630abee6d3b1469cab828ed0b16c1fc37ba12"),
    ("2026-08-20", "v1", "A short mains cut loses the control-plane quorum for 9 min 12 s and nothing detects it; written up here in full.", "5ee5e960472d03504314e601ecdbf472f94e3ac7"),
    ("2026-09-04", "v1", "The k3s cluster rebuilt from scratch on six machines; every published figure re-derived the same day.", "2389f943bf07fc37c0c5116e455c7d69c474b62d"),
    ("2026-09-09", "v1", "Fault injection fires for the first time; the documentation had claimed it ran earlier.", None),
    ("2026-09-16", "v1", "Database major-version upgrade without downtime: 87 to 142 s, no errors. It silently dropped synchronous commit, found on 2026-10-09.", None),
    ("2026-10-09", "v1", "The figures on this site are generated by a script for the first time, every page is re-derived, and claims that were wrong are retracted in public.", "d30aa08c2d20964525d47c4ff140015cc0799706"),
    ("2026-10-14", "v1", "Planned four-day shutdown and the first real cold start; 5 of 13 catch-up backups failed unnoticed.", None),
    ("2026-10-24", "v1", "Rule: git is the only way a change reaches the cluster, with a daily drift diff; all secrets encrypted in git from 2026-10-25.", None),
    ("2026-10-27", "v1", "The last generated V1.0 snapshot published here: 1,943 commits, 309 days old, 41 decision records.", "238890c21004249c0c64e670cbd22e49b7ce4dfa"),
    ("2026-10-31", "v1", "A training system on purpose, and objectives for the quarter, written here while V1.0 still ran.", "f96ef28d05041a99f5736f8df8153a9054337f7d"),
    ("2026-11-04", "v1", "A pull-based reconciler installed and the first workloads handed to it.", None),
    ("2026-11-05", "v1", "113 incidents and near misses written into one register, and the decision to rebuild in a new repository. The last V1.0 commit.", None),
    ("2026-11-05", "v2", "A new private repository: a charter, three objectives, no fixed dates.", None),
    ("2026-11-07", "v2", "Groundwork on throwaway local clusters: backup and restore, image admission, registry and provenance; a backup proof and a restore drill of V1.0 before its teardown (2026-11-08).", None),
    ("2026-11-10", "v2", "V1.0 taken down in stages; V2.0 built on the same six machines, about 4.5 hours from the first merge to a converged site; a restore drill passed.", None),
    ("2026-11-11", "v2", "This site re-pointed at V2.0, with V1.0 kept as dated history.", "3d2813cd29677daf63c440e7ccd74aa9f6a04c09"),
    ("2026-11-11", "v2", "Monitoring live on V2.0 and read the same day: 18 of 18 scrape targets up, 12 alert rules.", "489108b81dfb2a5b408ef0a90a5fae8df91ae19f"),
]

# --------------------------------------------------------------------------------- the contract
SCALARS = [("generated_at", "iso"), ("chart_days", "int")]
GROUPS = [
    ("v1", [
        ("first_commit", "date"), ("last_commit", "date"), ("retired", "date"), ("days", "int"),
        ("commits", "int"), ("active_days", "int"), ("merged_prs", "int"), ("first_merged_pr", "date"),
        ("ci_runs", "int"), ("first_ci_run", "date"), ("adrs", "int"), ("last_cluster_built", "date"),
    ]),
    ("v2", [("first_commit", "date"), ("built", "date")]),
    ("site", [
        ("first_commit", "date"), ("commits_v1_window", "int"),
        ("first_deployment", "iso"), ("deployments_before_v2", "int"),
    ]),
]
LISTS = [
    ("eras", [("name", "text"), ("track", "track"), ("from", "date"), ("to", "date?"),
              ("from_day", "int"), ("to_day", "int"), ("evidence", "evidence")]),
    ("months", [("month", "month"), ("days", "int"), ("commits", "int"), ("active_days", "int"),
                ("merged_prs", "int"), ("ci_runs", "int"), ("site_commits", "int")]),
    ("receipts", [("commit", "sha"), ("on_github", "iso"), ("generated_at", "iso"), ("v1_commits", "int"),
                  ("v1_age_days", "int"), ("v1_adrs", "int"), ("cluster_age_days", "int"),
                  ("v1_commits_counted_now", "int")]),
    ("milestones", [("date", "date"), ("track", "track"), ("text", "text"), ("commit", "sha?"),
                    ("on_github", "iso?")]),
]
# Month fields that add up to a v1 (or site) total; --verify checks every one.
SUMS = [("commits", "v1", "commits"), ("active_days", "v1", "active_days"), ("merged_prs", "v1", "merged_prs"),
        ("ci_runs", "v1", "ci_runs"), ("site_commits", "site", "commits_v1_window")]

KINDS = {
    "iso": re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"),
    "date": re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"),
    "month": re.compile(r"^[0-9]{4}-[0-9]{2}$"),
    "sha": re.compile(r"^[0-9a-f]{40}$"),
    "track": re.compile(r"^(v1|v2|site)$"),
    "evidence": re.compile(r"^(public|private)$"),
}
# Shapes a text value may never have. The leak guard checks the whole file as well; these make the
# generator refuse on its own, and --verify refuse a hand edit, with the reason in the message.
SUSPECT = [
    (re.compile(r"\b[0-9]{1,3}(\.[0-9]{1,3}){3}\b"), "an IPv4 address"),
    (re.compile(r"\b[0-9a-f]{1,4}(:[0-9a-f]{0,4}){2,7}\b", re.I), "an IPv6 address"),
    (re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://"), "a URL"),
    (re.compile(r"\b[a-z0-9-]+\.(local|lan|home|internal|ts\.net|net|com|org|io|dev)\b", re.I), "a host name"),
    (re.compile(r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{7,40}\b", re.I), "a commit id (it belongs in the commit field, where it is checked to be public)"),
    (re.compile(r"\b(AKIA|gh[pousr]_|github_pat_|glpat-|xox[abprs]-|sk-|eyJ)[A-Za-z0-9_-]{6,}"), "a token"),
    (re.compile(r"[@/\\]|\{\{|\{%"), "a path, a mail address or Liquid"),
]
RUNS_SPLIT = 1000  # GitHub's run search stops counting past a cap; ranges at or above this are halved
TEXT_MAX = 300


class Fail(Exception):
    """A measurement or a check failed. Nothing is written."""


def scrub(text, limit=160):
    """A tool's error text, safe to print: no URLs, hosts, addresses or paths, one line."""
    t = re.sub(r"[A-Za-z][A-Za-z0-9+.-]*://\S+", "<url>", str(text))
    t = re.sub(r"\b[0-9]{1,3}(\.[0-9]{1,3}){3}(:[0-9]+)?\b", "<addr>", t)
    t = re.sub(r"\b[A-Za-z0-9][A-Za-z0-9-]*(\.[A-Za-z0-9-]+)+(:[0-9]+)?\b", "<host>", t)
    t = re.sub(r"(?<![A-Za-z0-9])/[^\s\"']+", "<path>", t)
    t = re.sub(r"\b[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\b", "<name>", t)
    t = " ".join(t.split())
    return t if len(t) <= limit else t[:limit] + "..."


def run(cmd, cwd=None, timeout=180):
    """One command, no shell, no pipe; its stdout, or Fail."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        raise Fail(f"{cmd[0]}: not installed")
    except subprocess.TimeoutExpired:
        raise Fail(f"{cmd[0]} {cmd[1] if len(cmd) > 1 else ''}: timed out after {timeout}s")
    if p.returncode != 0:
        raise Fail(f"{cmd[0]} {cmd[1] if len(cmd) > 1 else ''}: exit {p.returncode}: {scrub(p.stderr)}")
    return p.stdout


def git(repo, *args):
    return run(["git", *args], cwd=repo)


def day(s):
    return dt.date.fromisoformat(s)


def slug_of(repo):
    """owner/name of a checkout's GitHub origin. Never printed."""
    url = git(repo, "remote", "get-url", "origin").strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(\.git)?/?$", url)
    if not m:
        raise Fail("a repository's origin is not on GitHub")
    return m.group(1)


def gh(path, jq, paginate=False):
    cmd = ["gh", "api", "-H", "Accept: application/vnd.github+json", path, "--jq", jq]
    if paginate:
        cmd.insert(2, "--paginate")
    return run(cmd, timeout=300)


class Clone:
    """A blob-less bare clone of a checkout's remote default branch, in a temporary directory."""

    def __init__(self, checkout, what):
        self.checkout, self.what = checkout, what

    def __enter__(self):
        if not self.checkout or not os.path.isdir(self.checkout):
            raise Fail(f"{self.what} is required: the path to a checkout of that repository")
        url = git(self.checkout, "remote", "get-url", "origin").strip()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self._tmp.name, "r.git")
        run(["git", "clone", "--bare", "--single-branch", "--filter=blob:none", "--quiet", url, self.repo],
            timeout=600)
        self.slug = slug_of(self.checkout)
        return self

    def __exit__(self, *exc):
        self._tmp.cleanup()
        return False


# ------------------------------------------------------------------------------------ measuring
def months_between(first, last):
    out, y, m = [], first.year, first.month
    while (y, m) <= (last.year, last.month):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def month_window(month, first, last):
    """The first and last day of a month, clipped to [first, last]."""
    y, m = int(month[:4]), int(month[5:])
    a = dt.date(y, m, 1)
    b = (dt.date(y + 1, 1, 1) if m == 12 else dt.date(y, m + 1, 1)) - dt.timedelta(days=1)
    return max(a, first), min(b, last)


def runs_between(slug, a, b):
    """Actions runs created from day a to day b inclusive (UTC), by halving ranges past the cap."""
    n = int(gh(f"repos/{slug}/actions/runs?per_page=1&created={a.isoformat()}..{b.isoformat()}", ".total_count").strip())
    if n < RUNS_SPLIT:
        return n
    if a == b:
        raise Fail(f"{n} Actions runs on one day reach the search cap; the count would be wrong")
    mid = a + (b - a) // 2
    return runs_between(slug, a, mid) + runs_between(slug, mid + dt.timedelta(days=1), b)


def commit_days(repo, ref, *extra):
    """Committer dates (in each commit's own time zone), one per commit."""
    out = git(repo, "log", "--format=%cd", "--date=format:%Y-%m-%d", *extra, ref)
    return [l for l in out.split("\n") if l]


def pushes(site_slug):
    """GitHub's record of updates to main: (UTC time, commit after), oldest first."""
    out = gh(f"repos/{site_slug}/activity?per_page=100&ref=refs%2Fheads%2Fmain", '.[] | "\\(.timestamp) \\(.after)"',
             paginate=True)
    rows = []
    for line in out.split("\n"):
        if line.strip():
            t, after = line.split()
            rows.append((t, after))
    return sorted(rows)


def on_github(site, push_rows, sha):
    """The first push to main that contained the commit, by GitHub's clock."""
    for t, after in push_rows:
        try:
            git(site, "merge-base", "--is-ancestor", sha, after)
            return t
        except Fail:
            continue
    raise Fail(f"no push recorded by GitHub contains the public commit {sha[:7]}")


def parse_stats_blob(text):
    """generated_at, repo.commits, repo.age_days, repo.adrs, cluster.age_days of an old stats.yml."""
    out, group = {}, None
    for line in text.split("\n"):
        m = re.match(r'^generated_at:\s*"([^"]+)"', line)
        if m:
            out["generated_at"] = m.group(1)
            continue
        m = re.match(r"^([a-z0-9_]+):\s*$", line)
        if m:
            group = m.group(1)
            continue
        m = re.match(r"^  ([a-z0-9_]+):\s*([0-9]+)\s*$", line)
        if m and group in ("repo", "cluster"):
            out[f"{group}.{m.group(1)}"] = int(m.group(2))
    return out


def measure():
    site = SITE
    site_ref = "origin/main"
    git(site, "rev-parse", "--verify", "--quiet", site_ref + "^{commit}")
    site_slug = slug_of(site)

    with Clone(V1_REPO, "V1_REPO") as v1c, Clone(V2_REPO, "V2_REPO") as v2c:
        v1, slug1 = v1c.repo, v1c.slug
        root = git(v1, "rev-list", "--max-parents=0", "HEAD").split()
        if len(root) != 1:
            raise Fail("the V1.0 repository has more than one root commit")
        first = day(git(v1, "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d", root[0]).strip())
        last = day(git(v1, "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d", "HEAD").strip())
        commits = int(git(v1, "rev-list", "--count", "HEAD").strip())
        cdays = commit_days(v1, "HEAD")
        if len(cdays) != commits:
            raise Fail("the V1.0 commit count and its list of commit dates disagree")
        adrs = sum(1 for f in git(v1, "ls-tree", "--name-only", "HEAD", "docs/adr/").split("\n")
                   if re.fullmatch(r"docs/adr/[0-9]{4}-.*\.md", f))

        # V2.0: its first commit, and the run records of the V1.0 teardown and the V2.0 bring-up
        v2 = v2c.repo
        v2root = git(v2, "rev-list", "--max-parents=0", "HEAD").split()
        v2first = day(git(v2, "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d", v2root[0]).strip())
        recs = git(v2, "ls-tree", "--name-only", "HEAD", "records/").split("\n")

        def record_date(suffix):
            ds = sorted(m.group(1) for f in recs
                        for m in [re.fullmatch(r"records/([0-9]{4}-[0-9]{2}-[0-9]{2})-" + suffix + r"\.md", f)] if m)
            if not ds:
                raise Fail(f"no run record of the {suffix.replace('-', ' ')} in the V2.0 repository")
            return day(ds[0])

        retired = record_date("old-platform-teardown")
        built = record_date("home-site-bring-up")

        # GitHub's clock for V1.0: merged pull requests and Actions runs, within V1.0's dates (UTC)
        merged = [t[:10] for t in gh(f"repos/{slug1}/pulls?state=closed&per_page=100",
                                     ".[] | select(.merged_at != null) | .merged_at", paginate=True).split()
                  if t[:10] <= last.isoformat()]
        if not merged:
            raise Fail("no merged pull request found for V1.0")
        months = months_between(first, last)
        runs = {}
        for mo in months:
            a, b = month_window(mo, first, last)
            runs[mo] = runs_between(slug1, a, b)
        first_run = None
        d = first
        while first_run is None and d <= min(last, first + dt.timedelta(days=62)):
            if runs_between(slug1, d, d):
                first_run = d
            d += dt.timedelta(days=1)
        if first_run is None:
            raise Fail("no Actions run found in V1.0's first two months")

        # This public repository: commits, deployments, pushes, and the old generated stats files
        site_days = [x for x in commit_days(site, site_ref) if first.isoformat() <= x]
        site_first = min(site_days)
        deploy_times = sorted(gh(f"repos/{site_slug}/deployments?per_page=100", ".[] | .created_at",
                                 paginate=True).split())
        if not deploy_times:
            raise Fail("this repository has no deployments to date the site by")
        push_rows = pushes(site_slug)

        receipts, seen = [], set()
        for sha in git(site, "log", "--reverse", "--format=%H", f"--before={v2first.isoformat()}T00:00:00",
                       site_ref, "--", "docs/_data/stats.yml").split():
            st = parse_stats_blob(git(site, "show", f"{sha}:docs/_data/stats.yml"))
            need = ("generated_at", "repo.commits", "repo.age_days", "repo.adrs", "cluster.age_days")
            if any(k not in st for k in need) or st["generated_at"] in seen:
                continue
            seen.add(st["generated_at"])
            receipts.append({
                "commit": sha, "on_github": on_github(site, push_rows, sha), "generated_at": st["generated_at"],
                "v1_commits": st["repo.commits"], "v1_age_days": st["repo.age_days"], "v1_adrs": st["repo.adrs"],
                "cluster_age_days": st["cluster.age_days"],
                "v1_commits_counted_now": int(git(v1, "rev-list", "--count", f"--before={st['generated_at']}", "HEAD").strip()),
            })
        if not receipts:
            raise Fail("no generated stats file from before V2.0 found in this repository")
        builds = {day(r["generated_at"][:10]) - dt.timedelta(days=r["cluster_age_days"]) for r in receipts}
        if max(builds) - min(builds) > dt.timedelta(days=1):
            raise Fail("the old stats files disagree on when the last V1.0 cluster was built")
        cluster_built = min(builds)

        mrows = []
        for mo in months:
            a, b = month_window(mo, first, last)
            in_mo = [x for x in cdays if x.startswith(mo)]
            mrows.append({
                "month": mo, "days": (b - a).days + 1, "commits": len(in_mo), "active_days": len(set(in_mo)),
                "merged_prs": sum(1 for t in merged if t.startswith(mo)), "ci_runs": runs[mo],
                "site_commits": sum(1 for x in site_days if x.startswith(mo) and x <= last.isoformat()),
            })

        chart_days = (retired - first).days + 1

        def off(d_):
            return (d_ - first).days

        eras = [
            ("Docker Swarm", "v1", first, day(SWARM_RETIRED), "private"),
            ("Kubernetes (k3s)", "v1", day(K3S_STOOD_UP), retired, "private"),
            ("Last k3s cluster build", "v1", cluster_built, retired, "public"),
            ("Public write-up of the platform", "site", day(site_first), None, "public"),
            ("This site on GitHub Pages", "site", day(deploy_times[0][:10]), None, "public"),
            ("V2.0 repository", "v2", v2first, None, "private"),
            ("V2.0 cluster", "v2", built, None, "private"),
        ]
        milestones = []
        for date, track, text, sha in MILESTONES:
            row = {"date": date, "track": track, "text": text, "commit": None, "on_github": None}
            if sha:
                git(site, "cat-file", "-e", sha + "^{commit}")
                git(site, "merge-base", "--is-ancestor", sha, site_ref)
                row["commit"], row["on_github"] = sha, on_github(site, push_rows, sha)
            milestones.append(row)

        return {
            "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "chart_days": chart_days,
            "v1": {
                "first_commit": first.isoformat(), "last_commit": last.isoformat(), "retired": retired.isoformat(),
                "days": (retired - first).days, "commits": commits, "active_days": len(set(cdays)),
                "merged_prs": len(merged), "first_merged_pr": min(merged), "ci_runs": sum(runs.values()),
                "first_ci_run": first_run.isoformat(), "adrs": adrs, "last_cluster_built": cluster_built.isoformat(),
            },
            "v2": {"first_commit": v2first.isoformat(), "built": built.isoformat()},
            "site": {
                "first_commit": site_first, "commits_v1_window": sum(r["site_commits"] for r in mrows),
                "first_deployment": deploy_times[0],
                "deployments_before_v2": sum(1 for t in deploy_times if t[:10] < v2first.isoformat()),
            },
            "eras": [{"name": n, "track": tr, "from": a.isoformat(), "to": b.isoformat() if b else None,
                      "from_day": off(a), "to_day": off(b) if b else chart_days, "evidence": ev}
                     for n, tr, a, b, ev in eras],
            "months": mrows,
            "receipts": receipts,
            "milestones": milestones,
        }


# ------------------------------------------------------------------------- render, parse, check
def scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        raise Fail("a boolean is not an accepted value")
    if isinstance(v, int):
        return str(v)
    return json.dumps(v, ensure_ascii=False)


def render(h):
    out = ["# Generated by scripts/gather-history.py - do not edit by hand. Regenerate with `make history`.",
           "# V1.0's history, frozen: counts, dates and dated lines only. How each is measured: the history",
           "# block of stats_methods.yml. --check re-measures and must find nothing changed but generated_at."]
    for k, _ in SCALARS:
        out.append(f"{k}: {scalar(h[k])}")
    for g, keys in GROUPS:
        out.append(f"{g}:")
        for k, _ in keys:
            out.append(f"  {k}: {scalar(h[g][k])}")
    for g, fields in LISTS:
        out.append(f"{g}:")
        for row in h[g]:
            for i, (k, _) in enumerate(fields):
                out.append(("  - " if i == 0 else "    ") + f"{k}: {scalar(row[k])}")
    return "\n".join(out) + "\n"


def parse(text):
    """Read back exactly the shape render() writes; anything else is refused with a line number."""
    data, group, item = {}, None, None

    def val(s, n):
        try:
            v = json.loads(s)
        except ValueError:
            raise Fail(f"{NAME}:{n}: {s[:40]!r} is not a number, a quoted string or null")
        if isinstance(v, (bool, float, list, dict)):
            raise Fail(f"{NAME}:{n}: only whole numbers, quoted strings and null are accepted")
        return v

    def put(d, k, v, n):
        if k in d:
            raise Fail(f"{NAME}:{n}: the key '{k}' appears twice (the last one would silently win)")
        d[k] = v

    for n, raw in enumerate(text.split("\n"), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^([a-z0-9_]+):(?: (.*))?$", raw)
        if m:
            if m.group(2):
                put(data, m.group(1), val(m.group(2), n), n)
                group = None
            else:
                put(data, m.group(1), None, n)
                group = m.group(1)
            item = None
            continue
        m = re.match(r"^  - ([a-z0-9_]+): (.*)$", raw)
        if m and group:
            if data[group] is None:
                data[group] = []
            if not isinstance(data[group], list):
                raise Fail(f"{NAME}:{n}: '{group}' mixes list items and keys")
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
                raise Fail(f"{NAME}:{n}: '{group}' mixes keys and list items")
            put(data[group], m.group(1), val(m.group(2), n), n)
            continue
        raise Fail(f"{NAME}:{n}: a line of an unexpected shape")
    return data


def kind_problem(v, kind):
    opt = kind.endswith("?")
    kind = kind.rstrip("?")
    if v is None:
        return None if opt else "is empty"
    if kind == "int":
        return None if isinstance(v, int) and v >= 0 else "is not a whole number >= 0"
    if not isinstance(v, str):
        return f"is not a {kind}"
    if kind == "text":
        if not 3 <= len(v) <= TEXT_MAX or "\n" in v:
            return f"is not a one-line text of 3 to {TEXT_MAX} characters"
        for rx, what in SUSPECT:
            if rx.search(v):
                return f"looks like it holds {what}"
        return None
    if not KINDS[kind].match(v):
        return f"{v!r} is not a {kind}"
    if kind in ("date", "iso"):
        try:
            dt.datetime.strptime(v, "%Y-%m-%d" if kind == "date" else "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return f"{v!r} is not a real {kind}"
    return None


def method_keys():
    keys = [k for k, _ in SCALARS if k != "generated_at"]
    keys += [f"{g}_{k}" for g, ks in GROUPS for k, _ in ks]
    keys += [f"months_{k}" for k, _ in dict(LISTS)["months"] if k != "month"]
    keys += [g for g, _ in LISTS if g != "months"]
    return keys


def history_methods(data_dir):
    """Keys of the history block in stats_methods.yml, with duplicates reported."""
    path = os.path.join(data_dir, "stats_methods.yml")
    if not os.path.isfile(path):
        raise Fail("docs/_data/stats_methods.yml is missing")
    keys, dups, inside = [], [], False
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^([a-z0-9_]+):", line)
            if m:
                inside = m.group(1) == "history"
                continue
            m = re.match(r"^  ([a-z0-9_]+):", line)
            if m and inside:
                (dups if m.group(1) in keys else keys).append(m.group(1))
    return keys, dups


def check(h, data_dir=None, today=None):
    """Every problem with a parsed history, as a list of strings (empty is good)."""
    p = []
    today = today or dt.datetime.now(dt.timezone.utc).date()
    for k, kind in SCALARS:
        why = kind_problem(h.get(k), kind) if k in h else "is missing"
        if why:
            p.append(f"{k} {why}")
    for g, keys in GROUPS:
        got = h.get(g)
        if not isinstance(got, dict):
            p.append(f"{g} is missing")
            continue
        for k, kind in keys:
            why = kind_problem(got.get(k), kind) if k in got else "is missing"
            if why:
                p.append(f"{g}.{k} {why}")
        extra = set(got) - {k for k, _ in keys}
        if extra:
            p.append(f"{g} has keys nobody declared: {sorted(extra)}")
    for g, fields in LISTS:
        rows = h.get(g)
        if not isinstance(rows, list) or not rows:
            p.append(f"{g} is missing or empty")
            continue
        for i, row in enumerate(rows, 1):
            if [k for k in row] != [k for k, _ in fields]:
                p.append(f"{g} row {i} has the fields {list(row)}, expected {[k for k, _ in fields]}")
                continue
            for k, kind in fields:
                why = kind_problem(row[k], kind)
                if why:
                    p.append(f"{g} row {i}: {k} {why}")
    extra = set(h) - {k for k, _ in SCALARS} - {g for g, _ in GROUPS} - {g for g, _ in LISTS}
    if extra:
        p.append(f"top-level keys nobody declared: {sorted(extra)}")
    if p:
        return p

    v1, site, months = h["v1"], h["site"], h["months"]
    first, last, retired = day(v1["first_commit"]), day(v1["last_commit"]), day(v1["retired"])
    # the months are V1.0's months, in order, with no gap, each no longer than its window
    want = months_between(first, last)
    if [m["month"] for m in months] != want:
        p.append(f"months must run from {want[0]} to {want[-1]} without a gap")
    else:
        for m in months:
            a, b = month_window(m["month"], first, last)
            if m["days"] != (b - a).days + 1:
                p.append(f"months {m['month']}: days is {m['days']}, the window has {(b - a).days + 1}")
            if m["active_days"] > m["days"] or m["active_days"] > m["commits"]:
                p.append(f"months {m['month']}: more active days than days or commits")
    for field, g, k in SUMS:
        total = sum(m[field] for m in months)
        if total != h[g][k]:
            p.append(f"months: {field} adds up to {total}, but {g}.{k} is {h[g][k]}")
    if v1["days"] != (retired - first).days:
        p.append(f"v1.days is {v1['days']}, but {v1['first_commit']} to {v1['retired']} is {(retired - first).days}")
    if h["chart_days"] != v1["days"] + 1:
        p.append("chart_days must be v1.days + 1")
    if not first <= last <= retired:
        p.append("V1.0's first commit, last commit and retirement are out of order")
    if not first <= day(v1["first_merged_pr"]) <= last or not first <= day(v1["first_ci_run"]) <= last:
        p.append("V1.0's first merged pull request or first CI run is outside its own dates")
    if not first <= day(v1["last_cluster_built"]) <= retired:
        p.append("V1.0's last cluster build is outside its own dates")
    if day(h["v2"]["built"]) < day(h["v2"]["first_commit"]):
        p.append("V2.0 was built before its repository existed")
    if day(site["first_commit"]) < first:
        p.append("site.first_commit is before V1.0 began; only the write-up of the platform counts")
    for i, e in enumerate(h["eras"], 1):
        a = (day(e["from"]) - first).days
        b = (day(e["to"]) - first).days if e["to"] else h["chart_days"]
        if (e["from_day"], e["to_day"]) != (a, b) or not 0 <= a <= b <= h["chart_days"]:
            p.append(f"eras row {i}: from_day/to_day do not match its dates inside the chart")
    prev = None
    for i, r in enumerate(h["receipts"], 1):
        if r["generated_at"][:10] >= h["v2"]["first_commit"]:
            p.append(f"receipts row {i} is not from before V2.0")
        if r["on_github"] < r["generated_at"]:
            p.append(f"receipts row {i} was pushed before it was generated")
        if prev and r["v1_commits"] < prev:
            p.append(f"receipts row {i}: V1.0's commit count went down")
        prev = r["v1_commits"]
    prev = None
    for i, ms in enumerate(h["milestones"], 1):
        if prev and ms["date"] < prev:
            p.append(f"milestones row {i} is out of date order")
        prev = ms["date"]
        if not first <= day(ms["date"]) <= today:
            p.append(f"milestones row {i}: {ms['date']} is outside {first} to today")
        if (ms["commit"] is None) != (ms["on_github"] is None):
            p.append(f"milestones row {i}: a public commit needs GitHub's push time, and only then")
        if ms["on_github"] and ms["on_github"][:10] < ms["date"]:
            p.append(f"milestones row {i}: the public record is older than the event it records")
        if ms["track"] == "site":
            p.append(f"milestones row {i}: a milestone belongs to v1 or v2")

    if data_dir is not None:
        keys, dups = history_methods(data_dir)
        p += [f"stats_methods.yml: history.{d} appears twice" for d in dups]
        want_keys = method_keys()
        p += [f"history.{k} has no method in stats_methods.yml" for k in want_keys if k not in keys]
        p += [f"history.{k} has a method in stats_methods.yml but no figure in {NAME}" for k in keys if k not in want_keys]
    return p


def leak_guard(text):
    """The site's own leak guard over the candidate file, before anything is written."""
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "docs", "_data")
        os.makedirs(d)
        with open(os.path.join(d, NAME), "w", encoding="utf-8") as fh:
            fh.write(text)
        env = dict(os.environ, GUARD_CONTENT_ONLY="1")
        p = subprocess.run([GUARD, "docs"], cwd=tmp, env=env, capture_output=True, text=True)
        if p.returncode != 0:
            labels = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
            raise Fail("the leak guard refused the generated file: " + "; ".join(labels))


def without_generated_at(text):
    return [l for l in text.split("\n") if not l.startswith("generated_at:")]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--verify", action="store_true")
    ap.add_argument("--data-dir", default=DATA)
    a = ap.parse_args()
    path = os.path.join(a.data_dir, NAME)
    try:
        if a.verify:
            if not os.path.isfile(path):
                raise Fail(f"docs/_data/{NAME} is missing; run make history")
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            problems = check(parse(text), a.data_dir)
            try:
                leak_guard(text)  # the guard runs content-only here, so it does not call --verify back
            except Fail as e:
                problems.append(str(e))
            for x in problems:
                print(x)
            return 1 if problems else 0

        h = measure()
        text = render(h)
        problems = check(parse(text), a.data_dir)
        if problems:
            raise Fail("the measured history fails its own checks: " + "; ".join(problems))
        leak_guard(text)
        if a.dry_run:
            sys.stdout.write(text)
            return 0
        if a.check:
            if not os.path.isfile(path):
                raise Fail(f"docs/_data/{NAME} is missing; run make history")
            with open(path, encoding="utf-8") as fh:
                old = fh.read()
            diff = list(difflib.unified_diff(without_generated_at(old), without_generated_at(text),
                                             f"committed {NAME}", f"measured now", lineterm="", n=0))
            if diff:
                print(f"{NAME} no longer matches its sources:")
                print("\n".join(diff))
                return 1
            print(f"ok: {NAME} matches its sources ({h['v1']['commits']} V1.0 commits, {len(h['months'])} months, "
                  f"{len(h['receipts'])} public receipts, {len(h['milestones'])} milestones)")
            return 0
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
        print(f"wrote docs/_data/{NAME}: {h['v1']['commits']} V1.0 commits in {len(h['months'])} months, "
              f"{len(h['receipts'])} public receipts, {len(h['milestones'])} milestones")
        return 0
    except Fail as e:
        print(f"gather-history: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
