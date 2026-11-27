---
title: Product practice
tldr_what: "How the platform decides what is worth building before it builds it: every app feature gets a four-risk box (value, usability, feasibility, viability) and is built in thin slices, the first of which runs end to end on a real phone. The product layer of the product production platform."
tldr_why: "Most homelab platforms stop at delivery, which is the easy half. Here a check fails the build if a design page has an empty risk cell, and from the second slice on, the value and usability cells must say what a real person's use showed. The first design is at slice 0, and the page says so."
tldr_use: "A lightweight way to put product discovery into a repository: a four-row table you can copy into any design doc, a slice rule that tests the riskiest part first, and a check that stops the table being filled in once and forgotten."
reread: 2026-11-27
summary:
  - "**What it is:** two rules adopted on 2026-11-17. Every app design page carries a four-risk box (value, usability, feasibility, viability: who judges, the cheapest test, the result). Every feature is built in thin slices, and the first one runs end to end on a real device before anything is built behind it."
  - "**What enforces it (built):** a check that fails a design page with an empty or placeholder risk cell, and from slice 2 on refuses \"not tested\" for value and usability. It checks the form, not that a result is true. The rule that a record of each slice's use comes before the next slice merges has no check yet (open)."
  - "**Where it stands, 2026-11-26:** one design page uses it, live updates for the location app. It is at slice 0: nobody has used a live update yet. Feasibility passed on the server side in throwaway clusters (two runs on a home CI machine failed); the phone side, value and usability are not tested."
  - "**What it is not:** proof of product success. There are no users and no market; the reference apps test the method, not demand. A proposal to make this the front end of a gated software factory is written and not accepted."
---

# Product practice: deciding what is worth building

{% include tldr.html %}

{% include in-short.html %}

A platform that ships anything reliably is only half of a product production platform. The other half is deciding what to ship,
and finding out early when the answer is wrong. This page describes that half as it is practised here. It is the youngest
part of the platform, and every statement carries one of the site's four words: **proven**, **built**, **planned** or **open**.

## Why a platform needs a product layer

Delivery answers "can we ship it safely?". It does not answer "should we?". A platform judged only on deploys, drills and
uptime can get very good at shipping things nobody uses. Platform engineering guidance warns against exactly this
("build it and they will come") and judges a platform by whether the work on it succeeds. So the platform's rules reach one
step further back than the pull request: into the design page, before any code exists.

## Dual track: discovery and delivery

