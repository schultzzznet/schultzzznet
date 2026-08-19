---
title: Legal, licensing, and the regulatory posture nobody publishes for a home project
---

# CRA, GDPR, app-store rules, and what a licence actually obligates

![cra](https://img.shields.io/badge/EU%20CRA-~70%25%20of%20substance%20in%20place-2088FF)
![gdpr](https://img.shields.io/badge/GDPR%20erasure-shipped%2C%20verified%20live-2EA44F)
![privacy](https://img.shields.io/badge/App%20Store%20privacy%20labels-false%20claim%20found%20%2B%20removed-orange)
![licence](https://img.shields.io/badge/own%20code-MIT-blue)
![agpl](https://img.shields.io/badge/AGPL%20dependencies-scoped%2C%20not%20triggered-005571)

Most write-ups of a home-built platform stop at the architecture diagram. This one also asks
the less flattering questions: if this had to face a regulator, an app store review, or a
licence audit tomorrow, what would actually hold up — and where is the honest gap. **Legal
and regulatory readiness is graded the same way the engineering is: against a stated target,
in public, including where it currently falls short.**

---

## The EU Cyber Resilience Act: mostly there by construction, not by design

The CRA sets baseline security expectations for anything with digital elements — squarely
including a fleet of network-connected embedded devices and the services they report to.
Nobody built this platform *to* satisfy it. The interesting finding is how much of it showed
up anyway, as a side effect of building the rest of this site's DevSecOps chain honestly:

| Expectation | What exists |
|---|---|
| A bill of materials | Every image and every embedded build carries one, continuously re-evaluated |
| A vulnerability-handling process | Build-time scanning plus continuous re-analysis against fresh vulnerability data, with suppressions traced to evidence |
| Coordinated disclosure | A published security policy with a private reporting channel |
| Integrity and provenance | Every image signed and provenance-attested |
| A security-update mechanism | Automatic OS patching, coordinated reboots, declarative platform-version rollout |
| Secure defaults | Default-deny public edge, enforced rate limiting, no component running with looser-than-necessary defaults by design |
| An incident process | A severity taxonomy and a mandatory blameless postmortem for anything that clears the bar |
| **A clause-by-clause conformity mapping** | **Not written.** Having the controls and being able to *demonstrate* conformity against the regulation's own article numbering are different documents |

**Roughly seventy percent of the technical substance was already true before anyone opened
the regulation** — which is either a coincidence or evidence that "build the DevSecOps chain
properly" and "meet a baseline security regulation" overlap far more than either camp usually
credits. The honest remainder is a mapping exercise, not new engineering, and it is named as
exactly that rather than left implied.

---

## GDPR: three apps that hold real personal data, graded against real rights

Three consumer-facing applications process genuine personal data: an identity account, in
one case precise location history, and user-generated content. That means the regulation's
data-subject rights are not a hypothetical.

| Right | Status |
|---|---|
| **Erasure** (the right to be forgotten) | **Shipped and verified against live data.** Full account deletion cascades through every database and the identity provider; the one application that can't fully delete a shared record instead anonymises it and removes the identity behind it. Verified end to end with real cross-user data, which surfaced and fixed three genuine bugs in the process rather than three theoretical ones. |
| **Portability** (take your data with you) | Open. Designed, not yet built. |
| **Transparency** (a real privacy notice) | Partial — one app has a complete policy; the other two do not yet, and this is the same gap as the item below. |
| **Retention enforcement** | The written policy promises old location history is purged. **No automated job enforces that promise yet** — a policy that exists only on paper is not a control. |

**The one item that blocks a public launch outright:** Terms of Service and a hosted privacy
policy for two of the three apps. This is deliberately ranked at the very top of the open
backlog, above every engineering item on the platform, because **it is the one gap that is a
legal precondition rather than an engineering nicety.** Building it is not hard. Not having
shipped it yet is the honest state, stated as such rather than assumed away.

### What the app stores actually check, and what was found

Both major app stores require a machine-readable declaration of what data an app collects and
why. Populating that declaration honestly means checking it against what the code actually
does, not what the product description says it does.

**One of those declarations was checked, and it was wrong.** A published privacy label
claimed the app collected crash and performance diagnostics. A direct inspection of every
dependency in that app found no diagnostics library of any kind present. The claim was
**removed**, not the code changed to match it — because the honest fix for an inaccurate
disclosure is a smaller disclosure, not new data collection invented to justify the old one.

That is precisely the discipline the rest of this site applies to alert thresholds and scan
scopes, aimed at a compliance artifact instead of a Prometheus rule: **check what the thing
actually does, and correct the claim to match reality — never the other way round.**

---

## Licensing: what running something obligates, versus what selling it would

The platform's own code is under a permissive licence with a single owner, no external
contributors, and nothing to reconcile. The dependency stack is a different question, because
open-source licences carry different obligations depending on how a component is used — and
"we run this for ourselves" and "we offer this as a service to other people" are legally
different acts under some of them.

| Licence family | Representative components | Obligation running it for yourself | Obligation if it became a paid hosted service |
|---|---|---|---|
| **Permissive** (Apache/MIT/BSD) | The orchestrator, the identity provider, the database operator, the storage operator, the metrics stack, the signing tooling | Attribution only | Attribution only — free to build a product on |
| **AGPL** | The dashboarding tool, the log aggregator, the object store | **None** — internal use is not distribution | **Triggered by offering the component itself over a network to third parties** — the obligation is real, but it attaches to *those specific components*, not to the applications built on top of them |
| **LGPL** | The storage engine, the code-quality server | None, and dynamic linking or running it as a separate service keeps it that way | Fine as long as it stays dynamically linked or accessed as a service, rather than statically compiled in |

**The practical read, stated plainly:** running AGPL software for internal use creates no
obligation at all. The trigger is offering *those components* to outside users over a
network — and the applications built on top of them are separately licensed and do not
inherit an obligation they were never subject to. A hypothetical commercial product built on
this stack would isolate or swap the handful of network-triggering components, not rewrite
the platform.

**Two findings from actually checking, rather than assuming the label was still accurate:**

- **One widely-used object-storage project's community edition went source-available and
  effectively unmaintained upstream part-way through this year.** That is a supply-chain fact
  about a dependency, not a licence problem, and it is the reason a Ceph-native object-storage
  path is now a live candidate rather than a someday item — a component's licence can be
  perfectly fine while its maintenance health quietly stops being fine.
- **An internal tooling document had the identity provider's licence wrong** — labelled as the
  more restrictive copyleft family when it is, in fact, permissively licensed. Caught and
  corrected the same way everything else on this page was: by checking the actual licence
  file instead of trusting an old note about it.

**What is not yet done:** there is no generated attribution/notice artifact, no "concluded"
licence scan that reads actual file headers rather than package metadata, and no trademark or
third-party creative-asset review. Named as open rather than implied complete.

---

## The pattern underneath all three sections

Every finding on this page came from the same move applied to a different domain: **stop
trusting the label, and check the thing the label describes.** A privacy declaration, a
licence note, a compliance checkbox — each one is a claim about reality, and each one was
verified against reality rather than taken on faith, exactly once each was actually asked.
Two turned out to be wrong. That ratio is the reason this page exists in public rather than
as an assumed-fine internal footnote.

---

## Read next

- **[DevSecOps, end to end](devsecops.md)** — the technical controls this page's CRA table
  draws its "already true" column from.
- **[Testing, quality gates, and grading our own maturity](quality.md)** — the same
  no-exemption grading applied to code quality instead of legal readiness.
- **[The embedded side](yocto.md)** — the connected devices this page's CRA scope most
  directly concerns.

---

<sub>Written for publication. Machines, addresses, hostnames and credential locations are
absent by construction and enforced by a guard that fails the build. Nothing on this page is
legal advice; it is an engineer's honest account of what has and has not been checked.</sub>
