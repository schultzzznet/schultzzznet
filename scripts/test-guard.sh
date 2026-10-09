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
  cp -R "$root/docs" "$root/examples" "$root/README.md" "$root/scripts" "$tmp/site/"
}

plant() { # <text>   appended to an existing, already-listed page, so only the content is wrong
  printf '%s\n' "$1" >> "$tmp/site/docs/lessons.md"
}

must_fail() { # <label> <rule that must be the one to fire>
  local out
  if out=$(cd "$tmp/site" && "$guard" 2>&1); then
    echo "FAIL: the guard PASSED with a planted fault: $1"
    exit 1
  fi
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
plant 'key lives in infra/.credentials/cosign.key'
must_fail "credential path" "credential paths"

scratch
sed -i.bak '/printing\.html/d' "$tmp/site/docs/_data/nav.yml"
must_fail "page missing from the nav" "docs/printing.md is not in docs/_data/nav.yml"

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
