#!/usr/bin/env bash
# Prove check-public-docs.sh can FAIL. A guard that has never failed has never been
# shown to work. Each case plants a fault in a scratch copy; the real tree is never
# touched and no real leak is ever committed.
#
# Each refusal must also be for the RIGHT reason: a case names the rule it expects to
# fire, so a fault cannot hide behind some other check failing at the same time.
#
# Usage: scripts/test-guard.sh     (run by CI and by `make check`)
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
guard="$root/scripts/check-public-docs.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

scratch() { # a fresh copy of the publishable tree
  rm -rf "$tmp/site" && mkdir -p "$tmp/site"
  cp -R "$root/docs" "$root/examples" "$root/README.md" "$root/SECURITY.md" "$root/scripts" "$tmp/site/"
}

plant() { # <text>   appended to an existing, already-listed page, so only the content is wrong
  printf '%s\n' "$1" >> "$tmp/site/docs/lessons.md"
}

last_out=""
must_fail() { # <label> <rule that must be the one to fire>   (the output is kept in last_out for further checks)
  local out
  if out=$(cd "$tmp/site" && "$guard" 2>&1); then
    echo "FAIL: the guard PASSED with a planted fault: $1"
    exit 1
  fi
  last_out="$out"
  if [[ "$out" != *"FAIL: $2"* ]]; then
    echo "FAIL: the guard refused '$1' but not by the rule '$2':"
    printf '%s\n' "$out"
    exit 1
  fi
  echo "  pass  guard refused: $1"
}

must_pass() { # <label>   a fault-shaped input that is NOT a fault must not trip the guard
  if ! (cd "$tmp/site" && "$guard" >/dev/null 2>&1); then
    echo "FAIL: the guard REFUSED something it should allow: $1"
    exit 1
  fi
  echo "  pass  guard allowed: $1"
}

scratch
(cd "$tmp/site" && "$guard" >/dev/null) || { echo "FAIL: the guard rejects the unmodified tree"; exit 1; }
echo "  pass  guard accepts the real tree"

scratch
plant 'host somehost.tail0d1f2e.ts.net'
must_fail "tailnet hostname" "tailnet hostnames"

scratch
plant 'the node at 192.168.1.241'
must_fail "LAN address" "private LAN addresses"

scratch
plant 'runs k3s v1.35.9 on six nodes'
must_fail "k3s version" "infrastructure software versions"

scratch
plant 'the release tag v1.35.9+k3s1'
must_fail "k3s release tag" "infrastructure software versions"

scratch
plant 'identity is Keycloak 26.1.4 behind Traefik 3.2'
must_fail "Keycloak and Traefik versions" "infrastructure software versions"

scratch
plant 'the databases run PostgreSQL 18 and the cluster has Ceph replica-3'
must_pass "major versions and non-version numbers"

scratch
plant 'GitOps by Flux 2.4.1 with Kyverno 1.12 and cert-manager 1.15'
must_fail "Flux, Kyverno and cert-manager versions" "infrastructure software versions"

scratch
plant 'the host layer is rehearsed on Lima 1.0.2 and secrets use SOPS 3.9'
must_fail "Lima and SOPS versions" "infrastructure software versions"

scratch
plant 'Cilium 1.16, Postgres 16.4, Docker 27.3, Podman 5.2, RAUC 1.12'
must_fail "network, database and container software versions" "infrastructure software versions"

scratch
plant 'we use Flux, Kyverno and Lima, and the data is 3 years old, at age 12'
must_pass "tool names with no version, and ordinary numbers"

scratch
plant 'see the Schultz Cluster repo'
must_fail "platform repo name with a space" "private platform repo name in published files"

scratch
plant 'see schultz-cluster and SchultzCluster'
must_fail "platform repo name hyphenated and without the article" "private platform repo name in published files"

scratch
plant 'a cluster of six nodes, Schultz said'
must_pass "the word cluster alone, and a surname"

scratch
plant 'key lives in infra/.credentials/cosign.key'
must_fail "credential path" "credential paths"

