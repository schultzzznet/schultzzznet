---
title: Why these tools, and what got rejected
reread: 2026-11-11
body_read: 2026-11-11
summary:
  - "**What it is:** for each tool, why it and not the obvious alternative, in three lists: *deferred*, *rejected on principle* (no cloud-only analysis services; the cloud AI models are a deliberate exception) and *rejected on right-sizing* (a named condition would change the answer). A rejection without a reopen-trigger is just an opinion."
  - "**Two triggers fired and were acted on:** GitOps (Flux, installed 2026-11-10, decided early; reconciling since then; the live Ready count is on the [status page](status.html)) and policy admission (Deny rules live since 2026-11-10). Both are about a day old on the new platform: not yet seen working over time."
  - "**Storage changed:** V1.0's replicated storage is gone; the new one has node-local storage only, and backups go to a small object store on one machine (one copy). A reviewed trade, not a hidden one."
  - "**Still open:** tracing is deployed but no trace has been read, encryption of secrets inside the cluster is configured but not read back, a service mesh is deferred, and a probe on 2026-11-10 found a 1 to 3 second window at pod start with everything open (the record's result is fail)."
---



# Choices — including the ones that were wrong, and the ones that are debts

![k3s nodes](https://img.shields.io/badge/k3s%20nodes-6-1A5276)
![right-sizing rejections with a reopen trigger](https://img.shields.io/badge/right--sizing%20rejections%20with%20a%20reopen%20trigger-all%20four%2C%20one%20reopened%2024%20Oct%202026%20and%20decided%2010%20Nov-2EA44F)

{% include in-short.html %}

*Written by hand. On 11 November 2026 the GitOps, admission, network, storage, database, tracing and secrets rows were re-read against the new platform (brought up on 10 to 11 November 2026, so about a day old: nothing here implies uptime). Figures here were read by hand from the live cluster on 11 November 2026; the [generated stats](status.md) are being regenerated for the new platform. Statements about V1.0 (retired on 10 November 2026) are kept, labelled and dated, because a decision log with its history cut out proves nothing. Anything else that is a snapshot says so where it appears.*

Every other page here says *what* is running. This one says *why that and not the obvious
alternative* — which is the question an experienced reader actually has, and the one most
write-ups skip because the honest answer is sometimes "because I already knew it."

Three lists, and the distinction between them is the whole point:

| List | Ruled out by | What changes it |
|---|---|---|
| **Deferred** | Not needed *yet* | The need arriving |
| **Rejected on principle** | A standing constraint | Nothing — the constraint is the design |
| **Rejected on right-sizing** | Current evidence | A named, written-down trigger |

> **A rejection without a reopen-trigger is just an opinion.** Every entry in the third list
> has a "Reopen if" column, and that column is what makes it a decision. If you can't state
> the condition, you haven't made a decision — you've expressed a preference.

> **Corrections, 9 October 2026.** An audit of this page against the live system found five
> things I had stated and should not have. The badge above used to say that *all* rejections
> had a reopen trigger; only one did, and the third list held a single entry. I wrote that
> the networking engine could not enforce policy; it can (below). I gave the wrong reason for
> not using Longhorn (below). I said the orchestrator was wrong "for a year"; it was about
> half of one. And I said drift was *monitored*; it was checked on demand (and, since 24 October, daily). Each is fixed where
> it appeared.

---

## The orchestrator, and the one that was wrong

| | |
|---|---|
| **In use** | **k3s** — 3 embedded-etcd servers and 3 agents, 6 nodes in all (read 2026-11-11). The new platform, built on 10 to 11 November 2026, chose k3s again with the same 3 + 3 shape. |
| Retired | **Docker Swarm** |
| Considered | upstream Kubernetes (kubeadm), k0s, MicroK8s, Nomad |

The platform ran on **Docker Swarm first**, for roughly 170 days from the first commit on
21 December 2025 to its decommissioning on 9 June 2026, and that was the wrong foundation —
covered at length in [what I'd do differently](lessons.md). What ended it was not a failure
but a ceiling: no operator pattern, no CRDs, no admission webhooks, so no database operator,
no storage operator, no policy tooling.

The alternatives, each in one line:

- **kubeadm / upstream Kubernetes** — ops cost exceeded the learning value at this scale.
- **k0s** — genuinely comparable to k3s. Bundled ingress and the backing organisation tipped
  it; this could have gone either way and I would not argue with someone who picked k0s.
- **MicroK8s** — snap-only, awkward across the mixed distributions on this hardware.
- **Nomad** — an *excellent* fit for this scale, and rejected for a reason that is honest
  rather than technical: the goal was fluency in the ecosystem the industry actually runs, and
  that ecosystem is Kubernetes. Nomad would likely have been less work and taught less.

---

## Networking and network policy: no longer a gap

**Flannel with the WireGuard backend** is the CNI on the new platform (built for anything beyond basic traffic: the encryption between nodes was configured, and a packet capture to prove it has not been done). It is IPv4-only, which is why every kubelet is pinned to an IPv4 node address.

Flannel on its own enforces nothing, but **k3s bundles a NetworkPolicy controller of its own**, and that is what enforces policy here. **Status, 11 November 2026: in use.** The cluster holds 27 NetworkPolicy objects, with a default-deny per tenant namespace and explicit allows on top (counts read from the API on 11 November 2026). Whether each allow is minimal is not audited, and a deny proven on V1.0 does not transfer. On the new one a live probe on 2026-11-10 showed **steady-state blocking**: once a pod had been up about 30 seconds, cross-namespace connections to the database and connections to off-list ports and machines were refused, while the allowed route worked. The same probe found that for about **1 to 3 seconds after a pod starts, everything is open**, and the probe's recorded result is **fail** because of that gap. Not proven: default-deny from the first packet, denial of ingress from outside the cluster, and limits on DNS egress. Treat it as **built**.

There is one measured cost. With default-deny, a new pod's first connections can fail for about 1 to 3 seconds while the controller programs its rules. Two candidates would shorten that, and **neither has been tested**: a **Cilium** CNI (eBPF datapath, richer policy and runtime visibility; a rebuild-level change), or an init-time wait in the pod that holds start-up until the rules exist.

**V1.0 (until 2026-11-10).** On 9 October 2026 V1.0 had 0 NetworkPolicy objects, and this page said so after first wrongly claiming the CNI could not enforce policy at all. The technology was never the gap; the missing policy was. That correction stays because segmentation is exactly the kind of gap a hardened stack can hide behind.

---

## Storage: the plan that changed twice, and a supply chain that moved under us

| | |
|---|---|
| **In use (11 November 2026)** | **The node-local default class only** (1 storage class in the cluster, marked default, read 2026-11-11). Volumes live on one machine's disk. |
| Backup object store | **Garage**, on a small always-on Mac: one machine, one copy. Chosen on 2026-11-07 by a head-to-head spike against the alternatives. |
| V1.0 (until 2026-11-10) | **Rook-Ceph** with replicated block storage, and **MinIO** as the object store |
| Rejected earlier | **Longhorn** |

**The trade, stated plainly.** The new platform does not replicate storage underneath the workloads. Replication is left to the database layer (database instances stream to each other), and everything else on a node-local volume is lost with its node unless it is backed up or rebuildable. That was a reviewed decision, not an oversight: a replicated storage tier was the most expensive thing on V1.0 to run and to reason about. The consequence is real. The backups sit on one small machine, so today there is **one copy**, and a restore from it was drilled once on 2026-11-10 (a scratch database built from the object store alone had its marker row and tables back, after temporary network rules were added because default-deny also blocks the recovery job), but a loss of that machine is not covered (status 11 November 2026: **open**).

**V1.0 (until 2026-11-10), kept as history.** Longhorn was the original plan and was installed on 9 June 2026, then reverted the same day: three of the five nodes then had a ZFS root, and ZFS cannot punch holes in a file, which Longhorn's replicas require. Loopback-file Ceph OSDs worked on the same disks. The decision that mattered more than the product choice was **removing the single-node provisioner entirely**, so an unqualified claim could never silently pin itself to one machine's disk. The new platform reverses that decision on purpose and knows it.

**And the uncomfortable one, which is why MinIO is a row of history.** MinIO's upstream community repository was **archived in April 2026**: source-only, no further binary releases, no security updates. That was found during a routine dependency review, not announced by anything, and it turned a migration into live work. Garage is the answer on the new platform; the head-to-head spike is the evidence, and the object store has run for about a day, so it is **built; not seen over time**.

> Supply-chain risk is not only "is this version vulnerable." It is also "is anyone still
> shipping fixes for it," and nothing in a CVE scanner asks that question.

---

## Databases, where the boring answer was right

**PostgreSQL**, always. **CloudNativePG** to operate it — one custom resource per cluster,
the operator handles failover and the read-write service always points at the current primary.
On 2026-11-11 the new platform ran 1 cluster with 3 instances (read from the API) (V1.0 ran thirteen clusters; the application set is smaller so far, and that is not a like-for-like comparison). The operator is unchanged. Backups use the operator's **barman-cloud plugin**, which writes to the object store above (installed and running on 11 November 2026; one restore drill passed on 2026-11-10; see [reliability](reliability.md)).

"One resource per cluster" cuts both ways, and I should say so. **V1.0, 2026-09 to 2026-10:** when the application and
identity clusters moved to PostgreSQL 18 on 16 September 2026, the cutover silently dropped
their quorum-synchronous commit, their resource limits and their failover tolerations. For
23 days the live databases were asynchronous while this site said otherwise. They were
restored on 9 October 2026 and a guard now fails when a successor cluster stops mirroring its
predecessor. The two-instance clusters are asynchronous by design. The details are in
[high availability, audited](reliability.md).

Considered and passed on: **Patroni on Kubernetes** (works, but a meaningfully rougher
interface than a single CR), the **Zalando operator** (excellent and older; lost on
documentation and velocity), **MySQL/MariaDB** (no reason to run a second relational engine),
and **MongoDB** (JSONB covers the document use cases). Redis is in the right-sizing table
below.

One retired: **Patroni**, the pre-Kubernetes database topology, which was retired with the
orchestrator rather than swapped out on its own.

---

## Deferred — needed eventually, not yet

| Topic | Candidate | Why not yet |
|---|---|---|
| Service mesh | Linkerd / Istio | No need for mTLS between pods or fine-grained traffic policy. Linkerd wins on day-one cost when that changes. |
| **Secrets** | SOPS + age — **not Vault** | **Done in git, 2026-11-11 status.** Secrets are encrypted in git with SOPS and age, and a check fails any new plaintext Secret. Vault is overkill for a handful of secrets and would itself become a thing to operate. *Inside the cluster:* encryption of secrets at rest in etcd is **configured but not read back**, so this page does not claim it. Rotation of the old values is open. |
| Backups beyond Postgres | Velero | **Unchanged: not used.** Velero matters when *generic* volume backup does, and the rule stays: only what nobody else holds. Caches re-download. |
| Tracing | OpenTelemetry + Tempo | **Tempo picked and deployed (a pod runs, 2026-11-11); no trace has been read, and the collector is still not deployed.** Built. The monitoring tenant that would show it was merged on 2026-11-11; its first run failed on a missing-namespace defect, the fix landed the same day, and at 07:00 UTC on 2026-11-11 its pods were Running; nothing from it has been read. |

**Policy admission was in this table until 2026-11-10.** It is no longer deferred: **Kyverno is live, with rules set to Deny** (since 2026-11-10; status: built, about a day old). The old sentence calling it the highest-leverage next security step is history now, kept in the V1.0 note under the quality page's gaps. What is proven: the policies exist and are enforcing. What is not: that every rule has had a negative test on this cluster, and signature-required-at-admission is only as good as the rule set behind it.

The secrets row is the one worth dwelling on: it is named
in [what this does not do](devsecops.md#7-what-this-does-not-do), because it is the recurring
root cause behind a whole class of placeholder-credential defects. Writing it down twice is
deliberate.

---

## Rejected on principle — cloud-only

A standing constraint: **no third-party analysis service gets source, telemetry or
repository access beyond the git host itself.** The code is on GitHub and always has been;
what the constraint rules out is handing it to a SaaS scanner on top of that. The cloud AI models are the deliberate exception: they read the code at development time and a day's alert text at run time, on purpose ([AI in development](ai-dev.md), [operations](aiops.md)).
Several of the products below are genuinely excellent. The right-hand column mixes what V1.0 did with what the new one does, and says which. That is not the deciding factor, and
the list exists to make the constraint explicit rather than to disparage them.

Where a row says "idea worth stealing", that is the whole verdict: take the idea, build or
self-host it.

| Candidate | What is done instead |
|---|---|
| **Aikido Security** (all-in-one AppSec) | **V1.0 (until 2026-11-10):** every scanner in its free tier ran self-hosted, aggregated into one findings tracker. Both the scanners and the tracker are gone with that platform, and **not rebuilt yet**. What stands on the new platform (11 November 2026): secret scanning with Gitleaks in the pre-commit and CI path, signing, and admission rules. Planned, not built: vulnerability scanning of images and dependencies, and an inventory of components. |
| **Socket.dev** (malicious packages) | Idea worth stealing: detect *malicious* rather than merely vulnerable packages. Watch the open malicious-package feeds instead (planned). |
| **Endor Labs** (reachability-based SCA) | Idea worth stealing: only alert on CVEs on code paths actually executed. A noise-reduction concept to watch for in open tooling. |
| **GitGuardian** (secret scanning) | The valuable half, *validity-checked* secrets, exists in open tooling (TruffleHog). Rated trial and **not running**; what runs is Gitleaks. |
| **StackHawk · Escape · 42Crunch** (DAST / API) | Spec-driven testing in-house: the contract fuzzer against the reference app's OpenAPI document runs in the pipeline's local-cluster gate (see [quality](quality.md)). |
| **Wiz · Sysdig · Datadog** (runtime / cloud security) | Agent-based and cloud-only. The open equivalent was deferred until there is something to triage the output. |
| **Snyk · Black Duck** (commercial SCA) | The open tooling that covered this on V1.0 is gone; the replacement is **planned, not built**. A gap, stated as one. |

> **A cloud-only scanner or analysis service can inspire something built or self-hosted here. It can never be
> adopted.** That is a design input, not a limitation to apologise for — but it does mean
> accepting that some capabilities arrive later and rougher than they would with a credit card.

---

## Rejected on right-sizing — good software, wrong problem

The hardest list to be honest about, because these are self-hostable, well-built and
genuinely standard. Trying any of them to learn it is free; keeping one running because it is what serious platforms use is
cargo-culting. The question for keeping is whether the problem is *observed here*. Each row names what
would change the answer. Only the ArgoCD / Flux trigger was written down before 9 October
2026; I stated the KEDA and VPA ones that day, from the reasons already given, and the VPA one is the weakest. **The first row has since changed side**, which is the point of having a trigger.

| Candidate | Why not here | Reopen if |
|---|---|---|
| **ArgoCD / Flux** | **Chosen: Flux, installed on the new platform on 2026-11-10 (partly reconciling on 2026-11-11).** Originally rejected: it solved multi-team drift and pull-based reconciliation, and neither existed at one-maintainer scale. | ~~A second maintainer joins, or manifests are observed drifting from git~~ Fired on 24 October 2026; decision date of 2026-12-01 was met early. See below. |
| **KEDA** | Would be a permanently-running component watching a metric that does not exist. | There is a real queue to scale on |
| **VPA** | Fights the HPA on the same metric unless carefully partitioned; requests are hand-tuned instead. | Something other than CPU drives scaling, so the two stop competing |

A fourth row, **Redis**, is gone: nothing of mine needed a cache or queue, and on the new platform no Redis-family service runs at all (11 November 2026). The one that did, bundled with a findings tracker on V1.0, left with it.

Autoscaling today is a **HorizontalPodAutoscaler** on CPU, two to four replicas on each of
the 2 that exist (cluster DNS and the reference app, read from the API on 2026-11-11): native, no extra component, and CPU is the honest signal for
these services. There is no cluster-autoscaler analogue, because the fleet is
6 fixed machines. Scale-out only. A platform that cannot add nodes should say so
rather than imply elasticity it does not have.

### The worked example: ArgoCD and Flux, a reopened decision

The case against was: deployment is already declarative and reproducible from nothing, and a drill proves configuration comes back from git. A reconciler would add a second source of truth and a permanently-running component.

> **Reopen if:** a second maintainer joins, **or** manifests are ever observed drifting from
> git. *(Written 9 October 2026.)*
>
> **History, V1.0:** drift was observed repeatedly with a cost each time, and on
> 24 October 2026 the decision was reopened in four stages: *detect* (a daily read-only diff),
> *secrets in git* (25 October), *roll out from git on merge* (Flux by default, decision date
> 2026-12-01), *the imperative steps* (later).
>
> **Outcome, 2026-11-10: chosen and installed.** Flux runs on the new platform, **pull-based, with prune on**. The reason that decided it was not drift this time: the home network sits behind carrier-grade NAT, so there is **no inbound path** for a push-based deploy to reach the cluster, and a reconciler inside the cluster that pulls from git needs none. Revert and prune were shown on a local rehearsal cluster before the real one. Status: **built**, about a day old, not yet seen working over time. The live count of Ready Kustomizations changes with every merge, so it is on the [status page](status.html). The one failure I saw on 2026-11-11 was the new monitoring tenant. The decision date of 2026-12-01 was met three weeks early. The older account is on [the delivery-chain page](platform.html#how-a-change-reaches-the-cluster).

That trigger is the part that makes this a decision rather than a preference: when the
question comes back, it is a lookup instead of a fresh argument.

---

## What this page is really arguing

Not that these choices are correct. Several are contested, one is a live risk, one was the
wrong foundation for its first half-year and shipped anyway, and a few of my stated reasons
turned out to be wrong too. The argument is that **each of them is explainable, and each
rejection says what would change it.** A stack you can only defend by listing what it
contains is a stack you have not actually chosen.

DHH, right-sizing in the opposite direction on the same question:

> *When we moved out of the cloud, I spent months getting Kamal off the ground, so we
> didn’t have to get mired in the complexity of Kubernetes.*
> — DHH, [A pond of interesting problems](https://world.hey.com/dhh/a-pond-of-interesting-problems-5f697567) (June 2026)

This site went the other way — Kubernetes complexity was accepted, because the learning value
at this scale is the entire reason the platform exists. Same principle; different evidence;
different answer. That is what a reopen trigger is for.

---

## Read next

- **[What I'd do differently](lessons.md)** — where several of these choices are re-examined
  with hindsight, including the orchestrator.
- **[DevSecOps, end to end](devsecops.md)** — what the security half of this stack actually
  proves, and where the measurements were wrong.
- **[High availability, audited](reliability.md)** — the storage and database choices under
  real failure.
- **[Live status](status.md)** — the generated figures this page draws on.

---

<sub>Written for publication. Machines, addresses, hostnames and credential locations are
absent by construction and enforced by a guard that fails the build.</sub>
