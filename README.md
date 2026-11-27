# Christian Schultz

**Software product developer and development manager, backed by real hands-on work: product, development, production,
security and hosting, with AI at both ends, scaled for teamwork and happy customers.**

> I built an app. Then what? It needed a production environment to support it. So I built one.

**Discovery just became cheap. Delivery still has to be solid.** AI has brought the cost of a live-data prototype, a thin
working slice in front of real users, "way down" (Marty Cagan,
[The purpose of prototypes](https://www.svpg.com/the-purpose-of-prototypes/), 2025), and a prototype is not the product.
This platform is the other half: a slice that earns its place is built properly, signed, traced, backed up and drilled.
That makes proper discovery and proper delivery affordable for one person or a small team. No live-data prototype has met a real outside
user yet.

**What this is.** A platform to make an app and sustain it: the killer app, when it comes. That production environment is now
most of the work: a
product production platform, the whole path from an idea to a running app and the years after, built from current
open-source practice on six retired laptops and small desktops, by one person with a frontier AI model as a reviewed peer.
It is also a training system, on purpose. Not a pivot: it stays platform first, but in the end it is all about delighting
real customers who pay (none yet), and a platform is judged by the work built on it
([DORA](https://dora.dev/capabilities/platform-engineering/)). In the order the work meets it:

1. **Decide and make the app.** Product first: Marty Cagan's four big risks
   ([SVPG](https://www.svpg.com/four-big-risks/)) answered before a feature is built, then Henrik Kniberg's thin slices
   (Crisp), each testable, usable or lovable, the first on a real phone. The API contract first, with a breaking-change gate, a
   contract fuzzer and a client generated from it. Extreme programming: small pull requests and continuous integration
   are real; test first (TDD) is the aim, not a rule yet. Rapid application development: *an app in a day* is the aim,
   not yet timed. Both are plan items since 2026-11-27.
2. **Run it in production.** K3s on six machines, everything pulled from git by Flux, PostgreSQL with three copies and
   restore drills, failure drills up to pulling the plug.
3. **Ship it.** CI on home machines, one throwaway virtual machine per job, signed images and admission control.
4. **Watch it and keep it.** Metrics, logs, alerts and dashboards; upgrades as reviewed plays; dependency updates held
   for a click.
5. **AI agents in both.** A frontier model builds through the same gates as a person; a small local model watches the
   running cluster, read-only.

The platform is private; the write-up at **<https://schultzzznet.github.io/schultzzznet/>** is public.

**Why it is interesting.** It is pushed to the edge, to prove it holds, and every miss is published with a date, what was
done about it, and whether that is proven. If it runs on this hardware, it runs anywhere.

- **Two replicas is a count, not a property.** Two cluster DNS replicas passed a pod-kill drill, then a power-off stalled
  lookups for 51 seconds. **Done:** DNS on every node, **proven** by a power-off on 2026-11-25.
  [Lesson 15](https://schultzzznet.github.io/schultzzznet/lessons.html#15-highly-available-on-paper-is-not-highly-available)
- **An upgrade that kept the uptime and lost the guarantee.** A PostgreSQL major-version cutover silently dropped
  synchronous commit; for 23 days the site promised no lost writes and it was not true. An audit found it, not an alert.
  **Done:** restored and read back on every primary the same morning, and a guard now fails a new cluster that lacks a
  setting its predecessor had.
  [Reliability](https://schultzzznet.github.io/schultzzznet/reliability.html#the-upgrade-that-kept-the-uptime-and-lost-the-guarantee)
- **Seven controls, deployed, green and doing nothing.** One reboot daemon reported "nothing to do" hourly for weeks while
  16,002 patched-but-not-running findings piled up. **Done:** each fixed; the lasting rule, every control reporting when it
  last acted, is written and **not built yet**. [Measurement traps](https://schultzzznet.github.io/schultzzznet/devsecops.html#6-measurement-traps-found-by-checking)
- **Failover timings, fails included.** A database primary kill took 48.6 s against a 30 s target, because the pooler cached
  a failed login. **Done:** the pooler no longer holds a failed login; the re-run took 27.9 s. [The table](https://schultzzznet.github.io/schultzzznet/reliability.html#the-scenarios-and-how-each-piece-fared)
- **What the AI got wrong, counted.** An AI review the site called required had run on none of 41 pull requests.
  **Done:** the site stopped claiming it; an independent reviewer is still owed.
  [AI in development](https://schultzzznet.github.io/schultzzznet/ai-dev.html#who-reviews-honestly)

**What it can be used for.** The platform is kept ready to make the killer app and sustain it, so that on that day the
app is the only new work; the product layer (deciding what to build) is the youngest part. Until then the reference apps
stand in for it. From the site you can take:
[four runnable examples](examples/), failover checks to run against your own cluster, a
[drill method](https://schultzzznet.github.io/schultzzznet/how-we-work.html#10-failure-scenarios-simulate-then-pull-the-plug), laptop exercises in the
[Academy](https://schultzzznet.github.io/schultzzznet/academy.html), and a way of reporting where every claim has a date and *not measured yet* replaces a zero.

> **Not measured yet (2026-11-20):** SBOM projects, alerts reaching a person (they reach a chat channel, which pages
> nobody), and electricity cost.
>
> **In short, as of 2026-11-26.** V2.0, a new K3s cluster, built on 2026-11-10 and 11 on the same six machines, with no
> paying customers, no users and no load. It continues V1.0, which ran from 2025-12-21 to 2026-11-10 with 2,051 commits and
> 226 merged pull requests ([History](https://schultzzznet.github.io/schultzzznet/history.html)).
> **Proven, with limits:** admission policies refused an off-list image (2026-11-10); restore drills of the warning app's
> database (2026-11-10) and of the login service's database (2026-11-15) passed, on databases of megabytes, from one backup
> machine. **Software failure drills, 2026-11-16 and 17:** 17 run on the live cluster (pods, database primaries and
> standbys, the pooler, the ingress, cluster DNS, admission, node drains), 15 passed and none lost an acknowledged write. They
> found one design flaw, the connection pooler holding on to a failed login after a database failover, fixed and passed on a
> re-run with a thin margin; one miss, with both backup-plugin pods down, is still open.
> **Power-off drills:** on 2026-11-19 the first (a plain worker) passed and the second found a timing flaw: cluster DNS
> stalled for about 51 seconds and two of the probe's test writes failed. The fix, cluster DNS on every node, went live on
> 2026-11-20, and in the power-off of 2026-11-25 no lookup on another node failed: **cluster DNS is the first single point
> of failure proven fixed** (1 of 30). **Rule since 2026-11-20:** every failure scenario is rehearsed first in a
> simulated cluster shaped like home, then run live. **Failed:** the default-deny network probe (2026-11-10), because a new
> pod is open for one to three seconds. **Not live:** replicated storage, an off-site backup copy (a second copy sits on the
> house NAS), a public name.
> Figures that cannot be measured yet say "not measured yet". V1.0 is
> described in dated notes. Start with
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

## Now

What is moving this week, from the same data file as [the Now page](https://schultzzznet.github.io/schultzzznet/now.html).

<!-- now:start -->
<!-- Written by scripts/build-now.py from docs/_data/now.yml; edit the data file and run it with --write. -->

*As of 2026-11-27 09:32 UTC. Updated on every change of state; the full board, with what was done recently, is on [Now](https://schultzzznet.github.io/schultzzznet/now.html).*

**2 of 12** build-order steps done; **4 of 125** objective rules built (23 partly); **19 of 24** drills on the home site passed; **1 of 30** single points of failure fixed (14 open).

**Running now:**

- The failover fixes, one at a time on the simulated cluster against the measured baseline, now that its three weak scenarios are repaired.

**Waiting on the owner:**

- A key custody proof, about ten minutes; the workstation is free for it now.
- The second power-off drill again, at the machines, planned for the next morning.
- A decision on a trial that passed its first proof: take the next step, reject it, or try another option.
- A decision on whether dependency updates held for approval may flow on their own.

**Next, in order:**

1. The second power-off drill again (a worker holding a database standby).
2. In parallel with the failover fixes: the second reference app starts moving to the new platform, phone first, reachable only from the owner's own devices at first.
3. The third power-off drill, after the failover fixes, then the rest of the series and the upgrade phase ([Progress](https://schultzzznet.github.io/schultzzznet/progress.html)).

<!-- now:end -->

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

**2. Push it to the edge on the weakest hardware, to prove it holds.**

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
| Pods running | 72 |
| Kustomizations ready | 24 of 24 |
| Admission policies ready | 5 of 5 |
| Tenants with default-deny (structural count) | 11 of 11 |
| Database instances ready | 6 of 6 |
| Backup objects completed in the last 24 hours | 2 |
| Latest restore drill on the home site | 2026-11-15, pass |
| Single points accepted, fixed, open | 15, 1, 14 |
| Alert rules | 91 |
| Decision records | 20 |
| Run records (pass of total) | 100 of 137 |
| Test definitions (counted, not run) | 89 |
| CI workflows | 14 |

*Measured 2026-11-27T09:35:20Z by `make stats`. What each figure counts, and the command behind it: [the status page](https://schultzzznet.github.io/schultzzznet/status.html).*
<!-- stats:end -->

V1.0, frozen and measured by `scripts/gather-history.py`: 2,051 commits from 2025-12-21 to 2026-11-05, 226 merged pull
requests and 12,937 CI runs, torn down on 2026-11-10. Month by month, with receipts in this repository: [History](https://schultzzznet.github.io/schultzzznet/history.html).

## What this is, and is not

- **Is:** a training system, run to production standards on purpose. Real applications behind real
  identity, no paying customers yet, a CI/CD pipeline that deploys the apps, scheduled database backups,
  and a habit of checking every claim by something other than the thing making it.
- **Is:** preparation. When a killer app appears, the platform, the patterns and the habits should already be in place;
  on that day the direction changes, and production becomes the main line.
- **Is not:** a product with an availability commitment, or long-lived. The current cluster was built
  on 2026-11-10 and 11, after the previous k3s cluster (built on 2026-09-04) was torn down on 2026-11-10; it had followed an earlier k3s build and a
  Docker Swarm cluster decommissioned on 2026-06-09. The platform and its practice date from 2025-12-21; no single cluster
  does. "Months of uptime" would not be true.
- **Is not highly available throughout.** The rule is that a single point of failure on an app's own path (the app, its login,
  its database, what its writes and failover depend on, its object store) is never accepted; only the shared way in, power, the
  network, the internet line and supporting systems may be. Read on 2026-11-26, the register of single points holds 30 rows: 15
  accepted, 1 fixed and 14 open, and 7 of the open ones are on the warning app's own path (pods, database, the login service and
  its database, operator, backup plugin, scaling); 4 are on the shared path (among them the ingress and admission)
  and 3 are supporting systems. A row only moves to fixed when a machine is powered off and the app goes on; the one fixed row is
  cluster DNS, by a power-off on 2026-11-25. Storage is node-local.
  The software failure drills (17 on 2026-11-16 and 17) timed each piece's failover; the power-off drills began on 2026-11-19:
  the first passed, the second found the cluster DNS timing flaw and stopped the series. After the fix (live 2026-11-20) the
  series started again on 2026-11-25: the first drill passed and the second passed in part on two runs. From 2026-11-20 each
  scenario is rehearsed first in a simulated cluster shaped like home, then run live; five rehearsals ran there by 2026-11-25,
  three passed. See [High availability](https://schultzzznet.github.io/schultzzznet/reliability.html).
- **Is not zero-loss.** Two database clusters (the warning app's and the login service's) have three instances each, a
  synchronous standby asked for in the specification, and a nightly backup to one machine. Restore drills passed on 2026-11-10
  and 2026-11-15 on databases of megabytes. No acknowledged write was lost in the failure drills, which is a result of those
  drills, not a guarantee. Point-in-time recovery, a total-loss restore and an off-site copy are untested. V1.0's
  synchronous-commit figures are not carried over.
- **Is not a user base.** There are no users on the new cluster. The login service runs two replicas on its own database since
  2026-11-15. The apps are deliberately modest demos that exercise every layer.

> **V1.0 (retired 2026-11-10): corrections, 2026-10-27.** Five statements on the site had turned stale in the pessimistic direction
> (pull requests, secrets in git, drift checking, the ops agent, a runner count), two on the embedded page
> were false throughout, and the uptime shortfall now has a cause. They are listed, with dates, on
> [the estate page](https://schultzzznet.github.io/schultzzznet/#v10-retired-2026-11-10-corrections-2026-10-27).
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

**Platform.** K3s on six nodes built by playbook and reconciled from git, node-local storage, two operator-managed PostgreSQL clusters
(the warning app's behind a connection pooler; the login service connects directly) with backups to an S3-compatible store on a small always-on Mac, admission policies and default-deny network rules (one probe failed, see above). Monitoring was merged on 2026-11-11 (its first live run failed on a missing-namespace defect in the node exporter manifests; the fix landed the same day) and runs with two metrics replicas since 2026-11-19; read on 2026-11-20: 57 scrape targets up, 51 alert rules, 7 dashboards. Alerts reach a chat channel; nothing pages a person. The cluster moved to a newer minor release of K3s on 2026-11-18, node by node, by playbook. V1.0 (retired 2026-11-10): it ran Ceph, MinIO, Prometheus, Loki, Grafana and Alertmanager; that is history. Apps are Spring Boot and
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
