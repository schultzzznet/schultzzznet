# schultzzznet - the profile README and the public Pages site (docs/).
#
#   make check   leak + nav guard, and proof the guard can fail (what CI runs)
#   make site    build the site locally with GitHub's own gem, then assert on it

.PHONY: help check site

help:
	@sed -n 's/^#   //p' $(MAKEFILE_LIST)

check:
	./scripts/check-public-docs.sh
	./scripts/test-guard.sh

site: check
	./scripts/build-site.sh
