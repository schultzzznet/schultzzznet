---
title: Applications of the platform
description: Which real workloads the platform serves or is meant to serve - embedded Linux, a mower, a rover, 3D printing, the reference apps and the killer app - each with a dated status word and what the platform still lacks for it.
reread: 2026-11-12
body_read: 2026-11-12
summary:
  - "**What it is:** the workloads the platform is meant to carry, one section each: embedded Linux (two boards), the mower, the rover, 3D printing, the reference apps and the killer app. Each has dated rows marked proven, built, planned or open, and a list of what the platform still lacks for it."
  - "**Proven on the new platform, 2026-11-12: one workload.** The Warn backend is up on the home site (2026-11-10/11), with one backup restored into a scratch cluster. The other applications are real work, but they ran on V1.0 (gone 2026-11-10), run on a bench or a workstation, or are not started."
  - "**The killer app does not exist.** There is no name, user, market or date. What exists is what the platform holds ready for the day: a written app standard (3 of 109 rules built), a template, 16 launch gates (0 done) and one green rehearsal."
  - "**The aim is to prove real, live applications of the platform.** Today this page is mostly the list of what still stands between the aim and the proof; it will get shorter in the right way when rows move to proven."
---

# Applications of the platform

{% include in-short.html %}

The aim of this estate is to be a platform that real applications run on, and to show it. This page is the account of how far that has got, **and the honest answer on 2026-11-12 is: not far.** Exactly one application, the Warn backend, is running on the new platform, and the cluster it runs on is days old. The other applications are real work (a hardened Linux image, a robot rig that draws straight lines, printed parts), but they were served by V1.0 until it was torn down on 2026-11-10, run on a bench or a workstation, or are only planned. The killer app does not exist at all. Every row below carries a date and one of four words: **proven** (a dated record shows it working), **built** (it exists, its working on the platform is not shown), **planned**, **open** (a question with no answer yet). Nothing here is an uptime or a user claim, and "production" appears only as a goal.

The word *application* is used loosely on purpose. A mobile app, a Linux image and a robot rig put different demands on the platform: public reads, signed delivery, a vulnerability record, a place to keep telemetry. That spread is the reason for choosing them.

