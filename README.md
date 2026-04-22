# Christian Schultz

**Platform engineer. Full-stack. AI-native.**

[![Java 17](https://img.shields.io/badge/Java-17%20LTS-ED8B00?logo=openjdk&logoColor=white)](https://openjdk.org)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2-6DB33F?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter&logoColor=white)](https://flutter.dev)
[![Docker Swarm](https://img.shields.io/badge/Docker%20Swarm-live-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/engine/swarm/)
[![k3s](https://img.shields.io/badge/k3s-live-326CE5?logo=kubernetes&logoColor=white)](https://k3s.io)
[![Ollama](https://img.shields.io/badge/Ollama-local%20AI%20ops-black)](https://ollama.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-live-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io)

---

> *The technology doesn't matter. What matters is what you can build with it that you couldn't build before.*
> — paraphrasing [Marty Cagan / SVPG](https://www.svpg.com)

---

## What's running right now

A live, production-grade platform on real hardware — in daily use, with months of
uptime. Not a concept. Not a lab that gets spun up for demos.

Two tracks running in parallel, both active:

**Track 1 — Full-stack platform mastery**

The question this track answers: *can you build the real thing, end to end, at production
standard — and know it works because it's actually running?*

**Yes. Here's the proof:**

A deployed Flutter iOS and Android mobile app, talking to Spring Boot backends with PostGIS
spatial queries, authenticated via Keycloak OAuth2/OIDC, sitting behind Traefik reverse proxy
and HAProxy TLS edge ingress — with HA Postgres underneath, full observability (Prometheus,
Loki, Grafana, Alertmanager), and the whole thing deployable to two orchestrators
simultaneously: **Docker Swarm and Kubernetes (k3s)**. Both are live. Same apps, same data,
same infrastructure patterns. Swarm because it's operationally simple and battle-tested.
k3s because it's where professional cloud-native deployments land. Running both in parallel
is the stress test: if a design decision only holds on one orchestrator, it's not good enough.

Everything is scripted. Everything is Ansible-managed. Nothing requires a manual step.
The bar is not "works on a laptop". The bar is: *would this fly in a cloud datacenter with
paying users, SLAs, and a 3am incident?*

The cluster runs on 11 machines — Dell servers, repurposed MacBook Pros and iMacs, Raspberry
Pi edge nodes, and an Apple Silicon AI host (Mac Mini M2 Pro). The dev machine is an Apple
Silicon Mac Studio. A word on that: M-series chips are genuinely extraordinary — unified
memory architecture, performance per watt that embarrasses x86 at the same price point, and
the ability to run serious local LLM inference without breaking a sweat or the power budget.
Having Apple Silicon at both ends — dev and AI inference — is not accidental. It's the right
tool for both jobs.

This is a **practice and proof-of-concept environment, not optimised for raw performance**
— it's optimised for learning. Deliberately heterogeneous commodity hardware, because that's
what makes the HA and orchestration design meaningful: if quorum tolerance and
zero-downtime deploys hold up across machines with different CPUs, RAM, disk speeds, and
boot behaviours, they hold up anywhere. Cloud VMs are the easy case. This is the harder
test — and the results transfer directly.

**Nothing here is proprietary.** No EKS. No managed Kubernetes. No vendor-specific APIs.
Every component — k3s, Swarm, Traefik, Keycloak, Patroni, CloudNativePG, Prometheus, Loki
— runs identically on bare metal, on cloud VMs, or in any environment that can run a
container. The Ansible playbooks that provision this cluster provision a cloud deployment
with the same commands. That's a deliberate architectural constraint: if the design requires
a managed service to function, it isn't portable enough. Running this on commodity hardware
*without* the managed-service safety net is how you prove it's genuinely cloud-agnostic —
moving to cloud becomes a runtime decision, not an architectural rewrite.

**Track 2 — AI-native engineering**

Two distinct AI deployment patterns, both live and in production use:

- **Development edge — Claude (cloud AI).** Architecture reasoning, code generation, security
  review (OWASP Top 10, CVE triage) — across Spring Boot, Flutter, Ansible, SQL, and
  Dockerfile simultaneously. One engineer. Team-speed output.

- **Production edge — Ollama + qwen3.5:9b (local AI, air-gapped, zero cloud dependency).**
  A Python agent polls every hour across Prometheus, Loki, and Alertmanager.
  **Slack is the ops console.** DM the bot: *"what's the heap on warn-app?"* — it decides
  which tools to call, queries Prometheus live, and replies. Type `drain <node>` — it
  proposes the command with a dry-run description and ✅ / ❌ approval buttons. Click ✅
  and it SSHes into the cluster and runs it. The agent uses the **ReAct tool-calling
  pattern**: the model decides which data to fetch, calls the tools, reads the results, and
  iterates until it can answer confidently. Not a keyword router — a genuine agentic loop,
  running locally, zero cloud dependency, full data sovereignty. The pattern transfers
  directly to any estate with an observable infrastructure.

These aren't substitutes for each other. They serve different threat models, different
data-sensitivity requirements, and different latency budgets. Running both simultaneously
is itself an architectural pattern.

---

> *The best engineers are not there just to code. They are there to solve problems.*
> — Marty Cagan, [Empowered](https://www.svpg.com/books/empowered-ordinary-people-extraordinary-products/)

---

**→ [the-docker-swarm-ai](https://github.com/schultzzznet/the-docker-swarm-ai)** — the full
story, including the complete AI-native development and operations breakdown.

---

[![GitHub Stats](https://github-readme-stats.vercel.app/api?username=schultzzznet&show_icons=true&theme=dark&hide_border=true&count_private=true)](https://github.com/schultzzznet)

---

[github@schultzzz.net](mailto:github@schultzzz.net) · [schultzzz.net](https://www.schultzzz.net) · Denmark
