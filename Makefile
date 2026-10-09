# schultzzznet - the profile README and the public Pages site (docs/).
#
#   make check   leak + nav + stats-freshness guard, and proof the guard can fail (what CI runs)
#   make stats   measure the live estate into docs/_data/stats.yml (needs the cluster and the
#                private repos; reads only), then run make check over the result
#   make site    build the site locally with GitHub's own gem, then assert on it
#
# make stats needs two paths to private checkouts, which no public file should hard-code:
#   PLATFORM_REPO   the platform repository   (default: $(HOME)/VisualStudioProjects/the-docker-swarm-ai)
#   HARDWARE_REPOS  the directory holding the hardware repositories
#                                             (default: $(HOME)/VisualStudioProjects)
# Override either on the command line or in the environment (make stats PLATFORM_REPO=...);
# scripts/gather-stats.py itself has no default and says so if it is run without them.
# KUBECONFIG defaults to ~/.kube/k3s-config. make stats writes nothing if any measurement fails,
# and refreshes the table between the stats markers in README.md if that file has them.

PLATFORM_REPO  ?= $(HOME)/VisualStudioProjects/the-docker-swarm-ai
HARDWARE_REPOS ?= $(HOME)/VisualStudioProjects
export PLATFORM_REPO HARDWARE_REPOS

.PHONY: help check stats site

help:
	@sed -n 's/^#   //p' $(MAKEFILE_LIST)

check:
	./scripts/check-public-docs.sh
	./scripts/test-guard.sh

stats:
	./scripts/gather-stats.py
	$(MAKE) check

site: check
	./scripts/build-site.sh
