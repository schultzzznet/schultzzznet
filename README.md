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

**Track 1 — Platform mastery**

11 machines. Deliberately heterogeneous — Dell servers, decommissioned MacBook Pros,
old iMacs, Raspberry Pis, Apple Silicon. Not identical cloud VMs. That's the point.
If HA, quorum tolerance, and zero-downtime deploys hold up across hardware with different
CPUs, RAM, disk speeds, and boot behaviours, they'll hold up anywhere. Cloud VMs are the
easy case. This is the harder test.

8 full cluster nodes: 3 as Docker Swarm quorum managers, 3 as k3s control-plane+etcd
servers, 2 as k3s workers. 2 Raspberry Pi edge nodes handling HAProxy TLS termination and
Tailscale ingress — cheap, replaceable, exactly what you'd use at the edge in a real
deployment. 1 Apple Silicon AI host (Mac Mini M2 Pro) running Ollama and the ops agent,
air-gapped from the internet.

The same Spring Boot + PostGIS apps run on both Swarm and k3s simultaneously — a
deliberate architectural stress test: if a design decision only holds on one orchestrator,
it's not good enough. Flutter iOS/Android mobile clients. Keycloak for OAuth2/OIDC.
Patroni HA Postgres on Swarm. CloudNativePG on k3s. Prometheus → Loki → Grafana →
Alertmanager. No single point of failure in any critical path.

This runs at production standard — real operational pressure, real failure modes, real
constraints. The kind of system you'd hand off to a team and go on holiday.

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
