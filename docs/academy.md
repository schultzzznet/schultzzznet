---
title: Academy
reread: 2026-11-20
body_read: 2026-11-20
summary:
  - "**What it is:** the platform's major components, one module each, explained in depth: what problem each one solves, how it works inside, how it is set up here, and how it is operated day to day."
  - "**How each module is built:** the same seven parts every time: the problem, the mechanism, our shape, how we operate it, what is proven and what is not (dated, failures included), a hands-on exercise for a laptop, and further reading."
  - "**What is written (2026-11-20):** the pilot, three of thirteen modules: the big picture, CI at home, and Flux. The other ten are planned and listed below in reading order."
  - "**What it is not:** a manual for this estate. It names roles, not machines, and leaves out addresses, exact versions and anything private, so the mechanisms carry over to any small cluster."
---

# Academy

{% include in-short.html %}

The rest of this site says what the platform is and what has been proven about it. The Academy says how it works. Each module
takes one major component and goes through it slowly enough that a capable engineer who has never seen this estate could run
it, break it on purpose and put it back.

Every module has the same seven parts, so you can read across them:

1. **The problem it solves.** What would be manual, fragile or impossible without it.
2. **How it works.** The moving parts and the order they move in, with a diagram.
3. **Our shape.** How it is set up here, by role ("three servers with embedded etcd"), not by machine.
4. **How we operate it.** Changing it, upgrading it, watching it, and what we do when it breaks.
5. **Proven and not proven.** Dated, with the failures. The words are the site's four: proven, built, planned, open.
6. **Try it yourself.** A small exercise on a laptop with public tools (kind or k3d), no access to this estate needed.
7. **Further reading.** The projects' own documentation, and the other pages of this site.

## The modules, in reading order

The order follows a change: from the commit, through the pipeline, into the cluster, and then what keeps it running.

| # | Module | What it covers | State |
|---|---|---|---|
| 0 | [The big picture](academy-big-picture.html) | How a change travels from git to the running cluster, and why the cluster pulls | written |
| 1 | [CI at home](academy-ci.html) | One fresh virtual machine per job on our own hardware, the two pools, the gate, merge on green | written |
| 2 | Supply chain | SBOMs, the vulnerability scan and its triage, signing, the signature checked again at admission | planned |
| 3 | [Flux and GitOps](academy-flux.html) | The configuration as an OCI artifact, Kustomizations in order, drift, what Flux does not own | written |
| 4 | The K3s cluster | Servers and embedded etcd, the API's virtual address, upgrades node by node | planned |
| 5 | Network and DNS | The pod network, default-deny, DNS on every node (and the 51-second stall that taught us) | planned |
| 6 | Admission | Policies, audit before refuse, policy reports, the one dated exception | planned |
| 7 | Data | The Postgres operator, connection poolers, backups and their copies, restore drills | planned |
| 8 | Identity | The login service, its database, sessions across replicas | planned |
| 9 | Observability | Metrics, alerts, logs, traces, probes, and the heartbeat that says the alerting itself is alive | planned |
| 10 | Secrets | Encrypted secrets in git, key custody, rotation | planned |
| 11 | Breaking it on purpose | Simulate first, then pull the plug: drills, their referees and their records | planned |
| 12 | AI in operations | The analyst and the reviewer, how their answers are evaluated, what stays local | planned |

## How the modules are kept true

Each module is written from the platform's own runbooks, decision records and dated run records, then checked by an
independent pass against those sources before it is published, the same way as the rest of the site. The date at the top of
each page says when it was last checked against the system; the site's build fails when that date grows old, so a module
cannot quietly go stale. When a module and the [status page](status.html) disagree, the status page is the newer word.

## Where to start

New to the estate: read [the big picture](academy-big-picture.html) first, then follow the table. Interested in one component:
each module stands on its own, and links back to the big picture where it needs it. For what the platform is, not how it
works, start at [the estate](./) or [How we work](how-we-work.html).
