# Christian Schultz

**Platform engineer. Full-stack. Working with AI on both ends of the pipeline.**

## What this is for

**A training system, on purpose.** I train principles, technologies and everything around them, as deep and as hands-on
as possible, on a **running system**: since 2026-11-10 a new cluster with one deployed reference app, and no public entrance, no users and
**no paying customers, yet**. V1.0 (retired 2026-11-10): it had real identity flows, real incidents and a public entrance.

- **The latest stack on the weakest hardware I could put to use.** The handicap is chosen: retired laptops and small
  desktops, to make it as hard as possible. If it runs here, it runs on any hardware; anything else is an upgrade.
- **AI all over.** On-prem and cloud, small local models and frontier models, simple setups and elaborate ones, at
  development time and at run time, each measured rather than trusted.
- **Two purposes at once.** Learn the maximum until the day a killer app appears, and be ready to grab that opportunity when
  it does. Until then everything here is learning and nothing is protected for uptime's sake; on that day the direction
  changes on purpose, and production becomes the main line.

- I run a Kubernetes platform at home: since 2026-11-10 a new K3s cluster on six retired machines (three control-plane servers that also run workloads, three laptop agents; the ones audited date from 2011 to 2020). It is about a day old, so no uptime is claimed. Monitoring is built (pods Running since 2026-11-11, nothing read from it yet); alerts to a person, replicated storage and a public name are not there yet. V1.0 ended on 2026-11-10 and its facts sit in dated notes on the site.
- A frontier model helps me build it, with a person approving what is merged. The small local operations agent belonged to V1.0 and is not part of this one (see the AI paragraph below).
- The in-cluster software is open source or community edition. Claude, which I work with, is a paid service.
- It is a **private** platform with a **public** write-up. The write-up is the deliverable; the repositories behind it are not open.
- The rule of the whole thing: assert the property, do not trust the report.

