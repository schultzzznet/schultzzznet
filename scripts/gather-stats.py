#!/usr/bin/env python3
"""Measure the estate and write docs/_data/stats.yml - the numbers behind docs/status.md.

Every figure is MEASURED here, at generation time, by a command this script runs:
kubectl, git, cloc, cosign, the Prometheus HTTP API (through a kubectl port-forward that
is always stopped again) and a few public endpoints. Nothing is copied from a document.

What it publishes is AGGREGATES ONLY - counts, percentages, versions, dates. It never
writes a host, address, namespace, workload or secret name. Three things enforce that:
each key is declared below with a strict value type (a number, a version, a timestamp
or a lower-case word - nothing free-form can get through); the finished file is run
through the site's own leak guard before it is written; and it fails loudly rather than
write a partial file when a measurement fails or a key has no method.

Usage:
  scripts/gather-stats.py                  measure, check, write docs/_data/stats.yml
  scripts/gather-stats.py --dry-run        measure and check, print the YAML, write nothing
  scripts/gather-stats.py --no-readme      measure and write stats.yml but leave README.md alone
  scripts/gather-stats.py --readme-from-stats FILE [--readme README]
                                           no measuring: rebuild the README table from an existing
                                           stats file (to try the block on a scratch copy)
  scripts/gather-stats.py --verify freshness [--max-age-days N] [--data-dir DIR]
  scripts/gather-stats.py --verify methods [--data-dir DIR]
                                           offline checks used by check-public-docs.sh
  scripts/gather-stats.py --vet FILE       run only the leak guard over FILE (used by test-guard.sh)

Environment (no machine-specific path is hard-coded here; `make stats` sets the owner's
defaults from $(HOME), see the Makefile header):
  PLATFORM_REPO    REQUIRED for a measuring run: the private platform repository checkout
  HARDWARE_REPOS   REQUIRED for a measuring run: the directory holding the private hardware
                   repositories
  KUBECONFIG       the cluster's kubeconfig (default: ~/.kube/k3s-config)
  GITHUB_TOKEN     optional; raises the GitHub API rate limit, never printed

README.md: if it contains the markers <!-- stats:begin --> and <!-- stats:end -->, whatever is
between them is replaced with a table of the headline aggregates, built from the same measured
values and vetted by the same leak guard. Without the markers nothing is touched.

Standard library only; it also needs kubectl, git, cloc and cosign on the PATH.
No command here pipes into another: output is filtered by the command's own options or
parsed in Python.
"""
import argparse
import atexit
import datetime as dt
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, "docs", "_data")
STATS = os.path.join(DATA, "stats.yml")
METHODS = os.path.join(DATA, "stats_methods.yml")
GUARD = os.path.join(SITE, "scripts", "check-public-docs.sh")
INDEX_MD = os.path.join(SITE, "docs", "index.md")

README = os.path.join(SITE, "README.md")
# No default: a path to a private checkout does not belong in a public file. A measuring run
# says so up front (see main) if either is unset.
PLATFORM_REPO = os.path.expanduser(os.environ.get("PLATFORM_REPO", ""))
HARDWARE_REPOS = os.path.expanduser(os.environ.get("HARDWARE_REPOS", ""))
KUBECONFIG = os.path.expanduser(os.environ.get("KUBECONFIG") or "~/.kube/k3s-config")

# hardware key -> directory name under HARDWARE_REPOS
HARDWARE = {
    "printing": "thePrintingIn3D",
    "yocto": "theSchultzYocto",
    "rover_platform": "theRoverPlatform",
    "mower": "theMowerRetrofit",
    "video_rover": "theVideoRover",
    "imx8": "theImx8Yocto",
}

# --- the contract: every published key, its group order, and what a value may look like ---
# kinds: int (>= 0), float (finite, >= 0), ver (a version string), iso (UTC timestamp),
# word (one lower-case word), head (a commit count and a date). Anything else is refused before it can be written.
SCHEMA = [
    ("cluster", [
        ("nodes", "int"), ("nodes_ready", "int"), ("control_plane", "int"), ("agents", "int"),
        ("k3s", "ver"), ("cores", "int"), ("ram_gb", "float"),
        ("pods_running", "int"), ("pods_total", "int"), ("namespaces", "int"),
        ("containers", "int"), ("deployments", "int"), ("statefulsets", "int"),
        ("daemonsets", "int"), ("cronjobs", "int"), ("hpas", "int"), ("ingresses", "int"),
        ("pvcs", "int"), ("pvc_gib", "float"), ("helm_releases", "int"), ("crds", "int"),
        ("age_days", "int"), ("restarts_total", "int"),
    ]),
    ("storage", [
        ("ceph_raw_gib", "float"), ("ceph_used_gib", "float"), ("ceph_stored_gib", "float"),
        ("osds", "int"), ("osds_up", "int"), ("mons", "int"), ("pools", "int"),
        ("pgs", "int"), ("pgs_clean", "int"), ("replica_size", "int"),
        ("health", "word"), ("health_warnings", "int"),
    ]),
    ("databases", [
        ("clusters", "int"), ("instances", "int"), ("replicas", "int"),
        ("pg16_clusters", "int"), ("pg18_clusters", "int"),
        ("synchronous_clusters", "int"), ("synchronous_clusters_spec", "int"),
        ("backups_total", "int"), ("backups_failed", "int"), ("backups_24h", "int"),
        ("archiving_clusters", "int"),
    ]),
    ("observability", [
        ("scrape_up", "int"), ("scrape_total", "int"), ("series", "int"),
        ("samples_per_sec", "int"), ("alert_rules", "int"), ("alert_rules_custom", "int"),
        ("recording_rules", "int"), ("dashboards", "int"), ("dashboards_custom", "int"),
        ("retention_days", "int"), ("retention_size_gib", "float"),
        ("data_span_days", "float"), ("notifications_failed", "int"),
        ("firing_now", "int"), ("firing_now_excl_meta", "int"),
    ]),
    ("supply_chain", [
        ("images_running", "int"), ("images_first_party", "int"),
        ("images_third_party", "int"), ("first_party_signed_verified", "int"),
        ("sbom_projects", "int"),
    ]),
    ("ci", [
        ("workflows", "int"), ("jobs", "int"), ("runs_on_self_hosted", "int"),
        ("runs_on_github_hosted", "int"), ("precommit_hooks", "int"),
    ]),
    ("repo", [
        ("commits", "int"), ("commits_30d", "int"), ("age_days", "int"), ("adrs", "int"),
        ("gaps_open", "int"), ("gaps_closed", "int"), ("make_targets", "int"),
        ("playbooks", "int"), ("manifests", "int"), ("runbooks", "int"),
        ("docs_pages", "int"), ("loc", "int"), ("loc_code", "int"), ("platform_head", "head"),
        ("tests_java", "int"),
        ("tests_python", "int"), ("tests_dart", "int"),
    ]),
    ("hardware", [
        ("printing_commits", "int"), ("yocto_commits", "int"),
        ("rover_platform_commits", "int"), ("rover_platform_tests", "int"),
        ("rover_platform_c_assertions", "int"),
        ("mower_commits", "int"), ("mower_tests", "int"),
        ("video_rover_commits", "int"), ("video_rover_tests", "int"),
        ("imx8_commits", "int"),
    ]),
    ("referees", [
        ("uptimerobot_7d", "float"), ("uptimerobot_30d", "float"),
        ("healthchecks", "word"), ("github_stars", "int"), ("github_pushed", "iso"),
    ]),
    ("site", [
        ("commits", "int"), ("pages", "int"), ("pages_last_build", "word"),
        ("pages_last_build_at", "iso"), ("guard_last_run", "word"),
    ]),
]
KINDS = {
    "ver": re.compile(r"^v?[0-9]+(\.[0-9]+){1,3}([+-][0-9A-Za-z.]+)?$"),
    "iso": re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"),
    "word": re.compile(r"^[a-z][a-z_-]{0,19}$"),
    # "<N> commits, HEAD dated <YYYY-MM-DD>": a count and a date, no hash
    "head": re.compile(r"^[0-9]+ commits, HEAD dated [0-9]{4}-[0-9]{2}-[0-9]{2}$"),
}

