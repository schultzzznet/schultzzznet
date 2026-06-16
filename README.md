# Christian Schultz

**Platform engineer. Full-stack. AI-native.**

[![CI](https://github.com/schultzzznet/the-docker-swarm-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/schultzzznet/the-docker-swarm-ai/actions)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Renovate](https://img.shields.io/badge/Renovate-enabled-brightgreen?logo=renovatebot&logoColor=white)](https://renovatebot.com)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-025E8C?logo=dependabot&logoColor=white)](https://github.com/dependabot)
<br>
[![Java 17 LTS](https://img.shields.io/badge/Java-17%20LTS-ED8B00?logo=openjdk&logoColor=white)](https://openjdk.org/projects/jdk/17/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2-6DB33F?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter&logoColor=white)](https://flutter.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-HA-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Keycloak](https://img.shields.io/badge/Keycloak-OIDC-4D4D4D?logo=keycloak&logoColor=white)](https://www.keycloak.org)
<br>
[![Kubernetes-native](https://img.shields.io/badge/Kubernetes-native-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![k3s](https://img.shields.io/badge/runs%20on-k3s-FFC61C?logo=k3s&logoColor=black)](https://k3s.io)
[![Docker Swarm](https://img.shields.io/badge/Docker%20Swarm-compatible-9E9E9E?logo=docker&logoColor=white)](https://docs.docker.com/engine/swarm/)
[![Helm](https://img.shields.io/badge/Helm-enabled-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![Traefik](https://img.shields.io/badge/Traefik-ingress-24A1C1?logo=traefikproxy&logoColor=white)](https://traefik.io)
[![Tailscale](https://img.shields.io/badge/Tailscale-Funnel-242424?logo=tailscale&logoColor=white)](https://tailscale.com/kb/1223/funnel)
[![Ansible](https://img.shields.io/badge/Ansible-IaC-EE0000?logo=ansible&logoColor=white)](https://www.ansible.com)
<br>
[![Prometheus](https://img.shields.io/badge/Prometheus-metrics-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-dashboards-F46800?logo=grafana&logoColor=white)](https://grafana.com)
[![Loki](https://img.shields.io/badge/Loki-logs-F9A03C?logo=grafana&logoColor=white)](https://grafana.com/oss/loki/)
[![Ollama](https://img.shields.io/badge/Ollama-local%20AI%20ops-black)](https://ollama.com)
<br>
[![SBOM: CycloneDX 1.6](https://img.shields.io/badge/SBOM-CycloneDX%201.6-blueviolet)](https://cyclonedx.org)
[![SBOM gen: Syft](https://img.shields.io/badge/SBOM%20gen-Syft-5C4EE5)](https://github.com/anchore/syft)
[![CVE scan: Trivy](https://img.shields.io/badge/CVE%20scan-Trivy-1904DA?logo=aquasecurity&logoColor=white)](https://aquasecurity.github.io/trivy/)
[![Dependency-Track](https://img.shields.io/badge/Dependency--Track-SBOM%20%2B%20VEX-005571)](https://dependencytrack.org)
[![Sigstore cosign](https://img.shields.io/badge/Sigstore-cosign%20%2B%20SLSA-2E2E5F?logo=sigstore&logoColor=white)](https://www.sigstore.dev)

---

> *The technology doesn't matter. What matters is what you can build with it that you couldn't build before.*
> — paraphrasing [Marty Cagan / SVPG](https://www.svpg.com)

---

## What I'm building

A **professional training ground** — live, running, and in daily use. Not a concept. Not a demo
lab. A self-hosted, production-grade platform on real hardware, built to professional standard,
with months of uptime behind it. **High availability and horizontal scalability done the way
they're meant to be done** — with best-in-class, widely-deployed designs that **actually work.**

It started as an infrastructure and full-stack engineering project. It's become broader: a live
proving ground for **AI-native development *and* AI-native operations** — both now first-class
citizens alongside the platform itself.

Two tracks, both live.

### Track 1 — A Best-in-Class Platform, the Way Production Should Be Built

Flutter iOS/Android → Spring Boot + PostGIS → Keycloak OAuth2/OIDC → Traefik → HAProxy TLS edge,
over **HA Postgres (CloudNativePG)** and full observability (Prometheus, Loki, Grafana,
Alertmanager). All Ansible-managed — zero manual steps, from a bare machine to a running service.

**Kubernetes-native, end to end.** Helm charts, operators, CRDs, admission control, plain
`kubectl` manifests — it's all standard Kubernetes. I run it on **k3s** for operational
simplicity and cost (a fully conformant, lightweight distribution), but nothing is k3s-specific:
the same manifests lift to **EKS, GKE, AKS, or any Kubernetes** unchanged. *Design for Kubernetes,
run on k3s.* And it stays portable below that line too — the apps and stacks were first proven on
**Docker Swarm** and the designs remain Swarm-compatible, so shifting back is a config choice, not
a rewrite. No managed control plane, no proprietary APIs, no lock-in.

**High availability with no single point of failure — proven, not assumed.** Quorum-tolerant
control plane, automatic Postgres failover, replicated ingress and identity. The bar isn't "works
on a laptop" — it's *survives a node loss, a rolling upgrade, and a 3am incident with real users.*

**Scales horizontally, on demand — and the AI watches the traffic that should drive it.** The
stateless app tier scales at will: `kubectl scale`, or just tell the bot *`scale warn-app to 4`*.
The signal is already live — the AI tracks request rates in Prometheus, with a specialist agent
flagging traffic spikes and near-zero drops hour-on-hour — so scaling follows real load, not
guesswork. Today it's one click on an AI-surfaced signal; the closed, traffic-driven autoscaling
loop is the short next step.

**DevSecOps, three supply-chain loops.** Every release ships an SBOM (syft → CycloneDX) and a CVE
scan (trivy) into **Dependency-Track**, which keeps re-analysing against fresh NVD/GHSA/OSV mirrors
— a release that was clean can light up critical overnight with no redeploy. A nightly CronJob
re-derives SBOMs from the live registry to catch silent base-image drift. Every image carries an
**SLSA v1.0** build-provenance attestation and is **cosign**-signed; the rollout pipeline verifies
the signature and refuses a tampered image. Self-rated **SLSA Build L2**, with the L3 path written
down.

### Track 2 — A Best-in-Class Cluster With a Real, Active, Working AI Brain

The part I'm proudest of: **the AI runs *inside* the platform, not beside it** — and it works. A
local LLM (Ollama + `qwen3:4b`, on-LAN, no cloud, no vendor dependency) is wired straight into the
observability stack and the cluster control path. The result is a cluster that watches itself,
reasons about itself, and helps run itself.

- **It watches and reasons.** Ask it in Slack *"what's the heap on warn-app?"* — it decides which
  tools to call, queries Prometheus live, reads the result, and answers. A genuine **ReAct
  tool-calling loop**, running locally — not a keyword bot.
- **It acts, under guardrails.** Type `drain <node>` or `scale warn-app to 4` — it posts the
  command with a dry-run and ✅ / ❌ approval buttons; click ✅ and it executes. Protected nodes,
  never-scale-to-zero, rate limits, auto-expiring proposals.
- **It improves the platform itself.** Self-strengthening specialist agents (Log / Telemetry /
  PR-health) continuously assess observability and pipeline coverage and post concrete,
  copy-paste-ready fixes to Slack. The cluster doesn't just run — it tells you how to make it
  better. **One deliberate step away from self-healing and traffic-driven autoscaling, and closing
  the gap.**

Two AI patterns by design — different threat models, data-sensitivity, and latency budgets;
running both at once *is* the architecture:

- **Dev edge — Claude (cloud), in VS Code.** A full-stack engineering peer: architecture
  reasoning, code generation, security review (OWASP Top 10, CVE triage) across Spring Boot,
  Flutter, Ansible, SQL, and Dockerfile at once — wired through **Jira and GitHub MCP servers (run
  via Docker Desktop's MCP gateway)** for governed, live access to the backlog and the repo. One
  engineer at small-team cadence.
- **Prod edge — Ollama (local).** The always-on, on-LAN brain described above — air-gapped from
  any cloud LLM, zero marginal cost, full data sovereignty.

> **Honest scope:** the apps (location sharing, hazard warnings, messaging) are deliberately
> non-trivial *demos* — enough to exercise every layer. The platform and the AI-ops brain are the
> real deliverable; the killer app is TBD. Full architecture, ADRs, and an incident diary are in
> the repo.

---

> *The best engineers are not there just to code. They are there to solve problems.*
> — Marty Cagan, [Empowered](https://www.svpg.com/books/empowered-ordinary-people-extraordinary-products/)

**→ [the-docker-swarm-ai](https://github.com/schultzzznet/the-docker-swarm-ai)** — full architecture, AI-ops breakdown, ADRs, and an incident diary.

---

[![GitHub Stats](https://github-readme-stats.vercel.app/api?username=schultzzznet&show_icons=true&theme=dark&hide_border=true&count_private=true)](https://github.com/schultzzznet)

---

[github@schultzzz.net](mailto:github@schultzzz.net) · [schultzzz.net](https://www.schultzzz.net) · Denmark
