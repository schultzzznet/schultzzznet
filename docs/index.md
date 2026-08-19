---
title: The estate
---

# One system, three repositories

[![Alerting alive](https://img.shields.io/endpoint?url=https%3A%2F%2Fhealthchecks.io%2Fbadge%2F3f30fa97-f736-45eb-befc-7e77b7%2Fj_HAzc4M.shields&label=alerting&logo=prometheus&logoColor=white)](https://healthchecks.io)
[![Public endpoint](https://img.shields.io/uptimerobot/ratio/7/m803634462-26ba093afb66ea071e032353?label=public%20endpoint%207d&logo=uptimerobot&logoColor=white)](https://stats.uptimerobot.com/uA0nWd408c)

*Those two are live.* The first is a dead-man's-switch: the cluster's alert pipeline proves
itself end to end on a schedule, and the badge goes red if the heartbeat stops. The second is
an off-site probe of the public entrance, run from outside the house entirely — so it still
reports when the power or the internet is what failed.

**Structural facts, current as of 2026-08-19:**

![nodes](https://img.shields.io/badge/bare--metal%20nodes-9-326CE5?logo=kubernetes&logoColor=white)
![control plane](https://img.shields.io/badge/control%20plane-3%20%C3%97%20etcd-419EDA?logo=etcd&logoColor=white)
![storage](https://img.shields.io/badge/every%20volume-replica--3-EF5423?logo=ceph&logoColor=white)
![postgres](https://img.shields.io/badge/Postgres%20clusters-8-4169E1?logo=postgresql&logoColor=white)
![sbom](https://img.shields.io/badge/images%20with%20an%20SBOM-62%20of%2062-blueviolet)
![signed](https://img.shields.io/badge/images-signed%20%2B%20verified-2E2E5F?logo=sigstore&logoColor=white)
![ha](https://img.shields.io/badge/failure%20domains%20HA-4%20of%2013-orange)
![assertions](https://img.shields.io/badge/reality%20assertions-35%20passing-2EA44F)

**A runtime snapshot, queried 2026-08-10** — a moment in time, not a claim of steady state.
It is here because every figure is one query away from being re-checked, which is the only
reason to publish a number at all:

![nodes ready](https://img.shields.io/badge/nodes%20Ready-9%20of%209-2EA44F?logo=kubernetes&logoColor=white)
![pods](https://img.shields.io/badge/running%20pods-167%20%C2%B7%2016%20namespaces-326CE5)
![scrape](https://img.shields.io/badge/scrape%20targets%20healthy-72%20of%2072-E6522C?logo=prometheus&logoColor=white)
![series](https://img.shields.io/badge/active%20metric%20series-~300k-E6522C?logo=prometheus&logoColor=white)
![restarts](https://img.shields.io/badge/container%20restarts%2024h-1-2EA44F)
![capacity](https://img.shields.io/badge/fleet-60%20cores%20%C2%B7%20141%20GB-575757)
![busy](https://img.shields.io/badge/CPU%20busy-13.4%25-2EA44F)

One alert was firing at that moment: the watchdog that is *supposed* to fire, continuously,
because its silence is what proves the alert pipeline has died.

This is a home-built platform that is run like a production one: nine bare-metal
Kubernetes nodes assembled from retired laptops and small-form-factor desktops, the
services that run on them, the embedded devices that talk to them, and the delivery
chain that ties the lot together.

Three repositories, bound by hard dependencies rather than theme.

| Repository | What it is | Bound to the platform by |
|---|---|---|
| **the-docker-swarm-ai** | The platform itself — k3s cluster, Spring Boot services, Flutter clients, the whole delivery chain | *is* the platform |
| **theSchultzYocto** | A custom embedded Linux image: signed over-the-air A/B updates, proven rollback on real hardware | Ships bills of materials into the platform's vulnerability tracking; devices report to a fleet service running on it |
| **post-app** | A **satellite** — its own repository, its own CI, deployed onto the platform from outside it | Calls the platform's published deploy contract: a Dockerfile and a conformant manifest, nothing more |

The third one is the interesting proof. **An application does not have to live in the
platform's repository to run on it.** The satellite brings two files; the platform supplies
the registry, signing chain, runtime, ingress, replicated storage, identity, metrics and
logs. If that contract is real, it can be exercised from outside — so it is.

It is also deliberately trivial: one endpoint, no database, no identity. The variable under
test is the *contract*, and a bigger application would only make it harder to see which half
broke. What it did surface is worth more than the deployment itself —
[the contract's silences are permissions](platform.md), and this one took every single one
of them.

The platform's name is a fossil: it began on Docker Swarm and has run on k3s for a long time
now. Renaming a repository breaks every link that points at it, so the name stayed.

---

## What is actually running

- **Nine nodes**, three of them control-plane with embedded etcd, on hardware spanning
  2011 laptops to modern small desktops. The heterogeneity is deliberate — it forces the
  scheduling and storage decisions to be explicit rather than accidental. Nodes carry
  labels for CPU class, disk class, sustained-load tolerance and **disk health**, and
  workloads are placed against those facts rather than against hope.
- **Replicated block storage**, three-way, host-level failure domain, as the sole storage
  class. The single-node storage provisioner is switched off on purpose so that an
  unqualified volume claim *cannot* silently pin itself to one machine's disk.
- **Eight Postgres clusters** under an operator — three at three instances, five at two. The
  application and identity databases run **synchronous** replication; every one of them
  archives continuously to object storage.
- **Five Spring Boot services** and **five Flutter clients**, plus identity, ingress,
  metrics, logs and dashboards. Two nodes are deliberately **tainted** — one has no wired
  network, one is a designated fault-injection target — so neither can quietly acquire
  production work.
- **A supply chain with teeth**: every image is signed, provenance-attested and scanned,
  and **62 distinct running images** — including all 56 third-party ones — have a bill of
  materials that is re-evaluated as new vulnerabilities are published.
- **Deliberate chaos**: a scheduled fault injector with a safety controller that halts it
  when the system is not in steady state, and escalates when a fault does not self-heal
  inside its recovery budget.
- **An operations agent** that reads live cluster state, correlates it, and proposes
  remediations — permitted to apply only the *additive* ones on its own.
- **35 automated assertions** that documentation, inventory and reality still agree, run on
  demand and failing loudly when they diverge.

And, because the number that is never on a landing page is the one worth trusting:
**four of thirteen failure domains are genuinely single-fault tolerant.** The other nine are
named, ranked and tracked in the open rather than rounded up —
[the audit is here](reliability.md).

Concrete numbers, machines, addresses and topology stay in the private repository. What is
here is the shape of the thing and the reasoning behind it.

---

## AI, twice

Two separate AI deployments, at two different points in the lifecycle, held to the same bar
as everything else here: **assert the property, do not trust the report.**

**Development time — a cloud model, in the loop, always reviewed.** Every repository in the
estate — including the words on this page — is built with a cloud LLM as a first-class
engineering peer rather than autocomplete: architecture reasoning, code, and documentation.
It works from a written working agreement and a persistent memory of decisions already made,
because a session that re-derives context from scratch is a session that re-litigates
mistakes already paid for. **It gets no exemption:** an AI-assisted change goes through the
identical pull-request gates as any other — [the same SAST, secret scan, tests and
signing](devsecops.md) — and a human remains accountable for reviewing what it produced.

**Run time — a separate, local, air-gapped model, with a narrow write path.** The cluster is
watched continuously by an on-prem operations agent, deliberately not the cloud model, so the
thing watching production has no dependency on someone else's API being reachable. It holds a
natural-language conversation over chat — but nothing it says is ever executed directly:
[**the model proposes; a fixed, allowlisted guardrail layer disposes**](aiops.md). Every
action is built from a small, closed vocabulary, shown as a dry run, and waits for a human's
explicit approval before anything runs against the cluster.

Which is the honest answer to the question this section exists to stop anyone rounding up:

- **A bounded, budgeted chaos-recovery loop runs unattended** — and escalates loudly if a
  fault does not self-heal inside its recovery budget.
- **Additive remediations run unattended, within configured limits** — scale up, restart a
  pod that has a survivor, clear a cache.
- **Anything that removes, reduces capacity, or reschedules always waits for a human's
  click.** No exceptions, regardless of how confident the model is.

**This is not a self-healing cluster.** It is a cluster where one narrow, budgeted case
heals itself and proves it, the additive case corrects itself within limits, and everything
else becomes a proposal a human has to approve. That is a smaller claim than the industry's
favourite phrase — and the one that is actually true today.

---

## The habit the whole thing is built on

> **Assert the property. Do not trust the report.**

The recurring defect class on this platform is not the crash. It is the thing that is
*configured, plausible-looking and quietly inert*. Real examples, all found by checking
rather than reading:

- A chaos schedule that had never once fired. Every dashboard was green. The field that
  would have revealed it — *when did this last run?* — was not on any of them.
- A kill switch that covered half the system, because it matched one hardcoded name while
  a second fault class had been added later.
- A safety controller that was never actually deployed to the machine whose only job was
  to hold it. Enabling it would have been a no-op that reported success.
- An automated reboot daemon that read the wrong path and therefore concluded, hourly on
  every node for weeks, that no machine needed restarting. Patches were applied to disk and
  never came into effect: **16,002 host findings, all of them already fixed upstream**, and
  four different kernel versions running at once.
- A documentation site workflow that ran **89 times and succeeded zero times** over three
  weeks, failing before its first step so there were no logs to look at. Nothing alerted.
- A workstation link that dropped **1,614 times in a day**, invisible to `ifconfig`
  because it recovered between samples. Only the system log could see it.
- A shared build cache that was populated, correct, and **bypassed on every single build**,
  because a prerequisite service that gives cache entries a stable identity was missing.

None of these errored. Each looked fine until something checked directly. So: run the
thing, read the value back off the live object, and make a test fail before trusting that
it passes. A green status line is a claim, not evidence.

---

## The stack

Everything is standard, widely-deployed, open-source tooling. No proprietary lock-in and no
vendor-specific magic — every choice maps cleanly onto what you would reach for in a cloud
datacentre, which is rather the point of building it on retired laptops.

**Platform & runtime**

![k3s](https://img.shields.io/badge/runs%20on-k3s-FFC61C?logo=k3s&logoColor=black)
![Kubernetes](https://img.shields.io/badge/Kubernetes-native-326CE5?logo=kubernetes&logoColor=white)
![containerd](https://img.shields.io/badge/containerd-runtime-575757?logo=containerd&logoColor=white)
![etcd](https://img.shields.io/badge/etcd-HA%20store-419EDA?logo=etcd&logoColor=white)
![CoreDNS](https://img.shields.io/badge/CoreDNS-service%20discovery-1D63C3?logo=coredns&logoColor=white)
![Traefik](https://img.shields.io/badge/Traefik-ingress-24A1C1?logo=traefikproxy&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-charts-0F1689?logo=helm&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-all%20provisioning-EE0000?logo=ansible&logoColor=white)
![Tailscale](https://img.shields.io/badge/Tailscale-public%20edge-242424?logo=tailscale&logoColor=white)

**Data & identity**

![Rook-Ceph](https://img.shields.io/badge/Rook--Ceph-replica--3%20RBD-EF5423?logo=ceph&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-HA-4169E1?logo=postgresql&logoColor=white)
![CloudNativePG](https://img.shields.io/badge/CloudNativePG-operator-1A5276?logo=postgresql&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-object%20store-C72E49?logo=minio&logoColor=white)
![Keycloak](https://img.shields.io/badge/Keycloak-OIDC-4D4D4D?logo=keycloak&logoColor=white)

**Supply chain & security**

![cosign](https://img.shields.io/badge/Sigstore-cosign%20%2B%20SLSA-2E2E5F?logo=sigstore&logoColor=white)
![CycloneDX](https://img.shields.io/badge/SBOM-CycloneDX%201.6-blueviolet)
![Syft](https://img.shields.io/badge/SBOM%20gen-Syft-5C4EE5)
![Trivy](https://img.shields.io/badge/CVE%20scan-Trivy-1904DA?logo=aquasecurity&logoColor=white)
![Dependency-Track](https://img.shields.io/badge/Dependency--Track-SBOM%20%2B%20VEX-005571)
![DefectDojo](https://img.shields.io/badge/DefectDojo-finding%20mgmt-DC143C)
![CodeQL](https://img.shields.io/badge/CodeQL-SAST-2088FF?logo=github&logoColor=white)
![gitleaks](https://img.shields.io/badge/gitleaks-secret%20scan-1E90FF)
![ZAP](https://img.shields.io/badge/OWASP%20ZAP-DAST-00549E?logo=owasp&logoColor=white)
![Renovate](https://img.shields.io/badge/Renovate-enabled-brightgreen?logo=renovatebot&logoColor=white)
![Dependabot](https://img.shields.io/badge/Dependabot-enabled-025E8C?logo=dependabot&logoColor=white)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)
![SonarQube](https://img.shields.io/badge/SonarQube-quality%20gate-4E9BCD?logo=sonarqube&logoColor=white)

**Observability & resilience**

![Prometheus](https://img.shields.io/badge/Prometheus-metrics-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-dashboards-F46800?logo=grafana&logoColor=white)
![Loki](https://img.shields.io/badge/Loki-logs-F9A03C?logo=grafana&logoColor=white)
![Alertmanager](https://img.shields.io/badge/Alertmanager-routing-E6522C?logo=prometheus&logoColor=white)
![Chaos Mesh](https://img.shields.io/badge/Chaos%20Mesh-scheduled%20faults-FF6600)
![kured](https://img.shields.io/badge/auto--patching-kured%20%2B%20SUC%2C%20no%20window-326CE5?logo=kubernetes&logoColor=white)
![Portainer](https://img.shields.io/badge/Portainer-CE-13BEF9?logo=portainer&logoColor=white)

**Applications & clients**

![Java](https://img.shields.io/badge/Java-17%20LTS-ED8B00?logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.5-6DB33F?logo=springboot&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-6BA539?logo=openapiinitiative&logoColor=white)
![Schemathesis](https://img.shields.io/badge/Schemathesis-contract%20tested-8A2BE2)
![k6](https://img.shields.io/badge/k6-load%20%2B%20soak-7D64FF?logo=k6&logoColor=white)

**Embedded**

![Yocto](https://img.shields.io/badge/Yocto-custom%20layer-0A64A4?logo=yoctoproject&logoColor=white)
![RAUC](https://img.shields.io/badge/RAUC-signed%20A%2FB%20OTA-4B8BBE)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-target%20hardware-A22846?logo=raspberrypi&logoColor=white)

> The stack badges above are statements of fact about what is deployed, not build status.
> **Workflow badges are deliberately absent**: the three project repositories are private, so
> their status badges return 404 to anyone but me — a broken image is worse than no image, and
> a badge nobody else can verify is decoration rather than evidence.

---

## Read next

- **[How the platform builds and ships things](platform.md)** — the delivery chain, why it
  is split across two kinds of runner, what an application has to bring to be deployable —
  and what the contract pointedly does *not* require.
- **[DevSecOps, end to end](devsecops.md)** — every gate from commit to running pod, what
  each one actually proves, and the measurement traps that produced confident wrong numbers.
- **[High availability, audited](reliability.md)** — four of thirteen failure domains, the
  maintenance that removed the tools needed to perform it, and why the automated patching
  loop is the best chaos experiment on the platform.
- **[The operations agent](aiops.md)** — a local model with a write path to a production
  cluster, and the single question that decides what it may do without asking.
- **[The embedded side](yocto.md)** — a custom Linux image with signed over-the-air updates,
  the work required to make a vulnerability scanner tell the truth about it, and three traps
  that only real hardware finds.

---

<sub>Written for this public site rather than copied from the private repository, and checked
on every commit by a guard that fails the build on hostnames, addresses and credential
paths. Starting clean is cheaper than scrubbing.</sub>