scratch
printf '%s\n' 'also reachable at somehost.tail0d1f2e.ts.net' >> "$tmp/site/SECURITY.md"
must_fail "tailnet hostname in SECURITY.md (it is published, so it is guarded)" "tailnet hostnames"

scratch
sed -i.bak '/printing\.html/d' "$tmp/site/docs/_data/nav.yml"
must_fail "page missing from the nav" "docs/printing.md is not in docs/_data/nav.yml"

# --- the fast reader's block: on every page, and not allowed to go stale ---
# Each case damages one page's front matter (or the landing page's "Recently" list) in the scratch copy and must be
# refused BY the summary rule, so a fault cannot hide behind another check failing at the same time. A case may also name
# the message the refusal must carry, and a fault that changes nothing stops the suite: a vacuous case proves nothing.
summary_fault() { # <label> <file under docs/> <python that edits the text held in t, using re and dt> [message the refusal must carry]
  scratch
  (cd "$tmp/site" && python3 - "docs/$2" "$3" <<'PY'
import datetime as dt, re, sys
path, code = sys.argv[1], sys.argv[2]
t = open(path).read()
env = {"t": t, "re": re, "dt": dt}
exec(code, env)
if env["t"] == t:
    sys.exit("test-guard: the planted fault changed nothing in " + path + ": " + code)
open(path, "w").write(env["t"])
PY
  )
  must_fail "$1" "every page has a fresh In short block"
  if [ -n "${4:-}" ] && [[ "$last_out" != *"$4"* ]]; then
    echo "FAIL: '$1' was refused, but the summary check did not say: $4"
    printf '%s\n' "$last_out"
    exit 1
  fi
}
summary_fault "a page with no summary" lessons.md \
  't = re.sub(r"summary:\n(?:  - .*\n)+", "", t, count=1)' "must be a list of"
summary_fault "a page that does not include the block" lessons.md \
  't = t.replace("{% include in-short.html %}", "")' "does not include the block"
summary_fault "a summary reread date long past" lessons.md \
  't = re.sub(r"^reread: .*$", "reread: 2020-01-01", t, count=1, flags=re.M)' "days old"
summary_fault "a summary reread date in the future" lessons.md \
  't = re.sub(r"^reread: .*$", "reread: 2099-01-01", t, count=1, flags=re.M)' "in the future"
summary_fault "a body_read date older than the limit" choices.md \
  't = re.sub(r"^body_read: .*$", "body_read: 2020-01-01", t, count=1, flags=re.M)' "body_read 2020-01-01 is"
# body_read later than reread: reread moves to the day BEFORE body_read, so the case holds whatever dates the page carries.
summary_fault "a body_read date later than the summary's" choices.md \
  'b = re.search(r"^body_read: (\S+)$", t, re.M).group(1); r = (dt.date.fromisoformat(b) - dt.timedelta(days=1)).isoformat(); t = re.sub(r"^reread: .*$", "reread: " + r, t, count=1, flags=re.M)' \
  "is later than reread"
summary_fault "a summary of seven items" lessons.md \
  't = t.replace("summary:\n", "summary:\n" + "  - \"padding\"\n" * 4, 1)' "must be a list of"
summary_fault "a summary item that is a wall of text" lessons.md \
  't = t.replace("summary:\n", "summary:\n  - \"" + "word " * 120 + "\"\n", 1)' "a summary is short"
summary_fault "Liquid in a summary" lessons.md \
  't = t.replace("summary:\n", "summary:\n  - \"{{ site.data.stats.cluster.nodes }} nodes\"\n", 1)' "contains Liquid"
summary_fault "a Liquid tag in a summary" lessons.md \
  't = t.replace("summary:\n", "summary:\n  - \"{% if true %}x{% endif %}\"\n", 1)' "contains Liquid"
summary_fault "a Recently list gone stale" _data/recently.yml \
  't = re.sub(r"date: \d{4}-\d{2}-\d{2}", "date: 2020-01-01", t)' "stopped being recent"
