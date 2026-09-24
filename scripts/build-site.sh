#!/usr/bin/env bash
# Build the Pages site locally with the SAME github-pages gem GitHub builds with,
# then assert what a reader must get. Catches a broken layout, Liquid or SCSS
# before it is pushed to a public site.
#
# Usage: scripts/build-site.sh      (or `make site`); output lands in _site/
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/_site"
# Pin to whatever GitHub runs today, so a local pass means the same thing there.
version="$(curl -fsS https://pages.github.com/versions.json |
  python3 -c 'import json,sys; print(json.load(sys.stdin)["github-pages"])')"

rm -rf "$out" && mkdir -p "$out"
docker run --rm \
  -v "$root/docs":/src:ro -v "$out":/out \
  -v schultzzznet-pages-gems:/usr/local/bundle \
  -e JEKYLL_ENV=production -e PAGES_REPO_NWO=schultzzznet/schultzzznet \
  ruby:3.3-slim sh -c "
    set -e
    gem list -i github-pages -v $version >/dev/null ||
      { apt-get update -qq && apt-get install -y -qq build-essential git >/dev/null &&
        gem install -N github-pages -v $version >/dev/null; }
    command -v git >/dev/null || { apt-get update -qq && apt-get install -y -qq git >/dev/null; }
    cp -R /src /tmp/src && git init -q /tmp/src
    github-pages build -s /tmp/src -d /out" >"$out.log" 2>&1 ||
  { cat "$out.log"; echo "FAIL: site build (github-pages $version)"; exit 1; }
echo "  ok    built with github-pages $version -> _site/"

fail=0
pages=0
for md in "$root"/docs/*.md; do
  name="$(basename "$md" .md)"
  html="$out/$name.html"
  pages=$((pages + 1))
  if [ ! -s "$html" ]; then echo "FAIL: $name.md produced no $name.html"; fail=1; continue; fi
  grep -q 'class="site-nav"' "$html" || { echo "FAIL: $name.html has no site nav"; fail=1; }
  current="$(grep -c 'aria-current="page"' "$html" || true)"
  [ "$current" = 1 ] || { echo "FAIL: $name.html marks $current nav entries as current (want 1)"; fail=1; }
done
grep -q '\.site-nav' "$out/assets/css/style.css" || { echo "FAIL: nav styles missing from the compiled CSS"; fail=1; }
grep -q '\.page-header' "$out/assets/css/style.css" || { echo "FAIL: theme styles missing from the compiled CSS"; fail=1; }

[ "$fail" = 0 ] || exit 1
echo "  ok    $pages pages: nav on each, exactly one current entry; theme + nav CSS compiled"
