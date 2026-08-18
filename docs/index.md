---
title: The estate
---

# One system, four repositories

This is a home-built platform that is run like a production one: nine bare-metal
Kubernetes nodes assembled from retired laptops and small-form-factor desktops, the
services that run on them, the embedded devices that talk to them, and the delivery
chain that ties the lot together.

Four repositories, bound by hard dependencies rather than theme.

| Repository | What it is | Bound to the platform by |
|---|---|---|
| **the-docker-swarm-ai** | The platform itself — k3s cluster, Spring Boot services, Flutter clients, the whole delivery chain | *is* the platform |
| **theSchultzYocto** | Custom embedded Linux images | Ships SBOMs into the platform's vulnerability tracking |
| **theMowerRetrofit** | Retrofitting a robot mower with real autonomy | Uses the platform's app-deploy contract |
| **theDroneSwarm** | Autonomous drone work | Calls the platform's reusable deploy workflow directly in CI |

The name is a fossil: it began on Docker Swarm and has run on k3s for a long time now.
Renaming a repository breaks every link that points at it, so the name stayed.

---

## What is actually running

- **Nine nodes**, three of them control-plane with embedded etcd, on hardware spanning
  2011 laptops to modern small desktops. The heterogeneity is deliberate — it forces the
  scheduling and storage decisions to be explicit rather than accidental.
- **Replicated block storage** across three of the nodes, so a node loss is survivable.
- **Five Spring Boot services** and **five Flutter clients**, plus identity, ingress,
  metrics, logs and dashboards.
- **A supply chain with teeth**: every image is signed, provenance-attested, and scanned;
  SBOMs land in a vulnerability tracker that re-evaluates them as new CVEs appear.
- **Deliberate chaos**: a scheduled fault injector with a safety controller that halts it
  when the system is not in steady state, and escalates when a fault does not self-heal
  inside its recovery budget.

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

---

<sub>Written for this public site rather than copied from the private repository, and checked
on every commit by a guard that fails the build on hostnames, addresses and credential
paths. Starting clean is cheaper than scrubbing.</sub>
