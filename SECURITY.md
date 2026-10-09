# Security policy

## What this covers

This repository is a **public write-up** of a private homelab platform: the site in `docs/`, the
profile `README.md`, a few scrubbed artifacts in `examples/`, and the scripts that build and check
the site (`scripts/`). That is the whole scope.

**The platform the site describes is private and is not offered for testing.** Please do not probe,
scan or attempt to access any infrastructure it describes, whatever you infer about it from the
pages. Reports based on such testing will not be treated as good-faith research.

## What I most want to hear about

1. **Something published here that should not be.** A hostname, address, credential path, key,
   token, internal name or anything else that identifies or opens the private estate. A leak guard
   (`scripts/check-public-docs.sh`) is meant to make this impossible, so a hit means the guard has a
   gap, and that is worth knowing about as much as the leak.
2. **A vulnerability in the scripts or examples**, for instance in `scripts/` or in the shell and
   YAML under `examples/`, that could harm someone who runs them.
3. **A claim on the site that is wrong in a way that could mislead a reader about security.** The
   site's purpose is to check its own claims, so a correction is welcome here too.

## How to report

- **Preferred:** GitHub's private vulnerability reporting. On the repository, open the *Security*
  tab and choose *Report a vulnerability*.
- **Fallback, or if that option is not shown:** email **github@schultzzz.net** with *security* in
  the subject.

Please include what you found and where, what an attacker could do with it, and how to reproduce it.
A fix suggestion is welcome but not required. Please do not open a public issue with the details.

## What to expect

This is a personal project, not a company with a security team or an SLA. There is no bug bounty.
I aim to acknowledge a report within about a week, to fix a real leak as fast as I can (removing it
from the site first, then from history if it matters), and to say so publicly when something the
site claimed was wrong. I will credit you if you want that.

## Supported versions

Only the current `main` branch, which is what the published site is built from.
