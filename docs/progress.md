---
title: Progress
description: Where the work on the new platform stands. Build, then break, then upgrade, with measured counts as of 2026-11-26.
reread: 2026-11-26
summary:
  - "**What it is:** where the work on the new platform stands, in one picture and a few tables. The counts were copied on 2026-11-26 from the platform's own generated status page, its plan and its run records, and a script draws the picture from them. There is no list of plan items here, and an open weakness is named only as a known gap."
  - "**The rule is build, then break, then upgrade.** A failure test runs only on something built to survive it, and an upgrade only on a cluster that has survived losing a node. On 2026-11-26 the work is in the break part, at phase 4 of the phases 0 to 5: the power-off drills."
  - "**Counts on 2026-11-26:** 2 of 12 build-order steps are done, and 2 more on a test cluster only. 3 of 110 objective rules are built. 19 of 24 drills on the home site passed. 98 of 133 run records pass. 1 of 30 single points of failure is proven fixed: cluster DNS, by a power-off on 2026-11-25."
  - "**Next:** the rest of the power-off drills, each rehearsed on a simulated cluster before it runs live. The second passed in part on 2026-11-25 and waits for the owner's word; the third waits for a known gap of its rehearsal. Then the upgrade phase."
---
{% assign p = site.data.progress %}
{% assign c = p.counts %}

# Progress

{% include in-short.html %}

**As of {{ p.as_of }}.** Every number on this page is a count on that day. It was copied by hand from the private platform
repository's generated status page, its plan and its run records, into
[one data file](https://github.com/schultzzznet/schultzzznet/blob/main/docs/_data/progress.yml). The page and the picture
are both drawn from that file, so they cannot disagree. A guard fails the build when the file's sums do not add up, when
the picture was drawn from other data, or when the file is more than three weeks old. The figures that [Status](status.html)
also shows are measured there by a script, on their own date. Where the two dates differ, the numbers may differ too.

This page shows where the work stands. It is not a promise of dates: the plan sets no dates for the phases or the cutover, and the next drill can turn a
pass into a fail.

## The picture

<a href="assets/diagrams/progress.pdf"><img src="assets/diagrams/progress.png" alt="Progress on {{ p.as_of }}: five headline counts; the six phases under build, break and upgrade, with phase {% for x in p.phases %}{% if x.state == 'current' %}{{ x.number }}, {{ x.title | downcase }},{% endif %}{% endfor %} marked as now; the twelve steps of the build order coloured by state; every drill as one block, passed or not; the rules per objective; and what comes next" width="1568" loading="lazy" style="max-width:100%;height:auto"></a>

[The PDF](assets/diagrams/progress.pdf) zooms and prints. The drawing is
[progress.tex](assets/diagrams/progress.tex), and its numbers come from the data file by
[a script](https://github.com/schultzzznet/schultzzznet/blob/main/scripts/build-progress.py).

## Build, then break, then upgrade

The work runs in three parts and six phases. **Build** comes first, so that a failure test runs only on something built to
survive it. **Break** is the drills, software first, then power-offs. **Upgrade** comes last, so that a rolling upgrade runs
only on a cluster that has been shown to survive a node going away. One Kubernetes upgrade ran ahead of this order, on 2026-11-18, at
the owner's go; the phase table says so.

| Phase | Part | State | Where it stands |
| --- | --- | --- | --- |
{% for x in p.phases %}| {{ x.number }}. {{ x.title }} | {{ x.group }} | {% case x.state %}{% when 'current' %}**now**{% when 'partly' %}partly done{% when 'not-started' %}not started{% else %}{{ x.state }}{% endcase %} | {{ x.note }} |
{% endfor %}

**Now.** {{ p.now }}

## The counts

| What | Count on {{ p.as_of }} | What it counts |
| --- | --- | --- |
| Steps of the build order | {{ c.steps_done }} of {{ c.steps_total }} done | {{ c.steps_done_on_kind }} more are done on a test cluster only, {{ c.steps_partly }} partly, {{ c.steps_not_started }} not started and {{ c.steps_gated }} waits on its gate. Each step has a written done-when test, and a step is done only when that test passes. |
| Objective rules | {{ c.rules_built }} of {{ c.rules_total }} built | {{ c.rules_partly }} partly built, {{ c.rules_not_built }} not built. The rules sit under eleven objectives, and each names the check that would show it is met. Built means a check enforces the rule, not that it has held for long. |
| Run records | {{ c.records_pass }} of {{ c.records }} pass | {{ c.records_fail }} fail, {{ c.records_partial }} pass in part and {{ c.records_note }} are notes (a reading, no test). A record is written each time a test or drill runs and its result matters. A failure is kept when it taught something, and a record is never edited to change its result. The latest is dated {{ c.records_latest }}. |
| Single points of failure | {{ c.single_points_fixed }} of {{ c.single_points }} fixed | {{ c.single_points_accepted }} accepted and {{ c.single_points_open }} open. A point counts as fixed only after a drill has powered off the machine that held it and the service went on. |

## Drills

Each drill is one test, run once and written up as a record.

| Kind | Where | When | Run | Passed | What it is |
| --- | --- | --- | --- | --- | --- |
{% for x in p.drills %}| {{ x.kind }} | {% if x.where == 'live' %}home site{% else %}simulated cluster{% endif %} | {{ x.dates }} | {{ x.run }} | {{ x.passed }} | {{ x.what }} |
{% endfor %}

A failure drill passes when the service came back within its written target and no acknowledged write was lost. The
simulated cluster is shaped like home, with three servers and three agents. A rehearsal there does not count as proof for
the home site: real network cards, the firewall and the old laptops' speed can change the timing. Its job is to find a
fault before the live drill does. The results up to 2026-11-20, drill by drill, are on [Reliability](reliability.html).

## The build order

Twelve steps, each with a written done-when test.

| Step | What | State |
| --- | --- | --- |
{% for s in p.steps %}| {{ s.number }} | {{ s.title }} | {% case s.state %}{% when 'done-on-kind' %}done on a test cluster only{% when 'partly' %}partly done{% when 'not-started' %}not started{% when 'gated' %}waits on its gate{% else %}{{ s.state }}{% endcase %} |
{% endfor %}

A test cluster is a throwaway cluster on one machine. The home site is the real one, on six retired machines. A step done
on a test cluster only has its test passing there, not yet on the home site.

## What comes next

{% for x in p.next %}{{ forloop.index }}. {{ x.text }}
{% endfor %}

## How this page is kept honest

- **Counts, not targets.** Every figure is a count on the day named at the top. Nothing here is an estimate or a goal.
- **One source.** The page and the picture read the same data file, and the picture carries a digest of the data it was
  drawn from. The guard fails when the digest does not match.
- **A date that can go stale.** The guard fails when the data file is more than three weeks old. It also fails when the
  generated status figures were measured later than the file and disagree with it.
- **Sums that must add up.** The steps by state must add up to the steps, the rules per objective to the rules, and the
  records by result to the records. Any count typed in the summary at the top must be a count of the file.
- **What is left out on purpose:** plan items, machine names, addresses and software versions. An open weakness appears
  only as a known gap. The detail stays in the private repository; the trace from each number to its source line is
  recorded in the pull request that changed it.
