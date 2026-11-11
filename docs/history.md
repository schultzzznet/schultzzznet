---
title: "History: V1.0, then V2.0"
description: V1.0 ran from 2025-12-21 to 2026-11-10, and V2.0 was built on the same machines from what it taught. Month by month, dated milestones, and receipts anyone can check.
reread: 2026-11-11
body_read: 2026-11-11
summary:
  - "**What it is:** the history behind a day-old cluster. V1.0, the platform in the old private repository, ran for 324 days, from 2025-12-21 to 2026-11-10: Docker Swarm first, k3s beside it from 2026-04-04, Swarm retired on 2026-06-09. V2.0 was built on the same six machines on 2026-11-10 and 11."
  - "**V1.0 in numbers (frozen):** 2,051 commits on 198 days, with a commit in every calendar month from December 2025 to November 2026; 226 merged pull requests (the first gated merge was on 2026-08-06); 12,937 CI runs; 42 decision records."
  - "**Receipts you can check:** this public repository described V1.0 from 2026-04-18, with push times recorded by GitHub, and published V1.0's commit count rising from 1,749 to 1,943 in October 2026, before V2.0's repository existed."
  - "**Not claimed:** uptime. No single cluster ran 324 days: the last V1.0 cluster ran from 2026-09-04 to 2026-11-10. The monthly counts come from private repositories, so they are my report, with the method public."
  - "**Why V2.0:** each of its main changes answers something V1.0 measured or got wrong, listed [below](#what-v10-taught-and-what-v20-does-because-of-it) with dates."
---
{% assign h = site.data.history %}
{% assign v1 = h.v1 %}
{% assign rp = site.data.stats.repo %}
{% assign gen_date = site.data.stats.generated_at | slice: 0, 10 %}
{% assign repo_url = "https://github.com/schultzzznet/schultzzznet" %}
{% assign window = 0 %}{% for m in h.months %}{% assign window = window | plus: m.days %}{% endfor %}

# History: V1.0 ran for {{ v1.days }} days, and V2.0 was built from it

{% include in-short.html %}

The cluster this site describes is new: it was built on {{ h.v2.built }}. The platform and the practice behind it are
not. **V1.0** is everything that ran from the old private repository, from its first commit on {{ v1.first_commit }} to
its teardown on {{ v1.retired }}: {{ v1.days }} days, a Docker Swarm cluster first, a k3s cluster beside it from
2026-04-04, Swarm retired on 2026-06-09, and the k3s cluster last rebuilt from scratch on {{ v1.last_cluster_built }}.
**V2.0** is the next step: a new private repository from {{ h.v2.first_commit }}, built on the same six machines from
{{ h.v2.built }}, and shaped by what V1.0 measured. [The diff list](versions.html) compares the two area by area; this
page is the line between them.

**What this page claims, and what it does not.** It claims a platform that ran and a practice that did not stop: a
commit in every calendar month from December 2025 to November 2026, on {{ v1.active_days }} of the
{{ window }} days from its first commit to its last
(it ran {{ v1.days }} days in all, to its teardown). It does **not** claim uptime.
No single cluster ran {{ v1.days }} days: the last V1.0 cluster ran from {{ v1.last_cluster_built }} to {{ v1.retired }},
and the one before it was wiped. An earlier version of this site said the core had been "constant for eight months";
that sentence was [removed on 2026-10-09]({{ repo_url }}/commit/15914e05770344683667d2af2ecc0fa6ab48a417), and nothing
here brings it back.

## The whole time, on one line

{{ v1.first_commit }} on the left, {{ v1.retired }} on the right. Hatched bars are dated from my private record; the
plain ones can be checked in this public repository.

<div class="hist-legend"><span class="hist-k-v1">V1.0</span><span class="hist-k-site">Public record of it</span><span class="hist-k-v2">V2.0</span></div>
<div class="hist-gantt" role="img" aria-label="Timeline from {{ v1.first_commit }} to {{ v1.retired }}">
{%- for e in h.eras %}
{%- assign left = e.from_day | times: 100.0 | divided_by: h.chart_days | round: 2 %}
{%- assign width = e.to_day | minus: e.from_day | times: 100.0 | divided_by: h.chart_days | round: 2 %}
  <div class="hist-row"><span class="hist-label">{{ e.name }}<small>{{ e.from }} to {% if e.to %}{{ e.to }}{% else %}now{% endif %}</small></span><span class="hist-track"><span class="hist-bar hist-{{ e.track }}{% if e.evidence == 'private' %} hist-private{% endif %}" style="left: {{ left }}%; width: {{ width }}%"></span></span></div>
{%- endfor %}
{%- assign t0 = v1.first_commit | date: "%s" | plus: 0 %}
{%- assign quarters = "2026-01-01,2026-04-01,2026-07-01,2026-10-01" | split: "," %}
  <div class="hist-row hist-axisrow"><span></span><span class="hist-axis">
{%- for q in quarters %}
{%- assign qd = q | date: "%s" | minus: t0 | divided_by: 86400 | times: 100.0 | divided_by: h.chart_days | round: 2 %}<span style="left: {{ qd }}%">{{ q | date: "%b %Y" }}</span>
{%- endfor %}</span></div>
</div>

