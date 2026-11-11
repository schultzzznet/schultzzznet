---
title: How we work
reread: 2026-11-11
body_read: 2026-11-11
summary:
  - "**What it is:** how changes are made, checked, approved and recovered on the new platform. Each way of working has a date and one of four words: proven, built, planned, open. The platform was brought up on 2026-11-10/11, so nothing here claims uptime."
  - "**Seen working (dated):** a hand patch on the live site was reverted by Flux (2026-11-10); a restore from the backup store alone worked once (2026-11-10); a throwaway ruleset blocked a pull request on a red gate (2026-11-10)."
  - "**Not shown:** main's own branch protection was never tested; the delivery artifact is unsigned; monitoring is running since 2026-11-11 (18 of 18 scrape targets up, 12 alert rules, no dashboards); no alert has reached a person."
  - "**The failures that taught me** are below, with dates."
---

# How we work

{% include in-short.html %}

This page describes how changes are made, checked, approved and recovered on the new platform, and what each way of working has and has not been shown to do. Every claim carries a date, and each section ends with what it does not prove. The platform was rebuilt on 2026-11-10 and brought up on 2026-11-10/11. It is a day old, and nothing here claims uptime.

**Why there are no links to the records.** The repository behind this page is private, by choice. A claim here comes from a run record with fixed fields: date, what was done, result, what it proves, what it does not prove. I can show one on request.

**Key to the labels.** "Proof B" is a test of whether the aggregate gate can be a required check (section 5). A "step" is one item in the order of work, and a "decision record" is a written decision with a number. Machines are described by role, never by name, and software without versions.

V1.0 stories are collected in their own list at the end of section 9 and in the last section.

## How to read this page

Every way of working below carries one of four words.

| Status | Meaning |
| --- | --- |
| **proven** | Seen working on a live run, with a date. It means once, on that date, not "has always worked". |
| **built** | In place in the repository or on a host. Nobody has yet seen it work under the failure it exists for. |
| **planned** | Decided and written down, not built. |
| **open** | A known gap or an unanswered question. Listed so it is not rediscovered later. |

A rule I apply to myself: a test counts only once it has been seen to fail on purpose. A check
that has only ever been green is not yet evidence that it can go red.

## 1. The rule: git is the only way in

The charter was merged on 2026-11-05 (decision record 1, accepted). It has ten rules for how
we work, and the first is that the repository is the only way a change reaches the cluster.
The charter also fixes how each layer of the plan may change:

| Layer | How it may change |
| --- | --- |
| Purpose and aims | By decision record only |
| Objectives | By pull request |
| Key results | Reset every quarter |
| How we work | By a short pull request |

### The road of a change

```
pull request -> checks -> squash merge -> signed bundle -> Flux pull -> admission
   (git)        (CI)       (main)         (not yet signed)  (cluster)   (policies)
```

| Step | State on 2026-11-11 | Status |
| --- | --- | --- |
| A pull request carries the objectives line | A workflow that runs from the base commit checks it, so the pull request cannot edit the check it is judged by | built (seen to fail a pull request without the line on a planted case) |
| Required checks pass | Two checks are required on main: the main check and the objectives line. Strict up-to-date rule | built. A throwaway ruleset was tested on 2026-11-10; main's own protection was never tested (section 5) |
| Squash merge | Linear history | built; the history is linear so far, not tested by a refused merge |
| A publish step builds an artifact from main | Runs on merge | proven 2026-11-10/11 |
| Flux polls the source every 2 minutes; the Kustomizations reconcile every 5 minutes | No inbound path, and the pipeline holds no cluster credential | proven 2026-11-10/11 |
| A chain of Kustomizations | Operators first; base and secrets after; policies after base; ingress after policies and the load balancer; tenants last | On a reading at 2026-11-11 (after the monitoring tenant was merged) the operators, base, policies, load balancer, ingress and four tenants were Ready; the monitoring tenants and their secrets were not Ready, and one was still reconciling; a later reading at 07:00 UTC the same day found all 19 Ready. The live figure is on the [status page](status.html), because a count here would age |
| The artifact is signed | It is not. It is read through a moving tag | open (signing or pinning is the next step) |
| Everything is reconciled | Software installed from Helm charts (the operators and ingress) is put in by the bootstrap script, not reconciled by Flux | open |
| An independent daily drift guard | Not built | planned |

The evidence that git is the only way: on 2026-11-10, on the live site, fields were changed by
hand and Flux put it back within minutes, and reported it. That was not a planned drift test: it was the quota patches I applied by hand during the bring-up fault (section 9), and it covered a few fields on one object. It is thin evidence.