# Out of order: the SECOND date line is made one day newer than the first, whatever dates the list carries. A list with
# fewer than two entries, or an edit that changes nothing, stops the suite instead of passing vacuously.
summary_fault "a Recently list out of order" _data/recently.yml \
  'ds = list(re.finditer(r"^- date: (\S+)$", t, re.M)); assert len(ds) >= 2, "recently.yml has fewer than two entries"; bump = (dt.date.fromisoformat(ds[0].group(1)) + dt.timedelta(days=1)).isoformat(); t = t[:ds[1].start(1)] + bump + t[ds[1].end(1):]' \
  "newest first"
# The cap of 12 entries is enforced in check-summaries.py: the first entry is copied in front of the list until there are 13.
summary_fault "a Recently list of thirteen entries" _data/recently.yml \
  'blocks = re.split(r"(?m)^(?=- date:)", t); head, entries = blocks[0], blocks[1:]; t = head + entries[0] * max(1, 13 - len(entries)) + "".join(entries)' \
  "expected 3 to 12 entries"
summary_fault "a Recently entry with a malformed date" _data/recently.yml \
  't = re.sub(r"^- date: \S+$", "- date: 2026-13-45", t, count=1, flags=re.M)' "bad date"
echo "  pass  the In short check refused every planted fault"

# --- the machine-generated stats page: freshness, completeness, and the newer leak shapes ---

scratch
sed -i.bak 's/^generated_at: .*/generated_at: "2020-01-01T00:00:00Z"/' "$tmp/site/docs/_data/stats.yml"
must_fail "stale stats (generated years ago)" "stats are fresh"

scratch
sed -i.bak '/^generated_at:/d' "$tmp/site/docs/_data/stats.yml"
must_fail "stats with no generated_at" "stats are fresh"

scratch
rm "$tmp/site/docs/_data/stats.yml"
must_fail "stats missing altogether" "stats are fresh"

scratch
plant 'the registry is at somebox.local'
must_fail "mDNS .local name" "mDNS (.local) names"

scratch
plant 'dns is a.svc.cluster.local but the registry is somebox.local'
must_fail ".local host beside an allowed cluster.local on one line" "mDNS (.local) names"

scratch
plant 'dns is only a.svc.cluster.local'
must_pass "in-cluster DNS (svc.cluster.local) on its own"

scratch
plant 'adapter 3c:22:fb:9a:01:7e'
must_fail "MAC address" "MAC addresses"

scratch
plant 'pull registry.example.net:5000/app:1'
must_fail "registry host:port" "registry host:port"

scratch
plant 'tickets at https://example.atlassian.net/browse/X-1'
must_fail "issue-tracker site" "issue-tracker sites"

scratch
printf '%s\n' 'repo: theMowerRetrofit' > "$tmp/site/docs/_data/planted.yml"
must_fail "private repo name in generated data" "private repo names in generated data"

scratch
plant 'See theMowerRetrofit for the mower.'
must_pass "a private repo name in prose (named there on purpose)"

scratch
sed -i.bak '/^  nodes_ready:/d' "$tmp/site/docs/_data/stats_methods.yml"
must_fail "a stat with no method" "every stat has a published method"

scratch
sed -i.bak '/^  nodes_ready:/d' "$tmp/site/docs/_data/stats.yml"
must_fail "a method with no stat" "every stat has a published method"

# --- freshness must not fail OPEN: a future timestamp never ages out, so it is refused ---

scratch
sed -i.bak 's/^generated_at: .*/generated_at: "2030-01-01T00:00:00Z"/' "$tmp/site/docs/_data/stats.yml"
must_fail "stats dated in the future (2030)" "stats are fresh"

scratch
future=$(python3 -c 'import datetime as d; print((d.datetime.now(d.timezone.utc)+d.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ"))')
sed -i.bak "s/^generated_at: .*/generated_at: \"$future\"/" "$tmp/site/docs/_data/stats.yml"
must_fail "stats dated three hours ahead (beyond the clock-skew allowance)" "stats are fresh"

