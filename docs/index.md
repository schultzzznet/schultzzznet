---
title: The estate
tldr_what: "A platform to make an app and keep it running for years: the killer app. It began with wanting to build one app. Six retired machines, one person, a frontier AI model. In order: make the app (product first, slices, contracts, tests), run it (K3s, GitOps, drills), ship it (CI/CD), watch and keep it, and AI agents in both."
tldr_why: "It is pushed to the edge, to prove it holds, and the misses are published with dates. A power-off showed cluster DNS stalling for 51 seconds; on V1.0 a database upgrade silently dropped synchronous commit for 23 days; seven controls sat green and did nothing. If it runs on this hardware, it runs anywhere."
tldr_use: "It is kept ready to make the killer app and sustain it; the product half (deciding what to build) is the youngest part. You can take failover timings to hold against your own cluster, a drill method, exercises and four runnable files in [examples](https://github.com/schultzzznet/schultzzznet/tree/main/examples)."
reread: 2026-11-26
body_read: 2026-11-26
summary:
  - "**What it is:** a platform to make an app and sustain it, the killer app; it began with wanting to build one app. It is also a training system on retired hardware, built from the current state of the art, with DevSecOps as one layer. Reliability is the aim, not yet a claim."
  - "**Proven, with limits (dated):** admission refused an off-list image (2026-11-10); restore drills of two databases passed (2026-11-10 and 2026-11-15, megabytes), and one on 2026-11-24 was partial (an older backup stopped at a segment the store could not serve). 17 software failure drills (2026-11-16 and 17): 15 passed, none lost an acknowledged write. The default-deny probe failed (a 1-3 s gap at pod start)."
  - "**Power-off drills:** on 2026-11-19 the second found cluster DNS stalling for about 51 s; the fix, DNS on every node, went live on 2026-11-20, and in the power-off of 2026-11-25 no lookup on another node failed. Cluster DNS is the first single point proven fixed, 1 of 30 ([Progress](progress.html)). Every failure scenario is now rehearsed in a simulated cluster shaped like home before it runs live."
  - "**Not live (2026-11-26):** alerts that page a person (they reach a chat channel), replicated storage, an off-site backup copy (a second copy sits on the house NAS), a public name, two of the three reference apps."
  - "**History:** the cluster is new; the platform is not. V1.0 ran from 2025-12-21 to 2026-11-10 (Docker Swarm first, k3s from 2026-04, Swarm retired 2026-06-09): 2,051 commits and 226 merged pull requests, written up here in public since 2026-04-18. V2.0 is its next step on the same six machines: [History](history.html)."
  - "**V1.0 against V2.0:** [a dated diff list](versions.html), including where V1.0 did better. V2.0 is declarative and pull in the cluster, scripted and push at the edges, so not fully GitOps yet ([two axes](how-we-work.html#two-axes-what-you-write-and-who-applies-it)). V1.0's own figures stay lower on this page under dated headings; none is a claim about the new cluster."
---
{% assign s = site.data.stats %}
{% assign c = s.cluster %}
{% assign st = s.storage %}
{% assign rc = s.reconciler %}
{% assign ad = s.admission %}
{% assign db = s.databases %}
{% assign ev = s.evidence %}
{% assign ci = s.ci %}
{% assign rp = s.repo %}
{% assign hw = s.hardware %}
{% assign hv = site.data.history.v1 %}
{% assign gen_date = s.generated_at | date: "%Y-%m-%d" %}

# A complete SDLC platform, so good that the work is delighting customers, not fighting the platform

**Develop, improve and sustain my apps with agentic AI and agile practice, on open-source software, aiming for best in
class: hybrid cloud and home, six retired machines and CI on two iMacs from 2013, pushed to the edge, through real
failures, to prove it holds.**

{% include tldr.html %}

## Why it exists

> I built an app. Then what? It needed a production environment to support it. So I built one.

It started with an app. Running it for real meant building everything around it: somewhere to run it, a way to ship
every change safely, eyes on it once it runs, and a way to keep it up to date for years. That infrastructure became the
bigger part of the work, and the larger part of this site.

The real purpose is still the app: to **make an app and sustain it**, the killer app, when it comes. The platform is kept
ready so that on that day the app is the only new work. The other aims still hold: learn on hardware nobody would choose,
use the current state of the art, and be production ready, proven by drills rather than claimed. No killer app is named
yet; the reference apps stand in for it.

This is not a pivot: the work stays platform first. But a platform is judged by what gets built on it, and in the end
that means **delighting real customers who pay**. So product practice comes first on the path. Before a feature is
built, Marty Cagan's four big risks are answered: will people value it, can they use it, can it be built, does it work
for the business ([SVPG](https://www.svpg.com/four-big-risks/)). It is then built in Henrik Kniberg's thin slices, each one
testable, usable or lovable, the first on a real phone (*Making sense of MVP*, Crisp). There are no paying customers yet,
and the product layer is the youngest part. [Product practice](product.html)

The platform will be judged the same way. DORA's research on
[platform engineering](https://dora.dev/capabilities/platform-engineering/) measures a platform by the success of the work
built on it, not by its features. DORA's four keys (how often a change ships, how long a change takes to reach production,
how many changes fail, how fast service comes back after a failure) are planned as the platform's own figures, read
from git, the pull requests, the cluster's pull loop and the drill records. None is published yet (2026-11-27).

## The path, layer by layer

One app's way from an idea to production and through the years after, in five layers and in the order the work meets
them. Each line says what is built and what is only the aim, with a date. Read 2026-11-27.

**1. Decide and make the app: product first, rapid (RAD), test first (XP, TDD), contract first.**
- **Product first, in thin slices** (a practice since 2026-11-17): every feature gets a four-risk box (value, usability,
  feasibility, viability: who judges, the cheapest test, the result), after Marty Cagan. It is built in slices after
  Henrik Kniberg, the riskiest first, and the first slice runs end to end on a real phone before the rest is built.
  [Product practice](product.html)
- **Contracts first** (built for the warning app): its API is a written OpenAPI contract. A pull request that breaks it
  fails a breaking-change gate; the test-cluster gate fuzzes the live app against it (eight faults when added,
  2026-11-07 and 08, and a real bug on 2026-11-11); the phone client is generated from it, and a check fails if the two
  drift. Of the 12 contract rules in the plan, 3 are partly built. Consumer-driven contracts are later.
  [Quality](quality.html#the-contract-testing-story-and-the-trap-inside-it)
- **Rapid application development: an app in a day** (an aim, a plan item since 2026-11-27). After James Martin's
  *Rapid Application Development* (1991): working software early, in short timeboxes, with the user. An app lands by one
  tenant entry, without touching platform code. Today: the warning app did it once, by its author, untimed. Next: the
  location app's first slice is the first timed run, from an empty repository made from the template to a real phone,
  with every hold-up published. [Applications](applications.html)
- **Extreme programming, test first included** (partly real, the rest an aim and a plan item since 2026-11-27). After
  Kent Beck's *Extreme Programming Explained* and *Test-Driven Development: By Example*. Real today: small pull requests,
  continuous integration on every change, the AI as the pair that writes and the checks as the referee. The aim: test
  first (TDD) as a rule for app work, starting with the location app, and a published share of app changes that add or
  change a test with the code. Today tests exist in the warning app, but test first is not a rule and is not measured.

**2. Run it in production: K3s, GitOps, reliability.** {{ c.nodes_ready | default: "6" }} machines in one K3s cluster;
Flux pulls everything in the cluster from git; databases run three copies with restore drills; 17 software failure drills
and five power-offs so far. Reliability is the aim, not yet a claim. [Reliability](reliability.html),
[How we work](how-we-work.html)

**3. Ship it: CI and CD.** Every pull request runs on home machines, one throwaway virtual machine per job, on two iMacs
from 2013 and a spare laptop; hosted runners take only the few jobs that hold a key or a write token. Images are signed and
admission refuses anything off the list; the cluster pulls a merged change within minutes.
[The delivery chain](platform.html), [DevSecOps](devsecops.html)

**4. Watch it and keep it: telemetry and maintenance.** {{ s.observability.scrape_targets }} scrape targets,
{{ s.observability.alert_rules }} alert rules and {{ s.observability.dashboards }} dashboards, about
{{ s.observability.metric_history_days }} days of history. Upgrades run as reviewed plays (K3s, 2026-11-18; the database
operator, 2026-11-25), and dependency updates wait on a click. Alerts reach a chat channel, not yet a person.
[Status](status.html), [Progress](progress.html)

**5. AI agents, in building and in running.** In development a frontier cloud model writes the changes, and every one
passes the same gates as a person's ([AI in development](ai-dev.html)). In production a small local model answers
questions about the cluster, read-only since 2026-11-25, and executes nothing ([the operations agent](aiops.html)).
A frontier model at run time is not built.

**Hybrid, on purpose.** Each part runs where it does best. In the cloud: the code host, the few CI jobs that need a key,
and the frontier model that builds with us. At home: the cluster, everyday CI, the small local model that watches it, and
the backups (there is no off-site copy yet). Home is cheap and teaches the most; the cloud buys what home cannot do well.
[Academy: CI at home](academy-ci.html)

## What we hold ourselves to

{% assign p = site.data.progress %}
Four aims and fourteen objectives, set in the platform's charter and sharpened on 2026-11-27 around the purpose above.
Each objective is a promise with a page of rules, and every rule names the check that would prove it. A rule counts as
built only when its check runs and passes, so most of them are aims today, and they are shown as aims. Counts on
{{ p.as_of }}: {{ p.counts.rules_built }} of {{ p.counts.rules_total }} rules built, {{ p.counts.rules_partly }} partly built,
{{ p.counts.rules_not_built }} not built ([Progress](progress.html)).

| Aim | Objective | In plain words | Rules: built, partly, of |
| --- | --- | --- | --- |
{% assign o = p.objectives | where: "name", "Product first" | first %}| Product and Flow | **Product first** | We decide what is worth building with the people it is for, before we build it, and say "no customers" until there are some. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Flow" | first %}| Product and Flow | **Flow** | A change reaches a user fast and safely: small slices, test first, and DORA's four keys against the best published band. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Contracts" | first %}| Production Ready | **Contracts** | Every app states in a written contract what it offers and who may call it, before the code. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Production-ready apps" | first %}| Production Ready | **Production-ready apps** | An app is ready for a stranger to install, trust and get help with, and every new app starts from the same base. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Recover" | first %}| Production Ready | **Recover** | Backups count when restored and failover counts when someone pulled the plug. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Portable" | first %}| Production Ready | **Portable** | The same git repository runs on a cloud cluster or in someone else's hosting, with a way out of every service. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Many hands" | first %}| Production Ready | **Many hands** | A new developer, a person or an AI with no memory, joins and ships from the docs alone. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Git is the only way" | first %}| State of the Art | **Git is the only way** | Every change is in git first and the machines pull it; a hand fix is found and reverted. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Secure by default" | first %}| State of the Art | **Secure by default** | Security is in the first version and graded by outside tools, not by us. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Observe and operate" | first %}| State of the Art | **Observe and operate** | We know something is wrong before a user does, and every alert is tested by making it fire. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "AI in development" | first %}| Learning Platform | **AI in development** | The AI that writes code is a developer with its own login, least access and its work reviewed. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "AI in production" | first %}| Learning Platform | **AI in production** | AI watches and advises, a person decides, and its answers are graded. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Learning" | first %}| Learning Platform | **Learning** | We try what teaches most, and the tests decide what stays. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |
{% assign o = p.objectives | where: "name", "Shown in the open" | first %}| Learning Platform | **Shown in the open** | Plain words, dated claims, misses next to wins, tested on readers from outside. | {{ o.built }}, {{ o.partly }}, of {{ o.rules }} |

