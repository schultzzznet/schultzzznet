---
title: What I'd do differently
---

# What I'd do differently

![decisions](https://img.shields.io/badge/decision%20records-33-1A5276)
![reversed](https://img.shields.io/badge/reversed%20on%20evidence-6-orange)
![rebuilt](https://img.shields.io/badge/full%20cluster%20rebuilds-2-326CE5)

Every other page here describes something that works. This one is the list of things that
were wrong on the way, several of which are still visible in the system today. It is the
page I would want to read about someone else's platform, and the one most projects don't
write — a "what we learned" section that names no mistakes is marketing.

The rule for what goes on this page: it has to have **cost something**, and the cost has to
be describable. Regret without a number attached is just modesty.

---

## 1. Starting on the wrong orchestrator — and why I'd do it again

The platform's repository is still called `the-docker-swarm-ai`. It has run Kubernetes for
most of its life. That name is a fossil of the first real architectural decision, and the
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

### Update: this one got acted on — the cluster is now six

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
control-plane member, and both all-in-ones were then retired behind it, leaving **six**. So it
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

Replicated block storage across three nodes was the correct decision and I would make it
again. The **sequencing** was wrong.

It went in *after* several stateful workloads were already running on single-node local
volumes, which meant a migration under load rather than a clean start — and, worse, a period
where "the storage is replicated" was true of some volumes and not others. That is precisely
the ambiguous half-state this platform is otherwise built to avoid.

**The fix that mattered** was not the migration itself but making the wrong thing impossible
afterwards: the single-node storage provisioner is now **switched off entirely**, so an
unqualified volume claim fails loudly instead of silently pinning itself to one machine's
disk. That is the pattern worth stealing — *remove the unsafe default rather than
documenting it.*

**What I'd do differently:** storage first, before anything stateful. It is the one layer
that is genuinely painful to retrofit, and every hour spent getting it right up front is
repaid the first time a node dies.

---

## 4. Three OSDs is a number that looks like resilience

Related, and sharper. Three storage nodes with three-way replication sounds robust. It is
not what most people assume it is.

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
states in the tracker from the very first automation, not as a lesson learned seven times.
Every scheduled thing should ship with a `last-fired` signal *and* an alert on its absence —
and the alert on absence has to be written **before** the thing is called done, because
afterwards there is never a reason to go back and add it.

---

## 6. Two sources of truth, every single time

Node labels lived in a provisioning playbook *and* in the inventory the playbook was
supposed to read from. They drifted apart on a third of the fleet, silently, and nothing
compared them.

The fix was to **delete one**, not to reconcile them. Same story with the public-path
allowlist, which is stated in the edge config and in the scanner's classifier — except that
one is deliberate, and a verifier fails the build when they disagree.

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

Six reversals in the visible history. The number is low because most wrong ideas die before
they are written down; it is not zero because the ones that survive long enough to be
written down are worth keeping visible.

---

## 8. What I'd keep, unchanged

Shorter list, and the reason the rest was survivable:

- **Making rebuilding cheap.** The entire cluster has been wiped and rebuilt from scratch
  twice. That is only tolerable because it is an afternoon, and it is an afternoon because
  everything is a derivative of a git repository. **Being wrong stopped being expensive**,
  which is what made it possible to be wrong usefully.
- **Writing down decisions with their alternatives.** Thirty-odd decision records, several of
  which have been reversed *by referring back to them* — including one that corrected a
  claim about why an earlier decision had been made, which turned out to be unsupported by
  the record it cited.
- **Refusing to round numbers up.** Four of thirteen failure domains are genuinely
  single-fault tolerant. Publishing "four" instead of a nicer figure is why the other nine
  are tracked instead of forgotten.
- **Pruning the backlog on purpose.** Thirty-four of fifty-nine open items were closed in one
  pass — some done, some obsolete, and nine as **won't-do**, each with a reason. Deciding
  what will never be done is the judgement call that keeps a register from becoming a guilt
  pile.

---

## Read next

- **[High availability, audited](reliability.md)** — the inventory these lessons came out of.
- **[DevSecOps, end to end](devsecops.md)** — the measurement traps, in more detail and with
  the code.
- **[`examples/`](https://github.com/schultzzznet/schultzzznet/tree/main/examples)** — four
  of these lessons, extracted as runnable artifacts.

---

<sub>Written for publication. Machines, addresses, hostnames and credential locations are
absent by construction and enforced by a guard that fails the build.</sub>
