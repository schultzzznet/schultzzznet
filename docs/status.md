---
title: Status
description: Every figure measured by a command, with the command beside it. A dated snapshot of the new platform, not a feed.
reread: 2026-11-11
body_read: 2026-11-11
summary:
  - "**What it is:** the one page where figures are regenerated, not remembered. Each is read off the running platform by a script, with the command and what was counted printed beside it. Dated 2026-11-11."
  - "**The cluster is about a day old:** it was rebuilt on 2026-11-10 and 2026-11-11, so nothing here is an uptime claim (the platform's [history](history.html) goes back to 2025-12-21). It is a snapshot, not a feed: a guard fails the build when the numbers are more than three weeks old."
  - "**Two evidence records are shown with what they do not prove:** a restore drill passed on 2026-11-10 and a default-deny probe failed the same day (a new pod was open for about 1 to 3 seconds). Open item."
  - "**Monitoring is running and read, and there is no external referee yet.** Figures that no probe can read yet say not measured yet, never zero and never an old number. V1.0's headline figures are kept below as history only."
---

# Live status

{% include in-short.html %}

{% assign s = site.data.stats %}
{% assign gen = s.generated_at | date: "%s" %}
{% assign built = site.time | date: "%s" %}
{% assign age_s = built | minus: gen %}
{% assign age_d = age_s | divided_by: 86400.0 | round: 1 %}