scratch
near=$(python3 -c 'import datetime as d; print((d.datetime.now(d.timezone.utc)+d.timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"))')
sed -i.bak "s/^generated_at: .*/generated_at: \"$near\"/" "$tmp/site/docs/_data/stats.yml"
must_pass "stats dated 30 minutes ahead (ordinary clock skew)"

# --- duplicate keys: a YAML loader keeps the last one silently ---

dup_line() { # <file> <line-prefix>   repeat the first line starting with the prefix (sed's \n is not portable)
  python3 - "$1" "$2" <<'PY'
import sys
path, prefix = sys.argv[1], sys.argv[2]
lines = open(path).read().split("\n")
i = next(n for n, l in enumerate(lines) if l.startswith(prefix))
lines.insert(i, lines[i])
open(path, "w").write("\n".join(lines))
PY
}

scratch
dup_line "$tmp/site/docs/_data/stats.yml" "  nodes_ready:"
must_fail "a figure repeated in stats.yml" "every stat has a published method"

scratch
dup_line "$tmp/site/docs/_data/stats.yml" "generated_at:"
must_fail "a doubled generated_at" "stats are fresh"

scratch
dup_line "$tmp/site/docs/_data/stats_methods.yml" "  nodes_ready:"
must_fail "a method repeated in stats_methods.yml" "every stat has a published method"

# --- every rule is case-insensitive ---

scratch
plant 'the registry is at SOMEBOX.LOCAL'
must_fail "uppercase .LOCAL name" "mDNS (.local) names"

scratch
plant 'host somehost.TAIL0D1F2E.TS.NET'
must_fail "uppercase TS.NET" "tailnet hostnames"

scratch
plant 'tickets at https://example.ATLASSIAN.NET/browse/X-1'
must_fail "uppercase ATLASSIAN.NET" "issue-tracker sites"

scratch
plant 'the node DELLI7C1 is the primary'
must_fail "uppercase fleet hostname" "fleet hostnames"

scratch
plant 'dns is A.SVC.CLUSTER.LOCAL but also SOMEBOX.LOCAL'
must_fail "uppercase .LOCAL beside an uppercase allowed suffix" "mDNS (.local) names"

scratch
plant 'dns is only A.SVC.CLUSTER.LOCAL'
must_pass "uppercase in-cluster DNS on its own"

# --- registry host:port: any dotted host with a 4-5 digit port, and a bare IP:port ---

scratch
plant 'pull reg.example.com:30500/app:1'
must_fail "registry on port 30500" "registry host:port"

scratch
plant 'pull reg.example.com:8443/app:1'
must_fail "registry on port 8443" "registry host:port"

scratch
plant 'pull reg.example.com:6000/app:1'
must_fail "registry on port 6000" "registry host:port"

scratch
plant 'pull 8.8.8.8:5000/app:1'
must_fail "bare IP with a port" "registry host:port"

scratch
plant 'see https://example.com/path and prometheus.monitoring.svc.cluster.local:9090/x'
must_pass "a public URL with no port, and in-cluster DNS with its port"

scratch
plant 'prometheus.monitoring.svc.cluster.local:9090 but reg.example.com:5000'
must_fail "an allowed in-cluster port beside a real registry port" "registry host:port"

# --- shapes added later: digests, tokens, IPv6, other MAC spellings, the whole of 10/8 ---

scratch
plant "image app@sha256:$(printf 'ab12%.0s' {1..16})"
must_fail "image digest" "image digests"

scratch
plant "key $(printf 'AKIA')$(printf 'ABCDEFGHIJKLMNOP')"
must_fail "AWS-style access key id" "token shapes"

scratch
plant "token $(printf 'gh')$(printf 'p_')$(printf 'a1B2%.0s' {1..9})"
must_fail "GitHub-style token" "token shapes"

scratch
plant 'tailnet address fd7a:115c:a1e0::1'
must_fail "Tailscale ULA IPv6 address" "IPv6 addresses"

scratch
plant 'address 2001:db8:0:0:0:0:0:1'
must_fail "full IPv6 address" "IPv6 addresses"

