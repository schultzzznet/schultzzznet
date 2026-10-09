---
title: Legal, licensing, and the regulatory posture nobody publishes for a home project
---

# CRA, GDPR, app-store rules, and what a licence actually obligates

{% assign s = site.data.stats %}
{% assign gen_day = s.generated_at | slice: 0, 10 %}
{% assign signed = s.supply_chain.first_party_signed_verified | append: " of " | append: s.supply_chain.images_first_party | append: " first-party images verify" | url_encode | replace: "-", "--" | replace: "+", "%20" %}
![cra](https://img.shields.io/badge/EU%20CRA-clause%20mapping%20not%20written-orange)
![gdpr](https://img.shields.io/badge/GDPR%20erasure-shipped%20and%20verified%202026--07--02-2EA44F)
![privacy](https://img.shields.io/badge/privacy%20label-false%20draft%20caught%20before%20any%20submission-orange)
![licence](https://img.shields.io/badge/MIT-platform%20and%20OS%20layer%20only-blue)
![signing](https://img.shields.io/badge/signing-{{ signed }}-005571)
![agpl](https://img.shields.io/badge/AGPL%20dependencies-scoped%2C%20not%20triggered-005571)

*Status as of 2026-10-09. Where a figure comes from the estate it is read off the running
system by [the stats generator](status.md), measured at {{ s.generated_at }}.*

Most write-ups of a home-built platform stop at the architecture diagram. This one also asks
the less flattering questions: if this had to face a regulator, an app store review, or a
licence audit tomorrow, what would actually hold up, and where is the gap. **Legal and
regulatory readiness is graded the same way the engineering is: against a stated target, in
public, including where it currently falls short.**

*Retractions, 2026-10-09. This page used to say "roughly seventy percent" of the CRA was
already true. That number was an estimate carried over from my private gap register; nothing
ever counted it, and the table below does not add up to it, so it is gone. It also said every
image was signed, that a security policy was published, and that nothing ran with
looser-than-necessary defaults. All three were wrong, and the rows below say what is true.*

---

## The EU Cyber Resilience Act: partly there by construction, not by design

The [Cyber Resilience Act](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)
(Regulation (EU) 2024/2847) sets baseline security expectations for anything with digital
elements, which squarely includes a fleet of network-connected embedded devices and the
services they report to. Nobody built this platform *to* satisfy it. Some of it showed up
anyway, as a side effect of building the rest of the DevSecOps chain honestly. The status
column is my own grading, not a conformity assessment.

| Expectation | Status | What exists |
|---|---|---|
| **A clause-by-clause conformity mapping** | **Open** | **Not written.** Having controls and being able to *demonstrate* conformity against the regulation's own article numbering are different documents. |
| **Coordinated disclosure** | **Open** | A written security policy exists, but only in the private repository. This public repository has none, so an outside reporter cannot find one. A published policy with a reachable contact is the fix. |
| **Integrity and provenance** | Partial | {{ s.supply_chain.first_party_signed_verified }} of {{ s.supply_chain.images_first_party }} first-party images verify against the release key (measured {{ gen_day }}). Provenance is attached at build. Nothing enforces signatures at admission, and the {{ s.supply_chain.images_third_party }} third-party images are upstream's, not signed by me. |
| **Secure defaults** | Partial | The public edge is default-deny and rate-limited. Inside the cluster it is not; see the measured posture below. |
| A bill of materials | Partial | {{ s.supply_chain.sbom_projects }} SBOM uploads returned HTTP 200 in the latest nightly runs. That is acceptance of an upload, not a count read from the tracker and not analysis. The embedded repository says its release is snapshotted to the tracker; I have not re-measured that. |
| A vulnerability-handling process | Partial | Build-time image scanning (last scheduled run succeeded 2026-09-29). As of 2026-10-09, 0 CVEs against the running kernels on {{ s.cluster.nodes }} nodes. Whether the tracking tools re-analyse on fresh data I did not measure; their APIs sit behind credentials I did not use, so I quote no severity counts. |
| A security-update mechanism | Done, as designed | Automatic OS patching, coordinated reboots, declarative platform-version rollout. Not re-measured for this page. |
| An incident process | Done, as designed | A severity taxonomy and a mandatory blameless postmortem for anything that clears the bar; [one of them in full](incident.md). |

The honest remainder is a mapping exercise plus the open rows, named as exactly that. I have
stopped putting a percentage on it.

### The measured posture behind "secure defaults"

Counted read-only from the cluster on 2026-10-09, as counts only:

- **{{ s.cluster.containers }} containers** run, of which **29 are privileged**, across 3 namespaces.
- **15 pods** use the host network.
- **116 containers** declare no resource limits.
- **0 NetworkPolicies** exist; nothing restricts pod-to-pod traffic.
- Pod Security labels are set on **1 of {{ s.cluster.namespaces }} namespaces**.

Some of that is justified (storage and node agents need host access). But the old sentence
was an absolute, and the numbers say otherwise. It is a tracked gap, not a finished control.

---

## GDPR: three apps that hold real personal data, graded against real rights

Three consumer-facing applications process genuine personal data: an identity account, in
one case precise location history, and user-generated content. The data-subject rights are
not a hypothetical.

| Right | Status |
|---|---|
| **Erasure** (the right to be forgotten) | **Shipped 2026-07-02, and verified against the live cluster with real cross-user data that day, which surfaced and fixed three genuine bugs.** On 2026-07-02 the cascade removed the user's rows from each database those three apps use, and from the identity provider; the one application that can't fully delete a shared record anonymises it and removes the identity behind it. The deletion endpoint exists in these three apps. The fleet and mower backends have no such endpoint, and I have not graded whether they hold personal data. I have not re-run a deletion since, because it is destructive. |
| **Portability** (take your data with you) | Open. Designed, not yet built. |
| **Transparency** (a real privacy notice) | Partial. One app has the policy text; none is hosted yet. Same gap as the item below. |
| **Retention enforcement** | The written policy promises old location history is purged. **No automated job enforces that promise yet.** A policy that exists only on paper is not a control. |

**The one item that blocks a public launch outright:** Terms of Service and a hosted privacy
policy for all three apps. It sits at the top of the open backlog, above every engineering
item, because **it is a legal precondition rather than an engineering nicety.** Building it
is not hard. Not having shipped it is the honest state.

### What the app stores check, and what was found

Both major app stores require a machine-readable declaration of what data an app collects and
why. Populating it honestly means checking it against what the code does, not what the
product description says.

**No app has been submitted to a store.** All three are pre-launch. But the draft privacy
label, written in the private repository ahead of any submission, claimed the app collected
crash and performance diagnostics. A direct inspection of every dependency in that app found
no diagnostics library of any kind. The claim was **removed from the draft**, not the code
changed to match it, because the honest fix for an inaccurate disclosure is a smaller
disclosure. It was caught before it could be filed, and I will not pretend it was ever live.

That is the discipline the rest of this site applies to alert thresholds and scan scopes,
aimed at a compliance artifact: **check what the thing actually does, and correct the claim
to match reality, never the other way round.**

---

## Licensing: what running something obligates, versus what selling it would

**Scope of "MIT", corrected 2026-10-09:** the private platform repository and the OS layer
are MIT-licensed. This public site repository and the hardware repositories carry **no
licence file**, which means default copyright applies, the opposite of what an MIT badge on
a public site implies. Whether that is deliberate is still undecided; adding a licence is an
open item, and I have not done it here. There are no external contributors, so nothing needs
reconciling.

The dependency stack is a different question, because open-source licences carry different
obligations depending on use, and "we run this for ourselves" and "we offer this as a service
to other people" are legally different acts under some of them.

| Licence family | Representative components | Running it for yourself | If it became a paid hosted service |
|---|---|---|---|
| **Permissive** (Apache/MIT/BSD) | The orchestrator, the identity provider, the database operator, the storage operator, the metrics stack, the signing tooling | Attribution only | Attribution only |
| **AGPL** | The dashboarding tool, the log aggregator, the object store | **None**; internal use is not distribution | **Triggered by offering the component itself over a network to third parties.** It attaches to *those components*, not to the applications built beside them, which do not inherit it. |
| **LGPL** | The storage engine, the code-quality server | None | Fine while dynamically linked or run as a separate service |

A hypothetical commercial product on this stack would isolate or swap the handful of
network-triggering components, not rewrite the platform. These licence classes are as
declared upstream. I have **not** re-read the licence files for this table, which is the very
check the next two findings come from.

**Two findings from actually checking, rather than trusting the label:**

- **The object-storage project's upstream repository was archived in April 2026** (GitHub
  reports it archived, last push 2026-04-24). It still runs here as the only object store and
  the database backup target, from a private copy. That is a supply-chain fact, not a licence
  problem, and the reason a Ceph-native object-storage path is a live candidate. There is
  still none in place. A component's licence can be fine while its maintenance health quietly
  stops being fine.
- **An internal tooling document had the identity provider's licence wrong**, labelled as the
  more restrictive copyleft family when it is permissive. Caught by reading the actual licence
  file.

**Not yet done:** a generated attribution/notice artifact, a "concluded" licence scan that
reads file headers rather than package metadata, and a trademark and third-party
creative-asset review.

---

## The pattern underneath

Every finding here came from the same move: **stop trusting the label, and check the thing
the label describes.** Counting this page's own claims the same way, the score is poor: the
privacy label, the CRA percentage, the "every image signed" line, the published-policy line,
the MIT scope and the secure-defaults line were all wrong, and the first one only by luck
of being caught early. That is the reason this page is in public.

---

## Open items

- A conformity mapping against the CRA's article numbering.
- A published security policy in this repository, with a dedicated reporting contact.
- A licence decision for this repository and the hardware repositories.
- Terms of Service and a hosted privacy policy for all three apps; automated retention.
- Signature enforcement at admission, and the in-cluster defaults above.

## Read next

- **[DevSecOps, end to end](devsecops.md)**: the technical controls the CRA table draws on.
- **[Testing, quality gates, and grading our own maturity](quality.md)**: the same
  no-exemption grading applied to code quality.
- **[The embedded side](yocto.md)**: the connected devices the CRA scope most directly concerns.
- **[Live status](status.md)**: the measured figures, with the command beside each.

---

<sub>Written for publication. Machines, addresses, hostnames and credential locations are
absent by construction and enforced by a guard that fails the build. Nothing on this page is
legal advice; it is an engineer's account of what has and has not been checked.</sub>
