---
title: What I'd do differently
reread: 2026-11-11
body_read: 2026-11-11
summary:
  - "**What it is:** the list of things that were wrong on the way, several still visible in the system. The rule for an entry is that it cost something and the cost can be described: regret without a number attached is just modesty."
  - "**The recurring ones:** believing status output, over and over; two sources of truth, every time; and two foundational calls (the orchestrator, nine nodes) that were wrong and are why the estate looks the way it does."
  - "**What I would keep, unchanged,** is in lesson 8. The decision records are the reason the argument does not have to be re-had."
  - "**Retired 2026-11-10:** the platform these lessons were written on was wiped and rebuilt as a new cluster. Old-platform figures stay under dated labels; the new platform was about 14 hours old on 2026-11-11 and nothing here claims uptime."
  - "**New on 11 November:** sequels to lessons 3, 5, 8 and 13, and a new lesson 14 on the first night of the new platform. Reviewers are AI models of the same family that helps build the estate, so the dates matter more than the grades."
---

# What I'd do differently

{% include in-short.html %}

![decisions](https://img.shields.io/badge/decision%20records-41%20in%20the%20old%20repository%2C%208%20in%20the%20new%20one-1A5276)
![reversed](https://img.shields.io/badge/reversed%20on%20evidence-9-orange)
![nodes](https://img.shields.io/badge/nodes%20now-6%20as%20of%202026--11--11-326CE5)

Every other page here describes something that works. This one is the list of things that
were wrong on the way, several of which are still visible in the system today. It is the
page I would want to read about someone else's platform, and the one most projects don't
write — a "what we learned" section that names no mistakes is marketing.

*Update, 2026-11-11: the platform described below was retired on 2026-11-10 and rebuilt as a
new cluster on the same six machines. Lessons 1 to 13 are dated history of the previous
platform and are left as written, apart from labelled notes. The sequels and lesson 14 describe
the new platform, each with a date and a status word (proven, built-not-proven, planned, open).
The cluster was about 14 hours old at 06:50 on 2026-11-11; nothing here implies it has run for long.*

*Retraction, 2026-10-09: this page used to carry a badge saying the cluster had been fully
rebuilt twice. I cannot back that number: the git history suggests more than two such
rebuilds and I never kept a list. The badge is gone rather than corrected to another guess.
The reversal badge said six while the table below listed seven; it now counts the rows.*

The rule for what goes on this page: it has to have **cost something**, and the cost has to
be describable. Regret without a number attached is just modesty.

---

## 1. Starting on the wrong orchestrator — and why I'd do it again

The previous platform's repository is still called `the-docker-swarm-ai`. It ran Kubernetes
for most of its life. (Since 2026-11-10 the platform lives in another repository and this one
is the record.) That name is a fossil of the first real architectural decision, and the
wrong one.

**What happened:** the whole estate was built on Docker Swarm first. Swarm is genuinely
simpler — the learning curve is a fraction of Kubernetes, a working multi-node cluster is a
single afternoon — and for the first few months it did everything asked of it. Then the
requirements arrived that it could not meet without fighting it: real storage orchestration,
an operator ecosystem, mature policy tooling, anything with a controller pattern. The
migration was not a weekend.

**The honest accounting, though:** Swarm taught the concepts — service, task, overlay
network, declarative desired state, rolling update — at a fraction of the cognitive cost of
learning them inside Kubernetes. Arriving at Kubernetes already fluent in *what* it was
doing, and only needing to learn *how*, was worth more than the migration cost.

**What I'd actually change:** not the choice — the **framing**. It was treated as the
permanent foundation rather than as a deliberately cheap first draft. Had it been named a
draft, the app manifests would have been written portable from day one instead of
retrofitted, and the repository would have a name that means something.

> **The transferable version:** picking the simpler tool to learn on is defensible. Failing
> to write down that you have done so is not — because six months later nobody remembers it
> was supposed to be temporary, and the name outlives the decision by years.

**Cost:** one full migration, plus a repository name that will now never be right, because
renaming it breaks every inbound link. Roughly the same trade every organisation makes with
a service called `api-v2-new-final`.

---

## 2. Nine nodes was two too many

Nine machines was never a capacity decision. It was an "I have these lying around" decision,
retrofitted with a capacity justification afterwards.

**What it actually bought:** genuine hardware heterogeneity, which forced every scheduling
and storage decision to be explicit rather than accidental. That was real value and it is
not hindsight-obvious.

**What it actually cost:** two of the nine were a net drain. One was effectively a 2011 laptop
running at 800 MHz whose only defensible role became "deliberately unreliable chaos target"
— a role a software fault injector can simulate perfectly well without occupying a physical
machine, a power socket, a switch port and a slot in every fleet-wide playbook run. Every
`ansible` run waited for it. Every upgrade cycle included it. Every audit listed it.

**What I'd do:** stop at seven, and treat "I already own it" as the weakest possible
argument for putting something in a production topology. The retirement plan for those two
is written and waiting on a replacement machine — which is itself the tell that the decision
was overdue.

> A node you keep because it exists is not free. It costs a slot in every loop that iterates
> over the fleet, forever.

### Update: this one got acted on — the cluster was brought down to six

**Both machines are out.** The paragraphs above were written while they were still running,
and are left exactly as they were so the prediction can be checked against the outcome
rather than quietly reconciled with it.

- **2026-08-26** — the chaos-target node left. Its "deliberately unreliable" role was
  replaced *in software* by a scheduled network-loss experiment, which is the specific claim
  the lesson made and the reason the hardware role could retire cleanly. The machine was not
  scrapped: it is now a Linux CI runner, a job it is perfectly adequate at.
- **2026-08-29** — the second node left. The single application replica it hosted was absorbed
  by its sibling with **zero downtime**; it held no etcd seat and no storage daemon, so there
  was no quorum or data migration to do. That was checked before the drain, not assumed.

**The honest accounting, though, because "the lesson worked" is too clean a story:** only
*one* of the two left for the reason argued above. The other left because the hardware was
wanted for an unrelated project. The right thing happened to both, but the reasoning above
is responsible for one of them, and claiming the pair would be taking credit for a
coincidence.

**The part that is genuinely useful is the bit the original got wrong.** The retirement plan
was described as "waiting on a replacement machine". No replacement ever arrived. Both nodes
left anyway, the cluster went from nine to seven with nothing added, and nothing needed
replacing — the capacity justification had been retrofitted, exactly as the first paragraph
suspected, so removing the machines removed a cost rather than a capability. **The blocker
was fictional, and it survived months of being written down as real.**

**Second update, 2026-09-04 — the number moved again, past where the lesson said to stop.**
The advice above was "stop at seven". The fleet did not: a faster machine joined as a third
control-plane member, and both all-in-ones were then retired behind it, leaving **six**
(six nodes, three of them control-plane, as of 2026-09-04; the new cluster since 2026-11-10 has
the same shape, 6 nodes with 3 control-plane, kubectl, 2026-11-11). So it
landed one below the recommendation, by a route the lesson never considered — *replacing*
capacity rather than only removing it. Worth saying plainly, because the tidy version of this
story would be "the lesson said seven and we got seven". The count was never the point. "I
already own it" being the weakest possible reason to keep a machine is the point, and that
held all four times.

> **The transferable version:** a documented blocker is not a verified one. "Waiting on X"
> written in a plan is a claim like any other, and it should be checked the same way — by
> asking what actually breaks if you proceed without X. Here the answer was *nothing*, and
> the question had never been put.

---

## 3. Storage: right call, wrong sequencing

**Stated gap, 2026-11-10 (status: deferred, not built; the database restore of lesson 14 shows
backup and restore through the object store, not storage durability).** The new platform runs with
the single-node provisioner as its **only** storage class (one class, kubectl, 2026-11-11). That is
the opposite of the "pattern worth stealing" below. It is a stated, deferred gap, not a reversed
decision: replicated block storage is the planned fix and is not built. Replication is left to the
database layer, and it is recorded as straining the recover objective, because a lost machine
takes its volumes with it. What follows is the previous platform's lesson, kept as written.

Replicated block storage (three nodes at the time) was the correct decision and I would make it
again. The **sequencing** was wrong.

It went in *after* several stateful workloads were already running on single-node local
volumes, which meant a migration under load rather than a clean start — and, worse, a period
where "the storage is replicated" was true of some volumes and not others. That is precisely
the ambiguous half-state this platform is otherwise built to avoid.

**The fix that mattered** was not the migration itself but making the wrong thing impossible
afterwards: the single-node storage provisioner is now **switched off entirely**, so an
unqualified volume claim fails loudly instead of silently pinning itself to one machine's
disk. That was the pattern worth stealing on the previous platform — *remove the unsafe default rather than
documenting it.*

**What I'd do differently:** storage first, before anything stateful. It is the one layer
that is genuinely painful to retrofit, and every hour spent getting it right up front is
repaid the first time a node dies.

---

## 4. Three OSDs is a number that looks like resilience

Related, and sharper. Three storage nodes with three-way replication sounds robust. It is
not what most people assume it is. *(Written when there were three storage hosts; see the
note at the end of this section for today. The mechanism is unchanged.)*

With replicas spread by host and exactly three eligible hosts, **every object already
occupies every host.** Lose one and the placement algorithm has nowhere to put the missing
third copy. The cluster parks in a degraded-but-serving state and stays there until that
specific machine comes back. Data is safe, service continues — but the self-healing
everybody assumes is present is not, and won't be until there is a fourth host.

A documented claim of "kill a node and watch it re-replicate" had to be **corrected by
addendum** once this was checked properly. It is true of a transient restart. It is not true
of a node loss.

> **N replicas across exactly N hosts is not the same as N-way redundancy.** The margin you
> actually have is `hosts − replicas`, and at zero the system is serving, not healing.

**Note, 2026-10-09:** the section above went stale when a fourth host joined in early
September, and I did not come back to it. Previous platform, typed by hand because that storage no longer exists:
checked on 2026-10-09 with `ceph osd tree`, read-only, four
hosts and four OSDs, with three-way replication, so a
lost host had somewhere to re-replicate to. That is the arithmetic. Whether it *did* is
a separate claim: storage health read `warn` with
four warnings on 2026-10-27, and I
had not drilled a node loss since the fourth host arrived, so "self-heals" was never
asserted here. That storage was retired on 2026-11-10 together with the question.

---

## 5. Believing status output, repeatedly

This is less a decision than a habit, and it is the most expensive thing on the page because
it recurs. Every one of these was deployed, green, and doing nothing:

- a fault injector that had **never once fired** — the field that would have shown it,
  *when did this last run*, was on no dashboard
- a reboot daemon reading a path inside its own container, logging "nothing to do" hourly on
  every node **for weeks**, while 16,002 patched-but-not-running findings accumulated
- a safety controller **never deployed to the one machine whose only job was to hold it** —
  enabling it would have been a no-op that reported success
- a documentation pipeline that ran **89 times and succeeded zero times**, failing before its
  first step so there were no logs to look at
- a shared build cache, correctly populated, **bypassed on every single build**
- a kill switch matching one hardcoded name while a second fault class had been added later
- a periodic timer that fired **exactly once per boot**, because a `RemainAfterExit=yes` on
  the paired service meant every retrigger was a no-op against an already-"active" unit

**What I'd do differently:** treat "deployed" and "observed to have acted" as two different
states in the tracker from the very first automation, not as a lesson learned seven times
(and more since: see sections 9 to 11 and the sequel below).
Every scheduled thing should ship with a `last-fired` signal *and* an alert on its absence —
and the alert on absence has to be written **before** the thing is called done, because
afterwards there is never a reason to go back and add it.

**Sequel, 2026-11-10 (proven, all three happened on the first day of the new platform).**
The habit came back in new clothes.

- The host layer's own first health check expected HTTP 200 from the cluster API. The API
  correctly answers 401 to an anonymous caller. The check was wrong, not the cluster, and it
  failed the first run until the expectation was fixed.
- A tenant quota I patched by hand to let a database start was reverted by the reconciler that
  owns it, minutes later. The hand patch was a claim about desired state that the system did
  not share. The figure belongs in the repository, not in the cluster.
- The default-deny network probe was recorded as a FAIL, and left as a FAIL (lesson 14, story 4).
  A red result written down is the opposite of a green line that asked nothing.

---

## 6. Two sources of truth, every single time

Node labels lived in a provisioning playbook *and* in the inventory the playbook was
supposed to read from. They drifted apart on a third of the fleet, silently, and nothing
compared them.

The fix was to **delete one**, not to reconcile them. Same story with the public-path
allowlist, which is stated in the edge config and in the scanner's classifier — except that
one is deliberate, and a verifier fails the build when they disagree.

It came back once more, in the artifact repository: its configuration was created by *two*
setup scripts in two repositories, and they already disagreed about whether a published
release may be overwritten. Neither ran on a rebuild. Now there is one declaration, applied on
every deploy, and a drill that configures an empty instance from it and fails on any drift.

> **Two sources of truth is a bug with a delay on it.** Either delete one, or write the
> check that compares them — and if writing the check feels like too much work, that is the
> argument for deleting one.

---

## 7. Things I was wrong about, in public

Kept because a page of decisions with no reversals is not credible:

| I claimed | Reality | How it was found |
|---|---|---|
| Older laptops would ride out a power cut on battery | Two of them had **no battery device at all** — swollen and physically removed | Read `/sys/class/power_supply/` on every node instead of assuming |
| A node was pinned to an old kernel by package holds | The holds were **inert**; a name-based bootloader default was the actual pin | Checked what was installed vs what was booted |
| Dust was causing the thermal excursions | **CPU frequency governor** at `performance`. Both machines had already been opened and cleaned first | The temperature didn't move after cleaning |
| A load test was causing intermittent connection errors | The network re-detected itself **~545 times a day regardless** — same rate with the test off | Compared the rate during and outside the test window |
| An interrupted deploy caused a NIC failure | First link drop was **an hour before** anything was run | Read the timestamps rather than the narrative |
| A merge step was stripping licence data | It wasn't — a **filter clause before upload** was, and two competing theories were disproved on the way | Uploaded the unfiltered document and looked |
| A mirror-upload script was never called by anything, so the mirror was empty by neglect | It ran **every night**; its larger half had been switched off on purpose after it filled the store — the "never called" claim even made it into a commit message | The search that found no caller had an include pattern that **matched no files**; "no match" was read as "no caller". The retraction is in the next commit |
| The four application and identity databases were highly available with **RPO 0**, in the public docs, after the move to PostgreSQL 18 | The move had silently dropped synchronous commit, resource limits and failover tolerations. From the cutover on 2026-09-16 to 2026-10-09 they were asynchronous and the docs still said zero | Auditing the public claims against the live system. Quorum-synchronous commit was restored that morning and checked on each primary |
| A database replica that crash-looped had a **corrupt checkpoint**, then a **stray timeline-5 file**; and "no alert fired" | None of the three. The replica had diverged at a failover on 2026-09-25 and sat 14 days not streaming; its first restart exposed it. Three warning-level alerts did fire, buried among the alerts from the reboot, and I do not know whether I saw them | Reading what the replica and the alerts actually said, instead of the story I had already built |

Nine reversals in the visible history (the last two added 2026-10-09; the badge at the top
is typed by hand, so I count the rows). The number is low because most wrong ideas die before
they are written down; it is not zero because the ones that survive long enough to be
written down are worth keeping visible.

---

## 8. What I'd keep, unchanged

Shorter list, and the reason the rest was survivable:

- **Making rebuilding cheap.** The entire cluster has been wiped and rebuilt from scratch
  more than once (see the retraction at the top about the count). That is only tolerable because it is an afternoon, and it is an afternoon because
  everything is a derivative of a git repository. **Being wrong stopped being expensive**,
  which is what made it possible to be wrong usefully.
  **Twice proven, 2026-11-10:** the old cluster was taken down in stages (a pause with a base
  backup of every database, a drain, storage down, uninstall) with no failed task (the stage 2 drain timed out on four app pods and the node objects were
  deleted anyway), and the new
  cluster came up on the same six machines the same day. From the first merge to the fix that let it converge
  took about 4.5 hours, read from merge times rather than a stopwatch, with a person at the
  keyboard throughout. The limits matter as much as the number: it was a playbook run in order
  with a person watching, nothing was restored automatically, and **a wipe is not a migration**.
  The eight old restore drills were waived, and 0 of 257 old alerts, 0 of 74 mechanisms and 0 of
  16 power-off proofs carried over. The cutover gate is not passed.
- **Writing down decisions with their alternatives.** 41 decision records in the old repository
  (2026-10-27), 8 in the new one (as of 2026-11-11), several of the old ones
  which have been reversed *by referring back to them* — including one that corrected a
  claim about why an earlier decision had been made, which turned out to be unsupported by
  the record it cited.
- **Refusing to round numbers up.** At the first count, four of thirteen failure domains were genuinely
  single-fault tolerant. Publishing "four" instead of a nicer figure is why the other nine
  were tracked instead of forgotten. (That was the first count; the
  [reliability page](reliability.md) holds the current one.)
- **Pruning the backlog on purpose.** Thirty-four of fifty-nine open items were closed in one
  pass — some done, some obsolete, and nine as **won't-do**, each with a reason. Deciding
  what will never be done is the judgement call that keeps a register from becoming a guilt
  pile. (Frozen history of the previous platform; its open-item register was retired with it.)

---

## 9. A green line that never asked the right question

A database replica diverged at a failover on 2026-09-25 and then sat 14 days not streaming
from its primary. Nothing stopped it; the first restart crash-looped, which is how I found out.

**What I'd do differently:** assert the property you mean, not a proxy for it. The property
was *every replica is streaming*, and nothing checked that. New alerts now cover this class (replica not
streaming, container crash-looping, instance not ready), added the same day, which is the
wrong order — see section 5.

---

## 10. A copy that "mirrors the shape" is not the original

The PostgreSQL 18 cutover on 2026-09-16 was meant to mirror the high-availability shape of
the old clusters. It mirrored most of it. Synchronous commit, the resource limits and the
failover tolerations were silently dropped, so for three weeks the four three-instance
application and identity databases were asynchronous while the docs said RPO 0. Nothing
was red. The replacement was healthy; it just was not the thing documented.

I found it by auditing the public claims against the live system, which is the exercise this
site exists to make routine. Those four are back on quorum-synchronous commit (any one of two
standbys), checked on each primary on 2026-10-09. The two-instance clusters are asynchronous
by design and say so.

> **A generated copy needs a guard that compares it to its source.** "Mirrors" is a claim in
> a commit message. A check that fails when the successor differs from the original is a
> property. One now exists for this exact case.

---

## 11. Three wrong claims in one diagnosis

When that replica crashed, I diagnosed a corrupt checkpoint. Wrong. Then a stray timeline-5
file. Also wrong. I had also said no alert fired. Also wrong: three warning-level alerts had
fired, buried among the alerts from the reboot, and I do not know whether I saw them. Three
confident claims, none checked against what the system had actually recorded.

> **Before diagnosing, read what the system recorded.** The status line was the weakest
> evidence available; the alert history and the replica's own logs were there.

---

## 12. The bug that signed people out, and the wrong diagnosis that explained it

The report was "old devices time out very, very fast". The natural suspect was the identity
provider's timeouts, so I read its settings and made them explicit (an hour for the access
token, thirty days idle for the offline refresh token, declared as code since 2026-10-09 by the old platform's playbook, which was retired on 2026-11-10). That was worth
doing, and it was a diagnosis of the server, from the server's side. It was not the cause.

The apps ended a session on **any** failure while refreshing a token. A dropped connection,
a restart of the identity provider, a proxy error page, a phone waking with a dead socket:
each was read as "the server rejected you", the tokens were deleted, and the person was
sent to the login screen holding a perfectly good refresh token that I had just deleted for
them. No timeout had expired anything. The apps did.

The fix is to ask a better question. A refresh now has three outcomes (worked, rejected,
undecided), and only a reply that is *exactly* the OAuth `invalid_grant`, or having no
token at all, counts as rejected. The classifier is strict on purpose: on Android the
library reports any reply with an `error` field as an OAuth error regardless of the HTTP
status, so a proxy's error page would otherwise look like a revoked session. Roughly
twenty tests per app (18 to 25, counted by hand) pin both platforms' error shapes.

The fix also needed a way to test it. **A test account must not be an account that real
phones use**: the identity provider locks an account after repeated failed logins, and a
test that fails on purpose should not be able to do that to a person. The synthetic traffic
has had a user of its own since 2026-10-09.

> **When a person says "it logs me out", look first at what the client does with an error,
> not at how long the server says a session lives.** The server's number was correct. The
> client's reaction to a hiccup was the bug, and no server setting could have fixed it.
> [The apps](apps.md) have the rest of the story.

---

## 13. What outside reviews found

*Added 2026-10-27, extended 2026-11-11. Four reviews in fourteen days in October and two more in November, each dated, each with a worklist.*

The site's thesis is that naming mistakes in public is the point, and until now it named only the
ones I found myself. In October the estate was reviewed from the outside four times, by an AI model
asked to read read-only, grade against the objectives the repositories state for themselves, and
be unkind. Two caveats first, because they decide how much to trust any of this. **The reviewer is
the same family of model that helps build the estate**, so it is a checklist generator with
unusual stamina, not an independent audit. And a first run of sixteen reviewers was cut off by a
session limit after three finished, which is why the method section of that review comes before its
findings. What made the findings usable is that the high-severity ones were handed to separate
skeptic agents told to refute them: 18 of them, of which **15 were confirmed, 3 were downgraded and
none was refuted**. Every downgrade corrected the finding's premise, not its substance, and was
recorded beside the original rather than edited into it.

| Review | Verdict in one line | What changed because of it |
|---|---|---|
| **The whole estate**, 14 October | The peg is real and the learning is real; the gap is between them. Graded 4 of 5 on learning, 3 on process, **2.5 on claims versus reality**. The operational layer and this site told the truth; the repository's own README and eight topology documents did not. | The README's retracted claims were replaced with what is true; topology documents re-read against the cluster; ADR statuses fixed and given a daily probe; twelve guards put on a schedule (sixteen now); 81 broken links fixed and kept at zero by a hook. |
| **How someone could get in**, 22 October | No direct path from the internet to cluster-admin was found; **the inside is soft**: what a foothold becomes is worse than how one is gained. | Key-only SSH on the nodes, proven by a fresh login (22 October); a generated Grafana password in place of a committed default; test passwords out of command lines. The rest is tracked privately and deliberately not itemised here until it is fixed. |
| **The AI in the cluster**, 26 October | The summaries were inflated and one data source had been blind for fourteen days without a mention; a model-supplied name reached a root command. | The agent was hardened and put under measurement the same day: [the account is here](aiops.html#the-agent-since-2026-10-26). |
| **This site**, 27 October | Clarity 4, completeness 3, fast-reader accessibility 2: no page had a summary, and five statements had turned stale in the pessimistic direction. | An *In short* block on every page, enforced by the build; a dated *Recently* list; this lesson; and the corrections on the [estate page](index.html#corrections-2026-10-27). |
| **The old platform's carry-over**, 8 November | 188 findings, 21 of them high, about what the previous platform's habits, claims and mechanisms should or should not follow into the new one. | By 2026-11-10, 17 of the 21 high findings were closed, 3 open and 1 in review. 116 of the 188 findings were still open or in review that day. The review is private; this is its dated summary. |
| **"The move, six days in"**, 10 November | The old cluster was healthy but unattended: its daily guards were red every day from 2026-11-02 to 2026-11-09. 76 of 77 commits went in through pull requests. The kind-cluster gate over its last 30 runs: 22 green, 5 red, 3 cancelled. The quarterly OKR page was still a draft with no start date. | The findings are open work, not fixed work, on 2026-11-11. Private review, cited by date only. |

Six reviews, then, not four, and the two newest are the first about the move rather than the
estate: they found the habits of the old platform going stale unattended, and a young platform
with gates not yet passed.

**What I would carry from it.** First, the best finding of the lot was not a vulnerability: the
habit this site is built on, *assert the property, do not trust the report*, was applied to the
cluster and to this site and **not to the repository's own prose**, which is where the claims
that did not survive were. The front door was the least-checked part. Second, a review of an
estate that moves faster than its documents goes stale the day it is filed: the 14 October review's
top finding, the repository's README contradicting this site, had been fixed by the 21st. The
number to quote is therefore never the grade; it is the date.

---

## 14. What the first night of the new platform taught

*Added 2026-11-11, about 14 hours after the new cluster came up. Dated 2026-11-10 and 2026-11-11.
Each story has a status word. These are first-night facts, not a track record.*

**1. A secrets apply that waited for itself (fixed, proven 2026-11-10).** One shared unit held
the app namespace and the login service's secrets. The app namespace waited for the login
service, which waited for its admin secret, which sat in the same failing apply. A deadlock
with no error, only waiting. The fix was one unit per namespace.
> Put things that wait for each other in different units.

**2. The first backup failed on a name pods cannot resolve (fixed, proven 2026-11-10).** The
backup target was addressed by a name ending in the local-network suffix, which works on a laptop
and not inside a pod. The bootstrap now refuses such a name, and its self-test shows the refusal
can fail, so it is not a check that cannot go red.

**3. The restore drill hit three walls in the platform's own safety rules (proven 2026-11-10).**
The rules that protect the cluster also blocked the drill that proves it. The database restore
then succeeded once, by hand: 60 seconds, a few MB, from an on-demand backup into a scratch cluster with temporary network rules. The scheduled backup was not restored, and the backup store is one machine. The recovery point is bound by write-ahead-log
archiving and is **not measured yet**. One manual restore of a tiny database is not a drill.

**4. Default-deny held except for the first one to three seconds (open, 2026-11-10).** The
probe recorded a FAIL: traffic got through briefly while a new workload came up. The gap is
open and the FAIL stays on the record.

**5. The fix that fixed nothing (proven 2026-11-11).** SSH to the nodes by name took 10 to 20
seconds. The first fix opened IPv6 link-local in the firewall and did nothing, because the names
resolve to global IPv6 addresses. The real fix made the nodes announce IPv4 only over
mDNS; a login by name now takes 0.2 to 0.8 seconds (timed during the bring-up, not re-timed on 2026-11-11).
> Measure before and after. A fix you did not time is a guess.

**6. The rehearsal found defects the real machines would have (proven 2026-11-10).** Before
the real run, the whole install ran in virtual machines on a Mac. It found a home-folder path in
the key check, virtual machines that could not reach each other, no route from the Mac into the
VM network, and a clock check run seconds after boot. After fixes it took 4 min 11 s, and a
second run changed nothing. Limits: aarch64 only and one distribution only, so it rehearses the
playbooks, not the hardware.

**7. The wipe left things the uninstaller did not (fixed, proven 2026-11-10).** A virtual
address stayed on one node and a node-password file on all six. One of the assistant's own
claims during the session was wrong about this (the Ceph disk images) and was corrected after reading the machines.

**8. A lost working tree (rule adopted, 2026-11-10).** Uncommitted files were lost once by
removing a worktree after a hook rejected a commit. The rule: keep the worktree until the
commit succeeds.

**9. A cancelled required check blocks a merge (proven 2026-11-10).** After a watchdog
fallback, the red aggregate result stayed on the pull request and the green dispatched run did
not reach it. The merge stayed blocked for 28 minutes after the green existed. "Re-run all
jobs" cleared it.
> A required check is a property of the pull request, not of the repository's latest run.

---

## Read next

- **[High availability, audited](reliability.md)** — the inventory these lessons came out of.
- **[DevSecOps, end to end](devsecops.md)** — the measurement traps, in more detail and with
  the code.
- **[`examples/`](https://github.com/schultzzznet/schultzzznet/tree/main/examples)** — some
  of these lessons, extracted as runnable artifacts.
- **[Live status](status.md)** — the figures quoted on this page, regenerated rather than
  remembered.

---

<sub>Written for publication. Machines, addresses, hostnames and credential locations are
absent by construction and enforced by a guard that fails the build.</sub>
