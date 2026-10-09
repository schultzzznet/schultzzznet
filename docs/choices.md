---
title: Why these tools, and what got rejected
---

{% assign s = site.data.stats %}
{% assign gen = s.generated_at | date: "%-d %B %Y" %}

# Choices — including the ones that were wrong, and the ones that are debts

![k3s nodes](https://img.shields.io/badge/k3s%20nodes-{{ s.cluster.nodes }}-1A5276)
![ceph replicas](https://img.shields.io/badge/ceph%20replicas-{{ s.storage.replica_size }}-326CE5)
![right-sizing rejections with a reopen trigger](https://img.shields.io/badge/right--sizing%20rejections%20with%20a%20reopen%20trigger-all%20four%2C%20three%20stated%209%20Oct%202026-2EA44F)

*Written by hand and last reviewed on 9 October 2026. Figures rendered from the
[generated stats](status.md) are as of {{ gen }}. On that day I also re-read the node
topology, the storage class, the autoscalers and the NetworkPolicy count from the cluster;
the rest, including the secrets-at-rest and self-hosted-scanner statements, rests on the
earlier audit and the repository, not on a live check. Anything else that is a snapshot says
so where it appears.*

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
> half of one. And I said drift was *monitored*; it is checked on demand. Each is fixed where
> it appeared.

---

## The orchestrator, and the one that was wrong

| | |
|---|---|
| **In use** | **k3s** — {{ s.cluster.control_plane }} embedded-etcd servers and {{ s.cluster.agents }} agents, {{ s.cluster.nodes }} nodes in all (as of {{ gen }}) |
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

## The networking caveat, and the premise I had wrong

**Flannel (VXLAN)**, the bundled CNI, kept because it works on a mixed-hardware LAN with no
tuning. It is IPv4-only, which is why every kubelet is pinned to an IPv4 node address.

I believed this meant the cluster had no way to enforce network policy. That was wrong.
Flannel on its own enforces nothing, but **k3s bundles a NetworkPolicy controller of its own**
and the install never disables it. I have not tested that it blocks anything, because there
is nothing to test it with:

> **The cluster has 0 NetworkPolicy objects** (read from the API on 9 October 2026).
> Pod-to-pod traffic is unrestricted because I have not written a policy, not because the
> technology cannot enforce one. The first step is to write default-deny policies per
> namespace and prove one blocks something, not to swap the CNI.

A CNI swap to **Cilium** (eBPF datapath, richer policy, runtime visibility in the same
family) is still a rebuild-level change on a running cluster, and would now be justified by
those extras rather than by a gap that was never there. This section stays on the page
because segmentation is exactly the kind of gap a stack this otherwise-hardened can hide
behind, and because I was confidently wrong about its cause.

---

## Storage: the plan that changed, and a supply chain that moved under us

| | |
|---|---|
| **In use** | **Rook-Ceph**, block mode, {{ s.storage.replica_size }}-way replication — the *sole* storage class (as of {{ gen }}) |
| Rejected | **Longhorn** — the original plan |
| Future | **Ceph RGW**, to collapse two systems into one |

Longhorn was the plan, and it was installed. On 9 June 2026 it went in cleanly (every pod up,
a test volume bound with three replicas) and was reverted the same day. Three of the five
nodes then had a ZFS root, and ZFS cannot punch holes in a file, which Longhorn's replicas
require; every replica that landed on one of them faulted. Loopback-file Ceph OSDs need only
plain allocation, worked on the same disks, and cost nothing. So the reason was a blocker I
hit, not a preference I reasoned my way to.

The decision that mattered more than the product choice was **removing the single-node
provisioner entirely**. An unqualified volume claim now lands on replicated Ceph, because
that class is the default, and it can never silently pin itself to one machine's disk.
Delete the unsafe default rather than documenting it.

**And an uncomfortable one, because it is the kind of thing that gets left out:** the object
store in use is **MinIO**, and its upstream community repository was **archived in April
2026**. Source-only, no further binary releases, no security updates, with upstream pointing
at a commercial product instead. That was found during a routine dependency review, not
announced by anything.

It converts a "nice-to-have someday" migration — Ceph's own S3 gateway, which would remove
MinIO rather than replace it — into a live piece of work. It is on the register, it is not
done, and the honest status is *known risk, accepted for now, with a named replacement*.

> Supply-chain risk is not only "is this version vulnerable." It is also "is anyone still
> shipping fixes for it," and nothing in a CVE scanner asks that question.

---

## Databases, where the boring answer was right

**PostgreSQL**, always. **CloudNativePG** to operate it — one custom resource per cluster,
the operator handles failover and the read-write service always points at the current primary.
As of {{ gen }} that is {{ s.databases.clusters }} clusters and {{ s.databases.instances }} instances.

"One resource per cluster" cuts both ways, and I should say so. When the application and
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
| **Secrets at rest** | SOPS + age, or sealed secrets — **not Vault** | **Genuinely sub-baseline today**: plaintext base64 in cluster secrets. The fix should be the *lightest* self-hosted option; Vault is overkill for a handful of secrets and would itself become a thing to operate. |
| Policy admission | Kyverno / OPA / sigstore policy controller | Worth doing once there is one hard rule worth enforcing — and there is: **signature-required at admission**. Signatures are verified in CI but are not yet load-bearing at deploy time. Highest-leverage next security step. |
| Backups beyond Postgres | Velero | No longer "the database tier is the only stateful tier": the OTA release store and the build host's signing keys now have purpose-built backups, each with a restore drill (see [reliability](reliability.md#restore-is-drilled-not-assumed)). Velero matters when *generic* volume backup does — and the rule stays the same: only what nobody else holds. Caches re-download. |
| Tracing | OpenTelemetry + Tempo | The collector has to land before instrumenting applications is worth anything. |

The secrets row is the one worth dwelling on: it is listed in the deferred table *and* named
in [what this does not do](devsecops.md#10-what-this-does-not-do), because it is the recurring
root cause behind a whole class of placeholder-credential defects. Writing it down twice is
deliberate.

---

## Rejected on principle — cloud-only

A standing constraint: **no third-party analysis service gets source, telemetry or
repository access beyond the git host itself.** The code is on GitHub and always has been;
what the constraint rules out is handing it to a SaaS scanner or agent on top of that.
Several of the products below are genuinely excellent. That is not the deciding factor, and
the list exists to make the constraint explicit rather than to disparage them.

Where a row says "idea worth stealing", that is the whole verdict: take the idea, build or
self-host it.

| Candidate | What is done instead |
|---|---|
| **Aikido Security** (all-in-one AppSec) | Every scanner in its free tier already runs self-hosted, aggregated into one findings tracker, plus signing and provenance it does not offer. Its OSS in-app firewall is the one genuinely different piece, and *is* self-hostable, so it is tracked separately. |
| **Socket.dev** (malicious packages) | Idea worth stealing: detect *malicious* rather than merely vulnerable packages. Watch the open malicious-package feeds instead. |
| **Endor Labs** (reachability-based SCA) | Idea worth stealing: only alert on CVEs on code paths actually executed. A noise-reduction concept to watch for in open tooling. |
| **GitGuardian** (secret scanning) | The valuable half, *validity-checked* secrets, exists in open tooling (TruffleHog). That is rated trial and **not running yet**; what runs today is Gitleaks plus a custom sweep. |
| **StackHawk · Escape · 42Crunch** (DAST / API) | Spec-driven scanning done in-house against the OpenAPI documents the services already emit. |
| **Wiz · Sysdig · Datadog** (runtime / cloud security) | Agent-based and cloud-only. The open equivalent was deferred until there was something to triage the output — which now exists. |
| **Snyk · Black Duck** (commercial SCA) | Covered by open tooling, which additionally re-analyses *already-shipped* inventories against new advisories. |

> **A cloud-only tool can inspire something built or self-hosted here. It can never be
> adopted.** That is a design input, not a limitation to apologise for — but it does mean
> accepting that some capabilities arrive later and rougher than they would with a credit card.

---

## Rejected on right-sizing — good software, wrong problem

The hardest list to be honest about, because these are self-hostable, well-built and
genuinely standard. Adopting a tool because it is what serious platforms use is
cargo-culting; the question is whether the problem is *observed here*. Each row names what
would change the answer. Only the ArgoCD / Flux trigger was written down before 9 October
2026; I stated the KEDA, VPA and Redis ones that day, from the reasons already given. They
are decisions from that date, not older ones, and the VPA one is the weakest of the four.

| Candidate | Why not here | Reopen if |
|---|---|---|
| **ArgoCD / Flux** | Solves multi-team drift and pull-based reconciliation; neither exists at one-maintainer scale. See below. | A second maintainer joins, or manifests are observed drifting from git |
| **KEDA** | Would be a permanently-running component watching a metric that does not exist. | There is a real queue to scale on |
| **VPA** | Fights the HPA on the same metric unless carefully partitioned; requests are hand-tuned instead. | Something other than CPU drives scaling, so the two stop competing |
| **Redis** | None of my own services needs a cache or queue. The only one running is Valkey, bundled as DefectDojo's task queue. Adding one in advance is how a platform accumulates components nobody understands. | An application of mine has a cache or queue workload |

Autoscaling today is a **HorizontalPodAutoscaler** on CPU, two to four replicas on each of
the {{ s.cluster.hpas }} that exist (as of {{ gen }}): native, no extra component, and CPU is the honest signal for
these services. There is no cluster-autoscaler analogue, because the fleet is
{{ s.cluster.nodes }} fixed machines. Scale-out only. A platform that cannot add nodes should say so
rather than imply elasticity it does not have.

### The worked example: ArgoCD and Flux

Deployment is already declarative and reproducible from nothing, and there is a drill that
*proves* configuration comes back from git — the same guarantee, demonstrated more simply.
A reconciler would add a second source of truth and a permanently-running component.

> **Reopen if:** a second maintainer joins, **or** manifests are ever observed drifting from
> git. Both are checkable on demand (`make helm-drift`, `make iac-coverage`). Neither runs
> continuously, and that is the honest remaining gap: an arbitrary edit made by hand is not
> caught until someone asks.

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
