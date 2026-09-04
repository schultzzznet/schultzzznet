---
title: Why these tools, and what got rejected
---

# Choices — including the ones that were wrong, and the ones that are debts

![in use](https://img.shields.io/badge/tools%20in%20use-40%2B-1A5276)
![rejected](https://img.shields.io/badge/rejected%20with%20a%20reason-20%2B-orange)
![reopen](https://img.shields.io/badge/rejections%20with%20a%20reopen%20trigger-all-2EA44F)

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
> names the condition that would change the answer. If you can't state that condition, you
> haven't made a decision — you've expressed a preference.

---

## The orchestrator, and the one that was wrong

| | |
|---|---|
| **In use** | **k3s** — three embedded-etcd servers, six agents |
| Retired | **Docker Swarm** |
| Considered | upstream Kubernetes (kubeadm), k0s, MicroK8s, Nomad |

The platform ran on **Docker Swarm first**, and that was the wrong long-term call — covered
at length in [what I'd do differently](lessons.md). Swarm did everything asked of it for
months: declarative compose-shaped stack files, near-zero ops overhead, working fine on
wildly heterogeneous hardware. What ended it was not a failure but a ceiling — no operator
pattern, no CRDs, no admission webhooks, so no database operator, no storage operator, no
policy tooling. Everything the ecosystem had built in the previous five years was on the
other side of that line.

The alternatives, each in one line:

- **kubeadm / upstream Kubernetes** — ops cost exceeded the learning value at this scale.
- **k0s** — genuinely comparable to k3s. Bundled ingress and the backing organisation tipped
  it; this could have gone either way and I would not argue with someone who picked k0s.
- **MicroK8s** — snap-only, awkward across the mixed distributions on this hardware.
- **Nomad** — an *excellent* fit for this scale, and rejected for a reason that is honest
  rather than technical: the goal was fluency in the ecosystem the industry actually runs, and
  that ecosystem is Kubernetes. Nomad would likely have been less work and taught less.

---

## The networking caveat I would rather not advertise

**Flannel (VXLAN)**, the bundled CNI, kept because it works on a mixed-hardware LAN with no
tuning. The honest cost, stated plainly because it is a real security property:

> **Flannel ships no NetworkPolicy engine. Pod-to-pod traffic inside this cluster is
> unrestricted.** Not "restricted by default and opened where needed" — unrestricted. It is
> also IPv4-only, which is why every kubelet is pinned to an IPv4 node address.

The upgrade path is **Cilium** (eBPF datapath, real NetworkPolicy, plus runtime security in
the same family) or **Calico** if eBPF proves troublesome on the decade-old kernels here. It
is not done because a CNI swap on a running cluster is a rebuild-level change, and it is
listed here rather than quietly omitted because segmentation is exactly the kind of gap that
a stack this otherwise-hardened can hide behind.

---

## Storage: the plan that changed, and a supply chain that moved under us

| | |
|---|---|
| **In use** | **Rook-Ceph**, block mode, three-way replication — the *sole* storage class |
| Rejected | **Longhorn** — the original plan |
| Future | **Ceph RGW**, to collapse two systems into one |

Longhorn was the intended choice until loopback-file Ceph OSDs turned out to be simpler and
zero-spend on a fleet of single-disk machines. The decision that mattered more than the
product choice was **removing the single-node provisioner entirely**, so an unqualified
volume claim fails loudly instead of silently pinning itself to one machine's disk. Delete
the unsafe default rather than documenting it.

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

Considered and passed on: **Patroni on Kubernetes** (works, but a meaningfully rougher
interface than a single CR), the **Zalando operator** (excellent and older; lost on
documentation and velocity), **MySQL/MariaDB** (no reason to run a second relational engine),
**MongoDB** (JSONB covers the document use cases), and **Redis** (no cache or queue workload
exists yet — adding one to be ready for a workload that has not arrived is how a platform
accumulates components nobody understands).

One retired: **Patroni + repmgr**, which ran the pre-Kubernetes topology reliably for its
whole life and was retired with the orchestrator rather than because it failed.

---

## Autoscaling, and the component with nothing to scale on

**HorizontalPodAutoscaler** on CPU, two to four replicas. Native, no extra component, and CPU
is the honest signal for these particular services.

**KEDA** is the better tool the moment there is a real queue to scale on — and would today be
a permanently-running component observing a metric that does not exist. **VPA** fights the
HPA on the same metric unless carefully partitioned; resource requests are hand-tuned instead.

Note also what is *absent*: there is no cluster-autoscaler analogue, because the fleet is
six fixed machines. Scale-out only. A platform that cannot add nodes should say so rather
than imply elasticity it does not have.

---

## Deferred — needed eventually, not yet

| Topic | Candidate | Why not yet |
|---|---|---|
| Service mesh | Linkerd / Istio | No need for mTLS between pods or fine-grained traffic policy. Linkerd wins on day-one cost when that changes. |
| **Secrets at rest** | SOPS + age, or sealed secrets — **not Vault** | **Genuinely sub-baseline today**: plaintext base64 in cluster secrets. The fix should be the *lightest* self-hosted option; Vault is overkill for a handful of secrets and would itself become a thing to operate. |
| Policy admission | Kyverno / OPA / sigstore policy controller | Worth doing once there is one hard rule worth enforcing — and there is: **signature-required at admission**. Signatures are verified in CI but are not yet load-bearing at deploy time. Highest-leverage next security step. |
| Backups beyond Postgres | Velero | The database tier is the only stateful tier. Velero matters the moment that stops being true. |
| Tracing | OpenTelemetry + Tempo | The collector has to land before instrumenting applications is worth anything. |

The secrets row is the one worth dwelling on: it is listed in the deferred table *and* named
in [what this does not do](devsecops.md#10-what-this-does-not-do), because it is the recurring
root cause behind a whole class of placeholder-credential defects. Writing it down twice is
deliberate.

---

## Rejected on principle — cloud-only

A standing constraint: **no source, telemetry, or repository access leaves the network.**
Several of the products below are genuinely excellent. That is not the deciding factor, and
the list exists to make the constraint explicit rather than to disparage them.

| Domain | Candidate | What is done instead |
|---|---|---|
| All-in-one AppSec | Aikido Security | Every scanner in its free tier already runs self-hosted, aggregated into one findings tracker, plus signing and provenance it does not offer. Its OSS in-app firewall is the one genuinely different piece — and *is* self-hostable, so it is tracked separately. |
| Malicious-package detection | Socket.dev | The idea is worth stealing: detect *malicious* rather than merely vulnerable packages. Watch the open malicious-package feeds instead. |
| Reachability-based SCA | Endor Labs | Idea worth stealing: only alert on CVEs on code paths actually executed. The noise-reduction concept to watch for in open tooling. |
| Secret scanning | GitGuardian | The valuable half — *validity-checked* secrets — is available from open tooling run alongside the basic scanner. |
| DAST / API security | StackHawk · Escape · 42Crunch | Spec-driven scanning done in-house against the OpenAPI documents the services already emit. |
| Runtime / cloud security | Wiz · Sysdig · Datadog | Agent-based and cloud-only. The open equivalent was deferred until there was something to triage the output — which now exists. |
| Commercial SCA | Snyk · Black Duck | Covered by open tooling, which additionally re-analyses *already-shipped* inventories against new advisories. |

> **A cloud-only tool can inspire something built or self-hosted here. It can never be
> adopted.** That is a design input, not a limitation to apologise for — but it does mean
> accepting that some capabilities arrive later and rougher than they would with a credit card.

---

## Rejected on right-sizing — good software, wrong problem

The hardest list to be honest about, because these are self-hostable, well-built and
genuinely standard. Adopting a tool because it is what serious platforms use is
cargo-culting; the question is whether the problem is *observed here*.

**ArgoCD / Flux** — solves multi-team configuration drift and pull-based reconciliation.

Neither problem exists at single-maintainer scale. Deployment is already declarative and
reproducible from nothing, and there is a drill that *proves* configuration comes back from
git — the same guarantee, demonstrated more simply. A reconciler would add a second source of
truth and a permanently-running component.

> **Reopen if:** a second maintainer joins, **or** manifests are ever observed drifting from
> git. Both are checkable, and the second one is monitored.

That trigger is the part that makes this a decision rather than a preference. It has also
already been useful once: the rejection was re-litigated, the trigger was checked, and the
answer stayed the same — which took ten minutes instead of a fresh argument.

---

## What this page is really arguing

Not that these choices are correct. Several are contested, one is a live risk, and one was
wrong for a year and shipped anyway.

The argument is that **each of them is explainable, and each of the rejections names what
would change it.** A stack you can only defend by listing what it contains is a stack you
have not actually chosen — and the ones you passed on are more informative about your
judgement than the ones you kept.

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

---

<sub>Written for publication. Machines, addresses, hostnames and credential locations are
absent by construction and enforced by a guard that fails the build.</sub>