# The orchestrator this estate started on is retired but its tree is still in the platform
# repository. Counts of what is running exclude any path with this segment.
RETIRED_SEGMENT = "swarm"

# Alerts that report on the alerting system rather than on the estate: the heartbeat that
# is meant to fire permanently, and the inhibitor that appears whenever an info-level alert
# is active. Both ship with the monitoring chart.
META_ALERTS = ("Watchdog", "InfoInhibitor")

# cloc languages counted as programming code for repo.loc_code. Markdown, YAML, JSON, XML,
# HTML, SVG, INI, TOML, properties and build manifests are left out on purpose.
CODE_LANGUAGES = frozenset((
    "Dart", "Java", "Kotlin", "Swift", "Python", "Go", "C", "C++", "C/C++ Header", "Objective-C",
    "JavaScript", "TypeScript", "Bourne Shell", "Bourne Again Shell", "Zsh", "SQL", "Rust", "Ruby",
    "Lua", "Perl", "PowerShell"))

# Registries that are public. Any other registry host is the estate's own.
OWN_REGISTRY_SUFFIXES = (".local", ".lan", ".internal", ".home.arpa")

NOW = dt.datetime.now(dt.timezone.utc)
CLOCK_SKEW_DAYS = 2 / 24  # a generation time may be at most two hours ahead of this machine's clock


class Fail(Exception):
    """A required measurement failed. Nothing is written."""


def scrub(text, limit=160):
    """Make a tool's error text safe to print: no URLs, host:port, addresses or local paths,
    one line, truncated. kubectl's stderr is full of API-server URLs and node names."""
    t = re.sub(r"[A-Za-z][A-Za-z0-9+.-]*://\S+", "<url>", str(text))
    t = re.sub(r"\b[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{0,4}){3,}\b", "<addr>", t)
    t = re.sub(r"\b[0-9]{1,3}(\.[0-9]{1,3}){3}(:[0-9]+)?\b", "<addr>", t)
    t = re.sub(r"\b[A-Za-z0-9][A-Za-z0-9-]*(\.[A-Za-z0-9-]+)+(:[0-9]+)?\b", "<host>", t)
    t = re.sub(r"(?<![A-Za-z0-9])/[^\s\"']+", "<path>", t)
    t = " ".join(t.split())
    return t if len(t) <= limit else t[:limit] + "..."


