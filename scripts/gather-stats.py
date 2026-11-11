#!/usr/bin/env python3
"""Measure the estate and write docs/_data/stats.yml - the numbers behind docs/status.md.

Every figure is MEASURED here, at generation time, by a command this script runs:
kubectl (read-only, see below), git, cloc and the GitHub REST API. Nothing is copied from
a document, except the counts of steps, rules and components, which are parsed from the
platform repository's own generated status page (and that page is checked against its
tables so a change of shape fails loudly).

What it publishes is AGGREGATES ONLY - counts, percentages, dates, a few words. It never
writes a host, address, namespace, workload or secret name. Three things enforce that:
each key is declared below with a strict value type (a number, a date, a timestamp, a
lower-case word or the exact phrase 'not measured yet' - nothing free-form can get through);
the finished file is run through the site's own leak guard before it is written; and it
fails loudly rather than write a partial file when a measurement fails or a key has no method.

The platform repository is read from a fresh bare clone of its remote main branch, made
into a temporary directory and deleted again, so a half-edited local branch can never
move a published number. Offline, PLATFORM_REF=origin/main reads the local remote-tracking
branch instead, and fails if that was last fetched more than 24 hours ago. The hardware
repositories are read from their default branch, not from whatever is checked out.

THE CLUSTER ACCESS IS READ-ONLY BY CONSTRUCTION, NOT BY CREDENTIAL. The kubeconfig this
runs with may well be cluster-admin, so the only barrier is the allowlist in kubectl():
`get` (never of secrets, never watching), `get --raw` under the metrics API, `version` and
`top`. Everything else (exec, logs, port-forward, apply, patch, delete, create, edit,
label, annotate, cp, debug, ...) is refused before a process is spawned. Do not widen it
without a reason written next to the change. The one exception is class PrometheusForward:
a port-forward to the metrics store's own service (fixed namespace and service, loopback
only), used for three GET requests of its read-only HTTP API (targets, rules, one query) and
closed again. It starts its own process and does NOT go through kubectl(), so the allowlist
above does not cover it; the fixed arguments in that class are its only barrier.

Some figures cannot be measured yet because the thing they measure is not running. Those
carry the exact value 'not measured yet' (kind nm), never 0 and never an older number. A
registry of probes (PENDING) makes the generator FAIL as soon as one of those things
appears on the cluster, so the gap cannot silently outlive the day it closes.

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
  PLATFORM_REPO    REQUIRED for a measuring run: a checkout of the private platform repository
                   (only its origin URL is used, and never printed, unless PLATFORM_REF is set)
  HARDWARE_REPOS   REQUIRED for a measuring run: the directory holding the private hardware
                   repositories
  KUBECONFIG       REQUIRED for a measuring run: the cluster's kubeconfig. There is no default,
                   so a run can never silently measure an old cluster.
  PLATFORM_REF     optional, offline only: read this local ref (e.g. origin/main) instead of cloning
  GITHUB_TOKEN     optional; raises the GitHub API rate limit, never printed

README.md: if it contains the markers <!-- stats:begin --> and <!-- stats:end -->, whatever is
between them is replaced with a table of the headline aggregates, built from the same measured
values and vetted by the same leak guard. Without the markers nothing is touched.

Standard library only; it also needs kubectl, git and cloc on the PATH.
No command here pipes into another: output is filtered by the command's own options or
parsed in Python.
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, "docs", "_data")
STATS = os.path.join(DATA, "stats.yml")
METHODS = os.path.join(DATA, "stats_methods.yml")
GUARD = os.path.join(SITE, "scripts", "check-public-docs.sh")
INDEX_MD = os.path.join(SITE, "docs", "index.md")

README = os.path.join(SITE, "README.md")
# No default: a path to a private checkout does not belong in a public file. A measuring run
# says so up front (see main) if any of the three is unset.
PLATFORM_REPO = os.path.expanduser(os.environ.get("PLATFORM_REPO", ""))
PLATFORM_REF = os.environ.get("PLATFORM_REF", "")
HARDWARE_REPOS = os.path.expanduser(os.environ.get("HARDWARE_REPOS", ""))
KUBECONFIG = os.path.expanduser(os.environ.get("KUBECONFIG", ""))

# hardware key -> directory name under HARDWARE_REPOS
HARDWARE = {
    "printing": "thePrintingIn3D",
    "yocto": "theSchultzYocto",
    "rover_platform": "theRoverPlatform",
    "mower": "theMowerRetrofit",
    "video_rover": "theVideoRover",
    "imx8": "theImx8Yocto",
}

NM = "not measured yet"

# --- the contract: every published key, its group order, and what a value may look like ---
# kinds: int (>= 0), float (finite, >= 0), ver (a version string), iso (UTC timestamp),
# date (a day), word (one lower-case word), nm (exactly 'not measured yet'). Anything else
# is refused before it can be written.
SCHEMA = [
    ("cluster", [
        ("nodes", "int"), ("nodes_ready", "int"), ("control_plane", "int"), ("agents", "int"),
        ("cores", "int"), ("ram_gb", "float"),
        ("pods_running", "int"), ("pods_total", "int"), ("namespaces", "int"),
        ("containers", "int"), ("deployments", "int"), ("statefulsets", "int"),
        ("daemonsets", "int"), ("cronjobs", "int"), ("hpas", "int"), ("ingresses", "int"),
        ("pvcs", "int"), ("pvc_gib", "float"), ("crds", "int"),
        ("age_days", "int"), ("restarts_total", "int"),
    ]),
    ("storage", [
        ("storage_classes", "int"), ("default_storage_classes", "int"), ("pvcs_bound", "int"),
    ]),
    ("reconciler", [
        ("kustomizations", "int"), ("kustomizations_ready", "int"),
        ("kustomizations_suspended", "int"), ("kustomizations_prune_on", "int"),
        ("sources_ready", "int"), ("revisions_in_use", "int"), ("artifact_age_hours", "int"),
        ("artifact_signed", "nm"),
    ]),
    ("admission", [
        ("policies", "int"), ("policies_ready", "int"), ("policies_deny", "int"),
        ("namespaces_signature_enforced", "int"), ("namespaces_podsecurity_restricted", "int"),
        ("network_policies", "int"), ("tenant_namespaces", "int"), ("tenants_default_deny", "int"),
        ("quotas", "int"), ("quota_max_used_pct", "int"),
        ("first_party_signed_verified", "nm"),
    ]),
    ("databases", [
        ("clusters", "int"), ("instances", "int"), ("instances_ready", "int"), ("replicas", "int"),
        ("postgres_major", "int"), ("synchronous_clusters_spec", "int"),
        ("clusters_spread_over_nodes", "int"), ("poolers", "int"), ("scheduled_backups", "int"),
        ("backups_total", "int"), ("backups_failed", "int"), ("backups_24h", "int"),
        ("archiving_clusters", "int"),
    ]),
    ("evidence", [
        ("restore_drill_home_last", "date"), ("restore_drill_home_result", "word"),
        ("restore_drill_home_age_days", "int"), ("restore_drills_records", "int"),
        ("default_deny_probe_home_date", "date"), ("default_deny_probe_home_result", "word"),
        ("host_rehearsal_date", "date"), ("host_rehearsal_result", "word"),
        ("steps_total", "int"), ("steps_done", "int"), ("steps_done_on_kind", "int"),
        ("steps_partly", "int"), ("steps_not_started", "int"), ("steps_gated", "int"),
        ("rules_total", "int"), ("rules_built", "int"), ("rules_partly", "int"),
        ("inventory_total", "int"), ("inventory_proven", "int"), ("inventory_built", "int"),
    ]),
    ("observability", [
        ("scrape_targets", "int"), ("alert_rules", "int"), ("recording_rules", "int"),
        ("dashboards", "int"), ("metric_history_days", "float"),
        ("alerts_reaching_a_person", "nm"), ("sbom_projects", "nm"),
    ]),
    ("ci", [
        ("workflows", "int"), ("jobs", "int"), ("runs_on_self_hosted", "int"),
        ("runs_on_github_hosted", "int"), ("runs_on_routed", "int"), ("precommit_hooks", "int"),
    ]),
    ("repo", [
        ("commits", "int"), ("commits_30d", "int"), ("age_days", "int"), ("adrs", "int"),
        ("records", "int"), ("records_pass", "int"), ("records_fail", "int"),
        ("check_scripts", "int"), ("playbooks", "int"), ("manifests", "int"),
        ("runbooks", "int"), ("docs_pages", "int"), ("loc", "int"), ("loc_code", "int"),
        ("tests_java", "int"), ("app_warn_version", "ver"),
    ]),
    ("hardware", [
        ("printing_commits", "int"), ("yocto_commits", "int"),
        ("rover_platform_commits", "int"), ("rover_platform_tests", "int"),
        ("rover_platform_c_assertions", "int"),
        ("mower_commits", "int"), ("mower_tests", "int"),
        ("video_rover_commits", "int"), ("video_rover_tests", "int"),
        ("imx8_commits", "int"),
    ]),
    ("site", [
        ("commits", "int"), ("pages", "int"), ("pages_last_build", "word"),
        ("pages_last_build_at", "iso"), ("guard_last_run", "word"), ("last_push", "iso"),
    ]),
]
KINDS = {
    "ver": re.compile(r"^v?[0-9]+(\.[0-9]+){1,3}([+-][0-9A-Za-z.]+)?$"),
    "iso": re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"),
    "date": re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"),
    "word": re.compile(r"^[a-z][a-z_-]{0,19}$"),
    "nm": re.compile(r"^not measured yet$"),
}

# cloc languages counted as programming code for repo.loc_code. Markdown, YAML, JSON, XML,
# HTML, SVG, INI, TOML, properties and build manifests are left out on purpose.
CODE_LANGUAGES = frozenset((
    "Dart", "Java", "Kotlin", "Swift", "Python", "Go", "C", "C++", "C/C++ Header", "Objective-C",
    "JavaScript", "TypeScript", "Bourne Shell", "Bourne Again Shell", "Zsh", "SQL", "Rust", "Ruby",
    "Lua", "Perl", "PowerShell"))

NOW = dt.datetime.now(dt.timezone.utc)
CLOCK_SKEW_DAYS = 2 / 24  # a generation time may be at most two hours ahead of this machine's clock
MAX_REF_AGE_HOURS = 24    # an offline PLATFORM_REF may not have been fetched longer ago than this


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


# kubectl verbs that change or expose things. Named only so the refusal can say why; the
# allowlist below is what actually decides, and it refuses anything not on it.
KUBECTL_REFUSED = frozenset((
    "exec", "logs", "port-forward", "apply", "patch", "delete", "create", "edit", "label",
    "annotate", "cp", "debug", "replace", "scale", "rollout", "drain", "cordon", "uncordon",
    "taint", "set", "run", "expose", "attach", "proxy", "auth", "certificate", "config", "plugin"))
KUBECTL_METRICS_PREFIX = "/apis/metrics.k8s.io/"
KUBECTL_FORBIDDEN_FLAGS = ("--kubeconfig", "--token", "--as", "--server", "--context",
                           "--insecure", "--client-", "--username", "--password", "-s")


def check_kubectl(args):
    """Refuse, before any process exists, everything but a read-only get/version/top."""
    if not args:
        raise Fail("kubectl called with no arguments")
    verb = args[0]
    if verb in KUBECTL_REFUSED:
        raise Fail(f"kubectl {verb} is refused: this script only reads")
    if verb not in ("get", "version", "top"):
        raise Fail(f"kubectl {verb} is not on the allowlist (get, get --raw metrics, version, top)")
    for a in args[1:]:
        if a in ("-w", "--watch", "--watch-only"):
            raise Fail("kubectl get --watch is refused")
        if a.startswith(KUBECTL_FORBIDDEN_FLAGS):
            raise Fail("a kubectl flag that changes identity or server is refused")
    if verb != "get":
        return
    if "--raw" in args:
        i = args.index("--raw")
        if i + 1 >= len(args) or not args[i + 1].startswith(KUBECTL_METRICS_PREFIX):
            raise Fail("kubectl get --raw is allowed only under the metrics API")
        return
    positional = [a for a in args[1:] if not a.startswith("-")]
    if not positional:
        raise Fail("kubectl get without a resource is refused")
    for a in args[1:]:
        if a.startswith("-"):
            continue
        for part in a.split(","):
            if part.split("/")[0].split(".")[0].lower() in ("secret", "secrets"):
                raise Fail("kubectl get of secrets is refused")


def kubectl(*args, timeout=180):
    check_kubectl(args)
    return run(["kubectl", "--request-timeout=30s", *args], env=kenv(), timeout=timeout)


def kjson(*args):
    try:
        return json.loads(kubectl("get", *args, "-o", "json"))
    except json.JSONDecodeError as e:
        raise Fail(f"kubectl get {args[0]}: not JSON ({scrub(e)})")


def git(repo, *args):
    return run(["git", *args], cwd=repo)


class Snapshot:
    """The tree of one ref, extracted to a temporary directory.

    Counts are taken from what is COMMITTED on a named ref, not from whatever is half-edited
    in a working tree, so two runs against the same commit agree and a colleague's unsaved
    change cannot move a published number.
    """

    def __init__(self, repo, ref):
        self.repo, self.ref = repo, ref

    def __enter__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        p = subprocess.Popen(["git", "-C", self.repo, "archive", "--format=tar", self.ref],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=p.stdout, mode="r|") as tf:
                if hasattr(tarfile, "data_filter"):
                    tf.extractall(self.dir, filter="data")
                else:
                    tf.extractall(self.dir)
        except (tarfile.TarError, OSError) as e:
            p.kill()
            raise Fail(f"could not extract a repository ref: {scrub(e)}")
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


class PlatformSource:
    """(repo directory, ref) for the private platform repository's main branch.

    Normally a bare clone of the remote main into a temporary directory that is deleted on
    exit. The origin URL is resolved from the checkout and never printed (git's own errors
    go through scrub()). With PLATFORM_REF set (offline), that local ref is used instead,
    and it must have been fetched within MAX_REF_AGE_HOURS.
    """

    def __enter__(self):
        self._tmp = None
        if PLATFORM_REF:
            self.repo, self.ref = PLATFORM_REPO, PLATFORM_REF
            git(self.repo, "rev-parse", "--verify", "--quiet", self.ref + "^{commit}")
            fh = git(self.repo, "rev-parse", "--git-path", "FETCH_HEAD").strip()
            fh = fh if os.path.isabs(fh) else os.path.join(self.repo, fh)
            if not os.path.isfile(fh):
                raise Fail("PLATFORM_REF is set but the checkout has never been fetched; run git fetch")
            age_h = (NOW.timestamp() - os.path.getmtime(fh)) / 3600
            if age_h > MAX_REF_AGE_HOURS:
                raise Fail(f"PLATFORM_REF was last fetched {age_h:.0f} hours ago (limit {MAX_REF_AGE_HOURS}); "
                           "run git fetch, or unset PLATFORM_REF to clone")
            return self
        url = git(PLATFORM_REPO, "remote", "get-url", "origin").strip()
        self._tmp = tempfile.TemporaryDirectory()
        self.repo, self.ref = os.path.join(self._tmp.name, "p.git"), "main"
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        run(["git", "clone", "--bare", "--single-branch", "--branch", "main", "--quiet", url, self.repo],
            env=env, timeout=300)
        return self

    def __exit__(self, *exc):
        if self._tmp is not None:
            self._tmp.cleanup()
        return False


def default_ref(repo):
    """The repository's default branch as a ref: origin/HEAD if set, else origin/main|master, else main|master."""
    try:
        sym = git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD").strip()
        if sym:
            return sym[len("refs/remotes/"):]
    except Fail:
        pass
    for cand in ("origin/main", "origin/master", "main", "master"):
        try:
            git(repo, "rev-parse", "--verify", "--quiet", cand + "^{commit}")
            return cand
        except Fail:
            continue
    raise Fail("a hardware repository has no default branch to read")


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
    raise Fail(f"GET failed: {scrub(last)}")


