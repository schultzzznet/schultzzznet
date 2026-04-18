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

## What's running right now

A live, production-grade platform on real x86 hardware — in daily use, with months of uptime.
Not a concept. Not a lab that gets spun up for demos.

Two tracks running in parallel, both active:

**Track 1 — Platform mastery**

3-manager Docker Swarm + 3-server k3s with embedded etcd. The same Spring Boot + PostGIS apps
run on both orchestrators simultaneously — a deliberate architectural stress test: if a design
decision only holds on one, it's not good enough. Flutter iOS/Android mobile clients.
Keycloak for OAuth2/OIDC. HAProxy TLS edge. Patroni HA Postgres on Swarm. CloudNativePG on k3s.
Prometheus → Loki → Grafana → Alertmanager. No single point of failure in any critical path.

This runs at production standard — real hardware, real HA, real operational pressure.
The kind of system you'd hand off to a team and go on holiday.

**Track 2 — AI-native engineering**

Two distinct AI deployment patterns, both live and in production use:

- **Development edge — Claude (cloud AI).** Architecture reasoning, code generation, security
  review (OWASP Top 10, CVE triage) — across Spring Boot, Flutter, Ansible, SQL, and Dockerfile
  simultaneously. One engineer. Team-speed output.

- **Production edge — Ollama + qwen2.5:14b (local AI, air-gapped, zero cloud dependency).**
  A Python agent polls every 60 seconds across Prometheus, Loki, and Alertmanager.
  **Slack is the ops console.** DM the bot: *"what's the heap on warn-app?"* — it queries
  Prometheus and replies with live data. Type `drain <node>` — it proposes the command with
  a dry-run description and ✅ / ❌ approval buttons. Click ✅ and it SSHes into the cluster
  and runs it. Anomaly detection, alert enrichment, bidirectional conversation, supervised
  cluster execution — all guardrailed, no cloud dependency, full data sovereignty.

These aren't substitutes for each other. They serve different threat models, different
data-sensitivity requirements, and different latency budgets. Running both simultaneously
is itself an architectural pattern.

---

**→ [the-docker-swarm-ai](https://github.com/schultzzznet/the-docker-swarm-ai)** — the full story,
including the complete AI-native development and operations breakdown.

---

[![GitHub Stats](https://github-readme-stats.vercel.app/api?username=schultzzznet&show_icons=true&theme=dark&hide_border=true&count_private=true)](https://github.com/schultzzznet)

---

[github@schultzzz.net](mailto:github@schultzzz.net) · [schultzzz.net](https://www.schultzzz.net) · Denmark
