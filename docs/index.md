---
title: The estate
---

# One system, three repositories

This is a home-built platform that is run like a production one: nine bare-metal
Kubernetes nodes assembled from retired laptops and small-form-factor desktops, the
services that run on them, the embedded devices that talk to them, and the delivery
chain that ties the lot together.

Three repositories, bound by hard dependencies rather than theme.

| Repository | What it is | Bound to the platform by |
|---|---|---|
| **the-docker-swarm-ai** | The platform itself — k3s cluster, Spring Boot services, Flutter clients, the whole delivery chain | *is* the platform |
| **theSchultzYocto** | A custom embedded Linux image: signed over-the-air A/B updates, proven rollback on real hardware | Ships bills of materials into the platform's vulnerability tracking; devices report to a fleet service running on it |
| **post-app** | A **satellite** application — its own repository, its own CI, deployed onto the platform | Calls the platform's published deploy contract: a Dockerfile and a conformant manifest, nothing more |

The third one is the interesting proof. **An application does not have to live in the
platform's repository to run on it.** The satellite brings two files; the platform supplies
the registry, signing chain, runtime, ingress, replicated storage, identity, metrics and
logs. If that contract is real, it can be exercised from outside — so it is.

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
- **Seven Postgres clusters** under an operator, with quorum-based synchronous replication
  and continuous archiving to object storage.
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

Concrete numbers, machines, addresses and topology stay in the private repository. What is
here is the shape of the thing and the reasoning behind it.

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
- A documentation site workflow that ran **89 times and succeeded zero times** over three
  weeks, failing before its first step so there were no logs to look at. Nothing alerted.
- A workstation link that dropped **1,614 times in a day**, invisible to `ifconfig`
  because it recovered between samples. Only the system log could see it.

None of these errored. Each looked fine until something checked directly. So: run the
thing, read the value back off the live object, and make a test fail before trusting that
it passes. A green status line is a claim, not evidence.

---

## Read next

- **[How the platform builds and ships things](platform.md)** — the delivery chain, why it
  is split across two kinds of runner, and what an application has to bring to be deployable.
- **[DevSecOps, end to end](devsecops.md)** — every gate from commit to running pod, what
  each one actually proves, and the measurement traps that produced confident wrong numbers.
- **[The embedded side](yocto.md)** — a custom Linux image with signed over-the-air updates,
  and the work required to make a vulnerability scanner tell the truth about it.

---

<sub>Written for this public site rather than copied from the private repository, and checked
on every commit by a guard that fails the build on hostnames, addresses and credential
paths. Starting clean is cheaper than scrubbing.</sub>