> **Not measured yet (2026-11-11):** alert rules, dashboards, metric history, SBOM projects, alerts reaching a person, and electricity cost.
>
> **In short, as of 2026-11-11.** V2.0, a new K3s cluster, built on 2026-11-10 and 11 on the same six machines, with no
> paying customers, no users and no load. **Proven 2026-11-10, with limits:** admission policies are Ready and refused an off-list image once;
> one PostgreSQL cluster with a nightly backup and a restore drill that passed on 2026-11-10 (a few megabytes, not real size,
> and only one backup machine). **Failed:** the default-deny network probe, because a new pod is open for one to three seconds.
> **Not live:** monitoring and alerts (merged 2026-11-11, pods Running at 07:00 UTC, nothing read from it yet), replicated storage, durable identity, an off-site backup copy, a public name. Figures
> that cannot be measured yet say "not measured yet". V1.0 is described in dated notes. Start with
> [*V1.0 and V2.0: what changed*](https://schultzzznet.github.io/schultzzznet/versions.html) (the diff list),
> [*How we work*](https://schultzzznet.github.io/schultzzznet/how-we-work.html), the
> [*status*](https://schultzzznet.github.io/schultzzznet/status.html) or
> [*Recently*](https://schultzzznet.github.io/schultzzznet/#recently).

[![Scheduled jobs](https://img.shields.io/endpoint?url=https%3A%2F%2Fhealthchecks.io%2Fbadge%2F3f30fa97-f736-45eb-befc-7e77b7%2Fj_HAzc4M.shields&label=scheduled%20jobs&logo=prometheus&logoColor=white)](https://healthchecks.io)
[![Public endpoint 7d](https://img.shields.io/uptimerobot/ratio/7/m803634462-26ba093afb66ea071e032353?label=public%20endpoint%207d&logo=uptimerobot&logoColor=white)](https://stats.uptimerobot.com/uA0nWd408c)
[![Public endpoint 30d](https://img.shields.io/uptimerobot/ratio/30/m803634462-26ba093afb66ea071e032353?label=30d&logo=uptimerobot&logoColor=white)](https://stats.uptimerobot.com/uA0nWd408c)

V1.0 (retired 2026-11-10): those three badges were live and are retired with it (the public entrance is gone); the paragraph is kept as history. They were graded from outside the system they grade: a heartbeat
for the scheduled jobs, and an off-site probe of the public entrance. They were depressed on purpose
by reboots and fault injection, so they were not an availability promise. Everything else on this
page is text, and I have stopped badging tool names: a badge that prints "Kubernetes" proves nothing.

## Objectives and key results, Q4 2026

*Set before the platform change of 2026-11-10; the key results that name V1.0 (retired 2026-11-10) are scored as written and will say so in January. Figures in them were measured on V1.0.*

Set 2026-10-31, scored here in early January, misses included. Each key result is scored 0.0 to 1.0; around 0.7 is a good
quarter, and 1.0 everywhere would mean the targets were too easy. Running OKRs with misses shown is itself one of the things being
trained, so they point at work and dates that already exist rather than keeping numbers of their own.

**1. Learn as much as possible, hands-on, on the running system.**

- Three of the next tools learned to their own test: tracing (OpenTelemetry and Tempo), an AI evaluation framework, and a
  GitOps controller.
- The choice between a pull controller and push-on-merge made by 1 December, from what was measured.
- Each one written up here with its measured result.

**2. Prove it on the weakest hardware: break it on purpose, watch it heal.**

- The cause of the 5, 10 and 15 second request stalls named by measurement, and DNS lookup loss below 0.5 % on every
  machine (about 7 % on the two oldest today).
- Fault injection firing on its schedule again, for at least four consecutive weeks (its own safety gate has kept it
  paused since 13 October).
- One drill that powers a machine off, run end to end.

**3. AI all over, measured, not trusted.**

- The first person-graded sample of the operations agent's posts by 26 November, then one a month.
- The cloud reviewer's verdicts compared with the person's grades on the same posts, and the agreement published.
- Every kind of AI post recorded and checked (the morning digest too, since 30 October), with the flagged share published
  each month.

**4. Be ready for the killer-app day.**

- Two more of the seven launch gates closed or explicitly accepted: no default passwords anywhere, and real-time
  connections authenticated.
- Every secret that was ever in git in plaintext rotated.
- A rebuild from empty machines to running apps, from git, timed and published.

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
| Pods running | 28 |
| Kustomizations ready | 13 of 18 |
| Admission policies ready | 2 of 2 |
| Tenants with default-deny (structural count) | 4 of 5 |
| Database instances ready | 3 of 3 |
| Backup objects completed in the last 24 hours | 1 |
| Latest restore drill on the home site | 2026-11-10, pass |
| Alert rules | not measured yet |
| Decision records | 8 |
| Run records (pass of total) | 26 of 35 |
| Test definitions (counted, not run) | 58 |
| CI workflows | 9 |

*Measured 2026-11-11T05:59:42Z by `make stats`. What each figure counts, and the command behind it: [the status page](https://schultzzznet.github.io/schultzzznet/status.html).*
<!-- stats:end -->

## What this is, and is not

- **Is:** a training system, run to production standards on purpose. Real applications behind real
  identity, no paying customers yet, a CI/CD pipeline that deploys the apps, scheduled database backups,
  and a habit of checking every claim by something other than the thing making it.
- **Is:** preparation. When a killer app appears, the platform, the patterns and the habits should already be in place;
  on that day the direction changes, and production becomes the main line.
- **Is not:** a product with an availability commitment, or long-lived. The current cluster was built
  on 2026-11-10 and 11, after the previous k3s cluster was torn down on 2026-11-10 (it had followed a Docker Swarm cluster
  decommissioned on 2026-06-09). "Months of uptime" would not be true.
- **Is not highly available throughout.** The new cluster has three control-plane servers, but storage is node-local and
  the database has one backup machine, so a node loss is not yet survivable everywhere. The failure-domain review of 2026-09-09
  belonged to V1.0 and is not carried over.
- **Is not zero-loss.** The one database cluster has three instances and a nightly backup; a restore drill passed on 2026-11-10
  on a database of a few megabytes. A scheduled-backup restore and an off-site copy are untested. V1.0's
  synchronous-commit figures are not carried over.
- **Is not a user base.** There are no users on the new cluster; durable identity is not live. The apps are deliberately modest demos that exercise every layer.

> **V1.0 (retired 2026-11-10): corrections, 2026-10-27.** Five statements on the site had turned stale in the pessimistic direction
> (pull requests, secrets in git, drift checking, the ops agent, a runner count), two on the embedded page
> were false throughout, and the uptime shortfall now has a cause. They are listed, with dates, on
> [the estate page](https://schultzzznet.github.io/schultzzznet/#corrections-2026-10-27).
>
> **V1.0 (retired 2026-11-10): retractions, 2026-10-09.** Earlier versions of this profile said "no single points of
> failure", "RPO 0, proven" and "Docker Swarm compatible", and that the AI runs inside the
> cluster. None of those was true when I checked. The worst was the second: the PostgreSQL 18
> cutover on 2026-09-16 silently dropped synchronous commit, so until it was restored on
> 2026-10-09 the application databases were asynchronous while the documentation said RPO 0.
> A guard now fails if a successor cluster loses that setting. Swarm was decommissioned and is
> not a fallback. The ops agent and its model run on a Mac outside the cluster, deliberately,
> because an operator that dies with the cluster is not an operator.

## The parts, briefly

**Platform.** K3s on six nodes built by playbook and reconciled from git, node-local storage, an operator-managed PostgreSQL cluster
with backups to an S3-compatible store on a small always-on Mac, admission policies and default-deny network rules (one probe failed, see above). Monitoring was merged on 2026-11-11 (its first live run failed on a missing-namespace defect in the node exporter manifests; the fix landed the same day, and its pods were Running at 07:00 UTC) and nothing from it has been read. V1.0 (retired 2026-11-10): it ran Ceph, MinIO, Prometheus, Loki, Grafana and Alertmanager; that is history. Apps are Spring Boot and
Flutter. It is standard Kubernetes, but I have not tested it on a managed distribution, so I do
not claim it would move unchanged.

**Scaling.** V1.0 (retired 2026-11-10): CPU-based autoscalers existed; not re-measured on the new one. Scaling on request rate is not built.

**Supply chain (V1.0 (retired 2026-11-10), as of 2026-10-27).** First-party images are signed with cosign using a local key, so this is
signing, not keyless Sigstore. As of 2026-10-27, 6 of the 7 first-party images running verify
against the release key, and the tracker has accepted 71 SBOMs. Acceptance is not analysis.
I rate it SLSA Build L2 myself; nobody has audited that. **Secrets:** every Secret in git has been
encrypted with SOPS and age since 2026-10-25; the old values are not yet rotated and the cluster does
not encrypt them at rest.

**AI (V1.0 (retired 2026-11-10), as of 2026-10-30; the agent is not part of the new cluster).** Alerting was a loop with two models and a person: alerts go straight to Slack, an hourly post is composed by code, a small local model answers questions and writes a morning digest, and a cloud model grades the agent's posts once a day (drafts only, no tools; it is sent alert text, so the claim that nothing leaves the house is retired, see [the loop](https://schultzzznet.github.io/schultzzznet/aiops.html#the-loop-two-models-one-human)). The ops agent answers in Slack, queries Prometheus, and proposes actions such as a node
drain or a scale, which a human approves with a button. It does not act alone. Since 2026-10-26 its
arguments are validated, only named approvers count, and what it says is recorded and graded
(a first review found "critical" in 79 of 96 summaries, with no critical alert firing in 69 of them). An orchestrator
that closes the whole delivery loop into one policy-gated workflow is not built; chaos injection
is partial: my last self-rating (2026-09) counted 2 of 31 planned failure scenarios.

**Embedded.** A custom Yocto layer on the 6.0 LTS release (wrynose) for a Raspberry Pi 3 B+: a
signed RAUC A/B image, updated over the air, with an SBOM and CVE scan. **The nightly upload of that
SBOM to the tracker failed every night from at least 2026-09-24 until it was fixed on 2026-10-27, and no device has reported back
since 2026-09-01** (corrected on the site on 2026-10-27). A signed update and a deliberate rollback have both
been proven on the board, and the same path now carries an image for a bench test rig. A Pi 3 cannot do
hardware secure boot, so the updates are signed and integrity-checked, but the boot chain is not
verified.

## Read more

All on the site, **<https://schultzzznet.github.io/schultzzznet/>**:

- [Recently](https://schultzzznet.github.io/schultzzznet/#recently): what changed, newest first, with dates.
- [What I'd do differently](https://schultzzznet.github.io/schultzzznet/lessons.html): the mistakes, with their costs, and [what four outside reviews found](https://schultzzznet.github.io/schultzzznet/lessons.html#13-what-outside-reviews-found).
- [Measurement traps](https://schultzzznet.github.io/schultzzznet/devsecops.html#6-measurement-traps-found-by-checking): confident, wrong numbers, found by checking.
- [The apps](https://schultzzznet.github.io/schultzzznet/apps.html): three Flutter apps (location, hazard warnings, messaging) with screenshots, and what is not finished.
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
| [`kured-args.yaml`](examples/kured-args.yaml) | A reboot daemon that logged "nothing to do" hourly for weeks while 16,002 patched-but-not-running findings piled up (V1.0, retired 2026-11-10). |
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