scratch
plant 'link-local fe80::1'
must_fail "link-local IPv6 address" "IPv6 addresses"

scratch
plant 'adapter 3C:22:FB:9A:01:7E'
must_fail "uppercase MAC address" "MAC addresses"

scratch
plant 'adapter 3c22fb9a017e'
must_fail "colon-less MAC address" "MAC addresses"

scratch
plant 'adapter 3c22.fb9a.017e'
must_fail "dotted MAC address" "MAC addresses"

scratch
plant 'a total of 214748364800 bytes, and <img src="x.gif?v=2dcefa0da38a">'
must_pass "a 12-digit count and an image cache-buster hash"

scratch
plant 'the node at 10.200.3.4'
must_fail "10.x address outside 10.0-10.9 and 10.40-10.49" "private LAN addresses"

scratch
plant 'the node at 10.123.0.1'
must_fail "10.123 address" "private LAN addresses"

# --- the stats schema changes: values of an accepted kind, and no page may name a key that is gone ---
# The key every case below edits is cluster.nodes_ready; it must stay in stats.yml, stats_methods.yml and the README table.
set_nodes_ready() { # <raw YAML value>   rewrites the value of cluster.nodes_ready in the scratch stats.yml
  python3 - "$tmp/site/docs/_data/stats.yml" "$1" <<'PY'
import re, sys
path, val = sys.argv[1], sys.argv[2]
t = open(path).read()
new, n = re.subn(r"(?m)^  nodes_ready:.*$", "  nodes_ready: " + val, t, count=1)
if n != 1:
    sys.exit("test-guard: cluster.nodes_ready is not in stats.yml: the cases that edit it need it")
open(path, "w").write(new)
PY
}
values_rule="stats values are of an accepted kind"
refs_rule="no page references a stats key that does not exist"

scratch
set_nodes_ready '"about six"'
must_fail "a stats value that is text where a number is expected" "$values_rule"
[[ "$last_out" == *"string where a number"* ]] || { echo "FAIL: the refusal did not name the text value"; printf '%s\n' "$last_out"; exit 1; }

scratch
python3 - "$tmp/site/docs/_data/stats.yml" <<'PY'
import re, sys
p = sys.argv[1]
t = open(p).read()
new, n = re.subn(r"(?m)^  alert_rules:.*$", "  alert_rules: 42", t, count=1)
if n != 1:
    sys.exit("test-guard: observability.alert_rules is not in stats.yml")
open(p, "w").write(new)
PY
must_fail "a number in a monitoring figure while monitoring is not live" "$values_rule"

scratch
set_nodes_ready '"6"'
must_fail "a number written as a quoted string" "$values_rule"

scratch
set_nodes_ready '-3'
must_fail "a negative stats value" "$values_rule"

scratch
set_nodes_ready '"2026-13-45"'
must_fail "a malformed date in stats.yml (month 13)" "$values_rule"

scratch
set_nodes_ready '"2026-1-5"'
must_fail "a malformed date in stats.yml (not zero padded)" "$values_rule"

scratch
set_nodes_ready '2026-11-10'
must_fail "an unquoted date in stats.yml" "$values_rule"

scratch
set_nodes_ready '"not measured yet"'
must_pass "a stat whose value is the exact string 'not measured yet'"

scratch
set_nodes_ready '"2026-11-10"'
must_pass "a stat whose value is a quoted real date"

scratch
set_nodes_ready '"Not Measured Yet"'
must_fail "'not measured yet' in another spelling (the string is exact)" "$values_rule"

# A missing key renders as empty text in Jekyll and the build stays green; check-stats-refs.py is what turns it red.
scratch
plant 'The cluster has {{ site.data.stats.cluster.no_such_key }} nodes.'
must_fail "a Liquid reference to a key that is not in stats.yml" "$refs_rule"
[[ "$last_out" == *"docs/lessons.md:"* ]] || { echo "FAIL: the refusal did not carry file:line"; printf '%s\n' "$last_out"; exit 1; }

