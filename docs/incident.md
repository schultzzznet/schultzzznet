---
title: One incident, in full
---

{% assign s = site.data.stats %}
{% assign open_items = 2 %}
{% assign checked = "2026-10-09" %}
{% assign asof = s.generated_at | date: "%Y-%m-%d" %}

# A nine-minute quorum loss that nothing detected

![open items](https://img.shields.io/badge/open%20items-{{ open_items }}%20as%20of%20{{ checked | replace: "-", "--" }}-orange)

*Happened 20 August 2026. The status of every item below was last checked on 9 October 2026,
and says so where it matters.*

Every other page here summarises incidents. This one is a single real post-mortem, shortened
but not softened, because a summary of an incident is the part that is easy to write and the
part that teaches least. It is a condensed rewrite of the private original, not a copy: the
timeline is gone, and so is everything that names a machine. An earlier version of this page
said "close to verbatim". It was not, and that sentence is withdrawn.

It is also the most flattering-to-omit story on the site: the cluster survived, nobody
noticed at the time, and it would have been entirely possible to never write it down.

*Corrections made on 9 October 2026, all of them to claims this page made about itself, are
marked where they occur: the clusters count, "close to verbatim" (above), the owner column,
the "never pointed at hardware" claim, the rubric sentence, and the RPO row.*

---

## What happened

Mains power to the whole building dropped for **under a minute**.

Two of the three control-plane nodes hard-crashed and rebooted. The third did not, for a
reason that was not established until the next day, and one part of which is *still* open.

For **9 minutes and 12 seconds**, the surviving node was the cluster state store's only
reachable member. A three-member consensus cluster needs two votes to commit a write. It had
one.

| | |
|---|---|
| **Severity** | SEV1. "Quorum lost" is a named example in this platform's own taxonomy |
| **Quorum lost** | 9m 12s, precisely, reconstructed from the surviving node's own raft peer logs |
| **Detected by monitoring** | **No.** Nothing fired. Nothing could have |
| **How it was found** | A human felt the lights go out and asked for a status check |
| **Data lost** | None. Seven database clusters, the number there were that day, verified fully replicated afterwards. (An earlier version said eight; the post-mortem says seven.) |
| **User impact** | None observed. Already-scheduled pods keep running without the state store |
| **Recovery** | Fully automatic, no human action, no runbook invoked |
| **Fixed since** | State-store monitoring, on 3 September. See [Afterwards](#afterwards) |

**Since then:** the control plane was rebuilt on a different set of three machines on 4
September. Today the cluster has {{ s.cluster.control_plane }} control-plane nodes and
{{ s.cluster.agents }} agents ({{ s.cluster.nodes_ready }} of {{ s.cluster.nodes }} Ready, as of
{{ asof }}). Everything below about "the three" describes the
three of 20 August.

---

## Why nothing detected it

The five-whys, shortened but not softened:

**Why did quorum drop?** Two of three members lost power simultaneously.

**Why did that leave zero fault tolerance instead of one spare?** Because, and this is the
part worth reading, **there was no design here to fail.** The third seat had been placed for
consensus tolerance, on a documented and sound rationale that says nothing whatsoever about
power. Nobody had ever decided how power loss should be survived. It simply had not been a
question anyone asked.

**Why did nobody know the fleet's real power situation?** Because nobody had checked. Two
machines turned out to have **no battery at all**: one had swelled and been physically
removed, the other's charging path had failed to the point it ran from an external supply.
Both were correct responses to real hardware faults. Neither was written down anywhere,
because there was no inventory to write them down *in*.

**Why didn't monitoring catch the quorum loss?** Because **there was no etcd monitoring. At
all.** Not a threshold set too loosely: verified directly, zero scrape targets, zero alert
rules, zero service monitors mentioning the state store. An entire tier of the platform, and
the most important one, was invisible. (That was true on 20 August. It is not true now; see
[Afterwards](#afterwards).)

**Why did anyone find out?** A human experienced the power cut and asked. The same detection
mechanism as an earlier public-edge outage: *someone happened to look.*

---

## The correction that matters more than the incident

The first draft of this post-mortem said the topology had been **designed** around one
battery-backed node, and that this design's assumption had quietly broken.

That was checked against its own cited sources, the decision record and the inventory comment
it pointed at, and **neither mentions power or batteries at all.**

There was no power-diversity design. There was no broken assumption. There was an
**unexamined fact** that happened to matter on one particular afternoon.

> A post-mortem that invents a design in order to have something to blame is worse than no
> post-mortem, because it manufactures a false lesson and closes the question.

The real situation, once actually inventoried: of the three control-plane hosts on the day,
**exactly one** had a battery that still worked, and it was the one nobody would have guessed,
because its own hostname and earlier drafts of this document both described it as a desktop.
That single battery is the entire reason this was a nine-minute self-healing blip rather than
a total loss with no surviving member.

---

## What went well, badly, and where it was luck

Three separate headings on purpose. Collapsing them is how a post-mortem becomes marketing.

**Well.** Recovery was fully automatic: the lowest rung of the recovery ladder worked exactly
as designed and no human had to do anything. One database node with a genuine history of
corrupting on ungraceful restarts was **specifically checked** for that exact log signature
rather than assumed fine. It was clean.

**Badly.** An entire tier had no monitoring, and nobody had inventoried a physical fact that
was cheap to check and turned out to be load-bearing. See why 3 and 4 above.

**Lucky.** The one node that stayed up did so because of a battery nobody knew was there, and
that is luck, labelled as luck, not resilience. The sysfs reading of `100%` is *relative to
that battery's own degraded maximum*; real-world experience is that it bridges for **a few
minutes**, not hours. This outage fit inside that margin. A longer one would not have. I have
not found a timed test of the real bridge time, so I treat it as never measured. Absence of a
record is not proof that none was run, but it is all I have.

After the September rebuild the count changed, and I only know the count, not what it means:
**two of the three** current control-plane seats report a battery device (measured 9 October
2026, from the host metrics), where on the day it was one of three. The percentage those
batteries report is, again, relative to their own degraded maximum and says nothing about how
long they bridge. Nobody has timed either.

---

## What was actually changed

| Action | Owner | Tracked as | Status, checked {{ checked }} |
|---|---|---|---|
| Wire the state store into the metrics stack, with quorum alerting | Me | Private gap register, priority 1 | ✅ **Closed 3 September**, 14 days later. See [Afterwards](#afterwards) |
| Restore real power protection for a control-plane seat, or accept the residual risk in writing | Me | Private gap register, priority 1 | **Open, and re-scoped.** After the rebuild two of three seats have a battery. Nobody has re-derived whether that is enough, or timed it |
| Establish why the surviving node kept power | Me | The post-mortem | ✅ Closed. It has a working, badly degraded battery. Verified directly rather than inferred |
| Establish why that node's cluster process restarted *without* the OS rebooting | Me | **Nothing yet** | **Still open.** Consistent with a brief under-voltage event, never confirmed. Left open rather than closed with a plausible guess |

*Retraction, 9 October 2026:* this page used to say "every item has a link and an owner". The
table had neither column, and in the private post-mortem the owner column was empty on all
four rows. The owner is me, on all four, and is now written down. The last row still has no
register entry, only the post-mortem, which fails the rule below in its own way: that entry
is still to be written. The monitoring row was also called "the highest-priority gap on the
register". It was priority 1, and there is a priority 0 above it.

> **"Be more careful" is not an action item.** If it has no owner and no link, it did not
> happen.

The last row is the one worth defending. It would have been easy to write "likely a brief
power sag" and close it. A plausible explanation is not an established one, and the
difference between those two is the entire discipline.

---

## Afterwards

The first row above closed on 3 September. As of 9 October 2026 the state store has
3 of 3 etcd scrape targets up and an `etcd` alert group of 15 alerting rules (13 distinct
names), none firing. Two of them: no leader for 60 seconds, and too few members for 180
seconds, both critical. Either would have fired inside a 9 minute 12 second loss, **if**
Prometheus, Alertmanager and the notification route had stayed up. That has not been tested
by taking a member down on purpose.

It also did not stay fixed by itself. A later rebuild did not restore the drop-in that
exposes the etcd metrics endpoints, and the scrape list still named a machine that had stopped
being a member. The three targets went dark and were noticed only because a scrape count
dropped. The same blind spot reopened with the next change. etcd was fine throughout. What had broken was the ability to see it.

---

## The uncomfortable part: this was the test that was never run

The platform runs a scheduled fault injector with a safety controller, and it works: pod
kills and network faults, proven end to end, soaking continuously.

*Retraction, 9 October 2026:* this page used to say the injector had "never once been pointed
at hardware" and that "nothing has ever deliberately powered off a machine". That was false,
and the site's other pages already said so. On 14 August a control-plane node was drained and
powered off by hand for cleaning, and etcd ran two of three for about eight minutes. That is
the same event as the [drain that removed its own control surface](reliability.md#the-drain-that-removed-its-own-control-surface).
That section tells the forty minutes of improvised drain and does not mention the power-off
or the eight minutes; those come from my private post-mortem of the day.
Nodes have been powered off to measure a change, as [the estate page](index.md) says, and a
[real power-off for a test](reliability.md#scheduling-by-fact-not-by-hope) took a controller down
with its target. After this incident, drills also stopped the agent process on real workers
and measured the outage.

What is still true is narrower. The **scheduled** injector only ever hits disposable pods.
A script that cuts a node's power as a drill exists, and is held at draft, unvalidated. No
drill has cut power to a control-plane member, and none has taken two at once.

So the honest framing is this: **the outage was the experiment the drills had not run, run
for real, unplanned, by the electricity company.** It passed, but "passed" means "survived a
nine-minute event with one unmeasured battery of margin", not "is known to tolerate this."

The elite tier of this platform's maturity rubric asks for failure deliberately injected and
recovery proven. It does not mention hardware or power. A power cut on a control-plane member
is the obvious reading, but that is my reading, not the rubric's wording.

A deliberate version would answer the questions this one raised and could not: how long does
a battery actually bridge? What happens at fifteen minutes instead of nine? What happens if
the survivor is the one that drops?

---

## The reliability numbers, stated exactly

Conflating these two scenarios is the most common way to overstate a recovery posture.

| Scenario | RPO | RTO |
|---|---|---|
| **A single node or storage daemon is lost** | **Storage: 0.** Every block is stored {{ s.storage.replica_size }} times, {{ s.storage.pgs_clean }} of {{ s.storage.pgs }} placement groups active and clean (as of {{ asof }}). **Databases: 0 only while commits are synchronous, and for 23 days they were not** (below) | Automatic failover, not separately timed |
| **A whole database must be restored from backup** | **≤ 5 minutes**: continuous write-ahead-log archiving, {{ s.databases.archiving_clusters }} of {{ s.databases.clusters }} clusters archiving | **About 2 minutes for one 13 MB database on 2 July**, restored into a scratch namespace and fingerprint-verified against the live copy. That is one measurement of a small database; a large one will take longer |

*Retraction, 9 October 2026:* this table used to say RPO 0 for a lost node, on the grounds that
"synchronous commit and three-way replication mean surviving copies were never behind". The
storage half held. The database half did not hold from the PostgreSQL 18 cutover on 16
September until 9 October. The cutover had silently dropped quorum-synchronous commit from the
four application and identity clusters, so the live databases were asynchronous while the docs
said RPO 0, and a primary crash could have lost the last transactions. I found it on 9
October, and at about 09:21 CEST that day gave those four clusters synchronous commit back
(any one of two standbys; `sync_state=quorum` checked on each primary), along with resource
limits and failover tolerations that went missing the same way. A guard now fails when a
successor cluster does not mirror its predecessor's settings. The two-instance clusters were
asynchronous by design and still are, so a small RPO above zero is the stated cost there. As
of {{ asof }}, {{ s.databases.synchronous_clusters }} of
{{ s.databases.clusters }} clusters report a synchronous standby right now. That count
includes the PostgreSQL 16 copies kept for rollback. The long version is in
[reliability](reliability.md#the-upgrade-that-kept-the-uptime-and-lost-the-guarantee).

On the restore time: in September I found that the repeatable drill behind the 2 July number
had three bugs, one of which compared nothing to nothing. I fixed it on 16 September, and it
now runs weekly. The last three scheduled runs (21 September, 28 September, 5 October) all
concluded success; I did not read which database each one restored, and the run time is for
the whole job, not the restore. The drill is described in
[reliability](reliability.md#restore-is-drilled-not-assumed).

And on service levels, the honest version: **there is exactly one enforced SLO, and it is not
user-facing.** It is the fault injector's recovery budget: if an injected fault has not
self-healed within 300 seconds, the system escalates loudly instead of quietly re-pausing.
Availability and latency objectives with error-budget burn-rate alerting for the user-facing
apps **do not exist yet**. The design is written down, the work is not done, and it is on the
register as an open gap rather than implied by the presence of dashboards.

---

## Why publish this one

Because the version of this site that omits it is more impressive and less true. The cluster
came back by itself, no user noticed, no data was lost, and the health checks were clean
within about twenty minutes, apart from two scheduled jobs that failed once on a DNS race and
passed on their next run. That is precisely the profile of the incidents that teach the most
and get written up the least.

> **"Ready" and "never lost quorum" are different claims**, and only one of them is checked by
> the command everyone runs.

---

## Read next

- **[High availability, audited](reliability.md)**: the full single-fault inventory this
  incident tested, including what is deliberately *not* replicated.
- **[What I'd do differently](lessons.md)**, including believing status output, repeatedly.
- **[DevSecOps, end to end](devsecops.md)**: the patching loop that had the same shape of bug.

---

<sub>Written for publication. Machines, addresses, hostnames and credential locations are
absent by construction and enforced by a guard that fails its check on any push or pull
request. As of {{ asof }} the guard's last run was
"{{ s.site.guard_last_run }}"; it is a separate workflow from the Pages deploy, so it
reports a leak rather than preventing the publish.</sub>
