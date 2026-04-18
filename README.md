## Hi, I'm Christian Schultz

Platform engineer. Full-stack. AI-native.

I build production-grade platforms end to end — HA clusters, distributed databases, mobile
clients, and CI/CD that would hold up under real operational pressure. The bar I work to:
*would this fly in a cloud datacenter with paying users, SLAs, and a 3am incident?*

---

### What I'm running right now

A bare-metal homelab that's been in daily production use for months:

- **Docker Swarm + k3s** — same apps on two orchestrators in parallel, a deliberate
  architectural stress test
- **Spring Boot 3 / Java 17 + PostGIS** — location and hazard warning backends with spatial queries
- **Flutter** — iOS/Android mobile clients
- **Keycloak + Traefik + HAProxy** — full OAuth2/OIDC stack, edge ingress, TLS termination
- **Prometheus + Loki + Grafana + Alertmanager** — full observability, wired into everything

On top of that — a **local AI ops layer**:

- **Ollama + qwen2.5:14b** — runs on a Mac Mini M2 Pro, air-gapped, zero cloud dependency
- A Python agent polling every 60 seconds across Prometheus, Loki, and Alertmanager
- **Slack as the ops interface** — DM the bot to query live cluster state. Type `drain <node>`
  and it proposes the command with a dry-run description and ✅ / ❌ approval buttons.
  Click ✅ — it SSHes in and runs it. Anomaly detection, alert enrichment, bidirectional
  conversation, supervised execution — all through a chat window, all guardrailed,
  full data sovereignty.

→ **[the-docker-swarm-ai](https://github.com/schultzzznet/the-docker-swarm-ai)** — the full story

---

### Stack

`Java` `Spring Boot` `Flutter` `Python` `Docker Swarm` `k3s` `Postgres / PostGIS`
`Ansible` `Prometheus` `Grafana` `Loki` `Alertmanager` `Keycloak` `Traefik` `Ollama`