## Month by month

Every figure here is written by [`scripts/gather-history.py`]({{ repo_url }}/blob/main/scripts/gather-history.py) and is
frozen: V1.0's repository has had no commit since {{ v1.last_commit }}, and a re-run must find nothing changed.
December 2025 starts on the 21st and November 2026 ends on the 5th, V1.0's last commit.

{% assign maxc = h.months | map: "commits" | sort | last %}
<table class="hist-months">
  <thead><tr><th>Month</th><th>V1.0 commits</th><th>Days with a commit</th><th>Pull requests merged</th><th>CI runs</th><th>Commits to this public repository</th></tr></thead>
  <tbody>
{%- for m in h.months %}
{%- assign w = m.commits | times: 75 | divided_by: maxc %}
    <tr><td>{{ m.month }}{% if m.days < 28 %} <small>({{ m.days }} days)</small>{% endif %}</td><td class="hist-barcell"><span class="hist-mbar" style="width: {{ w }}%"></span>{{ m.commits }}</td><td class="hist-num">{{ m.active_days }} of {{ m.days }}</td><td class="hist-num">{{ m.merged_prs }}</td><td class="hist-num">{% include thousands.html n=m.ci_runs %}</td><td class="hist-num">{{ m.site_commits }}</td></tr>
{%- endfor %}
    <tr class="hist-total"><td>All {{ h.months | size }} months</td><td>{% include thousands.html n=v1.commits %}</td><td class="hist-num">{{ v1.active_days }} of {{ window }} <small>(first to last commit)</small></td><td class="hist-num">{{ v1.merged_prs }}</td><td class="hist-num">{% include thousands.html n=v1.ci_runs %}</td><td class="hist-num">{{ h.site.commits_v1_window }}</td></tr>
  </tbody>
</table>

