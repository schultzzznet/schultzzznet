---
title: Status
description: Every figure measured by a command, with the command beside it. A dated snapshot, not a feed.
---

# Live status

{% assign s = site.data.stats %}
{% assign gen = s.generated_at | date: "%s" %}
{% assign built = site.time | date: "%s" %}
{% assign age_s = built | minus: gen %}
{% assign age_d = age_s | divided_by: 86400.0 | round: 1 %}

**Measured at {{ s.generated_at }}.** When this page was last built, those figures were
{% if age_s < 3600 %}under an hour{% elsif age_d < 1 %}under a day{% else %}{{ age_d }} days{% endif %} old.
Every number below was read off the running estate by a command, at that moment, by a script
that is [in this repository](https://github.com/schultzzznet/schultzzznet/blob/main/scripts/gather-stats.py).
None was typed in, and none was copied from another page. The last column says what was
counted, and where the label is wider than the count, it says so.

The other pages hold snapshots written by hand on a given day, and they drift: a hand-kept
number is right once. This page exists so that there is one place where the figures are
regenerated rather than remembered, and so that the staleness of those figures is itself a
number you can read.

## The referees, live

These three are not part of the snapshot. They are graded from outside and fetched by your
browser when you open the page. The estate page says [what each of them does and does not
mean](index.html#none-of-this-is-a-demo).

[![Alerting alive](https://img.shields.io/endpoint?url=https%3A%2F%2Fhealthchecks.io%2Fbadge%2F3f30fa97-f736-45eb-befc-7e77b7%2Fj_HAzc4M.shields&label=scheduled%20jobs&logo=prometheus&logoColor=white)](https://healthchecks.io)
[![Public endpoint 7d](https://img.shields.io/uptimerobot/ratio/7/m803634462-26ba093afb66ea071e032353?label=public%20endpoint%207d&logo=uptimerobot&logoColor=white)](https://stats.uptimerobot.com/uA0nWd408c)
[![Public endpoint 30d](https://img.shields.io/uptimerobot/ratio/30/m803634462-26ba093afb66ea071e032353?label=30d&logo=uptimerobot&logoColor=white)](https://stats.uptimerobot.com/uA0nWd408c)

{% assign order = "cluster,storage,databases,observability,supply_chain,ci,repo,hardware,referees,site" | split: "," %}
{% assign titles = "The cluster,Storage,Databases,Observability,Supply chain,CI,The platform repository,Hardware repositories,The referees (snapshot),This site" | split: "," %}
{% for g in order %}
{% assign rows = s[g] %}
{% assign methods = site.data.stats_methods[g] %}
{% assign o = s.observability %}

## {{ titles[forloop.index0] }}

{% case g %}
{% when "cluster" %}
What Kubernetes reports about itself. These are counts of API objects, so a CronJob that is
suspended is still a CronJob, and a pod that finished is still a pod.
{% when "storage" %}
Ceph, asked through its own toolbox. *Raw* is before replication; *stored* is what the
applications actually wrote, so the ratio between them is the cost of replication.
{% when "databases" %}
Postgres under an operator. The two synchronous rows ask different questions: one reads what
the configuration requests, the other asks each primary what is true right now.
{% assign d = s.databases %}
{% if d.synchronous_clusters == d.synchronous_clusters_spec %}They agree at the moment of measurement.{% else %}**They disagree at the moment of measurement**, and the second one is the one to believe.{% endif %}
{% when "observability" %}
Prometheus, asked over its HTTP API. Read the history row before any rate. Retention is the
lower of two limits, a time limit of {{ o.retention_days }} days and
{% if o.retention_size_gib > 0 %}a size cap of {{ o.retention_size_gib }} GiB{% else %}no size cap{% endif %},
and the store holds {{ o.data_span_days }} days at the moment of measurement.
{% if o.data_span_days < 7 %}That is less than a week, so **no weekly or monthly figure is published from it**, and the
failed-notifications row counts over the history that exists rather than over seven days.
{% else %}That covers the week, so the failed-notifications row is a true seven-day count.{% endif %}
{% when "supply_chain" %}
What is running, and whether the signing story holds for the images that are ours. *Ours*
means built and pushed to the estate's own registry; a mirror of someone else's software is
counted as theirs, and if it is unsigned that is not a defect in our pipeline.
{% when "ci" %}
Parsed from the workflow files of the platform repository, not read from run history.
{% when "repo" %}
Counted from the committed tree of the private platform repository, so unsaved work cannot move
a number. The repository figures are the committed HEAD at generation time:
{{ s.repo.platform_head }}. The test figures are static counts of test
definitions in the source, **not a pass rate**: nothing is built or run to produce them.
{% when "hardware" %}
The sibling repositories, named here by role. Commits and static counts of test functions only;
nothing is built or run to produce them. The C assertions of the rover platform are a separate
row, because one test function holds several of them.
{% when "referees" %}
The same public endpoints the badges above read, fetched by the generator at the time
stamp, so each is the state at the generation instant. Unlike the badges, these do not move
until the next run.
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
    <tr><td>{{ m.label | escape }}</td><td><strong>{{ row[1] | escape }}</strong>{{ m.unit | escape }}</td><td>{{ m.how | escape }}</td></tr>
{%- endfor %}
  </tbody>
</table>
{% endfor %}

## What this page is not

**It is a snapshot, not a feed.** `make stats` runs the generator against the cluster, and
the file it writes is committed like any other change. Between runs the numbers stand still
while the estate does not. A guard fails the build when the file is more than three weeks
old, which keeps the timestamp honest; it cannot keep the figures current, only visible
when they are not.

**It is aggregates only, and the platform is private.** Counts, percentages, versions and
dates. No machine, address, namespace, workload or secret is named, and the generator runs
its own output through the same leak guard as every page on this site before it will write
the file, and refuses to write at all if a measurement fails. A partial page would be worse
than a stale one.

**Measured is not the same as good.** Each figure says what was counted, and that is all it
says. A count of alert rules is not a measure of whether they would fire; a count of tests
is not a pass rate; a green health word is a reading, not a verdict.

**Some things are missing on purpose.** Vulnerability counts by severity, the code-quality
gate, the number of identity realms and the findings in the tracking systems all sit behind
credentials that the generator does not hold. Nothing here guesses at them, and nothing is
published for them. If a figure you expected is absent, that is the reason.
