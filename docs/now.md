---
title: Now
tldr_what: "A live board of what is moving on the platform this week: four headline figures, what was done in the last few days, what is running now, what waits on the owner, and what comes next. It carries its own time, to the minute."
tldr_why: "It is updated on every change of state, a merge, an apply, a drill or a decision, from one data file that also writes the Now block on the GitHub profile, so the two cannot disagree. A guard fails the build when the board is more than 7 days old."
tldr_use: "The quickest way to see what is happening on the platform right now, and a pattern you can copy: one data file drawn in two places, with a guard that refuses a stale board."
description: What is moving this week on the new platform. Done in the last few days, running now, waiting on the owner, and next, kept current on every change of state.
reread: 2026-11-26
summary:
  - "**What it is:** a live board of what is moving this week: what was done in the last few days, what is running now, what waits on the owner, and what comes next, under four headline figures. The board carries its own time, to the minute."
  - "**How it stays current:** it is updated on every change of state (a merge, an apply, a drill, a decision), from one data file that also writes the Now block on the GitHub profile, so the two cannot disagree. A guard fails the build when the board is more than 7 days old."
  - "**What it is not:** not a promise of dates, and not the record. The counts and their sums are on [Progress](progress.html), measured figures on [Status](status.html), and what changed for good on [Recently](index.html#recently)."
  - "**What is left out on purpose:** machine names, addresses, exact versions, where secrets are kept and any weakness spelled out. Work that waits on the owner is named by its kind."
---
{% assign n = site.data.now %}

# Now

{% include tldr.html %}

{% include in-short.html %}

**As of {{ n.as_of }}.** This board is drawn from
[one data file](https://github.com/schultzzznet/schultzzznet/blob/main/docs/_data/now.yml), the same one that writes the
Now block on [the GitHub profile](https://github.com/schultzzznet) by
[a script](https://github.com/schultzzznet/schultzzznet/blob/main/scripts/build-now.py). It is updated on every change of
state: a merge, an apply, a drill, a decision of the owner's. The site is rebuilt when the file changes, never on a timer,
so the time above is the time the state was read, not the time you are reading it.

A guard fails the build when the board is more than 7 days old, when an item under *Done recently* is more than 14 days
older than the board, when a headline figure disagrees with a newer count on [Progress](progress.html) or
[Status](status.html), or when the profile's block is out of step with the file.

## Headline

| Figure | On {{ n.as_of }} |
| --- | --- |
{% for x in n.headline %}| {{ x.label }} | **{{ x.value }} of {{ x.of }}**{% if x.also %} ({{ x.also }}){% endif %} |
{% endfor %}

What each figure counts is under [the counts on Progress](progress.html#the-counts).

## Running now

<ul class="recently">
{%- for x in n.running %}
  <li>{{ x.text | markdownify | replace: "<p>", "" | replace: "</p>", "" | strip }}</li>
{%- endfor %}
</ul>

## Waiting on the owner

{% if n.waiting_on_owner and n.waiting_on_owner.size > 0 -%}
<ul class="recently">
{%- for x in n.waiting_on_owner %}
  <li>{{ x.text | markdownify | replace: "<p>", "" | replace: "</p>", "" | strip }}</li>
{%- endfor %}
</ul>
{%- else -%}
Nothing waits on the owner.
{%- endif %}

These are decisions and hands-on steps only the owner can take: approvals, work at the machines, and anything that touches
keys. Each is named by its kind, not its detail.

## Next, in order

<ol class="recently">
{%- for x in n.next %}
  <li>{{ x.text | markdownify | replace: "<p>", "" | replace: "</p>", "" | strip }}</li>
{%- endfor %}
</ol>

## Done recently

<ul class="recently">
{%- for x in n.done_recently %}
  <li><strong>{{ x.date | date: "%-d %b" }}.</strong> {{ x.text | markdownify | replace: "<p>", "" | replace: "</p>", "" | strip }}</li>
{%- endfor %}
</ul>

Items leave this list after two weeks. What changed for good stays on [Recently](index.html#recently) on the landing page.
