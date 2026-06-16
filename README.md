# Christian Schultz

**Platform engineer. Full-stack. AI-native.**

[![Java 17](https://img.shields.io/badge/Java-17%20LTS-ED8B00?logo=openjdk&logoColor=white)](https://openjdk.org)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2-6DB33F?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter&logoColor=white)](https://flutter.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-HA-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Keycloak](https://img.shields.io/badge/Keycloak-OIDC-4D4D4D?logo=keycloak&logoColor=white)](https://www.keycloak.org)

[![k3s](https://img.shields.io/badge/k3s-primary-326CE5?logo=kubernetes&logoColor=white)](https://k3s.io)
[![Docker Swarm](https://img.shields.io/badge/Docker%20Swarm-retired-9E9E9E?logo=docker&logoColor=white)](https://docs.docker.com/engine/swarm/)
[![Traefik](https://img.shields.io/badge/Traefik-ingress-24A1C1?logo=traefikproxy&logoColor=white)](https://traefik.io)
[![Tailscale](https://img.shields.io/badge/Tailscale-Funnel-242424?logo=tailscale&logoColor=white)](https://tailscale.com/kb/1223/funnel)
[![Ansible](https://img.shields.io/badge/Ansible-IaC-EE0000?logo=ansible&logoColor=white)](https://www.ansible.com)

[![Prometheus](https://img.shields.io/badge/Prometheus-live-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-dashboards-F46800?logo=grafana&logoColor=white)](https://grafana.com)
[![Loki](https://img.shields.io/badge/Loki-logs-F9A03C?logo=grafana&logoColor=white)](https://grafana.com/oss/loki/)
[![Dependency-Track](https://img.shields.io/badge/Dependency--Track-SBOM%20%2B%20VEX-005571)](https://dependencytrack.org)
[![Sigstore cosign](https://img.shields.io/badge/Sigstore-cosign%20%2B%20SLSA-2E2E5F?logo=sigstore&logoColor=white)](https://www.sigstore.dev)
[![Ollama](https://img.shields.io/badge/Ollama-local%20AI%20ops-black)](https://ollama.com)

---

> *The technology doesn't matter. What matters is what you can build with it that you couldn't build before.*
> — paraphrasing [Marty Cagan / SVPG](https://www.svpg.com)

---

## What I'm building

A live, self-hosted platform on real bare-metal hardware — in daily use, with months of
uptime. Not a concept, not a demo lab. Two tracks run in parallel:

### Track 1 — Full-stack platform, end to end

Flutter iOS/Android apps → Spring Boot backends with PostGIS spatial queries → Keycloak
OAuth2/OIDC → Traefik reverse proxy → HAProxy TLS edge, with **HA Postgres (CloudNativePG)**
and full observability (Prometheus, Loki, Grafana, Alertmanager) underneath. Everything is
Ansible-managed — no manual step — and runs on a **6-node k3s cluster** (3 control-plane with
embedded etcd, 2 workers, 1 Raspberry Pi edge).

The apps started on **Docker Swarm and k3s in parallel** — same apps, same data, two
orchestrators — precisely so design decisions could be tested for portability. k3s won; Swarm
was **retired ([ADR-0011](https://github.com/schultzzznet/the-docker-swarm-ai)) and frozen as
a reference**. Nothing is proprietary: no EKS, no managed control plane, no vendor APIs. The
same playbooks that provision this cluster would provision cloud VMs — so moving to cloud is a
runtime decision, not a rewrite.

The bar is not *"works on a laptop"*. It's: **would this survive a single-node failure, a
rolling upgrade, and a 3am incident with paying users?** Quorum-tolerant control plane,
automatic Postgres failover, replicated ingress and identity — no single point of failure in
any critical path.

**Supply chain, three loops.** Every release ships an SBOM (syft → CycloneDX) and a CVE scan
(trivy) into **Dependency-Track**, which continuously re-analyses against fresh NVD/GHSA/OSV
mirrors — so a release that was clean can light up critical the next morning without a
redeploy. A nightly k3s CronJob re-derives SBOMs from the live registry to catch silent
base-image rebuilds. And every image carries an **SLSA v1.0** build-provenance attestation
(`docker buildx --provenance`) and is **cosign**-signed; `ship-apps` verifies the signature
between build and rollout, so a tampered image fails the ship. Self-rated **SLSA Build L2**,
with Vault Transit / hardened-builder / admission-time policy as the documented L3 next steps.

### Track 2 — AI-native engineering

Two AI patterns, both live, deliberately different:

- **Dev edge — Claude (cloud).** A full-stack engineering peer: architecture reasoning, code
  generation, security review (OWASP Top 10, CVE triage) across Spring Boot, Flutter, Ansible,
  SQL, and Dockerfile at once. One engineer at small-team cadence.

- **Prod edge — Ollama + `qwen3:4b` (local, on-LAN, no LLM-vendor dependency).** A Python
  agent wired into the observability stack, **with Slack as the ops console.** DM it
  *"what's the heap on warn-app?"* — it decides which tools to call, queries Prometheus live,
  and replies. Type `drain <node>` — it posts the command with a dry-run description and ✅/❌
  approval buttons; click ✅ and it SSHes in and runs it, under guardrails (protected nodes,
  never-scale-to-zero, rate limit, auto-expiring proposals). It runs a genuine **ReAct
  tool-calling loop** — decide, fetch, read, iterate — not a keyword router. Plus
  self-strengthening specialist agents (LogAgent, TelemetryAgent, PRHealthAgent) that assess
  observability/PR-pipeline coverage and post copy-paste-ready fixes to Slack.

These aren't substitutes. Different threat models, data-sensitivity, and latency budgets —
running both at once is itself the architectural point.

> **Honest scope:** the apps (location sharing, hazard warnings, messaging) are deliberately
> non-trivial *demos* — enough to exercise every layer. The platform and the AI-ops patterns
> are the real deliverable; the killer app is TBD. The full story, including verified failover
> incidents and the enterprise-scale open questions, is in the repo.

---

> *The best engineers are not there just to code. They are there to solve problems.*
> — Marty Cagan, [Empowered](https://www.svpg.com/books/empowered-ordinary-people-extraordinary-products/)

**→ [the-docker-swarm-ai](https://github.com/schultzzznet/the-docker-swarm-ai)** — full architecture, AI-ops breakdown, ADRs, and an incident diary.

---

[![GitHub Stats](https://github-readme-stats.vercel.app/api?username=schultzzznet&show_icons=true&theme=dark&hide_border=true&count_private=true)](https://github.com/schultzzznet)

---

[github@schultzzz.net](mailto:github@schultzzz.net) · [schultzzz.net](https://www.schultzzz.net) · Denmark