**What this does not prove.** It does not prove that nothing can bypass git. Anyone holding the
cluster credential can still change things, and the independent guard that would notice a change
that Flux does not manage does not exist yet. It does not prove the artifact is the one that main
produced, because the artifact is not signed and the tag moves.

## 2. Secrets

Status and dates, 2026-11-11.

| Way of working | Status |
| --- | --- |
| Secrets live in git encrypted with SOPS and age | proven 2026-11-10/11 (the cluster decrypts and applies them) |
| One decryption unit per namespace, not one for all | proven 2026-11-10 (the reference app reached Ready after the split); the reason is the first-bring-up deadlock in the failures section |
| Values enter by files. They are never typed into a command, never passed as an argument | built (a rule and a habit; no check yet fails a typed value) |
| A token script checks the token's scope and expiry, tests a real image pull, and is written to clear the clipboard | built; used on 2026-11-10, the clipboard clearing was not checked |
| A recovery key exists | built. Restoring from it has not been tested (open) |
| Encryption at rest on the cluster | not claimed |

A recovery key exists, and restoring from it has not been tested. A second recipient and an off-machine copy are a planned step, and the person who has to do it is me. A rule that says "decrypt with the workstation off" has not been passed.

**What this does not prove.** That no secret value has ever leaked into a shell history or a
log. Checking for that is not built.

## 3. Admission

Two policies, both set to Deny, live on 2026-11-10/11.

| Policy | What it checks | Status |
| --- | --- | --- |
| Own images | A signature made by the CI key | built on the real cluster (the signature half was seen working on a throwaway local cluster) |
| Vendor images | A closed list, pinned by digest | proven 2026-11-10 for one refusal (below) |

A vendor image is trusted because the digest was pinned on a pull request that someone read, not
because the vendor signed it. That is a weaker kind of trust and it is an open gap against the
rule that every image is verified.

The first live refusal of an off-list vendor image happened on 2026-11-10 and is recorded in
the history of that day, not as a gate record with fixed fields. The other refusals exist as
procedures that have not yet been run on the live cluster and recorded.

**What this does not prove.** That every path to run a container is covered. Two policies are
two policies.

## 4. Decision records and run records

The plan is written down so that it can be checked rather than remembered.

| Thing | Count on 2026-11-11 | What keeps it checkable |
| --- | --- | --- |
| Objectives | 11 | Each is a page |
| Rules under the objectives | 109 | Every rule names the check that would show it is met |
| Components in the inventory | 95 | 15 seen working on the new platform |
| Steps in the order of work | 12 | 2 done, 2 done on a local cluster only, 5 partly, 2 not started, 1 gated |
| Decision records | 8 | 3 accepted, 5 proposed, each with a reopen trigger |
| Run records | 35 | 26 pass, 9 fail; fixed fields; never edited to change the result |
| Pre-commit hooks | 62 | Run locally and again in CI |

The rules, by what has been built: **3 built, 19 partly built, 87 not built.** That figure is shown on the front of the status file. The status page is generated from the objectives, the steps and the records, regenerated and
compared by a check, so it cannot drift from its sources by hand.

A run record is written when something was run and the result is known. A failure is recorded
whenever it taught something. The fixed fields are what was run, on what, the result, what it
does not prove, and the date. A record is never edited afterwards to turn a fail into a pass: a
new record is added instead.

Decision records can lag the truth in either direction. One proposed record already routes real
jobs: the home CI path (section 6) runs under a record that has not been accepted. The reverse,
an accepted decision that nobody built, is also here (section 9, last story).

**What this does not prove.** That the 87 unbuilt rules will be built. A rule on a page is a
statement of intent with a named check, nothing more.

## 5. Approvals

| Way of working | Status, 2026-11-11 |
| --- | --- |
| Main is protected: pull request, required checks, strict up-to-date, linear history, no force-push, binds admins | built. A ruleset on a throwaway pattern was tested on 2026-11-10; main's own protection was never tested, so it is unproven |
| Required checks on main | Two: the main check and the objectives line |
| I approve important changes myself | built, as a practice. No approval is on record: the decision record sets required approvals at 0 and all of the roughly 100 commits on main are under one human login |
| A reviewer agent approves the rest | planned. It is a proposal (decision record 4, Proposed). The reviewer identity does not exist |
| An agent merges only when asked, and never with an admin override | built, as a practice; not enforced |
| An agent review counts as independent judgement | no. A second identity of the same model family is a second identity, not a second mind |
| The aggregate gate is required | deliberately not yet (proof B below); the fix is open |
| A merge queue | none |
| Renovate | built. Configured with cooldowns, auto-merge of patches on green, and a needs-owner label for risky areas; not yet seen acting |
| No pinning | policy: go up a version, and a pin needs a stated reason and an expiry |

