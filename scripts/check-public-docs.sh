#!/usr/bin/env bash
# Fails if anything published to GitHub Pages leaks private-estate detail.
#
# This repo is PUBLIC. The infrastructure it describes is not. The docs here are
# written from scratch rather than copied out of the private repo, precisely so
# there is nothing to scrub — this script asserts that stays true.
#
# Usage: scripts/check-public-docs.sh [path ...]   (default: docs/ README.md)
set -euo pipefail

TARGETS=("$@")
[ ${#TARGETS[@]} -eq 0 ] && TARGETS=(docs README.md)

fail=0
report() { # <label> <regex> <why>
  local label="$1" pattern="$2" why="$3" hits
  hits=$(grep -rInE "$pattern" "${TARGETS[@]}" 2>/dev/null || true)
  if [ -n "$hits" ]; then
    fail=1
    echo "FAIL: $label"
    echo "      $why"
    printf '%s\n' "$hits" | sed 's/^/      /'
    echo
  else
    printf 'ok:   %s\n' "$label"
  fi
}

# Tailnet names are publicly resolvable and the Funnel edge is a real public
# endpoint — this is the one that actually matters.
report "tailnet hostnames" \
  '\.ts\.net|tail[0-9a-f]{6,}' \
  "Tailscale names resolve publicly and point at a live edge."

report "credential paths" \
  '\.credentials/|cosign\.key|api-token|api-key|\.env\b' \
  "Names where secrets live are a map for anyone looking."

report "private LAN addresses" \
  '\b(192\.168|10\.(4[0-9]|[0-9])\.|172\.(1[6-9]|2[0-9]|3[01])\.)[0-9.]*' \
  "RFC1918 addressing describes the internal topology."

report "fleet hostnames" \
  '\b(delli7c[0-9a-z]*|imaci7g[0-9a-z]*|mbpi[57][0-9a-z]*|rpi[0-9]+[a-z0-9]*|MacStudioM2Max12|MacMiniM2Pro10)\b' \
  "Real machine names; use role descriptions instead."

report "CGNAT / WAN addresses" \
  '\b100\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\.[0-9]+\.[0-9]+' \
  "Carrier-grade NAT range — identifies the live WAN allocation."

if [ "$fail" -ne 0 ]; then
  echo "Public docs guard FAILED — the above would be published to a public site."
  exit 1
fi
echo
echo "Public docs guard passed for: ${TARGETS[*]}"