# ----------------------------------------------------------------------------- cluster
def conds_true(obj, kind="Ready"):
    return any(c.get("type") == kind and c.get("status") == "True"
               for c in obj.get("status", {}).get("conditions", []))


def measure_cluster():
    nodes = kjson("nodes")["items"]
    pods = kjson("pods", "-A")["items"]
    ready = sum(1 for n in nodes if conds_true(n))
    cp = sum(1 for n in nodes if "node-role.kubernetes.io/control-plane" in n["metadata"].get("labels", {}))
    running = [p for p in pods if p["status"].get("phase") == "Running"]
    restarts = 0
    for p in pods:
        for c in p["status"].get("containerStatuses", []) + p["status"].get("initContainerStatuses", []):
            restarts += c.get("restartCount", 0)
    pvcs = kjson("persistentvolumeclaims", "-A")["items"]
    oldest = min(parse_time(n["metadata"]["creationTimestamp"]) for n in nodes)
    crds = [c["metadata"]["name"] for c in kjson("customresourcedefinitions.apiextensions.k8s.io")["items"]]

    def count(kind):
        return len(kjson(kind, "-A")["items"])

    images = [c["image"] for p in pods for c in p["spec"].get("containers", []) + p["spec"].get("initContainers", [])]
    names = [j["metadata"]["name"] for kind in ("jobs.batch", "cronjobs.batch") for j in kjson(kind, "-A")["items"]]
    ctx = {"crds": set(crds), "images": images, "job_names": names, "pods": pods}
    return {
        "nodes": len(nodes), "nodes_ready": ready, "control_plane": cp, "agents": len(nodes) - cp,
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
        "crds": len(crds),
        "age_days": int((NOW - oldest).total_seconds() // 86400),
        "restarts_total": restarts,
    }, ctx


# ----------------------------------------------------------------------------- storage
def measure_storage():
    classes = kjson("storageclasses.storage.k8s.io")["items"]
    default_keys = ("storageclass.kubernetes.io/is-default-class", "storageclass.beta.kubernetes.io/is-default-class")
    default = sum(1 for c in classes if any(c["metadata"].get("annotations", {}).get(k) == "true" for k in default_keys))
    pvcs = kjson("persistentvolumeclaims", "-A")["items"]
    return {
        "storage_classes": len(classes), "default_storage_classes": default,
        "pvcs_bound": sum(1 for c in pvcs if c.get("status", {}).get("phase") == "Bound"),
    }


# --------------------------------------------------------------------------- reconciler
SOURCE_KINDS = ("gitrepositories.source.toolkit.fluxcd.io", "ocirepositories.source.toolkit.fluxcd.io",
                "helmrepositories.source.toolkit.fluxcd.io", "buckets.source.toolkit.fluxcd.io")


def measure_reconciler():
    ks = kjson("kustomizations.kustomize.toolkit.fluxcd.io", "-A")["items"]
    if not ks:
        raise Fail("no Flux Kustomizations found")
    sources = [s for kind in SOURCE_KINDS for s in kjson(kind, "-A")["items"]]
    ages = []
    for s in sources:
        art = s.get("status", {}).get("artifact")
        if not art:
            continue
        built = art.get("metadata", {}).get("org.opencontainers.image.created") or art.get("lastUpdateTime")
        if built:
            ages.append((NOW - parse_time(built)).total_seconds() / 3600)
    if not ages:
        raise Fail("no source artifact with a build time found")
    return {
        "kustomizations": len(ks),
        "kustomizations_ready": sum(1 for k in ks if conds_true(k)),
        "kustomizations_suspended": sum(1 for k in ks if k["spec"].get("suspend")),
        "kustomizations_prune_on": sum(1 for k in ks if k["spec"].get("prune")),
        "sources_ready": sum(1 for s in sources if conds_true(s)),
        "revisions_in_use": len({k["status"].get("lastAppliedRevision") for k in ks
                                 if k.get("status", {}).get("lastAppliedRevision")}),
        # the age of the OLDEST artifact in use, so a stale one cannot hide behind a fresh one
        "artifact_age_hours": int(max(ages)),
        # a source verification block is the only thing that would make this measurable; the
        # artifact is not signed today, and a signed one would need a different probe
        "artifact_signed": NM,
    }


# ---------------------------------------------------------------------------- admission
POLICY_KINDS = ("validatingpolicies.policies.kyverno.io", "imagevalidatingpolicies.policies.kyverno.io",
                "mutatingpolicies.policies.kyverno.io")


def is_default_deny(np):
    """A structural test: selects every pod, covers both directions, allows nothing."""
    spec = np["spec"]
    return (not spec.get("podSelector")
            and set(spec.get("policyTypes", [])) >= {"Ingress", "Egress"}
            and not spec.get("ingress") and not spec.get("egress"))


def measure_admission():
    # The NEW policy kinds. The old ClusterPolicy kind is deliberately not counted: nothing
    # here uses it, and a count of it would read 0 and look like an absence of policy.
    pols = [p for kind in POLICY_KINDS for p in kjson(kind)["items"]]
    ready = sum(1 for p in pols if p.get("status", {}).get("conditionStatus", {}).get("ready") is True)
    deny = sum(1 for p in pols if "Deny" in (p["spec"].get("validationActions") or []))
    ns = kjson("namespaces")["items"]
    labels = [n["metadata"].get("labels", {}) for n in ns]
    sig = sum(1 for l in labels if l.get("signature-check") == "enforce")
    psa = sum(1 for l in labels if l.get("pod-security.kubernetes.io/enforce") == "restricted")
    nps = kjson("networkpolicies.networking.k8s.io", "-A")["items"]
    tenants = {n["metadata"]["name"] for n in ns if "signature-check" in n["metadata"].get("labels", {})}
    deny_ns = {np["metadata"]["namespace"] for np in nps if is_default_deny(np)}
    quotas = kjson("resourcequotas", "-A")["items"]
    pct = 0.0
    for q in quotas:
        hard = q.get("status", {}).get("hard", {})
        for res, h in hard.items():
            hv = quantity(h)
            if hv > 0:
                pct = max(pct, 100 * quantity(q["status"].get("used", {}).get(res, "0")) / hv)
    return {
        "policies": len(pols), "policies_ready": ready, "policies_deny": deny,
        "namespaces_signature_enforced": sig, "namespaces_podsecurity_restricted": psa,
        "network_policies": len(nps), "tenant_namespaces": len(tenants),
        "tenants_default_deny": len(tenants & deny_ns),
        "quotas": len(quotas), "quota_max_used_pct": int(round(pct)),
        # verifying a signature needs a registry credential, which this script must not hold
        "first_party_signed_verified": NM,
    }


# --------------------------------------------------------------------------- databases
def measure_databases():
    clusters = kjson("clusters.postgresql.cnpg.io", "-A")["items"]
    if not clusters:
        raise Fail("no database clusters found")
    # Operator objects only: no exec, no SQL. Whether a standby is synchronous RIGHT NOW is
    # therefore not measured; only what the spec asks for is.
    pods = kjson("pods", "-A", "-l", "cnpg.io/podRole=instance")["items"]
    by_cluster = {}
    for p in pods:
        key = (p["metadata"]["namespace"], p["metadata"]["labels"].get("cnpg.io/cluster"))
        by_cluster.setdefault(key, []).append(p["spec"].get("nodeName"))
    spread = sum(1 for c in clusters
                 if (lambda ns: len(ns) > 1 and None not in ns and len(set(ns)) == len(ns))(
                     by_cluster.get((c["metadata"]["namespace"], c["metadata"]["name"]), [])))
    majors = [c["status"]["pgDataImageInfo"]["majorVersion"] for c in clusters]
    sync_spec = archiving = 0
    for c in clusters:
        spec = c["spec"]
        sync_spec += bool(spec.get("postgresql", {}).get("synchronous")) or spec.get("minSyncReplicas", 0) > 0
        archiving += any(x["type"] == "ContinuousArchiving" and x["status"] == "True"
                         for x in c["status"].get("conditions", []))
    instances = sum(c["status"]["instances"] for c in clusters)
    # Plugin-driven backups leave the cluster's own lastSuccessfulBackup empty, so the Backup
    # objects are what is counted.
    backups = kjson("backups.postgresql.cnpg.io", "-A")["items"]
    day = 0
    for b in backups:
        s = b.get("status", {})
        if s.get("phase") == "completed" and s.get("stoppedAt") and \
                (NOW - parse_time(s["stoppedAt"])).total_seconds() <= 86400:
            day += 1
    return {
        "clusters": len(clusters), "instances": instances,
        "instances_ready": sum(c["status"].get("readyInstances", 0) for c in clusters),
        "replicas": instances - len(clusters),
        "postgres_major": min(majors),
        "synchronous_clusters_spec": sync_spec,
        "clusters_spread_over_nodes": spread,
        "poolers": len(kjson("poolers.postgresql.cnpg.io", "-A")["items"]),
        "scheduled_backups": len(kjson("scheduledbackups.postgresql.cnpg.io", "-A")["items"]),
        "backups_total": len(backups),
        "backups_failed": sum(1 for b in backups if b.get("status", {}).get("phase") == "failed"),
        "backups_24h": day, "archiving_clusters": archiving,
    }


# ----------------------------------------------------------------------- observability
# Five figures are measured from the running metrics store (a read-only port-forward to its
# HTTP API) and from git. Two cannot be yet: where alerts go and whether an SBOM is uploaded.
# Each probe below turns True the day its thing exists, and main() then FAILS, so a 'not
# measured yet' cannot outlive the gap by accident. When one fires: write the measurement,
# change the key's kind from nm, and delete the probe.
def _image_repo(ref):
    return ref.split("@")[0].rsplit(":", 1)[0].rsplit("/", 1)[-1] if ref else ""


# Receivers that wake a person: an on-call or SMS/phone/e-mail service. A chat webhook is
# not one (it is a window onto alerts, nothing keeps paging until someone answers).
PAGING_RECEIVERS = ("pagerduty_configs", "opsgenie_configs", "victorops_configs", "pushover_configs",
                    "sns_configs", "email_configs", "webex_configs", "telegram_configs",
                    "wechat_configs", "msteams_configs", "jira_configs", "rocketchat_configs")
ALERT_ROUTER_FILE = "platform/services/monitoring/alertmanager/alertmanager.yml"


def _alerts_page_someone(ctx):
    text = ctx.get("alert_router_config") or ""
    return any(re.search(rf"^\s*{k}\s*:", text, re.M) for k in PAGING_RECEIVERS)


PENDING = [
    ("an alert route that reaches a person (a paging, phone or e-mail receiver)", _alerts_page_someone),
    ("SBOM upload (an SBOM job or cron job)",
     lambda ctx: any("sbom" in n.lower() for n in ctx["job_names"])),
    ("Helm releases (the HelmRelease resource definition)",
     lambda ctx: "helmreleases.helm.toolkit.fluxcd.io" in ctx["crds"]),
]


def check_pending(ctx):
    for name, probe in PENDING:
        if probe(ctx):
            raise Fail(f"{name} is now measurable: replace the not-measured entry")


PROM_NAMESPACE, PROM_SERVICE, PROM_PORT = "monitoring", "prometheus", 9090


class PrometheusForward:
    """A read-only port-forward to the metrics store's service, open only while used.

    kubectl() refuses port-forward on purpose, so this is the single place that starts one:
    fixed namespace and service, local loopback only, a random local port, closed on exit.
    """

    def __enter__(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            self.port = s.getsockname()[1]
        self.proc = subprocess.Popen(
            ["kubectl", "--request-timeout=30s", "-n", PROM_NAMESPACE, "port-forward", "--address", "127.0.0.1",
             f"svc/{PROM_SERVICE}", f"{self.port}:{PROM_PORT}"],
            env=kenv(), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(30):
            if self.proc.poll() is not None:
                break
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=1):
                    return self
            except OSError:
                time.sleep(0.5)
        self.__exit__()
        raise Fail("could not open a read-only connection to the metrics store")

    def __exit__(self, *exc):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        return False

    def get(self, path):
        d = http_json(f"http://127.0.0.1:{self.port}{path}")
        if d.get("status") != "success":
            raise Fail(f"the metrics store answered {path.split('?')[0]} with an error")
        return d["data"]


def measure_observability(plat, ctx):
    with PrometheusForward() as prom:
        targets = prom.get("/api/v1/targets?state=active")["activeTargets"]
        groups = prom.get("/api/v1/rules")["groups"]
        # Oldest sample held anywhere (blocks and the in-memory head), as the store itself reports it,
        # against the store's own clock so this machine's clock cannot skew it.
        q = prom.get("/api/v1/query?query=" + urllib.parse.quote("time() - prometheus_tsdb_lowest_timestamp_seconds"))
        if q.get("resultType") != "vector" or len(q.get("result", [])) != 1:
            raise Fail("the metrics store did not report how old its oldest sample is")
        held = float(q["result"][0]["value"][1])
    rules = [r for g in groups for r in g.get("rules", [])]
    if not targets:
        raise Fail("the metrics store reports no active target")
    if not math.isfinite(held) or held < 0:
        raise Fail("the metrics store reported an unusable history length")
    # Dashboards: JSON files committed under the metrics UI's manifest directory in git (no
    # provisioning config is checked, other directories and ConfigMap YAML are not counted). Nothing is read from the running UI and nobody logs in to it.
    dashboards = sum(1 for f in plat.files
                     if f.startswith("platform/services/monitoring/grafana/") and f.endswith(".json"))
    ctx["alert_router_config"] = plat.read(ALERT_ROUTER_FILE) if ALERT_ROUTER_FILE in plat.files else ""
    out = {k: NM for k, _ in dict(SCHEMA)["observability"]}
    out.update({
        "scrape_targets": sum(1 for t in targets if t.get("health") == "up"),
        "alert_rules": sum(1 for r in rules if r.get("type") == "alerting"),
        "recording_rules": sum(1 for r in rules if r.get("type") == "recording"),
        "dashboards": dashboards,
        "metric_history_days": round(held / 86400, 2),
    })
    return out


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
    jobs = self_hosted = hosted = routed = 0
    for f in files:
        for runs in workflow_jobs(plat.read(f)):
            jobs += 1
            if runs is None:
                continue  # a job that calls a reusable workflow has no runner of its own
            if "${{" in runs:  # chosen by an expression at run time: classified before the name tests
                routed += 1
            elif "self-hosted" in runs:
                self_hosted += 1
            elif re.search(r"\b(ubuntu|macos|windows)-[A-Za-z0-9._-]+", runs):
                hosted += 1
            else:
                raise Fail("a workflow job has a runs-on this script cannot classify")
    hooks = len(re.findall(r"^\s*-\s*id:\s*\S+", plat.read(".pre-commit-config.yaml"), re.M))
    return {"workflows": len(files), "jobs": jobs, "runs_on_self_hosted": self_hosted,
            "runs_on_github_hosted": hosted, "runs_on_routed": routed, "precommit_hooks": hooks}


# ------------------------------------------------------------------------------ records
def record_fields(text):
    """The '- **Field:** value' lines of one run record, by lower-cased field name."""
    out = {}
    for m in re.finditer(r"^- \*\*([A-Za-z ]+):\*\*\s*(.*)$", text, re.M):
        out.setdefault(m.group(1).strip().lower(), m.group(2).strip())
    return out


def load_records(plat):
    recs = []
    for f in plat.files:
        if not re.fullmatch(r"records/20[0-9]{2}-[0-9]{2}-[0-9]{2}-[^/]+\.md", f):
            continue
        fields = record_fields(plat.read(f))
        d = re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", fields.get("date", ""))
        res = re.match(r"(pass|fail)\b", fields.get("result", "").lower())
        if not d or not res:
            raise Fail("a run record has no readable Date or a Result other than pass or fail")
        recs.append({"name": os.path.basename(f), "date": d.group(0), "result": res.group(1),
                     "home": "home site" in fields.get("where", "").lower()})
    if not recs:
        raise Fail("no run records found")
    return recs


def latest(recs, needle, home_only):
    """Latest record whose file name contains `needle`; 'home' records say 'home site' on their
    Where line, and old-platform records never count."""
    sel = [r for r in recs if needle in r["name"] and "old-platform" not in r["name"]
           and (r["home"] or not home_only)]
    if not sel:
        raise Fail("no run record matches a figure that needs one")
    return max(sel, key=lambda r: (r["date"], r["name"]))


def status_parse(text):
    """The aggregates of the platform repository's generated status page. The In short lines are
    matched with regexes, then cross-checked against the page's own tables; any change of shape fails."""
    def one(pattern, what):
        m = re.search(pattern, text)
        if not m:
            raise Fail(f"the status page no longer has the '{what}' line in the shape this parser expects")
        return [int(x) for x in m.groups()]

    st = one(r"\*\*Order of work:\*\* ([0-9]+) of ([0-9]+) steps are done, ([0-9]+) done on kind only, "
             r"([0-9]+) partly done, ([0-9]+) not started and ([0-9]+) gated", "order of work")
    ru = one(r"\*\*Rules:\*\* of ([0-9]+) rules on the objective pages, ([0-9]+) are built, "
             r"([0-9]+) partly built and ([0-9]+) not built", "rules")
    inv = one(r"\*\*Inventory:\*\* ([0-9]+) components\. ([0-9]+) are proven on the new platform, ([0-9]+) built,",
              "inventory")
    done, total, kind, partly, notstarted, gated = st[0], st[1], st[2], st[3], st[4], st[5]
    if done + kind + partly + notstarted + gated != total:
        raise Fail("status page: the step counts do not add up")
    if ru[1] + ru[2] + ru[3] != ru[0]:
        raise Fail("status page: the rule counts do not add up")
    section = text.split("## Order of work", 1)[-1].split("\n## ", 1)[0]
    rows = len(re.findall(r"^\| [0-9]+ \|", section, re.M))
    if rows != total:
        raise Fail("status page: the Order of work table does not have as many rows as the summary says")
    m = re.search(r"^\| Total \| ([0-9]+) \| ([0-9]+) \| ([0-9]+) \| ([0-9]+) \|$", text, re.M)
    if not m or [int(x) for x in m.groups()] != [ru[0], ru[1], ru[2], ru[3]]:
        raise Fail("status page: the Objectives table total disagrees with the summary line")
    m = re.search(r"^\| Total \| ([0-9]+) \| ([0-9]+) \| ([0-9]+) \|", text.split("## Inventory", 1)[-1], re.M)
    if not m or int(m.group(1)) != inv[0] or int(m.group(2)) != inv[1] or int(m.group(3)) != inv[2]:
        raise Fail("status page: the Inventory table total disagrees with the summary line")
    return {
        "steps_total": total, "steps_done": done, "steps_done_on_kind": kind, "steps_partly": partly,
        "steps_not_started": notstarted, "steps_gated": gated,
        "rules_total": ru[0], "rules_built": ru[1], "rules_partly": ru[2],
        "inventory_total": inv[0], "inventory_proven": inv[1], "inventory_built": inv[2],
    }


def measure_evidence(plat):
    recs = load_records(plat)
    drill = latest(recs, "restore-drill", True)
    probe = latest(recs, "default-deny-probe", True)
    rehearsal = latest(recs, "lima-rehearsal", False)
    out = {
        "restore_drill_home_last": drill["date"], "restore_drill_home_result": drill["result"],
        "restore_drill_home_age_days": max(0, (NOW.date() - dt.date.fromisoformat(drill["date"])).days),
        "restore_drills_records": sum(1 for r in recs if "restore" in r["name"]),
        "default_deny_probe_home_date": probe["date"], "default_deny_probe_home_result": probe["result"],
        "host_rehearsal_date": rehearsal["date"], "host_rehearsal_result": rehearsal["result"],
    }
    out.update(status_parse(plat.read("STATUS.md")))
    return out


# --------------------------------------------------------------------------------- repo
def pom_version(text):
    """The project's own <version>, which comes after the <parent> block (whose version is the
    framework's, not the application's)."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        raise Fail("the application's pom is not readable XML")
    for child in root:
        if child.tag.rsplit("}", 1)[-1] == "version" and child.text:
            return child.text.strip()
    raise Fail("no project-level version in the application's pom")


def measure_repo(plat, repo, ref):
    files = plat.files
    roots = [int(x) for x in git(repo, "log", "--max-parents=0", "--format=%at", ref).split()]
    cloc = json.loads(run(["cloc", "--git", ref, "--json", "--quiet"], cwd=repo, timeout=300))
    java = [f for f in files if re.search(r"/src/test/.*\.java$", f)]
    recs = load_records(plat)
    return {
        "commits": int(git(repo, "rev-list", "--count", ref)),
        "commits_30d": int(git(repo, "rev-list", "--count", "--since=30 days ago", ref)),
        "age_days": int((NOW.timestamp() - min(roots)) // 86400),
        "adrs": sum(1 for f in files if re.fullmatch(r"docs/adr/[0-9]{4}-.*\.md", f)),
        "records": len(recs),
        "records_pass": sum(1 for r in recs if r["result"] == "pass"),
        "records_fail": sum(1 for r in recs if r["result"] == "fail"),
        "check_scripts": sum(1 for f in files if re.fullmatch(r"scripts/check-[^/]+\.(py|sh)", f)),
        "playbooks": sum(1 for f in files if re.fullmatch(r"hosts/playbooks/[^/]+\.ya?ml", f)),
        "manifests": sum(1 for f in files if re.search(r"\.ya?ml$", f)
                         and re.match(r"(platform|sites|apps)/", f)
                         and re.search(r"^kind:", plat.read(f), re.M)),
        "runbooks": sum(1 for f in files if re.fullmatch(r"docs/runbooks/[^/]+\.md", f)
                        and not f.endswith("README.md")),
        "docs_pages": sum(1 for f in files if re.fullmatch(r"docs/.*\.md", f)),
        "loc": int(cloc["SUM"]["code"]),
        "loc_code": sum(int(v["code"]) for k, v in cloc.items() if k in CODE_LANGUAGES),
        "tests_java": count_in(plat, java, r"^\s*@(?:Test|ParameterizedTest|RepeatedTest)\b"),
        "app_warn_version": pom_version(plat.read("apps/warn/pom.xml")),
    }


def measure_hardware():
    need_dir(HARDWARE_REPOS, "HARDWARE_REPOS")
    out = {}
    for key, d in HARDWARE.items():
        repo = os.path.join(HARDWARE_REPOS, d)
        need_dir(repo, f"hardware repository '{key}'")
        ref = default_ref(repo)  # the default branch, whatever is checked out
        out[f"{key}_commits"] = int(git(repo, "rev-list", "--count", ref))
        if key in ("rover_platform", "mower", "video_rover"):
            with Snapshot(repo, ref) as snap:
                t = test_counts(snap)
            out[f"{key}_tests"] = t["py"] + t["go"]
            if key == "rover_platform":
                out["rover_platform_c_assertions"] = t["c"]
    return out


# ------------------------------------------------------------------------------- site
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


def github_slug():
    url = git(SITE, "remote", "get-url", "origin").strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    if not m:
        raise Fail("origin is not a GitHub remote")
    return m.group(1)


def github_headers():
    t = os.environ.get("GITHUB_TOKEN")
    return {"Authorization": f"Bearer {t}"} if t else {}





def measure_site():
    repo = http_json(f"https://api.github.com/repos/{github_slug()}", github_headers())
    runs = http_json(f"https://api.github.com/repos/{github_slug()}/actions/runs?per_page=100",
                     github_headers())["workflow_runs"]

    def latest_run(name):
        for r in runs:  # newest first
            if r["name"] == name and r.get("conclusion"):
                return r
        raise Fail("no finished workflow run found in the last 100")

    pages, guard = latest_run("pages build and deployment"), latest_run("Public docs guard")
    return {
        "commits": int(git(SITE, "rev-list", "--count", "HEAD")),
        "pages": sum(1 for f in os.listdir(os.path.join(SITE, "docs")) if f.endswith(".md")),
        "pages_last_build": pages["conclusion"], "pages_last_build_at": pages["updated_at"],
        "guard_last_run": guard["conclusion"],
        "last_push": repo["pushed_at"],
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


OTHER_DATA_GROUPS = frozenset(("history",))


def check_methods(stats_pairs=None, data_dir=DATA):
    problems = []
    for name in ("stats.yml", "stats_methods.yml"):
        # the generated file is checked as written; a candidate passed in has no duplicates by construction
        if stats_pairs is not None and name == "stats.yml":
            continue
        for d in yaml_scan(os.path.join(data_dir, name))[2]:
            problems.append(f"{name}: the key '{d}' appears more than once (the last one would silently win)")
    pairs = stats_pairs if stats_pairs is not None else yaml_keys(os.path.join(data_dir, "stats.yml"))[0]
    # Groups whose figures live in another data file are checked by that file's own generator
    # (history.yml: scripts/gather-history.py --verify), not against stats.yml.
    methods = {(g, k) for g, k in yaml_keys(os.path.join(data_dir, "stats_methods.yml"))[0] if g not in OTHER_DATA_GROUPS}
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
           "# Aggregates only: counts, dates, words. How each is measured: stats_methods.yml.",
           f'generated_at: "{generated_at}"']
    for g, keys in SCHEMA:
        out.append(f"{g}:")
        for k, kind in keys:
            v = stats[g][k]
            out.append(f'  {k}: "{v}"' if kind in KINDS else f"  {k}: {num(v, 1)}")
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
    c, a, d, o = stats["cluster"], stats["admission"], stats["databases"], stats["observability"]
    rc, e, r, ci = stats["reconciler"], stats["evidence"], stats["repo"], stats["ci"]
    rows = [
        ("Nodes (Ready)", f"{c['nodes']} ({c['nodes_ready']})"),
        ("CPU cores", num(c["cores"])),
        ("Memory", f"{num(c['ram_gb'], 0)} GB"),
        ("Pods running", num(c["pods_running"])),
        ("Kustomizations ready", f"{rc['kustomizations_ready']} of {rc['kustomizations']}"),
        ("Admission policies ready", f"{a['policies_ready']} of {a['policies']}"),
        ("Tenants with default-deny (structural count)", f"{a['tenants_default_deny']} of {a['tenant_namespaces']}"),
        ("Database instances ready", f"{d['instances_ready']} of {d['instances']}"),
        ("Backup objects completed in the last 24 hours", num(d["backups_24h"])),
        ("Latest restore drill on the home site", f"{e['restore_drill_home_last']}, {e['restore_drill_home_result']}"),
        ("Alert rules", o["alert_rules"]),
        ("Decision records", num(r["adrs"])),
        ("Run records (pass of total)", f"{r['records_pass']} of {r['records']}"),
        ("Test definitions (counted, not run)", num(r["tests_java"])),
        ("CI workflows", num(ci["workflows"])),
    ]
    lines = ["| Figure | Value |", "| --- | ---: |"] + [f"| {a_} | {b} |" for a_, b in rows]
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
        if not KUBECONFIG:
            raise Fail("KUBECONFIG is not set. There is no default, so a run cannot measure the wrong cluster: "
                       "run `make stats KUBECONFIG=...`")
        for tool in ("kubectl", "git", "cloc"):
            if shutil.which(tool) is None:
                raise Fail(f"{tool} is not installed")
        if not os.path.isfile(KUBECONFIG):
            raise Fail("KUBECONFIG does not point at a file")
        stats = {}
        stats["cluster"], ctx = measure_cluster()
        for group, fn in (("storage", measure_storage), ("reconciler", measure_reconciler),
                          ("admission", measure_admission), ("databases", measure_databases)):
            print(f"  measuring {group} ...", file=sys.stderr)
            stats[group] = fn()
        print("  reading the platform repository's main branch ...", file=sys.stderr)
        with PlatformSource() as src, Snapshot(src.repo, src.ref) as plat:
            print("  measuring observability ...", file=sys.stderr)
            stats["observability"] = measure_observability(plat, ctx)
            check_pending(ctx)
            print("  measuring evidence ...", file=sys.stderr)
            stats["evidence"] = measure_evidence(plat)
            print("  measuring ci ...", file=sys.stderr)
            stats["ci"] = measure_ci(plat)
            print("  measuring repo ...", file=sys.stderr)
            stats["repo"] = measure_repo(plat, src.repo, src.ref)
        for group, fn in (("hardware", measure_hardware), ("site", measure_site)):
            print(f"  measuring {group} ...", file=sys.stderr)
            stats[group] = fn()
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