### Proof B: the cancelled required check

On 2026-11-10 I tested, on a throwaway ruleset that required the aggregate gate (not on main), what a pull request reads after the fallback for a home job that never starts. The home job did not start; the watchdog cancelled the run and dispatched a hosted one. The cancelled run left a red gate result on the commit. The dispatched run finished green 26 minutes later. The pull request still read red and stayed blocked, 28 minutes after the green result existed: the red one wins. Only a full re-run of the original run cleared it.

So the aggregate gate is deliberately not required yet, and what is required on main is the two checks named above. The cost of that trade is that a failure in an unnamed check does not block a merge. The fix is open: a changed watchdog, and then this proof runs again.

The longer account of how reviews have gone, and why an agent's review is not independent, is in
[who reviews, honestly](ai-dev.html#who-reviews-honestly) and
[what outside reviews found](lessons.html#13-what-outside-reviews-found).

**What this does not prove.** The same on main's own protection (a different target), the order-reversed case (red newer than green), or that a changed watchdog fixes it.

## 6. Home CI

### Why

By 2026-11-09, day nine of the month, 2,685 of the 3,000 included hosted minutes were used (89.5 percent, my own tally; the budget tool read 92 percent, a different figure). A $20 budget covers the rest. A hosted gate costs real money per run, so I built a path that spends my own electricity instead.

### What it is

| Part | Description | Status |
| --- | --- | --- |
| A fresh VM per job | Thrown away after the job | proven 2026-11-10 |
| An allow-list proxy | The VM has no secret and no route to the home network | proven 2026-11-09 by breaking it on purpose, below |
| Jobs that hold a key | Stay on hosted runners | built |
| A route job | Decides hosted or home for each pull request | proven 2026-11-10 |
| A liveness probe | Raises an alert when the controller stops | proven 2026-11-10 for a stopped controller (fired, then cleared). The unreachable-host path was only a self-test, the copy on the small Mac is hand-copied and not from git, and delivery to a person was not seen |
| Two home CI hosts | One job VM at a time on each | built. Both took jobs in parallel for the first time on 2026-11-11; those gates had started when this was written, not passed |

### What was measured, 2026-11-09 and 2026-11-10

- Three proof attempts on throwaway pull requests (2026-11-09, 2026-11-10, 2026-11-10): two were red
  because of two different flakes in the gate itself (section 9) and the third went green in 32 min
  20 s. The pull requests were not the cause.
- A real pull request on 2026-11-10 took 33 min 12 s through the home path and was green first
  time. The same gate on hosted runners takes 24 to 27 minutes, so home is 1.2 to 1.35 times
  slower. The case for home CI is saved minutes, not speed.
- Isolation was broken on purpose on 2026-11-09. The VM only went red, meaning it could reach where
  it should not, when both firewall layers were opened in both directions. Either layer alone held.
  One layer alone would have been enough to fail silently, which is why both exist.
- A liveness alert, run by a probe on the small always-on Mac (not the route job), was active about 3 minutes after the controller was stopped on purpose on 2026-11-10. That a message reached a person was not seen.

### Open

Both hosts took jobs for the first time on 2026-11-11, in parallel. The gates had started when I wrote this; I do not yet claim they passed, and I do not claim failover between the hosts. The per-host heartbeat code was merged on 2026-11-10 but not applied to both hosts.

**What this does not prove.** One pull request through the path is one pull request. It does not
show how the path behaves under several at once, or after a host reboot.

## 7. The host layer

| Way of working | Status, 2026-11-11 |
| --- | --- |
| Ansible playbooks build a site from blank machines | proven 2026-11-10, in order, with a person watching. Six machines were built by playbook; it was not one command from blank |
| An inverse teardown play | proven 2026-11-10 (it is how V1.0 was removed, with leftovers; see section 9) |
| A health play | built |
| A firewall profile, key-only SSH | built, on the six machines. The bring-up found and fixed a firewall rule for link-local SSH, so the first profile was faulty |
| An installer stick built from git | built, for one stick |
| A rehearsal on local VMs | proven 2026-11-10, below |
| The host pull timer (decision record 7) | accepted and not built. Planned; it needs a deploy key and a per-host identity, which only I can create |

### The rehearsal

On 2026-11-10 the same playbook took three local VMs (two servers and one agent) to Ready in 4 min
11 s, and a second run changed nothing (changed=0). Four defects were found on the way, which
is what a rehearsal is for.

It does not show: a second Linux distribution (only one was used), a quorum test, a failover, or
anything on x86. The VMs were aarch64 and the real machines are not.

**What this does not prove.** That the real machines would rebuild from blank with one command.
The cutover rule asks for that on two distributions and it has not been met.

## 8. Restore drills

A backup counts only after a restore from the backup store alone. Having the files is not the
test; being able to get the data back with nothing else is.

| Drill | Result | What it showed |
| --- | --- | --- |
| 2026-11-10 | pass, about 60 s | A database backup from the live site was restored into a scratch cluster using the store alone. A marker row and 6 tables came back. The data was a few MB, so no claim about time or size at scale |
| Nightly backup, 02:00 on 2026-11-11 | completed | It has not been restored |

### What the drill does not prove

- It does not prove point-in-time recovery. The backup was taken on demand.
- It does not prove a restore from a nightly backup. No nightly backup has been restored.
- It does not prove survival of losing the store. The store is one small Mac with one copy, and
  there is no off-site copy.
- It covers one database of the apps on the cluster, not all of them. "A random database is
  restored" is the done-when for the step and it is not yet met.

## 9. The failures that taught us

Short stories, each with a date and what changed because of it.

**The secrets deadlock (2026-11-10).** On first bring-up the application namespace waited for the
login service, and the login service waited for its admin secret. Both were in the same failing
apply, so nothing could finish. The fix was one decryption unit per namespace, so a secret
arrives before the thing that needs it. Lesson: ordering is part of the design, and a single apply
hides it.

**The quota that refused the database (2026-11-10).** The namespace quota refused the database. I patched the quotas by hand, and Flux reverted my patches, because git did not hold them. That revert was accidental, not a planned drift test. The only fix that lasted was the one committed to git. That is the rule from section 1, learned from the wrong side.

**The backup store name pods cannot resolve (2026-11-10).** The backup store was named in a way pods
cannot resolve. The address had to be changed in git. Lesson: test the name from where the thing runs.

**The slow SSH fix that fixed nothing (2026-11-10).** A slow SSH login was "fixed" with a settings change that
changed nothing: the delay was the same afterwards. I record it because it is a clean example of a
fix applied before the cause was measured. The cause was found the same night: the nodes announced
both address families over local name discovery, and announcing IPv4 only brought logins to under a second.

**Default-deny, except for the first 1 to 3 seconds (2026-11-10, result: fail).** A probe found that default-deny
did not hold for the first 1 to 3 seconds. The run record says fail. The gap is open. A policy that is only
true after a delay is not the policy the rule asks for.

**Proof B: the red gate that wins (2026-11-10).** In section 5. The cancelled run's red result blocks the pull request after the green re-run, so the aggregate gate is not required yet.

**The gate that failed for its own reasons (2026-11-09 and 2026-11-10).** On three proof attempts on
throwaway pull requests the gate was red twice and went green on the third. The two reds were two
different flakes in the gate itself (a slow first signed-in call, and a dropped connection in the
fuzz test), not a fault in the change. Lesson: a gate that cries wolf is as costly as one that
sleeps, and each flake needs its own fix.

**The rehearsal that found defects (2026-11-10).** Four defects were found in the playbooks when
they ran on local VMs. All four would have cost time on the real machines.

**The wipe that left leftovers (2026-11-10).** The stock uninstall left a virtual address on one
node and a node-password file on all six. I removed them by hand. The Mac CI runners were retired
the same day, after a scan of 76 repositories found no registered runner. Afterwards every command
was pinned to one kubeconfig, because a default context once reached a dead local cluster. Lesson:
a teardown is only proven when a rebuild on top of it works.

**Hosted minutes ran down in nine days (2026-11-09).** Section 6: 2,685 of 3,000 used by day nine. The
cost was money and a day of waiting, and it is why the home path exists.

**An accepted decision is not a built one (2026-11-11).** The host pull timer is an accepted
decision, and it does not exist. The status of a decision record says what was decided, not what
runs. That is why this page uses its own status words, and why the generated status lists rules
as built or not, apart from the decision records.

### V1.0 (retired 2026-11-10)

- **Red guards.** The daily guards were red every day from 2026-11-02 to 2026-11-09 and nobody was looking. That is why I insist on an alert that reaches a person, and on a guard that is independent of the thing it guards.
- **A wipe is not a migration.** Of V1.0's 257 alerts, 74 mechanisms and 16 power-off proofs, 0 have been carried over, and the cutover gate is not passed. The new platform starts with fewer safety nets, and this page lists the ones that are missing.

Related pages: [the delivery chain](platform.html#how-a-change-reaches-the-cluster),
[what I'd do differently](lessons.html), [who reviews, honestly](ai-dev.html#who-reviews-honestly).
