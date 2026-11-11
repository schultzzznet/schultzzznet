# schultzzznet - the profile README and the public Pages site (docs/).
#
#   make check      leak + nav + stats-freshness guard, and proof the guard can fail (what CI runs)
#   make stats      measure the live estate into docs/_data/stats.yml (needs the cluster and the
#                   private repos; reads only), then run make check over the result
#   make stats-dry  the same measuring, checking and leak guard, printing the result and writing nothing
#   make site       build the site locally with GitHub's own gem, then assert on it
#
# make stats needs three things that no public file should hard-code:
#   KUBECONFIG      the cluster's kubeconfig. REQUIRED, no default, so a run can never measure the
#                   wrong cluster:  make stats KUBECONFIG=...
#   PLATFORM_REPO   a checkout of the private platform repository. REQUIRED, no default:
#                                             make stats PLATFORM_REPO=...
#   HARDWARE_REPOS  the directory holding the hardware repositories
#                                             (default: $(HOME)/VisualStudioProjects)
# Override any of them on the command line or in the environment (make stats PLATFORM_REPO=...);
# scripts/gather-stats.py itself has no default and says so if it is run without them.
# The platform repository is measured from a fresh bare clone of its remote main branch (offline:
# PLATFORM_REF=origin/main, fetched within 24 hours), the hardware repositories from their default
# branch. The cluster is only ever read: the generator allows get, get --raw on the metrics API,
# version and top, and refuses everything else before it starts a process.
# make stats writes nothing if any measurement fails, and refreshes the table between the stats
# markers in README.md if that file has them.

PLATFORM_REPO  ?=
HARDWARE_REPOS ?= $(HOME)/VisualStudioProjects
export PLATFORM_REPO HARDWARE_REPOS

.PHONY: help check stats stats-dry site need-kubeconfig

help:
	@sed -n 's/^#   //p' $(MAKEFILE_LIST)

check:
	./scripts/check-public-docs.sh
	./scripts/test-guard.sh

need-kubeconfig:
	@test -n "$(KUBECONFIG)" || { echo "KUBECONFIG is required: make stats KUBECONFIG=..." >&2; exit 2; }
	@test -n "$(PLATFORM_REPO)" || { echo "PLATFORM_REPO is required: make stats PLATFORM_REPO=..." >&2; exit 2; }

stats: need-kubeconfig
	KUBECONFIG="$(KUBECONFIG)" ./scripts/gather-stats.py
	$(MAKE) check

stats-dry: need-kubeconfig
	KUBECONFIG="$(KUBECONFIG)" ./scripts/gather-stats.py --dry-run

site: check
	./scripts/build-site.sh