**Measured at {{ s.generated_at | date: "%Y-%m-%d %H:%M" }} UTC.** When this page was last built, those figures were
{% if age_s < 3600 %}under an hour{% elsif age_d < 1 %}under a day{% else %}{{ age_d }} days{% endif %} old.
Every number below was read by a command, at that moment, by a script that is
[in this repository](https://github.com/schultzzznet/schultzzznet/blob/main/scripts/gather-stats.py).
The generator reads the cluster read-only, and the main branch of the private platform repository for the
repository counts. None of it was typed in. The last column says what was counted, and where the label is
wider than the count, it says so.

**The cluster is about a day old.** V1.0 was torn down on 2026-11-10 and this one was
brought up on 2026-11-10 and 2026-11-11. The platform is older: V1.0 ran from 2025-12-21, and its frozen
[history](history.html) is measured month by month. Nothing on this page is an uptime claim, and a count of things that
exist is not a claim that they have worked for any length of time. Where a figure cannot be measured yet, the
page says **not measured yet**. It does not show zero, and it never carries a number over from V1.0.

The other pages hold snapshots written by hand on a given day, and they drift: a hand-kept number is right
once. This page exists so that there is one place where the figures are regenerated rather than remembered,
and so that the staleness of those figures is itself a number you can read.

## No external referee yet (open, 2026-11-11)

On V1.0, outside monitors graded the public endpoint and the scheduled jobs, and their
badges sat on this page. Those monitors were paused on 2026-11-10 when the platform was torn down (proven on 2026-11-10 by the
teardown record). There is no public entrance to the new platform yet and no
external referee watching it, so the badges are gone from this page rather than left showing a false failure.
This is an open item: a new referee is planned together with a public entrance, and until then the page makes
no availability claim of any kind.

## V1.0 (retired 2026-11-10), measured 2026-10-27 (history only)

These are the headline figures the page showed on 2026-10-27 for a platform that no longer exists. They are
history, not a baseline for the new platform, and none of them is measured today.

- Replicated storage was in use for the cluster's volumes.
- 227 alert rules and 31 dashboards were configured.
- 13 PostgreSQL clusters were running.
- 124 scrape targets were monitored.
- 6 of 7 first-party images were signature-verified.
- The public endpoint's 7-day uptime read 99.95 percent.

### Notes on the badge wall {#notes-on-the-badge-wall}

*V1.0 (retired 2026-11-10). The measurement lessons stay because they were learned the hard way and
still apply to any monitor; the badges themselves are gone.*

- **The heartbeat badge read `late` once while the alert pipeline was provably healthy.** My first explanation
  (some other check was overdue) was wrong. The check's expected period equalled the sender's interval, five
  minutes against five minutes, with no headroom, so a ping a second late was late by construction. The
  ruler was the same length as the thing measured. A false positive gets the alarm muted, which manufactures
  the blindness of a false negative more slowly, and a single monitor gives you no way to find out.
- **There was deliberately no 90-, 180- or 365-day uptime figure.** On 2026-10-09 the monitor read 98.97
  percent for 90 days, 99.485 for 180 and 99.746 for 365. Multiply each back out and every window held the same
  1,335 minutes of downtime: the monitor had less history than the window, so the numerator was fixed and only
  the denominator grew. The 7- and 30-day figures moved independently, so those were measurements; the longer
  ones were arithmetic wearing a measurement's clothes.
- **The 30-day shortfall was a planned shutdown.** The whole estate was shut down on purpose from 2026-10-14
  to 2026-10-18, about 15 percent of thirty days. Both the off-site probe and the heartbeat counted it as
  downtime, because neither can be told that a shutdown is planned (see
  [the reliability page](reliability.html#the-estate-was-shut-down-on-purpose-for-four-days)).
- **The uptime numbers were never the goal.** The platform is a learning one operated to production standards,
  not a product carrying an availability commitment.

## The new platform, group by group

Each group below states what its figures are, and what they do not show. Anything about the new platform is
dated 2026-11-11 unless it says otherwise.

{% assign order = "cluster,storage,reconciler,admission,databases,evidence,observability,ci,repo,hardware,site" | split: "," %}
{% assign titles = "The cluster,Storage,The reconciler,Admission and policy,Databases,Evidence records,Observability,CI,The platform repository,Hardware repositories,This site" | split: "," %}
{% for g in order %}
{% assign rows = s[g] %}
{% assign methods = site.data.stats_methods[g] %}

## {{ titles[forloop.index0] }}

{% case g %}
{% when "cluster" %}
What Kubernetes reports about itself, three control-plane servers and three laptop agents. These are counts of
API objects, so a CronJob that is suspended is still a CronJob, and a pod that finished is still a pod.
Status on 2026-11-11 (proven by a read that day): all nodes Ready, the pods Running and the namespaces as
counted below. The age row is the age of the cluster, about a day, so no restart or age figure here is a
stability claim.
{% when "storage" %}
There is one storage class, node-local, and it is the default. A volume lives on one machine, so there is **no
replication at the storage layer**: losing that machine loses that volume's data, and durability comes from
database replicas and backups instead. The question of replicated block storage is open: it is not built, and no dated plan is published here. Claims bound
is a count of claims that found a volume, not a statement about their health.
{% when "reconciler" %}
The GitOps reconciler applies the repository to the cluster. At the generation time above, {{ s.reconciler.kustomizations_ready }} of {{ s.reconciler.kustomizations }} Kustomizations
were Ready (measured). A hand reading at 07:00 UTC on 2026-11-11 found all 18 Ready. Two limits. The artifact the reconciler reads is **not signed**
(planned: signing is not in place), and it is read through a moving tag, so what is applied is
whatever the tag points at when the reconciler looks. The artifact-signed row therefore reads
**not measured yet**. A Ready Kustomization means the last apply succeeded; it does not mean the workload is
correct.
{% when "admission" %}
The admission policies decide what may be created. On 2026-11-11 two policies are in Deny mode (proven 2026-11-11 by a
read). The default-deny network count is **structural**: it counts tenant namespaces that have a policy
object, not whether traffic is actually blocked. Beside it sits the one record that tested it. The probe of
{{ s.evidence.default_deny_probe_home_date }} has the result **{{ s.evidence.default_deny_probe_home_result }}**
(proven 2026-11-10): steady-state traffic was blocked after about 30 seconds, but a newly started pod was open for about
1 to 3 seconds (1, 2 and 2 open probes in three timed runs). Ingress denial from outside and DNS egress limits
were not tested. That gap is an open item. Whether first-party images are signature-verified is
**not measured yet**.
{% when "databases" %}
PostgreSQL under an operator, and the page separates what is configured from what is observed. Synchronous
commit is **configured, not read back**: the row counts clusters whose specification asks for it, and the
platform does not yet ask each primary what is true right now. The backup rows count backup objects that still
exist; the operator's plugin method leaves the cluster-level status empty, so the status field cannot be used
to count them. One database cluster of three instances was healthy on 2026-11-11, and the nightly backup
for 2026-11-11 showed completed when read (proven 2026-11-11 by that read; the time of day is not stated). A completed backup is not a tested restore: see the evidence records.
{% when "evidence" %}
The latest records of tests run on the platform, each with its date and result, and what it does **not**
prove. Restore drill, {{ s.evidence.restore_drill_home_last }}, result
**{{ s.evidence.restore_drill_home_result }}** (proven 2026-11-10): a marker row and six tables came back from the
object store alone in about 60 seconds, on a few megabytes. Not shown: size and time at real size, restore of the
scheduled backup, point-in-time recovery, loss of the object store host's disk, an application running against
the restored database, an off-site copy. Host-layer rehearsal, {{ s.evidence.host_rehearsal_date }}, result
**{{ s.evidence.host_rehearsal_result }}**: from creating three virtual machines to the end of a second run that changed nothing took
4 minutes 11 seconds, after earlier failed runs that exposed four defects. Not shown: a second distribution, x86 hardware, quorum or node failure, failover of the
virtual address. The default-deny probe is described under admission and is a **fail**. A record shows one
test on one day; it does not show the system keeps passing.
{% when "observability" %}
**Monitoring is running and read on the new platform (2026-11-11).** The monitoring tenant was merged into the private repository on 2026-11-11; its first live run failed on a missing namespace in the node exporter manifests, and a one-line fix for a missing namespace in the node exporter manifests landed the same day. At 07:00 UTC on 2026-11-11 all 18 Kustomizations were Ready, the metrics, alert, dashboard and state-metrics pods had been Running for a short time, and the node exporter ran on all six machines. It was then read: 18 of 18 scrape targets up, 12 alert rules, 0 recording rules, 0 dashboards, about an hour of history; no alert is known to reach a person. The rows below that still read
**not measured yet** (alerts reaching a person, SBOM projects) have nothing to count, and a zero would claim there are none rather
than that nothing is running. When the thing exists, the generator is built to fail until each row is given a real
method, so a stale "not measured yet" cannot sit beside a live system unnoticed.
{% when "ci" %}
Parsed from the workflow files of the private platform repository's main branch, not read from run history.
These rows count what the files declare, not where jobs ran: jobs that name a self-hosted runner, jobs fixed to a
GitHub-hosted image, and jobs whose runner is chosen at run time. No claim is made about where most jobs ran.
{% when "repo" %}
Counted from the committed main branch of the private platform repository, so unsaved work cannot move a
number. The repository is about a week old, so its commit rates are short-window figures. The test figures are
static counts of test definitions in the source, **not a pass rate**: nothing is built or run to produce them.
Record counts show how many written records pass the repository's own format check, not how many tests passed.
{% when "hardware" %}
The sibling repositories, named here by role. Commits and static counts of test functions only;
nothing is built or run to produce them. The C assertions of the rover platform are a separate
row, because one test function holds several of them.
{% when "site" %}
This repository. The commit count is taken before the commit that carries the file.
{% endcase %}

<table>
  <thead>
    <tr><th>Figure</th><th>Value</th><th>How it is measured</th></tr>
  </thead>
  <tbody>
{%- for row in rows %}
{%- assign key = row[0] %}
{%- assign m = methods[key] %}
{%- if row[1] == "nm" %}
    <tr><td>{{ m.label | escape }}</td><td><strong>not measured yet</strong></td><td>{{ m.how | escape }}</td></tr>
{%- else %}
    <tr><td>{{ m.label | escape }}</td><td><strong>{{ row[1] | escape }}</strong>{{ m.unit | escape }}</td><td>{{ m.how | escape }}</td></tr>
{%- endif %}
{%- endfor %}
  </tbody>
</table>
{% endfor %}

## What this page is not

**It is a snapshot, not a feed.** `make stats` runs the generator against the cluster, read-only,
and the file it writes is committed like any other change. Between runs the numbers stand still
while the estate does not. A guard fails the build when the file is more than three weeks
old, which keeps the timestamp current; it cannot keep the figures current, only visible
when they are not.

**It is aggregates only, and the platform is private.** Counts, percentages and
dates. No machine, address, namespace, workload or secret is named, and the generator runs
its own output through the same leak guard as every page on this site before it will write
the file, and refuses to write at all if a measurement fails. A partial page would be worse
than a stale one.

**Measured is not the same as good.** Each figure says what was counted, and that is all it
says. A count of alert rules is not a measure of whether they would fire; a count of tests
is not a pass rate; a green health word is a reading, not a verdict.

**Some things are missing on purpose.** Vulnerability counts by severity, the code-quality
gate, the number of identity realms and anything else behind credentials are not shown: the generator
does not hold those credentials, nothing here guesses at them, and nothing is published for them.
Figures that nothing measures yet read **not measured yet**. If a figure you
expected is absent, that is the reason.
