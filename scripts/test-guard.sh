#!/usr/bin/env bash
# Prove check-public-docs.sh can FAIL. A guard that has never failed has never been
# shown to work. Each case plants a fault in a scratch copy; the real tree is never
# touched and no real leak is ever committed.
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

must_fail() { # <label>
  if (cd "$tmp/site" && "$guard" >/dev/null 2>&1); then
    echo "FAIL: the guard PASSED with a planted fault: $1"
    exit 1
  fi
  echo "  pass  guard refused: $1"
}

scratch
(cd "$tmp/site" && "$guard" >/dev/null) || { echo "FAIL: the guard rejects the unmodified tree"; exit 1; }
echo "  pass  guard accepts the real tree"

scratch
printf '%s\n' 'host somehost.tail0d1f2e.ts.net' > "$tmp/site/docs/planted.md"
must_fail "tailnet hostname"

scratch
printf '%s\n' 'the node at 192.168.1.241' > "$tmp/site/docs/planted.md"
must_fail "LAN address"

scratch
printf '%s\n' 'key lives in infra/.credentials/cosign.key' > "$tmp/site/docs/planted.md"
must_fail "credential path"

scratch
sed -i.bak '/printing\.html/d' "$tmp/site/docs/_data/nav.yml"
must_fail "page missing from the nav"
