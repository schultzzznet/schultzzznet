---
title: Legal, licensing, and the regulatory posture nobody publishes for a home project
reread: 2026-11-11
body_read: 2026-11-11
summary:
  - "**What it is:** the less flattering questions asked of a home-built platform, graded against a stated target in public, including where it falls short. The platform was wiped on 2026-11-10 and rebuilt; every old measurement below is labelled previous platform."
  - "**The EU Cyber Resilience Act:** the clause-by-clause mapping is still not written. On the new platform (2026-11-11) signature enforcement is configured on first-party images (a refusal is shown only on a test cluster, not yet on the home site), but no automatic OS patching exists and no vulnerability tracker runs. **GDPR:** erasure was verified on 2026-07-02 on databases that are now wiped."
  - "**Licensing:** MIT for code and CC BY 4.0 for writing on this site. The licence table was written for the old stack; the new stack has not been checked against it yet."
  - "**Open items:** the clause mapping, terms of service and a hosted privacy policy, a hardware licence decision, an OS patching mechanism, and a fix for the 1 to 3 second start gap in default-deny."

---

# CRA, GDPR, app-store rules, and what a licence actually obligates

{% include in-short.html %}

{% assign s = site.data.stats %}
![cra](https://img.shields.io/badge/EU%20CRA-clause%20mapping%20not%20written-orange)
![gdpr](https://img.shields.io/badge/GDPR%20erasure-shipped%20and%20verified%202026--07--02-2EA44F)
![privacy](https://img.shields.io/badge/privacy%20label-false%20draft%20caught%20before%20any%20submission-orange)
![licence](https://img.shields.io/badge/licence-MIT%20code%20%C2%B7%20CC%20BY%204.0%20prose%20(this%20site)-blue)
![signing](https://img.shields.io/badge/signing-enforcement%20configured%2C%20refusal%20shown%20on%20a%20test%20cluster%20only%20(2026--11--11)-005571)
![agpl](https://img.shields.io/badge/licence%20table-new%20stack%20not%20yet%20checked-orange)

*Status as of 2026-11-11. The platform this page described was wiped on 2026-11-10 and a new cluster was built on 2026-11-10 and 2026-11-11, so it is about a day old: nothing here implies it has stayed up. Statements about the new platform carry a date and say whether they are proven by a record or a live check. Statements about the old one sit under a "previous platform" label with their own date. Generated figures elsewhere on the site are described by [the stats generator](status.md).*

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
| **Coordinated disclosure** | Partial | This public repository published a [security policy](https://github.com/schultzzznet/schultzzznet/blob/main/SECURITY.md) on 2026-10-09: scope (the site and its scripts; the private estate is explicitly not offered for testing), what is most wanted (a leak, above all), a reporting route and honest expectations (no SLA, no bounty). It names GitHub's private vulnerability reporting first, with an email fallback; Private reporting was switched on and confirmed through the repository's API on 2026-10-09; the email, a dedicated role address (`ciso@`), is the fallback. |
| **Integrity and provenance** | Partial | **New platform, 2026-11-11:** first-party images are signed in CI, and signature enforcement is configured and Ready on the live cluster (checked 2026-11-11); the running Warn image passes it. A refusal of an unsigned or wrong-key image was shown on a local test cluster on 2026-11-07, **not yet on the home site**. On the home site a vendor image that was not on the list was refused on 2026-11-10, which tests the list, not signing. Vendor images are held to a closed list by digest, not by signature, which is weaker and still open. How many running first-party images verify: not measured yet. *Previous platform, 2026-10-09:* nothing enforced signatures at admission. |
| **Secure defaults** | Partial | **New platform, 2026-11-11:** the restricted pod security level is enforced on 4 of 13 namespaces, and tenant namespaces have default-deny network rules (4 tenants have them). Default-deny has a recorded gap: a new pod has no policy for about 1 to 3 seconds after it starts. That test is recorded as a **fail** (2026-11-10). See the measured posture below. |
| A bill of materials | Open | **No tracker runs on the new platform (2026-11-11); one is planned.** The uploads recorded on the previous platform (2026-10-09) went to a tracker that is wiped. Nothing is measured here yet. |
| A vulnerability-handling process | Partial | **New platform (2026-11-11):** no image vulnerability scanning is recorded in its CI checks and no tracker runs; kernel versions on the new nodes are not recorded, so no kernel CVE figure exists (not measured yet, 2026-11-11). *Previous platform, 2026-10-09:* 0 CVEs against the running kernels on 6 nodes, and no severity counts, because the tracking tools sat behind credentials I did not use. |
| A security-update mechanism | **Open** | **Not done on the new platform (2026-11-11):** no automatic OS patching and no coordinated reboots exist yet. Platform versions roll out through Git, but that is not an update mechanism for the operating system. *Previous platform:* this row said "Done, as designed" and was not re-measured; the mechanism was torn down with the old cluster. |
| An incident process | Done, as designed (unchanged) | A severity taxonomy and a mandatory blameless postmortem for anything that clears the bar; [one of them in full](incident.md). |

The honest remainder is a mapping exercise plus the open rows, named as exactly that. I have
stopped putting a percentage on it.

### The measured posture behind "secure defaults"

**New platform, counted read-only from the cluster on 2026-11-11** (about a day after it was built):

- **27 NetworkPolicies** exist, in the four tenant namespaces, the flux namespace and the system namespace.
- **6 of 13 namespaces** carry Pod Security labels: the restricted level is enforced on 4 of them, baseline on the ingress namespace, and the Flux namespace only warns.
- **Limits are enforced by a resource quota and a limit range** in each of the four tenants, so a container there cannot run without limits.
- **Privileged and host-network pods are not counted on the new cluster yet** (not measured yet).
- The default-deny start gap (1 to 3 seconds for a new pod) is recorded as a failed result on 2026-11-10; the steady state held.

*Previous platform, counted 2026-10-09 (retired 2026-11-10):* 228 containers, of which 29 were privileged, across 3 namespaces; 15 pods on the host network; 116 containers with no resource limits; 0 NetworkPolicies; Pod Security labels on 1 of 22 namespaces.

Some host access is justified (node agents need it), so "not counted" is a gap in the measurement, not a clean bill. It is a tracked gap, not a finished control.

---

## GDPR: three apps that hold real personal data, graded against real rights

Three applications hold genuine personal data: an identity account, in
one case precise location history, and user-generated content. There are no outside users yet,
but the data-subject rights are built and verified on the live system now, not left for the day there are.

| Right | Status |
|---|---|
| **Erasure** (the right to be forgotten) | **Shipped 2026-07-02, and verified against the then-live cluster with real cross-user data that day, which surfaced and fixed three genuine bugs. Those databases were wiped on 2026-11-10, so the verification is previous-platform evidence.** The cascade code is unchanged, but it has not been run on the new platform (2026-11-11), where only the Warn reference app is deployed. The new identity provider also runs, in development mode with in-memory storage, so it holds no durable identity data and erasure has nothing durable to reach there. On 2026-07-02 the cascade removed the user's rows from each database those three apps use, and from the identity provider; the one application that can't fully delete a shared record anonymises it and removes the identity behind it. The deletion endpoint exists in these three apps. The fleet and mower backends have no such endpoint, and I have not graded whether they hold personal data. I have not re-run a deletion since, because it is destructive. |
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

**Scope of "MIT", corrected and then settled, 2026-10-09:** the private platform repository and
the OS layer are MIT-licensed. This public site repository had **no licence file** until
2026-10-09, which meant default copyright applied, the opposite of what an MIT badge on a
public site implies. It now has two: [MIT](https://github.com/schultzzznet/schultzzznet/blob/main/LICENSE)
for the code (`scripts/`, `examples/`, the Makefile and workflow) and
[CC BY 4.0](https://github.com/schultzzznet/schultzzznet/blob/main/LICENSE-docs) for the
writing and images, because MIT is a software licence and a write-up is not software. Quotations
stay with their authors. The hardware repositories are private and still carry no licence file;
that decision is open. There are no external contributors, so nothing needs reconciling.

The dependency stack is a different question, because open-source licences carry different
obligations depending on use, and "we run this for ourselves" and "we offer this as a service
to other people" are legally different acts under some of them.

| Licence family | Representative components | Running it for yourself | If it became a paid hosted service |
|---|---|---|---|
| **Permissive** (Apache/MIT/BSD) | The orchestrator, the identity provider, the database operator, the storage operator (previous platform), the metrics stack (previous platform), the signing tooling | Attribution only | Attribution only |
| **AGPL** (previous platform) | The dashboarding tool, the log aggregator, the object store: none of these runs now | **None**; internal use is not distribution | **Triggered by offering the component itself over a network to third parties.** It attaches to *those components*, not to the applications built beside them, which do not inherit it. |
| **LGPL** (previous platform) | The storage engine, the code-quality server: neither runs now | None | Fine while dynamically linked or run as a separate service |

**Status, 2026-11-11:** this table was written for the old stack, which was wiped on 2026-11-10. The new platform's back-up store is a different project, and its licence class has **not been checked** for this table yet: the platform's own tool list declares it AGPL-licensed, which, if it holds, puts it in the AGPL row, but I have not read the licence file. Until that is done, read the rows as history, not as a statement about what runs today.

A hypothetical commercial product on the old stack would isolate or swap the handful of
network-triggering components, not rewrite the platform. These licence classes are as
declared upstream. I have **not** re-read the licence files for this table, which is the very
check the next two findings come from.

**Two findings from actually checking, rather than trusting the label:**

- **Previous platform: the object-storage project's upstream repository was archived in April 2026** (GitHub
  reported it archived, last push 2026-04-24). It ran there as the only object store and
  the database backup target, from a private copy, until the cluster was wiped on 2026-11-10. That is a supply-chain fact, not a licence
  problem. A component's licence can be fine while its maintenance health quietly
  stops being fine. The new back-up store is a different project; its maintenance health is not checked either (2026-11-11).
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
- A licence decision for the hardware repositories.
- Terms of Service and a hosted privacy policy for all three apps; automated retention.
- Vendor images verified by signature, not only by digest list; an OS patching mechanism; a software-bill-of-materials tracker.
- Closing the 1 to 3 second default-deny start gap, and a licence check of the new stack's components.

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
