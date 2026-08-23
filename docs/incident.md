---
title: One incident, in full
---

# A nine-minute quorum loss that nothing detected

![severity](https://img.shields.io/badge/severity-SEV1-critical)
![quorum](https://img.shields.io/badge/quorum%20lost-9m%2012s-critical)
![detected](https://img.shields.io/badge/detected%20by%20monitoring-no-red)
![dataloss](https://img.shields.io/badge/data%20lost-none-2EA44F)
![open](https://img.shields.io/badge/action%20items%20still%20open-2-orange)

Every other page here summarises incidents. This one is a single real post-mortem, close to
verbatim, because a summary of an incident is the part that is easy to write and the part
that teaches least.

It is also the most flattering-to-omit story on the site: the cluster survived, nobody
noticed at the time, and it would have been entirely possible to never write it down.

---

## What happened

Mains power to the whole building dropped for **under a minute**.

Two of the three control-plane nodes hard-crashed and rebooted. The third did not — for a
reason that was not established until the next day, and one part of which is *still* open.

For **9 minutes and 12 seconds**, the surviving node was the cluster state store's only
reachable member. A three-member consensus cluster needs two votes to commit a write. It had
one.

| | |
|---|---|
| **Severity** | SEV1 — "quorum lost" is a named example in this platform's own taxonomy |
| **Quorum lost** | 9m 12s, precisely — reconstructed from the surviving node's own raft peer logs |
| **Detected by monitoring** | **No.** Nothing fired. Nothing could have. |
| **How it was found** | A human felt the lights go out and asked for a status check |
| **Data lost** | None. Eight database clusters verified fully replicated afterwards |
| **User impact** | None observed — already-scheduled pods keep running without the state store |
| **Recovery** | Fully automatic, no human action, no runbook invoked |

---

## Why nothing detected it

The five-whys, shortened but not softened:

**Why did quorum drop?** Two of three members lost power simultaneously.

**Why did that leave zero fault tolerance instead of one spare?** Because — and this is the
part worth reading — **there was no design here to fail.** The third seat had been placed for
consensus tolerance, on a documented and sound rationale that says nothing whatsoever about
power. Nobody had ever decided how power loss should be survived. It simply had not been a
question anyone asked.

**Why did nobody know the fleet's real power situation?** Because nobody had checked. Two
machines turned out to have **no battery at all** — one had swelled and been physically
removed, the other's charging path had failed to the point it now runs from an external
supply. Both were correct responses to real hardware faults. Neither was written down
anywhere, because there was no inventory to write them down *in*.

**Why didn't monitoring catch the quorum loss?** Because **there was no etcd monitoring. At
all.** Not a threshold set too loosely — verified directly: zero scrape targets, zero alert
rules, zero service monitors mentioning the state store. An entire tier of the platform, and
the most important one, was invisible.

**Why did anyone find out?** A human experienced the power cut and asked. The same detection
mechanism as an earlier public-edge outage: *someone happened to look.*

---

## The correction that matters more than the incident

The first draft of this post-mortem said the topology had been **designed** around one
battery-backed node, and that this design's assumption had quietly broken.

That was checked against its own cited sources — the decision record and the inventory
comment it pointed at — and **neither mentions power or batteries at all.**

There was no power-diversity design. There was no broken assumption. There was an
**unexamined fact** that happened to matter on one particular afternoon.

> A post-mortem that invents a design in order to have something to blame is worse than no
> post-mortem, because it manufactures a false lesson and closes the question.

The real situation, once actually inventoried: of the three control-plane hosts, **exactly
one** has a battery that still works — and it is the one nobody would have guessed, because
its own hostname and earlier drafts of this document both described it as a desktop.

That single working battery is the entire reason this was a nine-minute self-healing blip
rather than a total loss with no surviving member. **That is luck, and it is labelled as luck
below, not as resilience.**

---

## What went well, badly, and where it was luck

Three separate headings on purpose. Collapsing them is how a post-mortem becomes marketing.

**Well.** Recovery was fully automatic — the lowest rung of the recovery ladder worked exactly
as designed and no human had to do anything. One database node with a genuine history of
corrupting on ungraceful restarts was **specifically checked** for that exact log signature
rather than assumed fine. It was clean.

**Badly.** An entire tier of the platform had no monitoring whatsoever — which is a worse
condition than a badly-tuned threshold, because there is nothing to tune. And nobody had
inventoried a physical fact that was cheap to check and turned out to be load-bearing.

**Lucky.** The one node that stayed up did so because of a battery nobody knew was there. And
the sysfs reading of `100%` is *relative to that battery's own degraded maximum* — real-world
experience is that it bridges for **a few minutes**, not hours. This outage fit inside that
margin. A longer one would not have, and the true bridge time has still never been measured.

---

## What was actually changed

Every item has a link and an owner. Two are still open, and are listed as open.

| Action | Status |
|---|---|
| Wire the state store into the metrics stack, with quorum alerting | **Open** — the highest-priority gap on the register |
| The control plane's assumed power diversity is false. Either restore real protection for one seat, or explicitly accept the residual risk in writing | **Open** |
| Establish why the surviving node kept power | ✅ Closed — it has a working, badly degraded battery. Verified directly rather than inferred |
| Establish why that node's cluster process restarted *without* the OS rebooting | **Still open.** Consistent with a brief under-voltage event, never confirmed. Left open rather than closed with a plausible guess |

> **"Be more careful" is not an action item.** If it has no owner and no link, it did not
> happen.

That last row is the one worth defending. It would have been easy to write "likely a brief
power sag" and close it. A plausible explanation is not an established one, and the difference
between those two is the entire discipline.

---

## The uncomfortable part: this was the test that was never run

The platform runs a scheduled fault injector with a safety controller, and it works — pod
kills and network faults, proven end to end, soaking continuously.

**It has never once been pointed at hardware.** Every fault class targets a disposable pod.
Nothing has ever deliberately powered off a machine, let alone two at once. The elite tier of
this platform's own maturity rubric names exactly that as the bar.

So the honest framing is this: **the outage was the hardware chaos experiment, run for real,
unplanned, by the electricity company.** It passed — but "passed" means "survived a
nine-minute event with one unmeasured battery of margin," not "is known to tolerate this."

A deliberate version would answer the questions this one raised and could not: how long does
that battery actually bridge? What happens at fifteen minutes instead of nine? What happens if
the survivor is the one that drops?

---

## The reliability numbers, stated exactly

Since an incident page invites the question, and since conflating these two is the most common
way to overstate a recovery posture:

| Scenario | RPO | RTO |
|---|---|---|
| **A single node or storage daemon is lost** | **0** — synchronous commit and three-way replication mean surviving copies were never behind | Automatic failover, not separately timed |
| **A whole database must be restored from backup** | **≤ 5 minutes** — continuous write-ahead-log archiving | **~2 minutes, measured on a real drill**, not estimated — restored into a scratch namespace and fingerprint-verified against the live copy |

And on service levels, the honest version: **there is exactly one enforced SLO, and it is not
user-facing.** It is the fault injector's recovery budget — if an injected fault has not
self-healed within 300 seconds, the system escalates loudly instead of quietly re-pausing.

Availability and latency objectives with error-budget burn-rate alerting for the user-facing
apps **do not exist yet**. The design is written down, the work is not done, and it is on the
register as an open gap rather than implied by the presence of dashboards.

---

## Why publish this one

Because the version of this site that omits it is more impressive and less true.

The cluster came back by itself. No user noticed. No data was lost. Every dashboard was green
within twenty minutes, and nobody would ever have known — which is precisely the profile of
the incidents that teach the most and get written up the least.

> **"Ready" and "never lost quorum" are different claims**, and only one of them is checked by
> the command everyone runs.

---

## Read next

- **[High availability, audited](reliability.md)** — the full single-fault inventory this
  incident tested, including what is deliberately *not* replicated.
- **[What I'd do differently](lessons.md)** — including believing status output, seven times.
- **[DevSecOps, end to end](devsecops.md)** — the patching loop that had the same shape of bug.

---

<sub>Written for publication. Machines, addresses, hostnames and credential locations are
absent by construction and enforced by a guard that fails the build.</sub>