scratch
plant '{% assign zz = site.data.stats.cluster %}Nodes: {{ zz.no_such_key }}'
must_fail "a reference to a missing key through an alias" "$refs_rule"

scratch
plant '{% assign top = site.data.stats %}{% assign grp = top.cluster %}{% assign n = grp.no_such_key | plus: 1 %}'
must_fail "a reference to a missing key through a chain of aliases" "$refs_rule"

scratch
plant '{{ site.data.stats.no_such_group.nodes }}'
must_fail "a reference to a group that is not in stats.yml" "$refs_rule"

scratch
printf '%s\n' '{{ site.data.stats.cluster.no_such_key }}' >> "$tmp/site/README.md"
must_fail "a reference to a missing key in the README" "$refs_rule"

scratch
sed -i.bak '/^  nodes_ready:/d' "$tmp/site/docs/_data/stats.yml"
plant '{{ site.data.stats.cluster.nodes_ready }} nodes are Ready'
must_fail "a page naming a key that was deleted from stats.yml" "$refs_rule"

scratch
plant '{% assign zz = site.data.stats.cluster %}{{ zz.nodes_ready }} Ready, {{ page.title }}, {% raw %}{{ site.data.stats.cluster.gone }}{% endraw %}'
must_pass "references to existing keys, unrelated Liquid, and a key shown inside a raw block"

echo "  ...  the reference checker's own self-test"
(cd "$tmp/site" && python3 scripts/check-stats-refs.py --self-test >/dev/null) || {
  echo "FAIL: check-stats-refs.py --self-test failed"; (cd "$tmp/site" && python3 scripts/check-stats-refs.py --self-test); exit 1; }
echo "  pass  check-stats-refs.py proves it can fail"

# --- machine-name shapes found later, and the current private repository's name ---
# The repository name is assembled here so this public script does not spell it out either.
new_repo="the""Schultz""Cluster"

scratch
plant 'the runner is theubuntuone'
must_fail "a home CI host name (theubuntu shape)" "fleet hostnames"

scratch
plant 'the standby is TheUbuntuTwo'
must_fail "a home CI host name in capitals" "fleet hostnames"

scratch
plant 'the standby is thedebian3'
must_fail "a home CI host name (thedebian shape)" "fleet hostnames"

scratch
plant 'rehearsed on k3s-rehearsal-1'
must_fail "a rehearsal VM name (k3s-rehearsal shape)" "fleet hostnames"

scratch
plant 'the Ubuntu hosts and the Debian host rehearse K3s in a VM'
must_pass "role words that only resemble the machine-name shapes"

scratch
printf 'repo: %s\n' "$new_repo" > "$tmp/site/docs/_data/planted.yml"
must_fail "the new private repo name in generated data" "private repo names in generated data"

scratch
plant "See $new_repo for the platform."
must_fail "the new private repo name in a page" "private platform repo name in published files"

scratch
plant "image path registry-example/$(printf '%s' "$new_repo" | tr '[:upper:]' '[:lower:]')/app"
must_fail "the new private repo name in lower case in an image path" "private platform repo name in published files"

scratch
printf '%s\n' "See $new_repo." >> "$tmp/site/README.md"
must_fail "the new private repo name in the README" "private platform repo name in published files"

scratch
plant 'See theMowerRetrofit and the-docker-swarm-ai for the history.'
must_pass "V1.0's repository named in prose, as history"

# --- the README stats block: replaced between the markers, left alone without them ---

stats_py="python3 scripts/gather-stats.py"
scratch
printf '%s\n' '# Title' 'intro text' '<!-- stats:begin -->' 'OLD TABLE' '<!-- stats:end -->' 'outro text' > "$tmp/site/README.md"
(cd "$tmp/site" && $stats_py --readme-from-stats docs/_data/stats.yml --readme README.md >/dev/null) ||
  { echo "FAIL: the generator could not write the README block"; exit 1; }