# ----------------------------------------------------------------------------- helpers
def run(cmd, cwd=None, timeout=180, env=None):
    """Run one command (no shell, no pipe) and return its stdout; Fail on any error."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, env=env, stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        raise Fail(f"{cmd[0]}: not installed")
    except subprocess.TimeoutExpired:
        raise Fail(f"{' '.join(cmd[:3])}: timed out after {timeout}s")
    if p.returncode != 0:
        raise Fail(f"{' '.join(cmd[:3])}: exit {p.returncode}: {scrub(p.stderr)}")
    return p.stdout


def kenv():
    e = dict(os.environ)
    e["KUBECONFIG"] = KUBECONFIG
    return e


def kubectl(*args, timeout=180):
    return run(["kubectl", *args], env=kenv(), timeout=timeout)


def kjson(*args):
    try:
        return json.loads(kubectl("get", *args, "-o", "json"))
    except json.JSONDecodeError as e:
        raise Fail(f"kubectl get {args[0]}: not JSON ({scrub(e)})")


def git(repo, *args):
    return run(["git", *args], cwd=repo)


class Snapshot:
    """The committed tree at HEAD, extracted to a temporary directory.

    Counts are taken from what is COMMITTED, not from whatever is half-edited in a
    working tree, so two runs against the same commit agree and a colleague's unsaved
    change cannot move a published number.
    """

    def __init__(self, repo):
        self.repo = repo

    def __enter__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        p = subprocess.Popen(["git", "-C", self.repo, "archive", "--format=tar", "HEAD"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=p.stdout, mode="r|") as tf:
                if hasattr(tarfile, "data_filter"):
                    tf.extractall(self.dir, filter="data")
                else:
                    tf.extractall(self.dir)
        except (tarfile.TarError, OSError) as e:
            p.kill()
            raise Fail(f"could not extract HEAD of a repository: {scrub(e)}")
        if p.wait() != 0:
            raise Fail("git archive failed: " + scrub(p.stderr.read().decode("utf-8", "replace")))
        self.files = sorted(
            os.path.relpath(os.path.join(d, f), self.dir)
            for d, _dirs, names in os.walk(self.dir) for f in names
            if os.path.isfile(os.path.join(d, f)))
        return self

    def __exit__(self, *exc):
        self._tmp.cleanup()
        return False

    def read(self, rel):
        with open(os.path.join(self.dir, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read()


def read(repo, rel):
    with open(os.path.join(repo, rel), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def need_dir(path, what):
    if not os.path.isdir(path):
        raise Fail(f"{what} is not a directory (check the environment variable of that name)")


def parse_time(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


QUANT = {"Ki": 2**10, "Mi": 2**20, "Gi": 2**30, "Ti": 2**40, "Pi": 2**50, "Ei": 2**60,
         "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9, "T": 1e12, "P": 1e15, "E": 1e18, "m": 1e-3, "": 1}


def quantity(q):
    m = re.fullmatch(r"([0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)([A-Za-z]*)", str(q))
    if not m or m.group(2) not in QUANT:
        raise Fail(f"unreadable Kubernetes quantity: {scrub(repr(q), 40)}")
    return float(m.group(1)) * QUANT[m.group(2)]


def http_json(url, headers=None, retries=3):
    h = {"User-Agent": "schultzzznet-gather-stats", "Accept": "application/json"}
    h.update(headers or {})
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ConnectionError) as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise Fail(f"GET {urllib.parse.urlsplit(url).netloc}: {scrub(last)}")


# ----------------------------------------------------------- port-forward, always stopped
_FORWARDS = []


def _stop_forwards():
    for p in _FORWARDS:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
    _FORWARDS.clear()


atexit.register(_stop_forwards)


def _die(signum, _frame):
    _stop_forwards()
    sys.exit(128 + signum)


for _sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(_sig, _die)


class PortForward:
    """kubectl port-forward on a free local port; stopped on exit, however we leave."""

    def __init__(self, namespace, target, port):
        self.args = ["kubectl", "port-forward", "-n", namespace, target, f":{port}"]
        self.port = None

    def __enter__(self):
        self.proc = subprocess.Popen(self.args, env=kenv(), stdin=subprocess.DEVNULL,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        _FORWARDS.append(self.proc)
        found = threading.Event()
        seen = []

        def pump():
            for line in self.proc.stdout:  # keeps draining so the pipe never fills
                m = re.search(r"Forwarding from 127\.0\.0\.1:([0-9]+)", line)
                if m and not found.is_set():
                    self.port = int(m.group(1))
                    found.set()
                elif not found.is_set():
                    seen.append(line.strip())

        threading.Thread(target=pump, daemon=True).start()
        if not found.wait(30):
            self.__exit__()
            raise Fail("port-forward did not come up: " + scrub(" ".join(seen)))
        return self

    def __exit__(self, *exc):
        p = self.proc
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
        if p.poll() is None:
            raise Fail("port-forward could not be stopped")
        return False


class Prom:
    def __init__(self, base):
        self.base = base

    def get(self, path, **params):
        url = self.base + path + ("?" + urllib.parse.urlencode(params) if params else "")
        r = http_json(url)
        if r.get("status") != "success":
            raise Fail(f"prometheus {path}: {r.get('status')}")
        return r["data"]

    def vector(self, expr):
        return [(s["metric"], float(s["value"][1])) for s in self.get("/api/v1/query", query=expr)["result"]]

    def scalar(self, expr, empty=None):
        v = self.vector(expr)
        if not v:
            if empty is None:
                raise Fail(f"prometheus returned nothing for: {expr}")
            return empty
        return v[0][1]


# ----------------------------------------------------------------------------- cluster
def measure_cluster():
    nodes = kjson("nodes")["items"]
    pods = kjson("pods", "-A")["items"]
    ready = sum(1 for n in nodes for c in n["status"]["conditions"]
                if c["type"] == "Ready" and c["status"] == "True")
    cp = sum(1 for n in nodes if "node-role.kubernetes.io/control-plane" in n["metadata"].get("labels", {}))
    server = json.loads(kubectl("version", "-o", "json"))["serverVersion"]["gitVersion"]
    running = [p for p in pods if p["status"].get("phase") == "Running"]
    restarts = 0
    for p in pods:
        for c in p["status"].get("containerStatuses", []) + p["status"].get("initContainerStatuses", []):
            restarts += c.get("restartCount", 0)
    pvcs = kjson("persistentvolumeclaims", "-A")["items"]
    # Helm v3 keeps one Secret per release revision; custom-columns prints labels only,
    # so no secret data ever reaches this script.
    helm = kubectl("get", "secrets", "-A", "--field-selector", "type=helm.sh/release.v1",
                   "-o", "custom-columns=NS:.metadata.namespace,NAME:.metadata.labels.name",
                   "--no-headers")
    releases = {tuple(line.split()) for line in helm.splitlines() if line.strip()}
    oldest = min(parse_time(n["metadata"]["creationTimestamp"]) for n in nodes)

    def count(kind):
        return len(kjson(kind, "-A")["items"])

    return {
        "nodes": len(nodes), "nodes_ready": ready, "control_plane": cp, "agents": len(nodes) - cp,
        "k3s": server,
        "cores": int(round(sum(quantity(n["status"]["capacity"]["cpu"]) for n in nodes))),
        "ram_gb": sum(quantity(n["status"]["capacity"]["memory"]) for n in nodes) / 1e9,
        "pods_running": len(running), "pods_total": len(pods),
        "namespaces": len(kjson("namespaces")["items"]),
        "containers": sum(len(p["spec"].get("containers", [])) for p in running),
        "deployments": count("deployments.apps"), "statefulsets": count("statefulsets.apps"),
        "daemonsets": count("daemonsets.apps"), "cronjobs": count("cronjobs.batch"),
        "hpas": count("horizontalpodautoscalers.autoscaling"),
        "ingresses": count("ingresses.networking.k8s.io"),
        "pvcs": len(pvcs),
        "pvc_gib": sum(quantity(c["spec"]["resources"]["requests"]["storage"]) for c in pvcs) / 2**30,
        "helm_releases": len(releases),
        "crds": len(kjson("customresourcedefinitions.apiextensions.k8s.io")["items"]),
        "age_days": int((NOW - oldest).total_seconds() // 86400),
        "restarts_total": restarts,
    }, pods


# ----------------------------------------------------------------------------- storage
def measure_storage():
    tools = kjson("deployments.apps", "-A", "-l", "app=rook-ceph-tools")["items"]
    if len(tools) != 1:
        raise Fail(f"expected exactly one Ceph toolbox deployment, found {len(tools)}")
    ns, name = tools[0]["metadata"]["namespace"], tools[0]["metadata"]["name"]

    def ceph(*args):
        out = kubectl("-n", ns, "exec", f"deploy/{name}", "--", "ceph", *args, "-f", "json")
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            raise Fail(f"ceph {args[0]}: not JSON")

    status, df, pools = ceph("status"), ceph("df"), ceph("osd", "pool", "ls", "detail")
    pg = status["pgmap"]
    clean = sum(s["count"] for s in pg["pgs_by_state"] if s["state_name"] == "active+clean")
    h = status["health"]["status"].replace("HEALTH_", "").lower()
    return {
        "ceph_raw_gib": df["stats"]["total_bytes"] / 2**30,
        "ceph_used_gib": df["stats"]["total_used_raw_bytes"] / 2**30,
        # logical bytes the applications stored: the sum of every pool's "stored" in ceph df
        "ceph_stored_gib": sum(p["stats"]["stored"] for p in df["pools"]) / 2**30,
        "osds": status["osdmap"]["num_osds"], "osds_up": status["osdmap"]["num_up_osds"],
        "mons": status["monmap"]["num_mons"], "pools": len(pools),
        "pgs": pg["num_pgs"], "pgs_clean": clean,
        "replica_size": min(p["size"] for p in pools),
        "health": h, "health_warnings": len(status["health"].get("checks", {})),
    }


# --------------------------------------------------------------------------- databases
def measure_databases():
    clusters = kjson("clusters.postgresql.cnpg.io", "-A")["items"]
    if not clusters:
        raise Fail("no database clusters found")
    sql = ("select current_setting('server_version_num'), "
           "(select count(*) from pg_stat_replication where sync_state in ('sync','quorum'))")
    pg = {16: 0, 18: 0}
    sync_spec = sync_seen = archiving = primaries = 0
    for c in clusters:
        st, spec = c["status"], c["spec"]
        primary = st.get("currentPrimary")
        if not primary:
            raise Fail("a database cluster reports no primary")
        primaries += 1
        major = st["pgDataImageInfo"]["majorVersion"]
        pg[major] = pg.get(major, 0) + 1
        want_sync = bool(spec.get("postgresql", {}).get("synchronous")) or spec.get("minSyncReplicas", 0) > 0
        sync_spec += want_sync
        # read-only SELECT on the primary: confirm the major, and whether a standby is
        # really synchronous right now (the spec only says what was asked for).
        out = kubectl("-n", c["metadata"]["namespace"], "exec", primary, "-c", "postgres", "--",
                      "psql", "-U", "postgres", "-At", "-F", "|", "-c", sql).strip()
        ver, sync_n = out.split("|")
        if int(ver) // 10000 != major:
            raise Fail("a cluster's reported major version disagrees with the server")
        sync_seen += int(sync_n) > 0
        archiving += any(x["type"] == "ContinuousArchiving" and x["status"] == "True"
                         for x in st.get("conditions", []))
    backups = kjson("backups.postgresql.cnpg.io", "-A")["items"]
    day = 0
    for b in backups:
        s = b.get("status", {})
        if s.get("phase") == "completed" and s.get("stoppedAt") and \
                (NOW - parse_time(s["stoppedAt"])).total_seconds() <= 86400:
            day += 1
    return {
        "clusters": len(clusters),
        "instances": sum(c["status"]["instances"] for c in clusters),
        "replicas": sum(c["status"]["instances"] for c in clusters) - primaries,
        "pg16_clusters": pg[16], "pg18_clusters": pg[18],
        "synchronous_clusters": sync_seen, "synchronous_clusters_spec": sync_spec,
        "backups_total": len(backups),
        "backups_failed": sum(1 for b in backups if b.get("status", {}).get("phase") == "failed"),
        "backups_24h": day, "archiving_clusters": archiving,
    }


# ----------------------------------------------------------------------- observability
def duration_days(s):
    m = re.fullmatch(r"([0-9]+)([smhdwy])", s.strip())
    if not m:
        raise Fail(f"unreadable Prometheus duration: {scrub(repr(s), 40)}")
    return int(m.group(1)) * {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31536000}[m.group(2)] / 86400


def size_gib(s):
    """A Prometheus ByteSize flag ('8GB', '512MB', '0B'). Prometheus reads these as powers of
    1024, so '8GB' is 8 GiB. 0 means no size limit."""
    m = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([KMGTP]?)i?B?", s.strip(), re.I)
    if not m:
        raise Fail(f"unreadable Prometheus size: {scrub(repr(s), 40)}")
    return float(m.group(1)) * 1024 ** ("BKMGTP".index(m.group(2).upper() or "B")) / 2**30


def measure_observability():
    svcs = kjson("services", "-A", "-l", "app=kube-prometheus-stack-prometheus")["items"]
    if len(svcs) != 1:
        raise Fail(f"expected exactly one Prometheus service, found {len(svcs)}")
    ns, name = svcs[0]["metadata"]["namespace"], svcs[0]["metadata"]["name"]
    port = next(p["port"] for p in svcs[0]["spec"]["ports"] if p["port"] == 9090)
    crs = kjson("prometheuses.monitoring.coreos.com", "-A")["items"]
    prefix = (crs[0]["spec"].get("routePrefix") or "/").rstrip("/") if len(crs) == 1 else ""
    rules_cr = kjson("prometheusrules.monitoring.coreos.com", "-A")["items"]
    custom = 0
    for r in rules_cr:
        if r["metadata"].get("labels", {}).get("app.kubernetes.io/managed-by") != "Helm":
            custom += sum(1 for g in r["spec"].get("groups", []) for x in g.get("rules", []) if "alert" in x)
    dashboards = dashboards_custom = 0
    for cm in kjson("configmaps", "-A", "-l", "grafana_dashboard")["items"]:
        n = sum(1 for k in cm.get("data", {}) if k.endswith(".json"))
        dashboards += n
        # the same test as alert_rules_custom: not installed by a Helm chart
        if cm["metadata"].get("labels", {}).get("app.kubernetes.io/managed-by") != "Helm":
            dashboards_custom += n

    with PortForward(ns, f"svc/{name}", port) as fwd:
        prom = Prom(f"http://127.0.0.1:{fwd.port}{prefix}")
        for _ in range(15):  # a fresh forward needs a moment
            try:
                prom.get("/api/v1/status/runtimeinfo")
                break
            except Fail:
                time.sleep(1)
        rules = prom.get("/api/v1/rules")["groups"]
        alerting = sum(1 for g in rules for r in g["rules"] if r["type"] == "alerting")
        recording = sum(1 for g in rules for r in g["rules"] if r["type"] == "recording")
        flags = prom.get("/api/v1/status/flags")
        span = prom.scalar("time() - prometheus_tsdb_lowest_timestamp_seconds") / 86400
        # Never publish a 7-day figure over less than 7 days of data: the window is
        # the shorter of 7 days and what the TSDB actually holds.
        hours = max(1, int(min(7 * 24, span * 24)))
        failed = prom.scalar(f"sum(increase(alertmanager_notifications_failed_total[{hours}h]))")
        alerts = prom.get("/api/v1/alerts")["alerts"]
        firing = [a for a in alerts if a["state"] == "firing"]
        out = {
            "scrape_up": int(prom.scalar("count(up == 1)", empty=0)),
            "scrape_total": int(prom.scalar("count(up)")),
            "series": int(prom.scalar("prometheus_tsdb_head_series")),
            "samples_per_sec": int(round(prom.scalar("sum(rate(prometheus_tsdb_head_samples_appended_total[5m]))"))),
            "alert_rules": alerting, "alert_rules_custom": custom, "recording_rules": recording,
            "dashboards": dashboards, "dashboards_custom": dashboards_custom,
            "retention_days": int(duration_days(flags["storage.tsdb.retention.time"])),
            "retention_size_gib": size_gib(flags["storage.tsdb.retention.size"]),
            "data_span_days": span,
            "notifications_failed": int(round(failed)),
            "firing_now": len(firing),
            "firing_now_excl_meta": sum(1 for a in firing if a["labels"].get("alertname") not in META_ALERTS),
        }
    return out


# ------------------------------------------------------------------------ supply chain
def image_parts(ref):
    first, _, rest = ref.partition("/")
    if rest and ("." in first or ":" in first or first == "localhost"):
        return first, rest
    return "docker.io", ref


def is_own_registry(host):
    return ":" in host or host.endswith(OWN_REGISTRY_SUFFIXES) or re.fullmatch(r"[0-9.]+", host) is not None


def measure_supply_chain(pods, plat):
    digests = {}
    for p in pods:
        if p["status"].get("phase") != "Running":
            continue
        refs = {c["name"]: c["image"] for c in p["spec"].get("containers", []) + p["spec"].get("initContainers", [])}
        for cs in p["status"].get("containerStatuses", []) + p["status"].get("initContainerStatuses", []):
            ref = refs.get(cs["name"])
            if ref:
                d = digests.setdefault(ref, set())
                m = re.search(r"@(sha256:[0-9a-f]{64})", cs.get("imageID", ""))
                if m:
                    d.add(m.group(1))
        for ref in refs.values():
            digests.setdefault(ref, set())
    # First party: pulled from the estate's own registry AND a flat repository name.
    # A mirror of someone else's software keeps its upstream org path, so it is not ours.
    first = []
    for ref in digests:
        host, path = image_parts(ref)
        if is_own_registry(host) and "/" not in path:
            first.append(ref)
    key = os.path.join(plat.dir, "infra", "k3s", "cosign.pub")
    if not os.path.isfile(key):
        raise Fail("signing public key not found in the platform repository")
    verified = 0
    for ref in first:
        if not digests[ref]:
            raise Fail("a first-party image has no recorded digest to verify")
        repo = ref.split("@")[0]
        repo = repo.rsplit(":", 1)[0] if re.search(r":[^/]+$", repo) else repo
        ok = True
        for d in sorted(digests[ref]):
            p = subprocess.run(
                ["cosign", "verify", "--key", key, "--insecure-ignore-tlog=true",
                 "--allow-insecure-registry", "--allow-http-registry", f"{repo}@{d}"],
                capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
            if p.returncode != 0:
                err = p.stderr.lower()
                if re.search(r"no such host|connection refused|timeout|dial tcp|i/o|eof", err) and "signature" not in err:
                    raise Fail("cosign could not reach the registry")
                ok = False
        verified += ok

    # SBOMs accepted by the tracker in the latest successful run of each SBOM CronJob.
    jobs = kjson("jobs.batch", "-A")["items"]
    latest = {}
    for j in jobs:
        owner = next((o["name"] for o in j["metadata"].get("ownerReferences", []) if o["kind"] == "CronJob"), None)
        if owner and "sbom" in owner and j["status"].get("succeeded") and j["status"].get("completionTime"):
            k = (j["metadata"]["namespace"], owner)
            if k not in latest or j["status"]["completionTime"] > latest[k][1]:
                latest[k] = (j["metadata"]["name"], j["status"]["completionTime"])
    if not latest:
        raise Fail("no successful SBOM job found")
    uploaded = 0
    for (ns, _owner), (job, _t) in latest.items():
        log = kubectl("-n", ns, "logs", f"job/{job}", timeout=120)
        uploaded += len(re.findall(r"uploaded to DT \(HTTP 200\b", log))
    return {
        "images_running": len(digests), "images_first_party": len(first),
        "images_third_party": len(digests) - len(first),
        "first_party_signed_verified": verified, "sbom_projects": uploaded,
    }


# ----------------------------------------------------------------------------------- ci
def workflow_jobs(text):
    """Jobs of one workflow file: [(runs-on text or None)], indentation-agnostic."""
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if re.match(r"^jobs:\s*(#.*)?$", l)), None)
    if start is None:
        return []
    jobs, jind, cur = [], None, None
    for l in lines[start + 1:]:
        if not l.strip() or l.lstrip().startswith("#"):
            continue
        ind = len(l) - len(l.lstrip(" "))
        if ind == 0:
            break
        if jind is None:
            jind = ind
        if ind == jind:
            cur = []
            jobs.append(cur)
        elif cur is not None:
            cur.append((ind, l))
    out = []
    for body in jobs:
        if not body:
            out.append(None)
            continue
        pind = min(i for i, _ in body)
        runs = None
        for n, (ind, l) in enumerate(body):
            m = re.match(r"^\s*runs-on:\s*(.*?)\s*$", l)
            if ind == pind and m:
                runs = m.group(1)
                if not runs:  # block-style list or mapping on the lines below
                    runs = " ".join(x.strip() for i2, x in body[n + 1:] if i2 > pind)
                break
        out.append(runs)
    return out


def measure_ci(plat):
    files = [f for f in plat.files if re.fullmatch(r"\.github/workflows/[^/]+\.ya?ml", f)]
    jobs = self_hosted = hosted = 0
    for f in files:
        for runs in workflow_jobs(plat.read(f)):
            jobs += 1
            if runs is None:
                continue  # a job that calls a reusable workflow has no runner of its own
            if "self-hosted" in runs:
                self_hosted += 1
            elif re.search(r"\b(ubuntu|macos|windows)-[A-Za-z0-9._-]+", runs):
                hosted += 1
            else:
                raise Fail("a workflow job has a runs-on this script cannot classify")
    hooks = len(re.findall(r"^\s*-\s*id:\s*\S+", plat.read(".pre-commit-config.yaml"), re.M))
    return {"workflows": len(files), "jobs": jobs, "runs_on_self_hosted": self_hosted,
            "runs_on_github_hosted": hosted, "precommit_hooks": hooks}


# --------------------------------------------------------------------------------- repo
def live(path):
    return RETIRED_SEGMENT not in path.split("/")


def make_targets(text):
    names = set()
    for line in text.split("\n"):
        if not line or line[0] in "\t #.@-" or line.startswith(("ifeq", "ifneq", "ifdef", "ifndef", "else", "endif")):
            continue
        head, sep, tail = line.partition(":")
        if not sep or tail.startswith("=") or "=" in head or head.strip() == "":
            continue
        for tok in head.split():
            if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.+-]*", tok) and "%" not in tok:
                names.add(tok)
    return len(names)


def gaps(text):
    open_ = closed = 0
    gap_table = False
    prev_table = False
    for l in text.split("\n"):
        is_row = l.startswith("|")
        if is_row and not prev_table:  # first row of a table is its header
            gap_table = re.match(r"^\|\s*ID\s*\|", l) is not None
        elif is_row and gap_table and re.match(r"^\|\s*\*\*[^*|]+\*\*\s*\|", l):
            open_ += 1
        prev_table = is_row
        if l.startswith("Closed:"):
            closed += len(re.findall(r"\*\*[^*]+\*\*", l))
    return open_, closed


def count_in(snap, files, pattern, flags=re.M):
    rx = re.compile(pattern, flags)
    return sum(len(rx.findall(snap.read(f))) for f in files)


def test_counts(snap):
    """Static counts of test definitions - not an executed pass count."""
    files = snap.files
    py = [f for f in files if re.search(r"(^|/)(test_[^/]*|[^/]*_test)\.py$", f)]
    go = [f for f in files if f.endswith("_test.go")]
    c = [f for f in files if re.search(r"(^|/)test_[^/]*\.c$", f)]
    return {
        "py": count_in(snap, py, r"^\s*(?:async\s+)?def test_\w*"),
        "go": count_in(snap, go, r"^func Test\w*\("),
        "c": count_in(snap, c, r"(?<!define )\bCHECK\("),
    }


def measure_repo(plat):
    r, files = PLATFORM_REPO, plat.files
    roots = [int(x) for x in git(r, "log", "--max-parents=0", "--format=%at").split()]
    gap_o, gap_c = gaps(plat.read("docs/maturity/GAPS.md"))
    cloc = json.loads(run(["cloc", "--git", "HEAD", "--json", "--quiet", f"--exclude-dir={RETIRED_SEGMENT}"],
                          cwd=r, timeout=300))
    java = [f for f in files if re.search(r"/src/test/.*\.java$", f)]
    dart = [f for f in files if re.search(r"(^|/)test/.*_test\.dart$", f)]
    pytests = [f for f in files if re.search(r"^apps/.*(^|/)(test_[^/]*|[^/]*_test)\.py$", f)]
    return {
        "commits": int(git(r, "rev-list", "--count", "HEAD")),
        "commits_30d": int(git(r, "rev-list", "--count", "--since=30 days ago", "HEAD")),
        "age_days": int((NOW.timestamp() - min(roots)) // 86400),
        "adrs": sum(1 for f in files if re.fullmatch(r"docs/adr/[0-9]{4}-.*\.md", f)),
        "gaps_open": gap_o, "gaps_closed": gap_c,
        "make_targets": sum(make_targets(plat.read(f)) for f in files
                            if live(f) and (f.rsplit("/", 1)[-1] == "Makefile" or f.endswith(".mk"))),
        "playbooks": sum(1 for f in files if live(f) and re.fullmatch(r".*/playbooks/[^/]+\.ya?ml", f)),
        "manifests": sum(1 for f in files if re.search(r"/manifests/.*\.ya?ml$", f)
                         and re.search(r"^kind:", plat.read(f), re.M)),
        "runbooks": sum(1 for f in files if live(f) and re.search(r"/runbooks/[^/]+\.md$", f)
                        and not f.endswith("README.md")),
        "docs_pages": sum(1 for f in files if live(f) and re.fullmatch(r"docs/.*\.md", f)),
        "loc": int(cloc["SUM"]["code"]),
        "loc_code": sum(int(v["code"]) for k, v in cloc.items() if k in CODE_LANGUAGES),
        "platform_head": f"{git(r, 'rev-list', '--count', 'HEAD').strip()} commits, HEAD dated "
                         f"{git(r, 'log', '-1', '--format=%cs', 'HEAD').strip()}",
        "tests_java": count_in(plat, java, r"^\s*@(?:Test|ParameterizedTest|RepeatedTest)\b"),
        "tests_python": count_in(plat, pytests, r"^\s*(?:async\s+)?def test_\w*"),
        "tests_dart": count_in(plat, dart, r"(?<![A-Za-z_])(?:test|testWidgets)\("),
    }


def measure_hardware():
    need_dir(HARDWARE_REPOS, "HARDWARE_REPOS")
    out = {}
    for key, d in HARDWARE.items():
        repo = os.path.join(HARDWARE_REPOS, d)
        need_dir(repo, f"hardware repository '{key}'")
        out[f"{key}_commits"] = int(git(repo, "rev-list", "--count", "HEAD"))
        if key in ("rover_platform", "mower", "video_rover"):
            with Snapshot(repo) as snap:
                t = test_counts(snap)
            out[f"{key}_tests"] = t["py"] + t["go"]
            if key == "rover_platform":
                out["rover_platform_c_assertions"] = t["c"]
    return out


# ------------------------------------------------------------------------------ referees
def github_slug():
    url = git(SITE, "remote", "get-url", "origin").strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    if not m:
        raise Fail("origin is not a GitHub remote")
    return m.group(1)


def github_headers():
    t = os.environ.get("GITHUB_TOKEN")
    return {"Authorization": f"Bearer {t}"} if t else {}


def shields_pct(url):
    m = re.fullmatch(r"([0-9.]+)%", http_json(url)["message"])
    if not m:
        raise Fail("uptime badge did not return a percentage")
    return float(m.group(1))


def measure_referees():
    idx = read(SITE, "docs/index.md")
    ids = {w: re.search(rf"uptimerobot/ratio/{w}/([A-Za-z0-9-]+)", idx) for w in ("7", "30")}
    hc = re.search(r"healthchecks\.io%2Fbadge%2F([0-9a-f-]+)%2F([A-Za-z0-9_-]+)\.shields", idx)
    if not all(ids.values()) or not hc:
        raise Fail("referee badges not found in docs/index.md")
    state = http_json(f"https://healthchecks.io/badge/{hc.group(1)}/{hc.group(2)}.shields")["message"]
    repo = http_json(f"https://api.github.com/repos/{github_slug()}", github_headers())
    return {
        "uptimerobot_7d": shields_pct(f"https://img.shields.io/uptimerobot/ratio/7/{ids['7'].group(1)}.json"),
        "uptimerobot_30d": shields_pct(f"https://img.shields.io/uptimerobot/ratio/30/{ids['30'].group(1)}.json"),
        "healthchecks": state.strip().lower(),
        "github_stars": int(repo["stargazers_count"]),
        "github_pushed": repo["pushed_at"],
    }


def measure_site():
    runs = http_json(f"https://api.github.com/repos/{github_slug()}/actions/runs?per_page=100",
                     github_headers())["workflow_runs"]

    def latest(name):
        for r in runs:  # newest first
            if r["name"] == name and r.get("conclusion"):
                return r
        raise Fail("no finished workflow run found in the last 100")

    pages, guard = latest("pages build and deployment"), latest("Public docs guard")
    return {
        "commits": int(git(SITE, "rev-list", "--count", "HEAD")),
        "pages": sum(1 for f in os.listdir(os.path.join(SITE, "docs")) if f.endswith(".md")),
        "pages_last_build": pages["conclusion"], "pages_last_build_at": pages["updated_at"],
        "guard_last_run": guard["conclusion"],
    }


# ------------------------------------------------------------------- schema, methods, YAML
def schema_keys():
    return [(g, k) for g, keys in SCHEMA for k, _ in keys]


def yaml_scan(path):
    """Scan the flat two-level YAML used here: (pairs, scalars, duplicates).

    A repeated key is not an error to a YAML loader - the last one silently wins - so the
    scan reports each one: a doubled generated_at, a doubled group, a doubled figure.
    """
    if not os.path.isfile(path):
        raise Fail(f"{os.path.relpath(path, SITE)} is missing")
    group, pairs, scalars, dups, groups = None, [], {}, [], set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r"^([a-z0-9_]+):\s*(.*)$", line)
            if m:
                name = m.group(1)
                if name in scalars or name in groups:
                    dups.append(name)
                if m.group(2) and not m.group(2).startswith("#"):
                    scalars[name] = m.group(2).strip().strip('"')
                    group = None
                else:
                    groups.add(name)
                    group = name
                continue
            m = re.match(r"^  ([a-z0-9_]+):", line)
            if m and group:
                if (group, m.group(1)) in pairs:
                    dups.append(f"{group}.{m.group(1)}")
                pairs.append((group, m.group(1)))
    return pairs, scalars, dups


def yaml_keys(path):
    pairs, scalars, _dups = yaml_scan(path)
    return pairs, scalars


def check_methods(stats_pairs=None, data_dir=DATA):
    problems = []
    for name in ("stats.yml", "stats_methods.yml"):
        # the generated file is checked as written; a candidate passed in has no duplicates by construction
        if stats_pairs is not None and name == "stats.yml":
            continue
        for d in yaml_scan(os.path.join(data_dir, name))[2]:
            problems.append(f"{name}: the key '{d}' appears more than once (the last one would silently win)")
    pairs = stats_pairs if stats_pairs is not None else yaml_keys(os.path.join(data_dir, "stats.yml"))[0]
    methods = set(yaml_keys(os.path.join(data_dir, "stats_methods.yml"))[0])
    for g, k in pairs:
        if (g, k) not in methods:
            problems.append(f"{g}.{k} is in stats.yml but has no method in stats_methods.yml")
    for g, k in sorted(methods - set(pairs)):
        problems.append(f"{g}.{k} has a method in stats_methods.yml but is not in stats.yml")
    return problems


def num(v, digits=1):
    if isinstance(v, int):
        return str(v)
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    return s if s else "0"


def validate(stats):
    """Every declared key present, nothing extra, every value of its declared kind."""
    for g, keys in SCHEMA:
        got = stats.get(g, {})
        for k, kind in keys:
            if k not in got:
                raise Fail(f"{g}.{k}: not measured")
            v = got[k]
            if kind == "int":
                ok = isinstance(v, int) and not isinstance(v, bool) and v >= 0
            elif kind == "float":
                ok = isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0
            else:
                ok = isinstance(v, str) and KINDS[kind].match(v) is not None
            if not ok:
                raise Fail(f"{g}.{k}: value is not a plain {kind}")
        extra = set(got) - {k for k, _ in keys}
        if extra:
            raise Fail(f"{g}: unexpected keys {sorted(extra)}")
    if set(stats) - {g for g, _ in SCHEMA}:
        raise Fail("unexpected group")


def render(stats, generated_at):
    out = ["# Generated by scripts/gather-stats.py - do not edit by hand. Regenerate with `make stats`.",
           "# Aggregates only: counts, percentages, versions, dates. How each is measured: stats_methods.yml.",
           f'generated_at: "{generated_at}"']
    for g, keys in SCHEMA:
        out.append(f"{g}:")
        for k, kind in keys:
            v = stats[g][k]
            out.append(f'  {k}: "{v}"' if kind in KINDS else f"  {k}: {num(v, 3 if k.startswith('uptimerobot') else 1)}")
    return "\n".join(out) + "\n"


README_BEGIN, README_END = "<!-- stats:begin -->", "<!-- stats:end -->"
STATUS_URL = "https://schultzzznet.github.io/schultzzznet/status.html"


def load_stats(path):
    """(stats, generated_at) from a stats.yml written by render()."""
    pairs, scalars, dups = yaml_scan(path)
    if dups:
        raise Fail("stats file has repeated keys: " + ", ".join(sorted(set(dups))))
    stats, group = {}, None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^([a-z0-9_]+):\s*$", line)
            if m:
                group = m.group(1)
                stats[group] = {}
                continue
            m = re.match(r"^  ([a-z0-9_]+):\s*(.*?)\s*$", line)
            if m and group:
                v = m.group(2).strip('"')
                if re.fullmatch(r"[0-9]+", v):
                    v = int(v)
                elif re.fullmatch(r"[0-9]+\.[0-9]+", v):
                    v = float(v)
                stats[group][m.group(1)] = v
    gen = scalars.get("generated_at")
    if not gen or not KINDS["iso"].match(gen):
        raise Fail("stats file has no valid generated_at")
    validate(stats)
    return stats, gen


def readme_block(stats, generated_at):
    """The headline aggregates as a compact Markdown table, from the measured values."""
    c, st, d, o = stats["cluster"], stats["storage"], stats["databases"], stats["observability"]
    r, ci = stats["repo"], stats["ci"]
    rows = [
        ("Nodes (Ready)", f"{c['nodes']} ({c['nodes_ready']})"),
        ("CPU cores", num(c["cores"])),
        ("Memory", f"{num(c['ram_gb'], 0)} GB"),
        ("Pods running", num(c["pods_running"])),
        ("Postgres clusters / instances", f"{d['clusters']} / {d['instances']}"),
        ("Clusters with a synchronous standby right now", f"{d['synchronous_clusters']} of {d['clusters']}"),
        ("Backup objects (completed in the last 24 hours)", f"{d['backups_total']} ({d['backups_24h']})"),
        ("Alert rules loaded", num(o["alert_rules"])),
        ("Scrape targets up", f"{o['scrape_up']} of {o['scrape_total']}"),
        ("Commits to the platform repository", num(r["commits"])),
        ("Decision records", num(r["adrs"])),
        ("Test definitions (counted, not run)", num(r["tests_java"] + r["tests_python"] + r["tests_dart"])),
        ("CI workflows", num(ci["workflows"])),
    ]
    lines = ["| Figure | Value |", "| --- | ---: |"] + [f"| {a} | {b} |" for a, b in rows]
    lines += ["", f"*Measured {generated_at} by `make stats`. What each figure counts, and the command "
                  f"behind it: [the status page]({STATUS_URL}).*"]
    return "\n".join(lines)


def readme_text(readme_path, block):
    """README text with the block spliced between the markers, or None if it has none.
    A single marker, or markers in the wrong order, is an error: silently doing nothing
    would leave a table that looks maintained and is not."""
    if not os.path.isfile(readme_path):
        return None
    with open(readme_path, encoding="utf-8") as fh:
        text = fh.read()
    b, e = text.count(README_BEGIN), text.count(README_END)
    if b == 0 and e == 0:
        return None
    if b != 1 or e != 1 or text.index(README_BEGIN) > text.index(README_END):
        raise Fail("README has the stats markers but not exactly one begin followed by one end")
    head, rest = text.split(README_BEGIN)
    _old, tail = rest.split(README_END)
    return f"{head}{README_BEGIN}\n{block}\n{README_END}{tail}"


def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def leak_guard(stats_yaml, readme_block_text=None):
    """Run the site's own leak guard over the candidate before anything is written."""
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "docs", "_data")
        os.makedirs(d)
        if stats_yaml is not None:
            with open(os.path.join(d, "stats.yml"), "w", encoding="utf-8") as fh:
                fh.write(stats_yaml)
            if os.path.isfile(METHODS):
                with open(METHODS, encoding="utf-8") as src, open(os.path.join(d, "stats_methods.yml"), "w", encoding="utf-8") as dst:
                    dst.write(src.read())
        if readme_block_text is not None:
            with open(os.path.join(tmp, "docs", "readme-block.md"), "w", encoding="utf-8") as fh:
                fh.write(readme_block_text)
        env = dict(os.environ, GUARD_CONTENT_ONLY="1")
        p = subprocess.run([GUARD, "docs"], cwd=tmp, env=env, capture_output=True, text=True)
        if p.returncode != 0:
            # the report names the pattern, not the match, so it is safe to show
            labels = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
            raise Fail("the leak guard refused the generated file: " + "; ".join(labels))


