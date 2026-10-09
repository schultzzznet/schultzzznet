# Christian Schultz

**Platform engineer. Full-stack. Working with AI on both ends of the pipeline.**

- I run a Kubernetes platform at home: six bare-metal nodes built from retired laptops (the five I have audited date from 2011 to 2019), with identity, Postgres, storage, observability and a signed supply chain.
- A frontier model helps me build it. A small local model, on a Mac outside the cluster, helps me operate it.
- The in-cluster software is open source or community edition. Claude, which I work with, is a paid service.
- It is a **private** platform with a **public** write-up. The write-up is the deliverable; the repositories behind it are not open.
- The rule of the whole thing: assert the property, do not trust the report.

[![Scheduled jobs](https://img.shields.io/endpoint?url=https%3A%2F%2Fhealthchecks.io%2Fbadge%2F3f30fa97-f736-45eb-befc-7e77b7%2Fj_HAzc4M.shields&label=scheduled%20jobs&logo=prometheus&logoColor=white)](https://healthchecks.io)
[![Public endpoint 7d](https://img.shields.io/uptimerobot/ratio/7/m803634462-26ba093afb66ea071e032353?label=public%20endpoint%207d&logo=uptimerobot&logoColor=white)](https://stats.uptimerobot.com/uA0nWd408c)
[![Public endpoint 30d](https://img.shields.io/uptimerobot/ratio/30/m803634462-26ba093afb66ea071e032353?label=30d&logo=uptimerobot&logoColor=white)](https://stats.uptimerobot.com/uA0nWd408c)

Those three badges are live, and they are graded from outside the system they grade: a heartbeat
for the scheduled jobs, and an off-site probe of the public entrance. They are depressed on purpose
by reboots and fault injection, so they are not an availability promise. Everything else on this
page is text, and I have stopped badging tool names: a badge that prints "Kubernetes" proves nothing.

## The numbers

Written by `scripts/gather-stats.py` in the site repository, from commands run against the
cluster. What each figure counts, and the command behind it, is on the
[status page](https://schultzzznet.github.io/schultzzznet/status.html).

<!-- stats:begin -->
| Figure | Value |
| --- | ---: |
| Nodes (Ready) | 6 (6) |
| CPU cores | 48 |
| Memory | 99 GB |
| Pods running | 191 |
| Postgres clusters / instances | 13 / 34 |
| Clusters with a synchronous standby right now | 8 of 13 |
| Backup objects (completed in the last 24 hours) | 343 (13) |
| Alert rules loaded | 222 |
| Scrape targets up | 123 of 123 |
| Commits to the platform repository | 1749 |
| Decision records | 39 |
| Test definitions (counted, not run) | 642 |
| CI workflows | 37 |

*Measured 2026-10-09T08:01:07Z by `make stats`. What each figure counts, and the command behind it: [the status page](https://schultzzznet.github.io/schultzzznet/status.html).*
<!-- stats:end -->

## What this is, and is not

- **Is:** a learning platform operated to production standards. Real applications behind real
  identity, a CI/CD pipeline that deploys the apps, scheduled database backups,
  and a habit of checking every claim by something other than the thing making it.
- **Is not:** a product with an availability commitment, or long-lived. The cluster was rebuilt
  on 2026-09-04, and k3s has been the only platform since the previous Docker Swarm cluster was
  decommissioned on 2026-06-09. "Months of uptime" would not be true.
- **Is not highly available throughout.** The platform's own failure-domain review, dated
  2026-09-09 and not re-measured since, counted 7 of 13 as highly available. The ones that are not: the public entrance, the physical layer (one switch, one power
  feed), the image registry, the steward, and the single-instance metrics and log stores.
- **Is not zero-loss everywhere.** Block storage is replica-3. As of 2026-10-09, the table above shows 8 of 13
  Postgres clusters with a synchronous standby. Those are the 8 three-instance clusters,
  configured to commit once any 1 of 2 standbys has the write. The 5 two-instance clusters are
  asynchronous by design.
- **Is not a user base.** Self-registration was switched off on 2026-09-29, per the platform's state notes (not
  re-checked today), so only I can create an account. The apps are deliberately modest demos that exercise every layer.

> **Retractions, 2026-10-09.** Earlier versions of this profile said "no single points of
> failure", "RPO 0, proven" and "Docker Swarm compatible", and that the AI runs inside the
> cluster. None of those was true when I checked. The worst was the second: the PostgreSQL 18
> cutover on 2026-09-16 silently dropped synchronous commit, so until it was restored on
> 2026-10-09 the application databases were asynchronous while the documentation said RPO 0.
> A guard now fails if a successor cluster loses that setting. Swarm was decommissioned and is
> not a fallback. The ops agent and its model run on a Mac outside the cluster, deliberately,
> because an operator that dies with the cluster is not an operator.

## The parts, briefly

**Platform.** k3s on six nodes, Ceph replica-3 block storage, CloudNativePG, Keycloak, Traefik,
Prometheus, Loki, Grafana and Alertmanager, largely managed by Ansible (a few steps, such as creating identity realms, are still by hand). Apps are Spring Boot and
Flutter. It is standard Kubernetes, but I have not tested it on a managed distribution, so I do
not claim it would move unchanged.

**Scaling.** CPU-based autoscalers are live. Scaling on request rate is not built.

**Supply chain.** First-party images are signed with cosign using a local key, so this is
signing, not keyless Sigstore. As of 2026-10-09, 6 of the 7 first-party images running verify
against the release key, and the tracker has accepted 70 SBOMs. Acceptance is not analysis.
I rate it SLSA Build L2 myself; nobody has audited that.

**AI.** The ops agent answers in Slack, queries Prometheus, and proposes actions such as a node
drain or a scale, which a human approves with a button. It does not act alone. An orchestrator
that closes the whole delivery loop into one policy-gated workflow is not built; chaos injection
is partial: my last self-rating (2026-09) counted 2 of 31 planned failure scenarios.

**Embedded.** A custom Yocto layer on the 6.0 LTS release (wrynose) for a Raspberry Pi 3 B+: a
signed RAUC A/B image, updated over the air, with an SBOM and CVE scan documented as a daily job. A signed update and a
deliberate rollback have both been proven on the board, and the last over-the-air update was
2026-09-01 (release 2026.09.1). A Pi 3 cannot do
hardware secure boot, so the updates are signed and integrity-checked, but the boot chain is not
verified.

## Read more

All on the site, **<https://schultzzznet.github.io/schultzzznet/>**:

- [What I'd do differently](https://schultzzznet.github.io/schultzzznet/lessons.html): the mistakes, with their costs.
- [Measurement traps](https://schultzzznet.github.io/schultzzznet/devsecops.html#6-measurement-traps-found-by-checking): confident, wrong numbers, found by checking.
- [Reliability](https://schultzzznet.github.io/schultzzznet/reliability.html) and [incidents](https://schultzzznet.github.io/schultzzznet/incident.html).
- [The AI ops agent](https://schultzzznet.github.io/schultzzznet/aiops.html) and [AI in development](https://schultzzznet.github.io/schultzzznet/ai-dev.html).
- [The embedded image](https://schultzzznet.github.io/schultzzznet/yocto.html).
- [Live status](https://schultzzznet.github.io/schultzzznet/status.html).

Code rather than prose: [`examples/`](examples/) holds four scrubbed artifacts from the running
system. Each exists because something looked correct and was not.

| | |
|---|---|
| [`trivy-kernel-ab-split.sh`](examples/trivy-kernel-ab-split.sh) | Host CVE counts that can never reach zero, and the regex that files a superseded kernel as live. Has a `--self-test` that demonstrates the bug. |
| [`duty-cycle-alert.yaml`](examples/duty-cycle-alert.yaml) | Why a `for:` alert cannot see a signal that sawtooths across its threshold, and the two-line fix. |
| [`kured-args.yaml`](examples/kured-args.yaml) | A reboot daemon that logged "nothing to do" hourly for weeks while 16,002 patched-but-not-running findings piled up. |
| [`systemd-oneshot-timer.md`](examples/systemd-oneshot-timer.md) | The `RemainAfterExit` trap that makes a timer fire once per boot. |

## Licence and security

- **Code** (`scripts/`, `examples/`, the `Makefile` and the workflow): [MIT](LICENSE).
- **Writing and images** (`docs/`, this README): [CC BY 4.0](LICENSE-docs). Reuse it, with credit.
- Quotations and linked material stay with their authors. The other repositories are separate
  projects with their own terms.
- Found something here that should not be public, or a flaw in the scripts?
  See [SECURITY.md](SECURITY.md).

## The repositories

Only this one is public. The rest are private, so there is nothing to link.

| Repository | What it is |
| --- | --- |
| [schultzzznet](https://github.com/schultzzznet/schultzzznet) | This site and its stats generator. |
| Platform | The cluster: Ansible, manifests, pipelines, decision records. |
| Yocto layer | The Raspberry Pi image and its OTA pipeline. |
| Mower retrofit | An RTK pattern-mowing brain for old robotic mowers. |
| Rover, video rover, i.MX8 Yocto, 3D printing | Smaller hardware projects. |

> *The best engineers are not there just to code. They are there to solve problems.*
> Marty Cagan, [Empowered](https://www.svpg.com/books/empowered-ordinary-people-extraordinary-products/)

[github@schultzzz.net](mailto:github@schultzzz.net) · [schultzzz.net](https://www.schultzzz.net) · Denmark