if grep -q 'OLD TABLE' "$tmp/site/README.md" || ! grep -q '^| Nodes (Ready) |' "$tmp/site/README.md" ||
   ! grep -q '^intro text$' "$tmp/site/README.md" || ! grep -q '^outro text$' "$tmp/site/README.md" ||
   ! grep -q '^\*Measured 20' "$tmp/site/README.md"; then
  echo "FAIL: the README block was not spliced between the markers"; cat "$tmp/site/README.md"; exit 1
fi
(cd "$tmp/site" && ./scripts/check-public-docs.sh >/dev/null) || { echo "FAIL: the guard refuses a README with a generated block"; exit 1; }
echo "  pass  generator replaced the README block and left the rest alone"

scratch
printf '%s\n' '# Title' 'no markers here' > "$tmp/site/README.md"
cp "$tmp/site/README.md" "$tmp/readme.before"
(cd "$tmp/site" && $stats_py --readme-from-stats docs/_data/stats.yml --readme README.md >/dev/null) ||
  { echo "FAIL: the generator failed on a README without markers"; exit 1; }
cmp -s "$tmp/readme.before" "$tmp/site/README.md" || { echo "FAIL: the generator changed a README without markers"; exit 1; }
echo "  pass  generator left a README without markers untouched"

scratch
printf '%s\n' '# Title' '<!-- stats:begin -->' 'only a begin marker' > "$tmp/site/README.md"
if (cd "$tmp/site" && $stats_py --readme-from-stats docs/_data/stats.yml --readme README.md >/dev/null 2>&1); then
  echo "FAIL: the generator accepted a README with only one marker"; exit 1
fi
echo "  pass  generator refused a README with a lone marker"

# --- the generator: no hard-coded checkout paths, and tool errors printed without URLs or hosts ---

if out=$(cd "$tmp/site" && env -u PLATFORM_REPO -u HARDWARE_REPOS python3 scripts/gather-stats.py --dry-run 2>&1); then
  echo "FAIL: the generator ran with PLATFORM_REPO unset"; exit 1
fi
if [[ "$out" != *"PLATFORM_REPO is not set"* ]]; then
  echo "FAIL: the generator did not say PLATFORM_REPO is missing:"; printf '%s\n' "$out"; exit 1
fi
echo "  pass  generator says so when PLATFORM_REPO is unset"

if grep -nE '/Users/|/home/[a-z]' "$root/scripts/gather-stats.py" "$root/Makefile" >/dev/null; then
  echo "FAIL: a user's home directory is hard-coded in a public file"; exit 1
fi
echo "  pass  no home directory is hard-coded in the generator or the Makefile"

scrubbed=$(cd "$tmp/site" && python3 - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location("g", "scripts/gather-stats.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
print(g.scrub("dial tcp 192.168.1.5:6443: i/o timeout GET https://api.example.ts.net:6443/x node delli7c1.local /Users/me/.kube/config"))
PY
)
for leaked in 192.168 https:// ts.net delli7c1 /Users/; do
  if [[ "$scrubbed" == *"$leaked"* ]]; then echo "FAIL: scrub() left '$leaked' in: $scrubbed"; exit 1; fi
done
echo "  pass  error text is scrubbed of URLs, addresses, hosts and paths"

# The generator vets its own output with the same guard before writing; show that it refuses.
scratch
(cd "$tmp/site" && python3 scripts/gather-stats.py --vet docs/_data/stats.yml >/dev/null) ||
  { echo "FAIL: the generator's own check rejects the real stats"; exit 1; }
echo "  pass  generator accepts the real stats"
printf '%s\n' 'k3s: "registry.local"' > "$tmp/site/planted-stats.yml"
if out=$(cd "$tmp/site" && python3 scripts/gather-stats.py --vet planted-stats.yml 2>&1); then
  echo "FAIL: the generator's own check PASSED a file naming a .local host"
  exit 1
fi
if [[ "$out" != *"mDNS (.local) names"* ]]; then
  echo "FAIL: the generator refused the .local name, but not by the mDNS rule:"
  printf '%s\n' "$out"
  exit 1
fi
echo "  pass  generator refused: a .local name in its own output"