| Application | What it is | Platform status, 2026-11-12 | Section |
|---|---|---|---|
| Embedded Linux (Pi) | Signed A/B Linux image with a bill of materials | Hardware-proven image; its supply-chain services were on V1.0 and are planned again | [below](#embedded-linux-two-boards) |
| Embedded Linux (i.MX 8M Nano) | An image for a second board | Planned; survey scripts only | [below](#embedded-linux-two-boards) |
| Mower | RTK-GPS pattern mowing, tried on a bench rig | Rig proven on the bench; no mower opened, no RTK fix | [below](#the-mower) |
| Rover | Shared robot code, plus a camera rover scaffold | Built; host tests exist, no run record cited | [below](#the-rover) |
| 3D printing | Parts as source code | Built; not on the cluster | [below](#3d-printing) |
| Reference apps | Warn, Loc8, Talk | Warn proven on the cluster; Loc8 and Talk planned | [below](#the-reference-apps) |
| The killer app | An application that does not exist yet | Open | [below](#the-killer-app) |

---

## Embedded Linux, two boards

**What it is.** A custom, minimal, hardened Linux image for a Raspberry Pi, updated over the air in signed A/B slots, with a bill of materials; and a second, much earlier project for a different board. The full account is on [the embedded page](yocto.html); this section only says how it relates to the platform.

**How it uses the platform (or will).**

- A shared artifact store for sources, releases and update streaming (V1.0; gone, planned again).
- A vulnerability tracker that received the nightly bill of materials (V1.0; gone, planned again).
- A fleet service that devices report to (V1.0; gone, planned again).
- A dependency mirror for the build (V1.0; gone, planned again).
- The build itself, the cache and the nightly job run on a separate small build host, not on the cluster. That is unchanged.

| Claim | Status | Date | Note |
|---|---|---|---|
| The image boots on a real board | proven | 2026-07-05 | First boot on a Pi 3 B+ |
| Signed A/B update, rollback and signing on hardware | proven | 2026-07-06, re-proven 2026-08-30 | The second date is the move to the current Yocto LTS |
| A release delivered over the air into the other slot | proven | 2026-09-01 | A bundle that broke later updates was withdrawn, not patched |
| A build from an empty cache restored 490 of 490 tasks; with a dead mirror, 0 | proven | 2026-09-25 | Not re-run since |
| Scanner truth: 0 findings, then about 100 raw matches, then 46 after triage | proven | 2026-07 | Old figure: first build on the previous LTS; not re-measured |
| Nightly upload of the bill of materials | open | 2026-10-27 | Refused for 28 of 28 retained nightly logs; fixed by hand once; the scheduled run was never shown to work, and the tracker is now gone |
| Vulnerability tracker, fleet service and dependency mirror on the new platform | planned | 2026-11-11 | None built |
| The same image carries the small bench rig used for the [mower and rover](#the-mower) work | proven | 2026-10-26 | An image, not a platform service; power cuts caused an automatic fall-back to the other slot |
| Secure boot | planned | 2026-11-07 | Written down only; the current page says there is none |
| A second board (i.MX 8M Nano) | planned | 2026-11-07 | Three commits (counted 2026-11-12): survey and backup scripts, a source brief, a written secure-boot chain. Nothing has been built, flashed or booted, and the survey was not checked as run |
| Pi 4 as a target | planned | 2026-11-07 | The default machine was changed; no boot is shown |

**What the platform still lacks for it.** Every service it used on V1.0: an artifact store, a tracker that takes the nightly upload, a fleet service, a dependency mirror, and an alert that reads the nightly job's exit code (nothing did, which is how 28 failures went unseen). The image pipeline is a candidate for the platform's signing and CI; it does not use them today. The second board is not an example of the platform at all yet.

---

## The mower

**What it is.** A project to replace the brain of old robotic lawn mowers with an RTK-GPS pattern-mowing stack, keeping the drive motors, blade and battery. It is a learning application, **not the killer app**. The north star ("drop it into any garden") is an aspiration, not a result. Everything is at the bench stage: no mower has been opened or driven, no RTK fix has ever been obtained, and nothing has cut grass. The repository has 268 commits, counted from the repository on 2026-11-12.

The hardware that exists is a small wheeled bench rig: a Pi on the A/B image, a microcontroller, motor drivers, wheel tachometers, a camera and a hobby GNSS receiver, on a printed LEGO Technic frame from the [printing](#3d-printing) work.

**How it uses the platform (or will).**

- The embedded image and its A/B updates (above): used on the rig.
- A simulation-first test gate that runs the real protocol and planner nightly: used.
- A pull-based heartbeat to a cloud app, with a phone client: source exists on the previous platform, not deployed (planned).
- The bill of materials, vulnerability matching and tracker for the mower image: a plan to reuse the embedded pipeline, nothing wired.

| Claim | Status | Date | Note |
|---|---|---|---|
| The rig drives an 80 x 80 cm square at 200 mm/s, every corner inside 2 cm | proven | 2026-10-26 | Wheel ticks alone; the owner's floor measurement |
| Three straight parallel 800 mm lanes, 200 mm apart, on wheel ticks alone | proven | 2026-11-06 | Lanes within about 1 degree of the tape, end about 7 mm off target; the referee was ink from a printed pen holder on the floor, not the rig's own estimate |
| Repeat runs overlap | proven | 2026-11-07 | Lines within about 1 cm run to run; turn pairs read 181 to 182.5 degrees for a 180 target |
| A rolling-diameter correction | proven | 2026-11-07 | At the first value every lane drew 5 to 8 percent short; the second value was measured. A ratio guess of 1.015 made one lane lean 13 degrees while the ticks said straight |
| A real GNSS receiver read by the tool | proven | 2026-10-13 | 10 seconds: any 3D fix 100 percent, **RTK fixed 0 percent**, verdict poor. Proof the tool works, and proof RTK is not shown. Date is that of the mower roadmap entry recording it |
| A/B install of the image on the rig | proven | 2026-10-26 | Both slots on the same bundle |
| Nightly simulation gate | built | 2026-07-30 | Added with the first platform commit; its checkout of the rover repository was fixed on 2026-10-11, after the shared code moved there on 2026-09-13. No run result is cited here, and a simulation result is not a field result |
| Gyro in the loop | planned | 2026-10-26 | Ordered; the reader code is tested in simulation only, never on the chip |
| Turn scatter of about 5 degrees on lane runs | open | 2026-11-07 | The ticks cannot see wheel slip; the gyro is the intended fix |
| RTK base and fix, mower teardown, cutting safety, docking | planned | 2026-11-12 | The roadmap says Phase 0 |
| Cloud app and phone client on the new cluster | planned | 2026-11-12 | Not deployed |

**What the platform still lacks for it.** A place for telemetry to arrive and be alerted on, a deployed cloud app, the bill-of-materials tracker, and a signing path for the image that is not the embedded project's own. The most useful thing the rig has produced is not a platform feature: ticks flattered curves, and ink and tape told the truth. An independent referee is the same habit the rest of this site argues for.

---

## The rover

**What it is.** Two things. First, a shared platform for slow ground machines: a safety-gated serial wire contract with the microcontroller as the safety authority, firmware core, an image base, a microcontroller update tool, navigation geometry and RTK tools. The bench rig above runs on it (33 commits, counted from the repository on 2026-11-12). Second, a video rover: a software scaffold for a self-driving camera carrier (3 commits, same count date). No video rover exists; its printed parts are on the [printing](#3d-printing) side and do not yet go together.

**How it uses the platform (or will).**

- One contract implemented three times (C, Python, Go) and pinned to the same reference frames, so drift fails a test instead of a machine. That is platform thinking applied to firmware.
- The image base and the boot-safety pieces (journal that survives power cuts, a console kept off the receiver's line): used on the rig.
- Its own CI: none. Tests are run by hand, and the mower's nightly gate checks it out.

| Claim | Status | Date | Note |
|---|---|---|---|
| The safety gate and the wire contract have host tests | built | 2026-09-13 | Date of the platform commit. Test counts are on the [status page](status.html); they count definitions, not a pass rate, and no dated run record is cited here. It is not certified and has not driven a real blade |
| The three implementations are pinned to the same reference frames | built | 2026-10-04 | Date of the latest golden-vector commit; no dated run record is cited here, and equality in tests is not interoperability on hardware |
| Boot safety and the persistent journal installed on the rig | proven | 2026-10-26 | The first install found a shell-compatibility fault, fixed the same day |
| A second consumer of the shared code | built | 2026-09-19 | The video rover scaffold runs against an in-process simulator only |
| A rover that drives, docks or charges | planned | 2026-11-12 | Nothing physical exists |
| Remaining shared parts moved in from the product repositories | planned | 2026-11-12 | The repository's own table marks them "to move" |

**What the platform still lacks for it.** CI for the shared repository itself, the same tracker and signing path as above, and a fleet service. With two consumers (one a scaffold) it is not a general robotics platform, and this page does not call it one.

---

## 3D printing

**What it is.** Parts as source code (OpenSCAD and Python), rendered to previews on a workstation; the mechanical layer behind the rig, the rover and a drone frame. The full account, with the parts, is on [the printing page](printing.html).

**How it uses the platform.** On V1.0 a gallery pod and a print-job schedule ran on the cluster. Both went with V1.0 on 2026-11-10; **no printing workload runs on the new cluster and none is planned** (checked 2026-11-11). Printing is therefore a source of parts for the applications above, not an application of the platform.

| Claim | Status | Date | Note |
|---|---|---|---|
| A printed copy of an open LEGO frame fits, hole for hole | built | 2026-11-03 | The commit "the printed pair is perfect" and a recorded fit gauge; no photograph or measurement is published here, so it is not marked proven |
| Frame, plate and pen-holder parts for the rig | built | 2026-11-06 | Not yet in the printing page's parts list (regenerated 2026-10-27) |
| Publish only parts that git tracks, behind the leak guard | built | 2026-10-27 | |
| Gallery and print pipeline on the new cluster | open | 2026-11-11 | An owner decision: add it as an application or retire it |

**What the platform still lacks for it.** Nothing it has asked for. It is the application that least needs a cluster, which is itself a finding: not every workload is a reason to run one.

---

## The reference apps

**What they are.** Three apps chosen to cover three shapes: **Warn** (public read, signed-in write), **Loc8** (private streaming inside groups) and **Talk** (user content between people). Each is a Flutter client and a Spring Boot service. The account of what they do, their screenshots and their bugs is on [the apps page](apps.html). They are not a product.

**How they use the platform.** A tenant entry in the platform repository, a database cluster with a connection pooler and backups, a signed image whose digest is committed, a contract fuzzed in CI, dashboards, and sign-in through the platform's identity provider. Of these, **Warn uses the first five; sign-in has not been shown on the new platform.**

| Claim | Status | Date | Note |
|---|---|---|---|
| Warn backend up and Ready on the home site: 2 replicas, a 3-instance database | proven | 2026-11-10/11 | Plain HTTP on the home network; no public address; no users beyond the owner |
| One real backup of Warn's database reached the object store and was restored into a scratch cluster | proven | 2026-11-10 | An on-demand backup, so no size or time claim |
| A fuzz run against Warn's contract found a bug (a repeated scalar query parameter), fixed | proven | 2026-11-11 | An example of the platform catching a fault |
| Signed image path, contract fuzz in CI, dashboards | built | 2026-11-11 | |
| A tenant identity with no cluster rights had 10 planted cluster-scope actions refused | built | 2026-11-09 | On a local test cluster; not seen green in CI |
| Warn's client moved into the platform repository | built | 2026-11-11 | On an unmerged branch; no device has run it against the new cluster |
| A sign-in by an app through the new identity provider | open | 2026-11-11 | The provider runs in development mode with in-memory storage |
| Loc8 on the new platform | planned | 2026-11-11 | Waits for a decision on how streams reach only current members (the old one kept streaming to people who had lost access) and a two-pod test |
| Talk on the new platform | planned | 2026-11-11 | Last in the order; mail, push and a store release are open |
| Any of them meeting the full app standard | open | 2026-11-12 | No score yet |

The other workloads on V1.0 (a fleet dashboard, the mower's cloud engine, a CI dashboard and a status page) are not applications of the new platform: they are gone or never ran there.

**What the platform still lacks for them.** A public address, a durable identity provider, a release path to testers for the clients, the stream-delivery decision for Loc8, mail and push for Talk, and a load test.

---

## The killer app

**It does not exist.** There is no name, no user, no market, no revenue and no date, and none is implied here. The rule is to wait for the app and not to hunt it; until it appears everything on this site is learning. The platform's job is to be ready, and the test applied to every decision is whether it would haunt us on killer-app day.

When one is chosen it gets its own repository and arrives by the same written contract as every other app: one tenant entry in the platform repository and no route only it may use. If it fits none of the three shapes above, the standard changes by pull request.

**What the platform holds ready.**

| Item | Status | Date | Honest count |
|---|---|---|---|
| App standard: about 90 rows in groups from delivery to launch | built | 2026-11-11 | Written, not enforced. Part of the register's 109 rules, of which 3 are built, 19 partly, 87 not. No app has a score |
| App template and a scaffolding script | built | 2026-11-11 | Only partly: passes its manifest check; one-file tenant entry, secrets layout, attack cases and drift report are not built |
| The Land test: a never-seen open-source app from an empty repository to public, signed, traced and backed up | built | 2026-11-09 | A rehearsal: one green run on a local test cluster with Warn as the stand-in, 635 seconds, after one red run; later commits have no green run. Not the real test: no random draw, no public address. The target times are proposals |
| Launch gates: 16 items such as terms, privacy, breach runbook, legal entity and store accounts | built | 2026-11-11 | A register only: 0 of 16 done; only the owner can do them. No stranger may sign up until they pass |
| Client release path to testers | planned | 2026-11-11 | Not built; no client has one |
| A register of "cheap now, expensive later" items | built | 2026-11-11 | About 30 items, mostly never run |
| Restore from backup | proven | 2026-11-10 | Once: one drill, on-demand, scratch cluster |
| Rebuild the whole platform from git, timed | planned | 2026-11-12 | Never run |
| Load test and a way to raise the ceiling per app | planned | 2026-11-12 | Not built |

**Day one, all planned.** The owner's decision records say the direction changes on that day and not before: production becomes the main line, learning moves to a branch, the launch gates become the first work, and uptime starts to count. That decision is a proposal until the day. "Production ready" here means the platform can carry a paying app and move to a site that can promise an SLA, which is not the same as taking customers on the home machines.

**What the platform still lacks for it.** Most of the above. The honest summary is [the status page](status.html) and [the diff list against V1.0](versions.html), not this paragraph.

---

## Hoped and expected

These are aims, kept apart from the tables above on purpose. None is a result, and none has a record. Each says what it rests on. When one comes true it moves into the table above with its dated record, and when it does not, the entry stays here with the reason.

| Application | Hoped or expected | What it rests on |
|---|---|---|
| Embedded Linux (Pi) | **Expected:** the signing, bill-of-materials and A/B update chain that ran on V1.0 runs again on the new platform, and a field update is applied with rollback. | The planned rows in the table above; the same tools are already picked for the cluster's own images. |
| Embedded Linux (i.MX 8M Nano) | **Hoped:** it reaches the same image pipeline as the Pi without a second set of rules. | The Pi pipeline being reusable; only survey scripts exist today. |
| The mower | **Hoped:** an RTK fix on the real receiver, then one real mowing pass driven by a pattern from git. | The bench rig and the receiver reading above; the fix depends on antenna placement and a correction source, not on the platform. |
| The rover | **Hoped:** telemetry, alerts and the tracker make the rig easier to run and debug than running it alone. | A planned test, not a result; the rig works without a cluster. |
| 3D printing | **Expected:** parts built from source in CI, with each printed result recorded against its change. | The parts-as-code flow already works by hand; CI for it is not built. |
| The reference apps | **Expected:** Loc8, then Talk, land on the platform by the written contract without touching platform code; **hoped:** that this takes days, not weeks. | Warn did it once, by its author. The Land test is a one-run rehearsal. |
| The killer app | **Hoped:** that when it appears, the platform is the part nobody has to think about, so the first work is the app and its launch gates. **Expected:** a first week of surprises anyway. | The app standard, the template and the gates exist as written; none has met a real app. |

## What this page does not prove

- **That any hope above is likely.** They are aims with the reasons given, not forecasts.
- **That the platform is reliable.** It is days old. The aim is reliability; there is no uptime to quote.
- **That a second application would land.** Warn is one app, moved by its author with full knowledge of the platform. The Land test exists to answer that, and has been rehearsed once.
- **That any of the hardware applications needs the platform.** The rig runs without a cluster. Whether telemetry, alerts and a tracker make it better is a planned test, not a result.
- **Anything about users.** There are none.

Dates on this page are the dates of the records behind them; a row that says "proven" says what was shown, on what, and when. Related pages: [the apps](apps.html), [the embedded side](yocto.html), [printing](printing.html), [status](status.html), [V1.0 and V2.0](versions.html).