The key results score the work each quarter from 0 to 1: about 0.7 is a good score and 1.0 is the stretch, on purpose.
Three stretch rungs were added on 2026-11-27: all four of DORA's keys at the top band of the DORA report current at
scoring; every app change carrying a test, enforced; and five readers from outside who, given only this site for ten
minutes, say correctly what it is and why it is interesting. The key results are still a draft, and none has been scored
yet.

## Why it is worth your time

Seven findings, each with a number and a link to the full account.

- **Two replicas is a count, not a property.** Two cluster DNS replicas on two machines passed a pod-kill drill, then
  failed a real power-off: lookups on the other nodes stalled for 51.1 s. A throwaway cluster reproduced it in six runs of
  six. The fix, DNS on every node, was proven by a power-off on 2026-11-25.
  [Lesson 15](lessons.html#15-highly-available-on-paper-is-not-highly-available)
- **Failover timings, fails included.** A database primary kill under a write probe took 48.6 s against a 30 s target,
  because the connection pooler cached a failed login for 15 s. After the fix: 27.9 s. No acknowledged write was lost in
  the software drills. [The table, piece by piece](reliability.html#the-scenarios-and-how-each-piece-fared)
- **An upgrade that kept the uptime and lost the guarantee.** On V1.0 a PostgreSQL major-version cutover with no
  maintenance window silently dropped synchronous commit. For 23 days the databases were asynchronous while this site said
  no committed write could be lost. An audit found it, not an alert.
  [The account](reliability.html#the-upgrade-that-kept-the-uptime-and-lost-the-guarantee)
- **Seven controls that were deployed, green and doing nothing.** One of them: a reboot daemon checked a path inside its
  own container and reported hourly, for weeks, that no reboot was needed, while 16,002 patched-but-not-running findings
  piled up. [Lesson 5](lessons.html#5-believing-status-output-repeatedly) and
  [the measurement traps](devsecops.html#6-measurement-traps-found-by-checking)
- **A quorum loss that nothing detected.** A mains drop of under a minute crashed two of three control-plane machines. For
  9 minutes 12 seconds the survivor was one vote short of a quorum, and nothing monitored the state store. A person felt
  the lights go out. [The post-mortem, in full](incident.html)
- **CI on old desktops, one throwaway virtual machine per job.** Every pull request job runs at home since the hosted
  minutes and the $20 limit ran out. A job's machine takes one job, holds no secret and has no route out except an
  allow-list proxy and DNS. 470 jobs in five days; a job that waits on no other started after a median of 1.2 minutes.
  [Academy: CI at home](academy-ci.html)
- **What the AI got wrong, counted.** On V1.0 a request for an AI review was rejected by the code host while the job
  stayed green: none of 41 pull requests had the review this site said was required. An operations agent wrote "critical"
  in 79 of 96 summaries, with no critical alert firing in 69.
  [AI in development](ai-dev.html#who-reviews-honestly), [the agent](aiops.html#the-agent-since-2026-10-26)

## What you can use it for

**The platform itself** is a product production platform: the whole path from an idea to an app that runs and stays up,
deciding what to build, building it, shipping it safely and running it. DevSecOps is the delivery and run layer of it, and
the most proven one; the product layer (testing an idea before building it, cutting it into small slices) is the youngest: [Product practice](product.html).
It is kept ready for any app, so that on the day an app matters, the app is the only thing that needs attention. Until
then it is a training system, on purpose. Today it carries one of three reference app backends (the
hazard-warning one: Spring Boot, with a Flutter client) and its login service. The embedded Linux image, a rover and
printed parts are the other workloads ([Applications of the platform](applications.html)). It is not a service anyone
else can use, and its repository is private.

**What you can take away:**

- **Code.** Four commented, MIT-licensed files in [`examples/`](https://github.com/schultzzznet/schultzzznet/tree/main/examples):
  an alert rule for a signal that sawtooths across its threshold, reboot-daemon arguments, a systemd timer trap, and a host
  CVE scan script with a self-test that shows its own bug. Also the
  [guard scripts](https://github.com/schultzzznet/schultzzznet/tree/main/scripts) that fail this site's build on a leaked
  hostname or a stale number.
- **Checks for your own cluster.** Does cluster DNS survive a machine that stops without warning, not only a pod kill?
  Does the pooler cache a failed login after a failover? Is every replica streaming? The mechanisms are on
  [Reliability](reliability.html) and [Lessons](lessons.html).
- **A drill method.** A probe as referee, a time target where a miss is a fail, an abort rule, a rehearsal on a simulated
  cluster first, and a single point counted as fixed only after a machine was powered off:
  [How we work](how-we-work.html#10-failure-scenarios-simulate-then-pull-the-plug), [Progress](progress.html).
- **Exercises for a laptop.** The same pull-based GitOps loop with kind and the flux command line in about 20 minutes, and
  an allow-list CI job with k3d in about ten: [Academy](academy.html).
- **A way of working with an AI model.** No exemption from the checks, a person approves what is merged, and review
  findings go to a second pass told to refute them: [AI in development](ai-dev.html),
  [lesson 13](lessons.html#13-what-outside-reviews-found).
- **A way of reporting.** Four status words (proven, built, planned, open), a date on every claim, *not measured yet* in
  place of a zero, retractions kept, and [a diff of V1.0 against V2.0](versions.html) that lists where the old one was
  better.

## The short account

**What else is here.** Beside the cluster: an embedded Linux image with signed A/B updates ([Embedded](yocto.html)), the
reference apps ([The apps](apps.html)), and printed parts built from source ([Printing](printing.html)). The platform
itself, with details and dates: [Platform](platform.html), [DevSecOps](devsecops.html), [Reliability](reliability.html),
and [Status](status.html) for what is proven, built, planned and open.

**Why it is built this way.** To prove it is possible: that one person, with AI doing much of the building and a person
approving what is merged, can run this whole stack well on the weakest hardware available. **The hardware is the handicap,
chosen on purpose:** retired laptops and small desktops (the ones audited date from 2011 to 2020). If it runs here it runs
anywhere, and any other hardware is an upgrade. And to learn as much as possible, hands-on, before the day a killer app
appears. Until then nothing is protected for uptime's sake; on that day production becomes the main line and the
experiments move to a branch.

**Where it stands.** The cluster is new; the platform is not. V1.0 ran for {{ hv.days }} days from {{ hv.first_commit }},
with a commit in every calendar month from December 2025 to November 2026 ([History](history.html), month by month, with
receipts in this public repository). On 2026-11-10 it was torn down, and the same six machines were rebuilt as a new K3s
cluster that day and the next: about {{ c.age_days }} days old by the count below, so no uptime is claimed, and
reliability is the aim, not yet a claim. The drills are in the *In short* block below and on
[Reliability](reliability.html). Two things it leaves out: one miss from the software drills
is still open (with both backup-plugin pods down the failover started late), and two failed lookups in the first soak of the
DNS fix are not explained. Single points proven fixed by a power-off: {{ ev.single_points_fixed }} of
{{ ev.single_points_accepted | plus: ev.single_points_fixed | plus: ev.single_points_open }} rows in the register
([Progress](progress.html)).

**No paying customers, no users and no load.** The synthetic load generator went with V1.0, and there is no public name.
Monitoring runs and has been read: merged on 2026-11-11 (its first live run failed on a missing-namespace defect in the
node exporter manifests, fixed the same day), two metrics replicas since 2026-11-19, and at the last reading
{{ s.observability.scrape_targets }} scrape targets up, {{ s.observability.alert_rules }} alert rules and
{{ s.observability.dashboards }} dashboards. Alerts reach a chat channel since 2026-11-16 (about six and a half minutes
after the machine went dark in the first power-off drill); nothing pages a person. **Not measured yet (2026-11-26):** SBOM
projects in a tracker, alerts reaching a person, and electricity cost. A figure below that cannot be measured yet says *not measured
yet*. What V1.0 measured and corrected is kept further down under dated headings and is not a claim about this cluster.

{% include in-short.html %}

## Where to start

| You have | Read |
|---|---|
| **2 minutes** | The *In short* block above, then *Recently* below |
| **How it got here** | [History](history.html): V1.0 from 2025-12-21 to 2026-11-10, month by month, the dated milestones, and receipts anyone can check |
| **What changed since V1.0** | [V1.0 and V2.0: what changed](versions.html): the diff list, area by area, with a status word on every V2.0 row |
| **How it works today** | [How we work](how-we-work.html): changes, secrets, admission, approvals, home CI, and the restore drill, each dated and marked proven or not |
| **5 minutes** | Add [the measurement traps](devsecops.html#6-measurement-traps-found-by-checking), seven controls that were configured, green, and inert (found on V1.0, retired 2026-11-10; the habit carries over) |
| **20 minutes** | Add [reliability](reliability.html), which describes the new platform's failure scenarios and the drills run against them (no uptime; the first machines were switched off on 2026-11-19), and [what outside reviews found](lessons.html#13-what-outside-reviews-found), which is about V1.0 (retired 2026-11-10) |
| **One story** | [One incident, in full](incident.html), from 2026-08-20 on V1.0 (retired 2026-11-10): a SEV1 quorum loss nothing detected, published because omitting it would be more impressive and less true |
| **An hour** | Add [the delivery chain](platform.html), which describes the new platform (its V1.0 parts are labelled), and [the operations agent](aiops.html), which is V1.0 (retired 2026-11-10); [AI in development](ai-dev.html) is the cloud half of the AI story |
| **Code** | [`examples/`](https://github.com/schultzzznet/schultzzznet/tree/main/examples), four extracted, runnable, commented artifacts, one with a self-test that demonstrates its own bug |
| **Tooling arguments** | [Why these tools, and what got rejected](choices.html) |
| **Hiring** | [What I'd do differently](lessons.html) is probably the most informative page here |
| **The rest** | [Quality and self-graded maturity](quality.html), [legal and regulatory posture](compliance.html), [the embedded side](yocto.html), [the mechanical side](printing.html), [live status](status.html), [where the work stands](progress.html), [what is moving now](now.html). Pages that still describe V1.0 (retired 2026-11-10) say so at the top or carry its dates |

## Recently

What changed, newest first. Each line is dated, the full account is on the page it links to, and
a check fails the build if this list stops being recent.

<ul class="recently">
{%- for r in site.data.recently %}
  <li><strong>{{ r.date | date: "%-d %b" }}.</strong> {{ r.text | markdownify | replace: "<p>", "" | replace: "</p>", "" | strip }}</li>
{%- endfor %}
</ul>

## Right now

Measured **{{ s.generated_at }}** by a script that queries the running cluster, not typed in.
How each figure is counted is on [the status page](status.html). This is a snapshot of a cluster that
was built on 2026-11-10: it says what exists, never how long it has stayed up.

{% assign ready_color = "2EA44F" %}{% if c.nodes_ready != c.nodes %}{% assign ready_color = "D9534F" %}{% endif %}
{% assign kust_color = "2EA44F" %}{% if rc.kustomizations_ready != rc.kustomizations %}{% assign kust_color = "D9534F" %}{% endif %}
![nodes ready](https://img.shields.io/badge/nodes%20Ready-{{ c.nodes_ready }}%20of%20{{ c.nodes }}-{{ ready_color }}?logo=kubernetes&logoColor=white)
![control plane](https://img.shields.io/badge/control%20plane-{{ c.control_plane }}%20servers-419EDA)
![pods](https://img.shields.io/badge/running%20pods-{{ c.pods_running }}%20of%20{{ c.pods_total }}-326CE5)
![reconciler](https://img.shields.io/badge/Kustomizations%20Ready-{{ rc.kustomizations_ready }}%20of%20{{ rc.kustomizations }}-{{ kust_color }})
![postgres](https://img.shields.io/badge/PostgreSQL%20instances%20ready-{{ db.instances_ready }}%20of%20{{ db.instances }}-4169E1?logo=postgresql&logoColor=white)
![policies](https://img.shields.io/badge/admission%20policies-{{ ad.policies_ready }}%20of%20{{ ad.policies }}-575757)
![fleet](https://img.shields.io/badge/fleet-{{ c.cores }}%20cores%20%C2%B7%20{{ c.ram_gb }}%20GB-575757)

Also in that run: {{ c.namespaces }} namespaces, {{ c.restarts_total }} container restarts since the
cluster was built (23 of them by 2026-11-11: the reference app's two pods restarted ten times each during the bring-up, one control-plane server's virtual-address pod twice and the tracing pod once, no cause verified; the failure drills since then kill pods on purpose),
{{ ad.network_policies }} network policies across {{ ad.tenant_namespaces }} tenant namespaces,
{{ db.backups_24h }} database backups completed in the last 24 hours, {{ db.backups_failed }} failed among
{{ db.backups_total }} on record, and WAL archiving on {{ db.archiving_clusters }} of {{ db.clusters }}
database clusters. The latest restore drill (recorded {{ ev.restore_drill_home_last }}, result
{{ ev.restore_drill_home_result }}) and the default-deny probe ({{ ev.default_deny_probe_home_date }}, result
{{ ev.default_deny_probe_home_result }}) are recorded results, not live checks.

| Measured on the new cluster | State at the generation time above |
|---|---|
| Metric scrape targets up | {{ s.observability.scrape_targets }} |
| Alert rules loaded | {{ s.observability.alert_rules }} alerting rules and {{ s.observability.recording_rules }} recording rules; they reach a chat channel (built 2026-11-16), and alerts reaching a person are **not measured yet** |
| Dashboards | {{ s.observability.dashboards }} (committed to git) |
| Metric history held | about {{ s.observability.metric_history_days }} days (the shorter of the two metrics replicas; the second is new since 2026-11-19) |
| Storage replication | none: node-local volumes only (a reviewed trade; replicated block storage is planned again, decision record first, kept on 2026-11-22) |
| Off-site backup copy | none (open). A second copy on the house NAS pulls from the store since 2026-11-24, and the newest backup restored from it that day |
| First-party images that verify against the release key | admission checks this at creation; a count is **not measured yet** |

**The three outside-referee badges are retired.** The scheduled-jobs heartbeat and the two public-endpoint
uptime probes graded V1.0 from outside it. Their monitors were paused when V1.0 was torn down on 2026-11-10, and there is no public endpoint for a probe to watch. Since 2026-11-16 one outside referee is back: an
off-site dead-man's switch on the alert heartbeat, which noticed a planted silence in about ten minutes in its test. It tells the owner, not this page, so the figures above are still the cluster describing itself, and the page says so.

{% comment %}V1.0 material follows after the new-platform sections.{% endcomment %}

## None of this is a demo

The repository for the platform is {{ rp.age_days }} days old, with {{ rp.commits }} commits, and it is a **new,
private repository started on 2026-11-05**. It follows the old one, kept as a record, whose {% include thousands.html n=hv.commits %} commits run from
{{ hv.first_commit }} to {{ hv.last_commit }}, with {{ hv.merged_prs }} merged pull requests; V1.0 itself was torn down on
{{ hv.retired }} ([History](history.html)). The **current cluster is {{ c.age_days }} days old** and has no uptime to boast about. The one
before it, V1.0's last k3s build, ran from {{ hv.last_cluster_built }} to {{ hv.retired }} and was torn down on purpose;
before that came an earlier k3s build from 2026-04 and a Docker Swarm cluster until 2026-06-09. That is not a hole
in the record, it is the record. Components are meant to be disposable, and
several have been disposed of. What has persisted is the practice around the cluster, not the cluster.

The chains here are meant to be wired end to end: commit, CI-built artifact, signed image, admission, and a reconciler
that pulls the result in; backup, then restore drill. As of 2026-11-26 I have seen the first of these
run on the new cluster ({{ rc.kustomizations_ready }} of {{ rc.kustomizations }} Kustomizations Ready), nightly backups complete, two
restore drills pass (2026-11-10 and 2026-11-15, with limits, described in [how we work](how-we-work.html)) and a third end partial
(2026-11-24: the newest backup restored from the store and from the NAS copy, an older one stopped at a log segment the store
could not serve), database failovers under a write probe in the failure drills of 2026-11-16 and 17, a second backup copy on
the house NAS (since 2026-11-24), and one single point of failure, cluster DNS, proven fixed by a power-off (2026-11-25). Of five
power-off drills, two passed, two were partial and one failed. I have **not** seen an alert page a person, a failover under
real load, or an off-site backup copy. Device heartbeats were retired for now on 2026-11-22. The satellite application is not running. It is a home-built platform
with {{ c.nodes }} bare-metal nodes from retired laptops and small desktops, run with production habits and with no production duties.

**V1.0 (retired 2026-11-10).** V1.0 was torn down in stages after a base backup of every database; the
machines were kept and now run the new cluster. Eight restore drills that were due were waived by the owner, because V1.0
was by then being treated as a test. Of V1.0's 257 alerts, 74 mechanisms and 16 power-off proofs (as of 2026-10), **none is carried
over**, and the cutover gate (the checklist that must pass before this cluster is treated as the platform) has **not** been passed.
The status register generated on 2026-11-10 counts 12 steps (2 done, 2 done only on a local test cluster, 5 partly done,
2 not started, 1 gated) and 109 rules (3 built, 19 partly built, 87 not built). Those numbers, not the old self-grades, are the
current maturity claim.

## A testing ground, not yet load-bearing

On V1.0 this was both a testing ground and load-bearing. Today only the first is true: nobody depends on
the new cluster. These pages describe *a* way through, written down with the
alternatives passed over, and each rejection names the condition that would change the
answer, because a rejection without a reopen-trigger is just an opinion. The damage would
be getting stuck: settling into caution before there is a reason to, so that nothing more is learned. The reason, when it comes, is a killer app; on that day production becomes the main line on purpose.

## The whole thing, on one screen

Status as of 2026-11-26. Solid boxes exist and are running.

```mermaid
flowchart TB
  subgraph DEV["Development, off-cluster"]
    WS["workstation<br/>+ cloud model as reviewed peer"]
    GH["GitHub<br/>pull request, checks"]
    CI["CI<br/>a fresh home VM per job<br/>hosted only where a secret forces it"]
    REG["image registry<br/>+ CI-built artifact"]
  end

  subgraph K3S["Six nodes: 3 servers with etcd (also run workloads) + 3 laptop agents"]
    FLUX["Flux<br/>pulls the artifact"]
    ADM["admission engine<br/>refuses unsigned or unlisted images"]
    TEN["tenant namespaces<br/>default-deny"]
    APP["reference app<br/>+ 3-instance PostgreSQL"]
  end

  subgraph OFF["Outside the cluster"]
    S3["S3-compatible store<br/>on a small always-on Mac"]
    NAS["second copy<br/>on the house NAS<br/>no off-site copy"]
  end

  WS --> GH --> CI --> REG
  REG --> FLUX
  FLUX --> ADM --> TEN
  TEN --> APP
  APP -->|"nightly backup + WAL"| S3
  S3 -->|"pulled by the NAS"| NAS

  style OFF fill:#f5f5f5
```

Left out to keep the picture to the delivery and data chains: the monitoring stack (merged 2026-11-11, read since), the
public edge (configured from git since 2026-11-25, and it publishes nothing), the outside referees (a dead-man's switch on
the alert heartbeat since 2026-11-16, and a probe board that runs the public attack cases from outside since 2026-11-25) and
the operations agent (back since 2026-11-25, read-only). The embedded devices update themselves and no longer report to the
cluster (heartbeats retired for now on 2026-11-22). No vulnerability tracker and no scheduled fault injector exist. V1.0's
picture is described in words in [V1.0 section](#v10-retired-2026-11-10) below.

## What it costs

| | |
|---|---|
| **Hardware** | The same {{ c.nodes }} machines, all retired or second-hand: laptops and small desktops. Old on purpose: the handicap is the point, because if it runs here it runs on anything better. It also cost next to nothing. |
| **Software licences** | **Zero.** Every tool is open source, a community edition, or a free tier. That is a standing constraint, and a filter: a tool that cannot be self-hosted for nothing does not get evaluated on features. |
| **Power** | One measurement exists. V1.0 (retired 2026-11-10), 2026-10: fixing the frequency governor on the two busiest nodes cut about 13.1 W continuously (about 115 kWh/year). It was measured with the CPUs' own energy counters, **not re-measured** on the new cluster, so no power figure is claimed for it. |
| **Time** | Evenings and weekends, over months. The up-front cost is real: {{ rp.adrs }} decision records so far in the new repository, refusing shortcuts that would have worked in the short run. |
| **Cloud spend** | Not zero any more. The included hosted CI minutes ran out on 2026-11-09 and a $20 budget began to be spent, at about $0.15 per hosted gate. Since 2026-11-12 every job runs at home on a fresh virtual machine per job, and a hosted runner is used only where a secret forces it, such as publishing and signing. The Mac runners were retired on 2026-11-10. Status: built; the saving is not measured. |

**One thing is not free.** The frontier AI used as a development peer is a paid
subscription. It reaches the running cluster only through plays, upgrades and drills run on the owner's go, each with a run
record. The largest cost of all
was **re-deriving context**, which is why the working agreement, the decision records and the
rolling state note exist.

## The apps

The load the platform is meant to prove itself against is three of the repository's five Flutter clients: **Loc8** shares location
inside invite-only groups, **Warn** maps road hazards people report, and **Talk** is a
messenger with live events. **As of 2026-11-26 only Warn is deployed on the new cluster**, with the login service it signs in
through. Loc8 and Talk are not, so this page quotes no version for them; Loc8's first slice is next, after the second
power-off drill. The Warn pods restarted ten times each during the bring-up on 2026-11-10 (cause not verified) and had not restarted in the seven hours before the read on 2026-11-11. They are not a product: not in any app store, built to talk to a
private homelab, with the unfinished parts listed. [The apps page](apps.html) has
screenshots, how they sign in, and the bug that signed people out for the wrong reason (written when all three ran).

## Repositories

Nine repositories show active work. **The platform is now a new private repository** ({{ rp.commits }} commits since it
was started on 2026-11-05, as of {{ gen_date }}); the old one ({% include thousands.html n=hv.commits %} commits from {{ hv.first_commit }} to {{ hv.last_commit }}, see [History](history.html)) is kept as a record and receives no platform changes. The embedded Linux layer, a
satellite application and the mechanical repository also get attention on this site; the rest are
a mowing robot, a drone swarm, a rover platform, a video rover and an i.MX8 layer. Commit
counts, as of {{ gen_date }}: embedded Linux {{ hw.yocto_commits }},
mechanical {{ hw.printing_commits }}, mower {{ hw.mower_commits }}, rover platform
{{ hw.rover_platform_commits }}, video rover {{ hw.video_rover_commits }}, i.MX8 {{ hw.imx8_commits }}.
They shared a registry, signing keys and a vulnerability tracker on V1.0; on the new
one the registry and signing exist and the tracker does not (planned).

The satellite was the proof, on V1.0, that **an application does not have to live in the
platform's repository to run on it.** It brought two files, a Dockerfile and a conformant
manifest. **It is not running on the new cluster** (as of 2026-11-26: not redeployed, and not in the new platform's inventory), so "deploys from outside" is a statement about
the past until it is. *History:* V1.0's repository name was a fossil: it began on Docker Swarm and ran on k3s
from some point on, and renaming would have broken every inbound link.

---

## What is actually running

All of this was read from the cluster or its records on 2026-11-11 and checked against the platform's records on 2026-11-26, unless it says otherwise.

- **{{ c.nodes }} nodes**: three control-plane servers with embedded etcd, and three laptop agents. The servers carry **no
  taint**, so they also run workloads. The hardware spans old laptops to newer small desktops; the
  heterogeneity is deliberate. Placement labels (CPU class, disk class, disk health) existed on the previous
  platform; I have *not re-read* them on this one and claim nothing about them. (proven 2026-11-11: nodes, roles)
- **Storage: node-local volumes are the only storage class.** Replicated block storage is planned again (kept on 2026-11-22, a decision record first). That is
  a reviewed trade: replication is left to the database layer, which keeps three copies of its own data. The cost is that a
  volume dies with its machine. (proven 2026-11-11: one default class, read back)
- **Databases: {{ db.clusters }} PostgreSQL clusters (the reference app's and the login service's), {{ db.instances }} instances, three per cluster on three nodes, PostgreSQL {{ db.postgres_major }}**, each with a
  connection pooler in front (the login service, though, connects to its database directly). Quorum-synchronous commit (the spec asks for one synchronous standby with required durability) was seen working once, for the reference app's database, in the power-off drill of 2026-11-19: with one standby's machine off, the primary kept committing through the other (the login database's not yet seen). V1.0 read its own back on 2026-10-09. Backups go through the barman-cloud plugin to an S3-compatible store
  on a small always-on Mac outside the cluster, and since 2026-11-24 the house NAS pulls a second copy from it; there is no off-site copy (open). Restore drills passed on 2026-11-10 (the app's database) and 2026-11-15 (the login service's), with limits (proven, with limits; see [how we work](how-we-work.html)). A third, by hand on 2026-11-24, was partial: the newest backup restored from the store and from the NAS copy, and an older one stopped silently at a log segment the store listed and could not serve. The database operator was upgraded live on 2026-11-25: every database and pooler pod rolled in under two minutes with one switchover per database, and no probed request failed. Killing a primary under a write probe lost no acknowledged write (2026-11-16 and 17); the first such kill missed its 30-second target at 48.6 s and found the pooler flaw, and after the fix it came back in 27.9 s (proven 2026-11-17, a thin margin).
- **Identity: the login service runs two replicas in production mode on its own three-instance database** since 2026-11-15 (a pod kill passed on 2026-11-16). Account deletion is live since 2026-11-16. The Warn app signed in through it once, on 2026-11-16, on the owner's word; a sign-in started on one replica and finished on the other has not been shown.
- **Tracing: a collector and a Tempo instance with its own disk**, both scraped, with alerts on dropped spans. On a throwaway cluster in CI the gate finds the trace of its own request; on the home cluster no trace has been looked up yet (built).
- **A supply chain with teeth, and the qualification.** The admission engine, in refuse mode and with three replicas since 2026-11-25, rejects unsigned CI-built images and
  vendor images that are not on a list or not pinned by digest; since 2026-11-21 it also refuses pods that break the baseline pod rules. Unsigned CI-built images were refused on a local test cluster on 2026-11-07, and one
  off-list refusal on the real cluster is recorded in the history of 2026-11-10 (proven 2026-11-10, one case). On 2026-11-11 two policies read as Ready on the cluster: that is a state read, not a new refusal. **Vendor images are not
  signature-checked** (open): the list and the digest pin are the control, not a signature. **The Flux artifact is unsigned**
  (open, read 2026-11-26). CI scans each first-party image and attaches a bill of materials (SBOM) to it before signing (merged 2026-11-13). A weekly scan of every running image is merged (2026-11-24) and not yet running on the cluster, and **there is no vulnerability tracker** (planned). The dependency bot opens pull requests; its updates are held for the owner's approval. The regulatory picture (CRA, GDPR,
  app-store labels) is on [the compliance page](compliance.html).
- **Not live on 2026-11-26:** any alert that pages a person (alerts reach a chat channel), any public name or HTTPS (the edge
  publishes nothing), replicated storage, an off-site backup copy, scheduled host patching, a second Linux distribution in the
  host rehearsal, the host pull timer, any action by the operations agent (it reads only), scheduled fault injection, a
  vulnerability tracker, and two of the three reference apps.
- **Retired from the present tense:** the chaos schedules, the reboot daemon and the 49-assertion audit were features of V1.0.
  Their history is in the dated section below. The operations agent is back since 2026-11-25, read-only (see below).

**Failure domains and maturity:** the 7-of-13 self-grade of 2026-09-09 is V1.0 (retired 2026-11-10) material and is not a claim about
this one. For the new platform, use the status register: on 2026-11-26 it counts 12 steps and 110 rules (3 built, 20 partly built, 87 not built).

**Security is structural, not a layer at the end,** and on the new repository some of it is now enforced. As of 2026-11-11 `main` is
protected: a pull request and the checks run are required, history stays linear, force pushes are blocked, and the rules bind
administrators (proven 2026-11-11, setting read back; read again on 2026-11-26, unchanged). Required checks on `main` are two: the main check and the objectives line. The aggregate gate is deliberately not required yet: a red result from a cancelled run beat a green re-run in a test, and the fix is open. **Review is not enforced.** Required approvals are 0. A scheme of an owner's approval on
important changes and a reviewer agent's on the rest was accepted on 2026-11-23, and the reviewer account it needs was never
created, so it is not in use. A single person authors and merges. 76 of the first 77 commits, over the first six days, came through a pull request. On the
V1.0 the repository was private on the free plan and nothing could be enforced.
Details are in [DevSecOps](devsecops.html) and [how we work](how-we-work.html).

Concrete addresses, machines and topology stay in the private repository. What is here is
the shape and the reasoning.

---

## AI, and where it stands

AI on every side was the plan, held to the same bar as everything else: **assert the property, do not trust the report.** As of 2026-11-26,
two of the three roles exist, the second only as a reader.

**Development time: a cloud model, in the loop (present).** Every repository,
including the words on this page, is built with a cloud LLM as an engineering peer, working
from a written agreement and persistent memory of decisions made. Its changes go through the same pull requests and checks as any other;
all 320 commits to the new repository by 2026-11-26 carry its co-author line. That is enforced for the pull request and the
checks, not for approval (see above), and I have not audited that every change was reviewed. It also runs plays, upgrades and
drills against the live cluster, only on the owner's go and each with a run record. [The fuller account is on its own page](ai-dev.html), including the time it confidently told a
reviewer two things about this platform that were not true.

**Run time: a reader, since 2026-11-25.** The operations agent runs again on the small always-on Mac, deployed from a merged
commit, and reads the cluster with a read-only token. Its remote shell was switched off at deploy time and refused one call,
and it answered one question about the cluster correctly. That it cannot act is shown for that one path only, and no grading
of its answers is built yet. Its V1.0 form, with a local model, a narrow write path and a cloud reader that graded its posts,
is described, dated, under V1.0 below and in [the agent's page](aiops.html).

---

## The stack

Standard, open-source tooling, so each choice maps onto what you would reach for in a
datacentre. Deliberately a table, not a badge wall: badges overclaim, and several that used
to be here did. Status as of 2026-11-26.

| Layer | What runs | Qualification |
|---|---|---|
| Platform | K3s, the current minor (containerd, embedded etcd, flannel with the WireGuard backend, CoreDNS on every node, Traefik, kube-vip), Ansible for the hosts, local VMs for rehearsal | The "retired laptops" part is literal. Upgraded live by a play on 2026-11-18 (partial: a network policy gap showed after). Rehearsal covers one distribution; a second is not live |
| Data and identity | Node-local storage (no Ceph), CloudNativePG with the barman-cloud plugin and PgBouncer, an S3-compatible store (Garage) on a small Mac outside the cluster with a second copy on the house NAS, Keycloak (two replicas, own database, since 2026-11-15) | No off-site copy; failovers drilled 2026-11-16 and 17; two power-offs of a machine holding a database standby on 2026-11-25 lost no row (both partial, for other reasons) |
| Change and secrets | Flux from a CI-built artifact, SOPS with age | The artifact is unsigned. The recovery key went into a password manager on 2026-11-26; a decrypt with the workstation off has not been tried (open) |
| Supply chain | cosign, Kyverno admission (Deny, three replicas), Syft and Grype in CI, gitleaks, Renovate, pre-commit | Renovate opens pull requests, held for approval. Vendor images are not signature-checked. The weekly scan of running images is not live. No tracker |
| Observability | Prometheus (two replicas since 2026-11-19), Alertmanager, Grafana, Loki with a log agent, Tempo, an off-site dead-man's switch | Built: merged 2026-11-11, first live run failed on a manifest defect, fixed the same day; alerts reach a chat channel, nothing pages a person |
| Applications | Java 25, Spring Boot 4 for the reference app | No load |
| Embedded | Yocto, RAUC signed A/B OTA, Raspberry Pi | Unchanged; the heartbeat to the cluster was retired for now on 2026-11-22 |

Workflow-status badges are deliberately absent: the project repositories are private, so
their badges return 404 to anyone but me, and a badge nobody else can verify is decoration.

---

## V1.0 (retired 2026-11-10)

Everything from here down was measured on, or says something about, the cluster that ran until it was torn down on 2026-11-10. It
is kept because the record is the point, with the dates it was true on. **None of it is a claim about the new cluster.** Where a
sentence names a figure, it was read on the date given and not re-measured since.


### V1.0 (retired 2026-11-10): what the page said and what it measured, as of 2026-10-27

V1.0 was a running estate of six nodes with a public entrance, real identity flows, a synthetic load generator, scheduled
chains, and a local model that helped run it. The figures in this section are hand-typed from the last generated run of
2026-10-27: 186 of 216 pods running, 22 namespaces, 124 of 124 scrape targets up, 227 alert rules loaded (78 written here), 31 dashboards,
replica-3 block storage with Ceph health at warn, 13 PostgreSQL clusters (5 on 16, 8 on 18), 7 first-party images of which 6 verified against the release key, and 1,943 commits in
the old repository. None of those is a current number.

The three badges below were graded by referees that sat outside the system they graded. As of 2026-11-10 their monitors are paused (see above);
they are described here as history, not shown:

- *scheduled jobs*: a dead-man's-switch, where the alert pipeline proved itself end to end on a schedule;
- *public endpoint 7d and 30d*: an off-site probe of the public entrance (99.95% over 7 days and 85.004% over 30 days on 2026-10-27).

**The uptime numbers were not the goal, and the 30-day one showed why.** I shut the whole
estate down on purpose from 2026-10-14 to 2026-10-18, while I was away (a planned holiday shutdown), so that window carried roughly
four and a half days of "downtime" in the 30-day figure. The badges could not be told
that a shutdown was planned. [Three more notes on reading these badges, and the arithmetic of why there was no
90-, 180- or 365-day figure, are on the status page](status.html#notes-on-the-badge-wall).

**The scrape figure used to be the interesting one.** In September I published **67 of 70**
and explained it: the three down were the etcd metrics endpoints, because a rebuild had not
restored the drop-in that exposes them. etcd was fine; what had broken was the ability to
*see* it. Rounding it up would have removed the only pressure that closed it. The same arc
applied to alerts: an earlier snapshot listed eight, two of them firing on **absent data
rather than on a sick database**, which is the more dangerous failure because an alert that
fires for the wrong reason cannot tell you anything when the right reason arrives. Those were
fixed, not silenced.

**The Postgres version count had a cost (September 2026).** The clusters went from 8 to 13
because the application databases were migrated from PostgreSQL 16 to 18 with no maintenance
window: a parallel cluster kept in sync by logical replication, then a cut-over by *pausing*
the connection pooler so clients blocked for a few seconds instead of erroring. Measured per
database: 87 to 142 seconds, zero errors, at the time. Five PostgreSQL 16
predecessors were still running as the rollback path on 2026-10-27; the operator is what made this a scripted procedure instead of a project.

### V1.0 (retired 2026-11-10): a correction on those databases, 2026-10-09

Until 2026-10-09 the page said the application and identity databases ran synchronous
replication. **They did not.** The 18 cutover on 2026-09-16 silently dropped the synchronous
setting, along with resource limits, the connection cap and failover tolerations, so for
23 days the live databases were asynchronous while the documentation said an RPO of zero. I
found it with an audit, not an alert. At about 09:21 CEST on 2026-10-09 quorum-synchronous
commit (any one of two standbys) was restored on the four three-instance application and
identity clusters, and `sync_state=quorum` was read back on each primary. The two-instance
clusters (the fleet service and the security tools' databases) were asynchronous by design. A
guard failed when a successor cluster did not mirror its predecessor's settings.
The lesson carries to the new cluster, where quorum-synchronous commit is in the spec. *Update, 2026-11-26:* it was seen working
once, for the reference app's database, in the power-off drill of 2026-11-19; the login database's has not been seen.

The same day, a replica that had silently diverged at a failover on 2026-09-25 sat 14 days
not streaming and crash-looped on its first restart. Alerts for that class (a replica not
streaming, a container crash-looping, an instance not ready) were added. The account is in
[the reliability page](reliability.html) and
[the lessons page](lessons.html#11-three-wrong-claims-in-one-diagnosis).

## V1.0 (retired 2026-11-10): corrections, 2026-10-27

*These corrections were made on 2026-10-27 about V1.0. They are kept as written, with that date.*
A second read of this site against the estate, nine days after the first, found statements that
had turned stale in the *pessimistic* direction (things that had since been fixed) and two that
were false the whole time. They are retracted here rather than quietly edited:


- **"Almost nothing goes through a pull request."** True until 2026-10-18; since then 112 of the
  133 commits to the platform repository carry a pull request number. They are still merged by
  the one person who wrote them, and the plan still cannot enforce review. See
  [AI in development](ai-dev.html#who-reviews-honestly).
- **"Secrets at rest are plaintext", "there is no secrets manager".** In git, no longer: since
  2026-10-25 every Secret in the manifests is encrypted with SOPS and age. Inside the cluster
  they are ordinary Kubernetes Secrets and encryption at rest is not switched on (read back
  2026-10-27), and the old values are still in git history until they are rotated. See
  [choices](choices.html#deferred--needed-eventually-not-yet).
- **"Drift is checked on demand; neither runs."** A daily read-only diff of every plain manifest
  against the live cluster has run since 2026-10-24, after the reopen-trigger written down for
  exactly this fired. See [how a change reaches the cluster](platform.html#how-a-change-reaches-the-cluster).
- **The operations agent page** described the agent as of 2026-10-09. It has since had its tool
  arguments validated, an approver allowlist, an audit file, deployment from git, and a quality
  loop that measures what it says. See [the agent](aiops.html).
- **The embedded page** said a daily job keeps the bill of materials current in the tracker and
  that devices report back. **Neither was true:** the upload was refused every night from at
  least 2026-09-24 until it was fixed on 2026-10-27 (the first scheduled run since is the test),
  and no device has reported since 2026-09-01. See [the embedded side](yocto.html#two-claims-on-this-page-were-false-on-27-october).
- **"I have not worked out where the downtime came from."** It was the four days from
  2026-10-14 to 2026-10-18, when I had shut the whole estate down on purpose while I was away. See [the status page](status.html#notes-on-the-badge-wall).
- **Fault injection** was described as running hourly on weekdays. It last fired on 2026-10-13. See
  [reliability](reliability.html#fault-injection-is-paused-by-its-own-safety-gate).

## V1.0 (retired 2026-11-10): corrections, 2026-10-09

*These corrections were made on 2026-10-09 about V1.0, and are kept as written.*
A fact audit measured the live system against this page. Some claims were wrong, and they
are retracted here rather than quietly edited:

- **"Real users."** The earlier headline and a later section said the services serve real
  users. There is no organic user base. Product analytics is at zero, so nobody measures use.
- **"Every image is signed."** 6 of 7 running first-party images
  verified against the release key (read 2026-10-27). The 61 third-party images were
  scanned and had a bill of materials, but were not signed by this platform.
- **"A scheduled fault injector removes things."** There were two schedules, a pod kill and a
  25% network loss for five minutes, on weekdays hourly, aimed at a two-replica sandbox
  workload. They exercised the recovery loop and could not move the public-endpoint figure.
- **Operations agent autonomy and "air-gapped".** The agent had five alert rules; only two
  could run unattended, both on-demand database backups, and even those only if auto-apply
  was switched on, which it was not by default. The model was local, but the agent was not
  air-gapped: it posted to chat and synced findings with a ticket tracker.
- **A cloud and self-hosted runner split.** On 2026-10-09 it did not exist: all CI ran on the estate's own runners. *Update, 2026-11-11:* a split exists
  again, by role, since 2026-11-10: hosted runners for jobs that carry keys, a fresh virtual machine per job on a Linux host at home for
  heavy secret-free jobs. *Update, 2026-11-26:* since 2026-11-12 every job runs at home and a hosted runner is used only where a secret forces it. See the cost table above.
- **Four of thirteen failure domains** was stale at the time (the self-grade of 2026-09-09 said seven of thirteen).
- **A licence and a security policy.** The compliance page carried an MIT badge while this
  repository had no licence file, and the only security policy lived in a private repository.
  As of 2026-10-09 both exist here: [MIT for the code and CC BY 4.0 for the
  writing](https://github.com/schultzzznet/schultzzznet/blob/main/LICENSE-docs), and a
  [security policy](https://github.com/schultzzznet/schultzzznet/blob/main/SECURITY.md) with
  private reporting switched on. See [compliance](compliance.html).

### V1.0 (retired 2026-11-10): what it ran, as of 2026-10-27

- **Six nodes with placement labels** for CPU class, disk class and disk health; no node carried a taint.
- **Replicated block storage**, 3-way, host-level failure domain, as the sole storage class. All of it is gone: the machines now run
  node-local volumes (see above).
- **13 Postgres clusters** under an operator, 8 on PostgreSQL 18 and 5 on 16 (the rollback predecessors), all archiving continuously to object storage. The
  guarantee claimed was quorum-synchronous commit on the four three-instance application and identity clusters, verified on 2026-10-09.
- **Spring Boot services and Flutter clients.** Five of each existed in the repository; four Spring Boot services were deployed. Beside them ran a Python
  service and a web portal, plus identity, ingress, metrics, logs and dashboards.
- **A supply chain with teeth, and the qualification (2026-10-27).** Of 68 distinct running images, 7 were first-party and 6 of those verified
  against the release key; 71 bills of materials were accepted by the tracker in the latest nightly run (which measures acceptance, not
  analysis). Signing and verification were build steps. **That enforcement lived in the pipeline, not at the cluster boundary:** there was no
  admission controller, so the guarantee was "the delivery path will not ship an unsigned image", not "the cluster will not run one". Admission now exists on the
  new cluster (see above).
- **Deliberate chaos, small by design.** Two Chaos Mesh schedules against a two-replica sandbox workload. As of 2026-10-27 both were
  paused by their own safety gate and had last fired on 2026-10-13. [The account is on the reliability page](reliability.html#fault-injection-is-paused-by-its-own-safety-gate).
- **An operations agent** that read cluster state, correlated it and proposed remediations.
- **Automated assertions** that documentation, inventory and reality agreed. The audit run on 2026-10-09 had 49 checks, 48 passing; the
  one that did not was Ceph not being `HEALTH_OK`, which was the check working.
- **227 alert rules loaded** (78 written here) and 31 dashboards (5 written here), on 2026-10-27.

**Failure domains (self-grade of 2026-09-09):** seven of thirteen single-fault tolerant, up from four in early July. That was a self-grade I did not re-derive, and
it contradicted the four on other pages dated earlier. It is not carried over to the new platform.

**Security on V1.0:** branch protection could not be enforced on a private repository under GitHub's free plan, so "gates" were CI
workflows and pre-commit hooks that one maintainer was bound to follow, and GitHub-native code scanning and secret scanning were off.

### V1.0 (retired 2026-11-10): its diagram and two dotted lines, 2026-10-27

V1.0's picture had a development side (workstation, self-hosted runners, a daily cloud reader), a public edge outside the
cluster on purpose (a relay and a reverse proxy with a default-deny allowlist), six nodes (three-member control plane, Spring Boot services,
Postgres clusters, replica-3 block storage, metrics and dashboards, a vulnerability tracker, a scheduled fault injector), and two things
outside it: the operations agent with its local model, and the external referees. The two dotted lines that mattered were the agent's narrow,
allowlisted write path and the referees grading from outside. *A monitor that dies with the thing it monitors is not a monitor.*

## V1.0 (retired 2026-11-10): why build it this way

**Why build it this way instead of stopping at a tutorial:** a system nobody has to operate
teaches a smaller skill than one that is running, with real incidents and a real pager. The
scars (a nine-day silent outage, a drain that removed its own control surface, a reboot
daemon that quietly never rebooted anything) exist only because the thing they happened to
was live. **On V1.0 the load was synthetic; the incidents were not.** Power cuts, thermal throttling,
disks reporting `FAILING_NOW`, a carrier-grade-NAT boundary, an ISP, a public entrance that
had actually been down, and kernel upgrades rolling across the machines unattended, one node
at a time, at whatever hour the kernel lands. The failures were never the part that needed
simulating.

### V1.0 (retired 2026-11-10): AI

AI was in three roles: a cloud model that helped build it, a small local model that helped run it, and a cloud model that graded the local one.

**Run time: a separate, local model, with a narrow write path.** An operations agent
off-cluster watched the cluster, deliberately not the cloud model, so the thing watching
the cluster had no dependency on someone else's API. The live work ran on a local model, so
no cluster data went to a model vendor *in the alert path*; the agent was **not air-gapped**, as
it posted to chat and synced findings with a ticket tracker. Nothing the model said was executed
directly:
[**the model proposes; a fixed, allowlisted guardrail layer disposes**](aiops.html). Every
action except the two auto-apply backup rules was a small closed vocabulary, shown as
a dry run, and waited for a human's approval.

**A reader between them (from 2026-10-28): the cloud model graded the local one.** Once a
day a cloud model read up to twelve of the agent's recent posts and drafted a grade for each,
on whether it was right and whether it was usable. It was outside the alert path, had no
tools, and its grades were drafts a person adopted or ignored. What it was sent was alert text and node names, trimmed,
so the statement that no cluster data leaves the house was true until that date and not after. [The whole loop, with the numbers](aiops.html#the-loop-two-models-one-human).

What it did on its own, as read on 2026-10-09: two rules could run unattended, both on-demand database backups, and only when auto-apply
was switched on, which it was not by default. Everything else was a proposal. A bounded chaos-recovery loop existed in the agent's
code, and I had not read its runtime state.

**That was not a self-healing cluster.** It was a cluster where one narrow case was automated
and everything else became a proposal.

**What changed on 2026-10-26, because it had been measured.** A review of the agent's first 96
hourly summaries found "critical" in 79 of them with no critical alert firing in 69, and a
data source that had been blind for fourteen days without one mention. The same review found that
a model-supplied name was being placed into a command run as root. Both were fixed: arguments were
validated, only named people could approve, every executed action was written to an audit file, the
severity line was written by code and not by the model, and every call was recorded so a monthly
graded sample and a set of golden test cases could say whether a change helped. The account, with
the numbers, is on [the agent's page](aiops.html#the-agent-since-2026-10-26).

### The habit the whole thing is built on (examples from V1.0, retired 2026-11-10)

> **Assert the property. Do not trust the report.**

The recurring defect is not the crash. It is the thing *configured, plausible-looking and
quietly inert*. All found on V1.0 by checking rather than reading:

- A chaos schedule that had never once fired. Every dashboard was green; the field that
  would have revealed it, *when did this last run?*, was on none of them.
- An automated reboot daemon that read the wrong path and concluded, hourly on every node
  for weeks, that nothing needed restarting. Patches were applied to disk and never took
  effect: **16,002 host findings, all fixed upstream**, and four kernel versions running at
  once. That story was closed on 2026-10-09 after reboot waves on 2026-09-24 and 2026-10-09.
- A shared build cache that was populated, correct, and **bypassed on every build**, because
  a prerequisite that gives cache entries a stable identity was missing.
- Most recently, this page: a synchronous-replication setting that every document said was
  there and the live databases did not have.

Four more, including a kill switch that covered half the system and a documentation workflow
that ran 89 times and never succeeded, are in
[the measurement traps](devsecops.html#6-measurement-traps-found-by-checking). None of them
errored. So: run the thing, read the value back off the live object, and make a test fail
before trusting that it passes. A green status line is a claim, not evidence. The new cluster has its own entry already: the default-deny probe
of 2026-11-10 recorded a fail (a one-to-three-second gap at start), and it stays a fail on this page until it is re-run and passes.

---

## V1.0 (retired 2026-11-10): why go to this much trouble

> Quality isn't a tax on speed. Past a very early point, it is the only source of speed.

Each of these happened on the previous fleet: two nodes powered off on a whim with the applications
staying up; a database primary failing over **during** a planned drain; node objects deleted
and rejoining on their own because the cluster is a derivative of git; the whole cluster
wiped and rebuilt; a topology decision reversed the same day it proved wrong. The sixteen power-off proofs and seventy-four mechanisms behind
that are **not carried over** to the new cluster.

**That up-front cost is what makes the list take minutes instead of weekends.** It is also
what the shortcuts cost, each with a foreseeable ending:


| The shortcut | Where it ends |
|---|---|
| Single-node volumes, because it's only a homelab | Every reboot risks data. You can't drain, so you can't patch. |
| One database per app, no operator | Every upgrade is a maintenance window; failover is a human at 3am. |
| Backups configured but never restored | You find out they don't work on the day you need them. |
| No decision records | The same arguments recur forever. |
| No contracts, no drills | The public edge silently widens; "it rebuilds from git" stays a belief. |
| Hand-configured nodes | The fleet diverges until nothing is reproducible. |

The second row stopped being hypothetical: in September 2026 the application databases moved from
PostgreSQL 16 to 18 while serving, between 87 and 142 seconds each, no errors, nobody woken.
Then the same migration dropped the replication guarantee and I found out three weeks late.
Both facts belong together. The operator made the migration a script; it did not make the
script right.

Two things assumed expensive were not, on V1.0: **high availability cost nothing in hardware**
(loopback-file storage daemons gave real replication on a single-disk fleet; the new cluster has dropped replicated storage on purpose), and **an elite
supply chain was mostly wiring**, since every component is open source and the work was
connecting them once.

### The condition that made it possible: no pressure (V1.0, retired 2026-11-10)


There was no commercial pressure of any kind: no runway, no board, no launch date, no
customer waiting. Every "properly instead of quickly" decision was made in the absence of the
force that normally makes that choice impossible. The industry default is not stupidity.
Under real pressure the order inverts: find product-market fit first, ship what proves it,
pay for the engineering later if there is a later. Anyone reading the table above and
thinking *"sure, but I have a deadline"* is describing the actual problem, and this site is
not evidence against them. So the reading is not "this is how it should be done". It
is **"this is what it looks like when the usual forcing function is absent"**. Customers
import the pressure, and that is why the order here is deliberate: learn it the expensive way
while nothing forces the shortcut, so that on the day a killer app arrives the platform, the
patterns and the habits are already in place, and a shortcut is a choice rather than the only
option.

Rigor did not transfer to every domain at once. V1.0 (retired 2026-11-10), as of 2026-10-27: open items remained for rotating the secrets that sat in git in plaintext, encryption at rest in the cluster, and a hosted privacy policy ([gaps](reliability.html), [legal posture](compliance.html)).


---

## V1.0 (retired 2026-11-10): so what happens to it now? (assessed 2026-10)


| | | |
|---|---|---|
| **Can it?** | capability | The only one that has to be *earned*. |
| **Should it?** | judgement | Answerable only once *can* is real. |
| **Want to?** | intent | A choice, and the easiest one to mistake for a plan. |
| **Done?** | past tense | Evidence. The rest of this site is the answer. |

An unearned *can* makes the whole chain weightless.

**Can it? Very nearly, on V1.0 (retired 2026-11-10).** Replicated storage under every volume, three control-plane
members, databases that fail over during a drain, backups with a timed restore, automated
patching with coordinated reboots, an incident practice with real postmortems. What is
missing is written down and mostly unglamorous.

**Should it? Not yet** (V1.0, as of 2026-10-27). Legal and regulatory sits well below its target in the
[self-assessment](quality.html), secrets are encrypted in git but not yet rotated or encrypted at rest in the cluster, the public entrance is one
small machine and one relay, and product analytics is at zero. Nothing here is one weekend
from being a business.

**And the plainest reason is the least often admitted: there is no killer app.** The
applications were chosen to be a demanding, realistic load, and none is a product anyone is
waiting for. A platform without something worth deploying on it is infrastructure looking for
a reason, and that gap is not solved by more engineering. Being ready when one appears is the
other half of what the training is for.

**Want to? Not yet, and that is a choice.** The platform is portable and the instance is not. The
*pattern* can travel: the contract, the pipeline, the assertions, the gap register as a
habit. Without a killer app this cluster stays a laboratory, doing what nothing in production
is allowed to do: get powered off on a whim, wiped, deliberately broken. On the day one is
chosen the direction changes on purpose: production becomes the main line and the experiments
move to a branch. The moment something here matters
to someone else, two nodes can no longer be switched off to see what happens, and the loop
that produced every finding here stops. **Let the pattern travel, and keep the laboratory a
laboratory.**



On the new platform the answer to *can it* is lower than that, on purpose and in the open: the status register of 2026-11-10 counted 3 of 109 rules built,
and on 2026-11-26 it counts 3 of 110 built and 20 partly built. The cutover decision is gated and not made.

---

## Open owner items (2026-11-26)

- A decrypt of the secrets with the workstation switched off, the last step of key custody (the recovery key went into a
  password manager on 2026-11-26).
- Approve the removal of the old cluster's remains from the six machines, and two database primary moves with it.
- The second power-off drill again, at the machines, after that removal.
- Next step, rejection or another option for the separate CI cluster trial.
- Two-factor sign-in on the code host and the reviewer account the merge-approval scheme needs.
- Whether held dependency updates flow on their own.
- The cutover decision (gated).

Closed since the list of 2026-11-11: the monitoring webhook (alerts reach a chat channel since 2026-11-16) and a second backup
copy (on the house NAS since 2026-11-24).

---


## Never done, by design

Nothing here describes a finished artifact. The loop is the same on every page:

> **ship → observe → learn → harden → prove → repeat.**

It has no last iteration, and this site does not claim one.

> *The age of agents has brought us endless execution. Every idea, every hunch, every
> experiment is now within immediate reach. Working with agents truly is magic — in the best
> possible sense of the word. What a time to be alive. Nay, what a blessing.*
> — DHH, [Endless execution](https://world.hey.com/dhh/endless-execution-4157e065) (August 2026)

<sub>Written for this public site rather than copied from the private repository, and checked
on every commit by a guard that fails the build on hostnames, addresses and credential
paths. Starting clean is cheaper than scrubbing.</sub>

<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
  document.querySelectorAll('pre > code.language-mermaid').forEach((el) => {
    const div = document.createElement('div');
    div.className = 'mermaid';
    div.textContent = el.textContent;
    el.parentElement.replaceWith(div);
  });
  mermaid.run();
</script>