- **Whose clock.** Commits and days with a commit are git's clock: the committer's own, which an author can set.
  Pull requests and CI runs are GitHub's clock (UTC), which I cannot set, but the repository is private, so you cannot
  look. The last column is this public repository, which you can (see [the receipts](#receipts-anyone-can-check)).
- **Why pull requests start in August.** Until the pull-request gate of 2026-07-30 changes went straight to the main
  branch. The first gated merge was on {{ v1.first_merged_pr }}.
- **CI runs** count every run of every workflow, green or red. The first was on {{ v1.first_ci_run }}, the day after the
  first commit. They show that the pipeline ran, not that it passed.
- **Not shown:** how many hours went into it, or whether the cluster was up. Running time is evidenced only by the dated
  snapshots below and, from 2026-07-31, by an outside probe whose figures were published while V1.0 ran.

## Receipts anyone can check

The commit dates in a git repository are set by its author, so on their own they prove nothing. What a reader can check
is GitHub's own record of when a push reached this public repository: its
[activity log]({{ repo_url }}/activity) and its [Pages deployments]({{ repo_url }}/deployments)
({{ h.site.deployments_before_v2 }} of them before V2.0's repository existed, the first on
{{ h.site.first_deployment | slice: 0, 10 }} at {{ h.site.first_deployment | slice: 11, 5 }} UTC). A commit fixes its
text by its id, so the push time proves that the text was public by then.

### V1.0's own count, published while it ran

Each row is a generated stats file from before V2.0. The V1.0 figures in it are what this site published at the time;
the last column is the private repository counted today, up to the same moment.

| Measured (UTC) | Pushed, by GitHub's clock | V1.0 commits published | Repository age then | Decision records | Cluster age then | V1.0 commits counted today, to that moment |
|---|---|---|---|---|---|---|
{% for r in h.receipts -%}
| [{{ r.generated_at | slice: 0, 10 }} {{ r.generated_at | slice: 11, 5 }}]({{ repo_url }}/blob/{{ r.commit }}/docs/_data/stats.yml) | {{ r.on_github | slice: 0, 10 }} {{ r.on_github | slice: 11, 5 }} | {% include thousands.html n=r.v1_commits %} | {{ r.v1_age_days }} days | {{ r.v1_adrs }} | {{ r.cluster_age_days }} days | {% include thousands.html n=r.v1_commits_counted_now %} |
{% endfor %}

The published count rose from 1,749 to 1,943 in public between 2026-10-09 and 2026-10-27, 27 to 9 days before
V2.0's repository was created on {{ h.v2.first_commit }}. Counting the private repository today gives figures within 4 of what was published; the
difference is commits made before a measurement and pushed after it. The cluster ages are where the date of the last
V1.0 cluster build, {{ v1.last_cluster_built }}, comes from.

### What cannot be checked from outside

Public receipts start on 2026-04-18, the first push to this repository that describes the platform. The four months
before that, the monthly counts above, and every line below marked *private record* come from private repositories,
measured by a committed script whose method is public. You cannot re-run it, so they are my report, not proof.

## The timeline

Dated milestones, written by hand and kept generic: no machine names, addresses or versions. A line with a commit
links to the public text, with the time GitHub recorded its push; a commit can be later than the event it records.

### V1.0, {{ v1.first_commit }} to {{ v1.retired }}

{% for m in h.milestones %}{% if m.track == "v1" %}
- **{{ m.date }}.** {{ m.text }} {% if m.commit %}*Public:* [`{{ m.commit | slice: 0, 7 }}`]({{ repo_url }}/commit/{{ m.commit }}), pushed {{ m.on_github | slice: 0, 10 }} {{ m.on_github | slice: 11, 5 }} UTC.{% else %}*Private record.*{% endif %}
{%- endif %}{% endfor %}

### V2.0, from {{ h.v2.first_commit }}

{% for m in h.milestones %}{% if m.track == "v2" %}
- **{{ m.date }}.** {{ m.text }} {% if m.commit %}*Public:* [`{{ m.commit | slice: 0, 7 }}`]({{ repo_url }}/commit/{{ m.commit }}), pushed {{ m.on_github | slice: 0, 10 }} {{ m.on_github | slice: 11, 5 }} UTC.{% else %}*Private record.*{% endif %}
{%- endif %}{% endfor %}

The V2.0 repository had {{ rp.commits }} commits on {{ gen_date }} ([status](status.html)). Its own run records stay
private; [How we work](how-we-work.html) describes them.

## What V1.0 taught, and what V2.0 does because of it

V2.0 is not a restart. Each of its main changes answers something V1.0 measured or got wrong, and the organising idea,
two independent axes (what you write, and who applies it), is explained in
[How we work](how-we-work.html#two-axes-what-you-write-and-who-applies-it). The status word is the one used on the
[diff list](versions.html): proven means seen working once, on that date.

| V1.0 taught | So V2.0 | Status, 2026-11-11 |
|---|---|---|
| On 2026-10-21 a second push from an out-of-date checkout rolled the cluster back to an old image, where it stayed for two days. The person running a command held the only copy of what should be there. | The cluster pulls its state from git and puts a hand edit back; no CI job holds a cluster credential. | **proven** 2026-11-10 |
| Of the hand-run steps I classified on 2026-10-27, only 19 were declarative applies a controller could own; most were checks, host automation and orchestration. | Only the cluster layer moved to declarative and pull. Checks and orchestration stay scripts, hosts stay playbooks: not fully GitOps yet. | **built**, by design |
| Image signatures were checked by scripts, not by the cluster: 6 of 7 first-party images verified on 2026-10-27, and nothing refused the seventh. | Admission refuses vendor images that are not on a pinned list, and own images without the CI signature. | **proven** once: one real refusal, 2026-11-10 |
| A rebuild from blank machines was never run before the teardown. | One supervised bring-up from blank machines: about 4.5 hours from the first merge to a converged site. | **proven** once, 2026-11-10 |
| Synchronous commit was silently dropped for 23 days while the documentation said RPO 0 (2026-09-16 to 2026-10-09). | No recovery-point number is published until one is measured; a setting in a spec is not a reading. | **open** |
| Learnings lived in session notes, and the 113 incidents were collected into one register only at the end (2026-11-05). | A run record goes in the same pull request as the change, failures kept: {{ rp.records }} records on {{ gen_date }}, {{ rp.records_fail }} of them fail. | **built** |
| Self-hosted runners held the admin credentials and the signing key, and hard resets and a full disk took them out. | Jobs that hold a key run on hosted runners, the signing key is limited to the main branch, and home builders get a fresh VM per job and no secrets. | **built** |
| The daily drift guard ran red from 2026-11-02 to 2026-11-09 and nobody read it. | Monitoring with alert rules from 2026-11-11; an alert that reaches a person is the next requirement. | monitoring **proven** 2026-11-11; alerts to a person **open** |

It is not all forward. In 30 rows of the diff list V1.0 was better, mostly in watching, scanning and surviving a lost
machine, and most of that is not rebuilt yet: [what V1.0 did better](versions.html#what-v10-did-better).

## How these numbers are made

`make history` in this repository runs the generator against local checkouts of both private repositories and GitHub's
API; `make history-check` measures again and fails if anything but the generation time changed. The file was generated
{{ h.generated_at | slice: 0, 10 }}. It holds counts, dates and the lines above, and passes the same leak guard as
every other page.

| Figure | How it is counted |
|---|---|
{% for pair in site.data.stats_methods.history -%}
| {{ pair[1].label }} | {{ pair[1].how }} |
{% endfor %}

Related pages: [V1.0 and V2.0: what changed](versions.html), [How we work](how-we-work.html), [status](status.html),
[one incident, in full](incident.html), [what I'd do differently](lessons.html).