# --------------------------------------------------------------------------------- main
def verify(what, max_age, data_dir):
    if what == "methods":
        problems = check_methods(None, data_dir)
    else:
        _pairs, scalars, dups = yaml_scan(os.path.join(data_dir, "stats.yml"))
        problems = [f"docs/_data/stats.yml: the key '{d}' appears more than once (the last one would silently win)"
                    for d in dups if d == "generated_at"]
        gen = scalars.get("generated_at")
        if not gen or not KINDS["iso"].match(gen):
            problems.append("docs/_data/stats.yml has no valid generated_at")
        else:
            age = (NOW - parse_time(gen)).total_seconds() / 86400
            if age > max_age:
                problems.append(f"docs/_data/stats.yml was generated {age:.1f} days ago (limit {max_age:g})")
            elif age < -CLOCK_SKEW_DAYS:
                # A timestamp in the future would never age out: it would pass this guard for
                # as long as it stayed in the future. Allow for clock skew, nothing more.
                problems.append(f"docs/_data/stats.yml claims to be generated {-age:.1f} days in the future "
                                f"(more than {CLOCK_SKEW_DAYS * 24:g} hours of clock skew is not allowed)")
    for p in problems:
        print(p)
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", choices=("freshness", "methods"))
    ap.add_argument("--max-age-days", type=float, default=21)
    ap.add_argument("--data-dir", default=DATA)
    ap.add_argument("--vet", metavar="FILE")
    ap.add_argument("--no-readme", action="store_true")
    ap.add_argument("--readme", default=README, metavar="FILE")
    ap.add_argument("--readme-from-stats", metavar="FILE")
    a = ap.parse_args()
    try:
        if a.readme_from_stats:
            stats, gen = load_stats(a.readme_from_stats)
            block = readme_block(stats, gen)
            new = readme_text(a.readme, block)
            if new is None:
                print("no stats markers in the README: nothing to do")
                return 0
            leak_guard(None, block)
            write_atomic(a.readme, new)
            print(f"updated the stats block in {os.path.basename(a.readme)}")
            return 0
        if a.vet:
            leak_guard(read("", a.vet) if os.path.isabs(a.vet) else read(os.getcwd(), a.vet))
            print("leak guard accepts the file")
            return 0
        if a.verify:
            return verify(a.verify, a.max_age_days, a.data_dir)
        # Everything the run needs, checked before the first measurement, so a missing
        # tool or path fails in a second rather than after half the cluster was read.
        for var, val in (("PLATFORM_REPO", PLATFORM_REPO), ("HARDWARE_REPOS", HARDWARE_REPOS)):
            if not val:
                raise Fail(f"{var} is not set. Export it (the private platform checkout, and the directory "
                           "holding the private hardware checkouts) or run `make stats`, which sets both "
                           "from $HOME; see the Makefile header.")
            need_dir(val, var)
        for tool in ("kubectl", "git", "cloc", "cosign"):
            if shutil.which(tool) is None:
                raise Fail(f"{tool} is not installed")
        if not os.path.isfile(KUBECONFIG):
            raise Fail("KUBECONFIG does not point at a file")
        stats = {}
        cluster, pods = measure_cluster()
        stats["cluster"] = cluster
        print("  extracting the committed platform tree ...", file=sys.stderr)
        with Snapshot(PLATFORM_REPO) as plat:
            for group, fn, args in (
                ("storage", measure_storage, ()), ("databases", measure_databases, ()),
                ("observability", measure_observability, ()),
                ("supply_chain", measure_supply_chain, (pods, plat)), ("ci", measure_ci, (plat,)),
                ("repo", measure_repo, (plat,)), ("hardware", measure_hardware, ()),
                ("referees", measure_referees, ()), ("site", measure_site, ()),
            ):
                print(f"  measuring {group} ...", file=sys.stderr)
                stats[group] = fn(*args)
        validate(stats)
        problems = check_methods(schema_keys())
        if problems:
            raise Fail("; ".join(problems))
        generated_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        text = render(stats, generated_at)
        block = readme_block(stats, generated_at)
        new_readme = None if a.no_readme else readme_text(a.readme, block)
        leak_guard(text, block if new_readme is not None else None)
    except Fail as e:
        print(f"FAIL: {e}\nNothing was written.", file=sys.stderr)
        return 1
    if a.dry_run:
        sys.stdout.write(text)
        print("dry run: nothing written", file=sys.stderr)
        return 0
    write_atomic(STATS, text)
    if new_readme is not None:
        write_atomic(a.readme, new_readme)
        print(f"updated the stats block in {os.path.basename(a.readme)}")
    print(f"wrote {os.path.relpath(STATS, SITE)} ({len(schema_keys())} figures, {generated_at})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