**Discovery just became cheap. Delivery still has to be solid.** Cagan's case for discovery rests on prototypes being
cheap, and in September 2025 he wrote that AI tools have brought the cost of live-data prototypes "way down", "truly game
changing for serious product creators", while such prototypes are "not for building actual products"
([The purpose of prototypes](https://www.svpg.com/the-purpose-of-prototypes/)). A platform where a proven slice becomes a
real product, signed, traced, backed up and drilled, is the other half, and together they make proper discovery and
delivery affordable for one person or a small team.

**The surgical team, again.** In *The Mythical Man-Month* (1975), Fred Brooks described the surgical team, after Harlan
Mills: one chief programmer does the core work, with a small crew in support. AI agents now fill much of that crew, so a
product team can shrink toward that size and spend more of its time on the problem to solve, and less on how to solve it,
which the AI does more of, through the same checks as anyone. Here it is one person with AI agents. Whether it holds for a
small team, and how much it adds, is not measured.

Two tracks, not two teams ([Dual-Track Agile](https://www.svpg.com/dual-track-agile/)): discovery quickly finds what is
worth building, and delivery builds it so it can be released and kept. What is practised and what is only the aim, read
2026-11-27:

| Idea | After | Here | Status |
| --- | --- | --- | --- |
| Four big risks answered before building | Cagan | the four-risk box on every design page, checked by a script | practised since 2026-11-17 |
| Thin slices: earliest testable, usable, lovable | Kniberg; Kniberg and Cockburn | slice labels, the riskiest part first, on a real phone | practised; one design, at slice 0 |
| Feasibility prototype | Cagan | a throwaway trial app proved the live-update path on throwaway clusters | practised (2026-11-17 and 19) |
| User and live-data prototypes | Cagan | a thin slice in front of outside users, with usage and variant events measured | aim; the usage and variant events are not built, and no outside user has seen a slice |
| Outcomes over output | Cagan, *Empowered* | every app names, before building, the measure that will say it worked | aim; a rule since 2026-11-27, nothing built |
| Build to learn, then build to earn | Cagan | a training system now, the killer app later | the stance of the whole platform |
| AI as a colleague, not a tool | Kniberg, *Generative AI in a Nutshell* | a frontier model writes, the checks referee, every change through the same gates | practised; its effect on output not measured |

## The four-risk box

Every app design page carries, near the top, one line that says which slice a person has last used, and a table with one row
per risk. The four risks are Marty Cagan's:

| Risk | The question |
| --- | --- |
| **Value** | Will someone use it, or choose it over what they do now? |
| **Usability** | Can they work out how to use it, without help? |
| **Feasibility** | Can it be built on this platform, with what we have? |
| **Viability** | Does it work for the rest of the business: cost, the launch gates, the law? |

Each row names **who judges** the risk, **the cheapest test** that would show the answer, and **the result**. The template
you can copy:

```text
**Slice:** 0 (nothing has been used yet)

## Four risks

| Risk | Who judges | Cheapest test | Result |
| --- | --- | --- | --- |
| **Value** | who decides it is worth having | the cheapest test that would show it | what the test showed |
| **Usability** | ... | ... | not tested |
| **Feasibility** | ... | ... | ... |
| **Viability** | ... | ... | ... |
```

The point of "who judges" is that each risk has an owner who is not the code. The point of "cheapest test" is that a risk is
tested with the least work that could answer it, which is rarely the full feature.

## Slices: the riskiest part first, on a real device

A feature is built in thin vertical slices, each running end to end, after Henrik Kniberg's account of the minimum viable
product and the "elephant carpaccio" exercise. Three rules:

1. **The first slice runs end to end on a real device** and tests the risk the feature exists to take, before anything is
   built behind it. For live updates in the location app that means one event published by one server and received on a real
   phone attached to another, before the outbox, failover and geofence work.
2. **Each slice is labelled testable, usable or lovable.** Kniberg's "lovable" includes "willing to pay for", which a
   household reference app cannot test, and the label says so rather than claiming it.
3. **A record of what the slice's use showed comes before the next slice merges.** The next step is decided by what a person
   did, not by the plan.

## What enforces it, and what does not

- **Built:** a check runs on every change and fails a design page whose risk table has an empty cell, or a placeholder
  (`...`, `TBD`, `TODO`) where a result should be. So a page copied from the template fails until it is written.
- **Built:** "not tested" is an allowed result at slice 0 or 1. From slice 2 on, the value and usability results must say what
  a person's use showed, and "not tested" fails. The box cannot be filled in once and left.
- **Built:** the check has a test that plants each fault and proves the check refuses it.
- **Open:** the check reads the form of the table, not whether a result is true. A person still has to read it.
- **Open:** the rule that a record of a slice's use comes before the next slice merges has no check yet.

## Where it stands, 2026-11-26

One design page uses the box so far: live updates for the location app (later also for the warning and messaging apps). It is
at **slice 0**: nobody has used a live update yet.

| Risk | Who judges | Cheapest test | Result, 2026-11-26 |
| --- | --- | --- | --- |
| **Value** | the owner | a week of the app's chat between two real accounts, one on a phone carried for real, then a geofence alert | not tested; one person on two devices tests use, not value between two people, and the page says so |
| **Usability** | the owner, on a phone | 30 minutes of a throwaway screen on cellular, with a Wi-Fi to mobile handover and a sign-in token rollover | not tested |
| **Feasibility** | the AI model, with an outside referee | the server side on a throwaway cluster, then the phone slice | server side passed on throwaway clusters (2026-11-17 and 2026-11-19); two runs on a home CI machine failed on 2026-11-19, on timing under limited CPU (open); phone side not tested |
| **Viability** | the owner | answer four written questions before any real location data is held | not tested; how long locations are kept and how deletion reaches the backups are decided, not built |

The table is copied, simplified, from the private design page. It is published to show the method working on a real design,
including that three of its four results are still "not tested".

## What this is not

- **Not proof of product success.** There are no users and no market. The reference apps test the method, not demand.
- **Not a full discovery practice.** Interviews, prototypes for many users and a product team are out of reach for one person;
  this is the part that fits in a repository and can be checked.
- **Not yet the front of a software factory.** A decision record proposes that the four-risk box becomes the "approve the
  spec" gate of one delivery line for every change, with review routed by risk. It is proposed (2026-11-22), not accepted,
  and none of it is built.

## Read next

- [Applications of the platform](applications.html): the products the platform is meant to carry, and what is proven for each.
- [The reference apps](apps.html): the three apps this practice is first used on.
- [How we work](how-we-work.html): the delivery half, change by change.

## Sources

- Marty Cagan, [The four big risks](https://www.svpg.com/four-big-risks/), [The purpose of prototypes](https://www.svpg.com/the-purpose-of-prototypes/)
  and [Build to learn vs build to earn](https://www.svpg.com/build-to-learn-vs-build-to-earn/).
- Henrik Kniberg, *Making sense of MVP* (2016), and Henrik Kniberg and Alistair Cockburn, *Elephant carpaccio* (2013): thin
  slices, and earliest testable, usable and lovable product.
- Marty Cagan, [Dual-Track Agile](https://www.svpg.com/dual-track-agile/) and
  [Empowered](https://www.svpg.com/books/empowered-ordinary-people-extraordinary-products/).
- Fred Brooks, *The Mythical Man-Month* (1975), the chapter "The Surgical Team".
- Henrik Kniberg, [Generative AI in a Nutshell](https://leanpub.com/ainutshell) (a video, then a book).
- DORA, [Platform engineering](https://dora.dev/capabilities/platform-engineering/): judging a platform by the success of the
  work on it, not by its features.
