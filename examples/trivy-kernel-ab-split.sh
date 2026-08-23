#!/usr/bin/env sh
# Split a Trivy host-filesystem report into "the kernel you are booted on" and
# "the kernel you are keeping as a rollback".
#
# ---------------------------------------------------------------------------
# WHY THIS EXISTS
#
# Trivy reads the dpkg database, so `trivy rootfs /host` reports every INSTALLED
# kernel — including the previous one the distro deliberately keeps bootable as
# a rollback. Roughly six binary packages share one kernel source
# (image / headers / modules / modules-extra / tools / ...), and each carries the
# full CVE list of that source.
#
# The consequence is not cosmetic. It makes the raw count structurally unable to
# reach zero on a fully patched machine, forever. Measured here: a real
# 300-findings-to-0 improvement showed up as "600 findings, unchanged", because
# the CVEs moved from the booted kernel to the retained one and the total never
# moved. Watching the number, you would conclude nothing had happened.
#
# So: split by the kernel the machine is actually RUNNING and file the halves
# separately. `uname -r` inside a container returns the HOST's kernel — containers
# share it — so this needs no extra mount and no extra privilege.
#
# This is SCOPING, NOT SUPPRESSION. Boot the fallback kernel and its CVEs move
# into the booted half on the very next scan, because the split keys off uname at
# runtime rather than off a static list.
# ---------------------------------------------------------------------------
#
# Usage:
#   trivy rootfs --quiet --scanners vuln --pkg-types os --ignore-unfixed \
#         --format json --output /tmp/trivy.json /host
#   ./trivy-kernel-ab-split.sh /tmp/trivy.json /tmp/booted.json /tmp/fallback.json
#
# Requires: jq

set -eu

# ---------------------------------------------------------------------------
# `./trivy-kernel-ab-split.sh --self-test` proves the regex claim above rather
# than asking you to believe it. It is deliberately the first thing in the file
# you can run.
# ---------------------------------------------------------------------------
if [ "${1:-}" = "--self-test" ]; then
  BUGGY='^linux-[a-z-]*[0-9]+\.[0-9]+\.[0-9]+-[0-9]+'
  FIXED='^linux-.*[0-9]+\.[0-9]+\.[0-9]+-[0-9]+'
  HWE='linux-hwe-6.14-headers-6.14.0-35'

  b=$(printf '"%s"' "$HWE" | jq --arg re "$BUGGY" 'test($re)')
  f=$(printf '"%s"' "$HWE" | jq --arg re "$FIXED" 'test($re)')

  echo "package under test: $HWE"
  echo "  buggy pattern says versioned-kernel = $b   <- wrong: filed as BOOTED"
  echo "  fixed pattern says versioned-kernel = $f   <- correct: filed as FALLBACK"

  [ "$b" = "false" ] && [ "$f" = "true" ] || { echo "SELF-TEST FAILED"; exit 1; }
  echo "self-test passed"
  exit 0
fi

IN="${1:?usage: $0 <trivy.json> <booted-out.json> <fallback-out.json>  (or --self-test)}"
BOOTED_OUT="${2:?}"
FALLBACK_OUT="${3:?}"

# Strip the flavour suffix: 6.14.0-27-generic -> 6.14.0-27
KVER="$(uname -r)"
KVER="${KVER%-generic}"

# ---------------------------------------------------------------------------
# THE REGEX IS THE WHOLE TRICK, AND THE OBVIOUS VERSION IS WRONG.
#
# First attempt:   ^linux-[a-z-]*[0-9]+\.[0-9]+\.[0-9]+-[0-9]+
# It looks right and it fails on hardware-enablement kernels, which are named
# like:            linux-hwe-6.14-headers-6.14.0-35
#
# `[a-z-]*` eats "hwe-", the pattern then demands a full version and hits
# "6.14-headers" instead, and it cannot backtrack past it. Those packages fall
# through as NON-kernel and get filed against the booted kernel — so a
# superseded kernel's CVEs are reported as live exposure.
#
# The fix is to stop anchoring the version immediately after the prefix and let
# it appear anywhere after it.
#
# This shipped broken. It was caught only because the deploy log printed
# "booted: 578" while every previous measurement said running exposure was 0 —
# the contradiction was the tell, not any test.
# ---------------------------------------------------------------------------
# shellcheck disable=SC2016  # $b and $kv are jq variables, not shell ones —
# single quotes are required here, and expanding them would break the program.
SPLIT='
  def is_versioned_kernel:
    .PkgName | test("^linux-.*[0-9]+\\.[0-9]+\\.[0-9]+-[0-9]+");
  def keep($b): select((is_versioned_kernel | not) or (.PkgName | contains($b)));
  def drop($b): select(is_versioned_kernel and ((.PkgName | contains($b)) | not));
'

jq --arg kv "$KVER" "$SPLIT"'
  .Results = ((.Results // []) | map(.Vulnerabilities = ((.Vulnerabilities // []) | map(keep($kv)))))
' "$IN" > "$BOOTED_OUT"

jq --arg kv "$KVER" "$SPLIT"'
  .Results = ((.Results // []) | map(.Vulnerabilities = ((.Vulnerabilities // []) | map(drop($kv)))))
' "$IN" > "$FALLBACK_OUT"

cnt() { jq '[.Results[]?.Vulnerabilities[]?] | length' "$1" 2>/dev/null || echo 0; }

n="$(cnt "$IN")"
nb="$(cnt "$BOOTED_OUT")"
nf="$(cnt "$FALLBACK_OUT")"

echo "total: $n   booted ($KVER): $nb   retained fallback: $nf"

# A split that silently loses findings would look exactly like progress, which is
# the failure mode this whole script exists to prevent. So assert the halves sum.
if [ "$(( nb + nf ))" -ne "$n" ]; then
  echo "REFUSING: split does not sum ($nb + $nf != $n) — not filing a partial report" >&2
  exit 1
fi

# What to do with the two files: file them as separate targets in whatever
# tracker you use — e.g. "host:<node>" and "host:<node>:fallback".
#
#   booted   MUST be able to reach zero. Alert on it.
#   fallback is structural and never zero. Do not alert on it, do not delete the
#            kernel to make it go away — it is the documented rollback path.
