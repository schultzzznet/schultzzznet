---
title: How we work
reread: 2026-11-20
body_read: 2026-11-20
summary:
  - "**What it is:** how changes are made, checked, approved, broken on purpose and recovered on the new platform. Each way of working has a date and one of four words: proven, built, planned, open. The cluster was brought up on 2026-11-10/11, so nothing here claims uptime; most of these ways of working were learned on V1.0 ([History](history.html))."
  - "**Seen working (dated):** a hand patch reverted by Flux (2026-11-10); restores from the backup store alone, of the reference app's database (2026-11-10) and the login service's (2026-11-15); 17 live software failover drills on 2026-11-16/17, 15 pass and 2 fail, neither losing an acknowledged write."
  - "**Failure scenarios** ([section 10](#10-failure-scenarios-simulate-then-pull-the-plug), 2026-11-20): five rungs, from one-node CI gates to the owner pulling the plug. The second power-off drill (2026-11-19) found a timing flaw in cluster DNS that a review on paper missed; a simulation reproduced it within minutes. So no live drill runs before its simulation has passed (**planned**)."
  - "**Not shown:** no single point is proven fixed (only a power-off drill can do that: 2 of 7 run, 1 failed); main's own branch protection was never tested; alerts reach a chat channel, but nothing pages a person, waits for an acknowledgement or escalates."
  - "**Two axes** ([below](#two-axes-what-you-write-and-who-applies-it)): what you write (declarative or scripted) and who applies it (pull or push) are independent. V2.0 is declarative and pull in the cluster, still scripted and push at the edges, so not fully GitOps yet."
  - "**The failures that taught me** are below, with dates, including a change-over step merged before its referee was read (2026-11-20)."
---

# How we work

{% include in-short.html %}
{% assign hw_ob = site.data.stats.observability %}
{% assign hw_ev = site.data.stats.evidence %}

This page describes how changes are made, checked, approved and recovered on the new platform, and what each way of working has and has not been shown to do. Every claim carries a date, and each section ends with what it does not prove. The cluster was rebuilt on 2026-11-10 and brought up on 2026-11-10/11. It was a day old when this page was first written (2026-11-11) and ten days old on 2026-11-20; nothing here claims uptime. The ways of working are older: most were learned on V1.0, from 2025-12-21 to 2026-11-10 ([History](history.html)).

**Why there are no links to the records.** The repository behind this page is private, by choice. A claim here comes from a run record with fixed fields: date, what was done, result, what it proves, what it does not prove. I can show one on request.

**Key to the labels.** "Proof B" is a test of whether the aggregate gate can be a required check (section 5). A "step" is one item in the order of work, and a "decision record" is a written decision with a number. Machines are described by role, never by name, and software without versions.

V1.0 stories are collected in their own list at the end of section 9. How failures are rehearsed and then caused on purpose, from a one-node CI gate to a machine held off by its power button, is section 10 (added 2026-11-20).

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

## Two axes: what you write, and who applies it

This is the organising reason for building V2.0 on top of what V1.0 taught me. Two questions about any change, and they are independent of each other.

1. **What do you write?** *Declarative*: you describe the end state in files, and the tool works out the steps and can compare what you asked for with what is there. *Scripted* (imperative): you list the steps, and the tool runs them in order.
2. **Who applies it?** *Pull*: something inside the cluster fetches the files and applies them by itself, again and again. *Push*: the operator's machine, or a CI job, pushes the change at the cluster when told to.

That gives four combinations, and one system can sit in different cells for different layers. A tool can be declarative and still pushed (a playbook run by hand). A script can be pulled (a timer that runs the same script every hour). Choosing one axis does not choose the other.

| | **Push** (the operator or CI applies it) | **Pull** (the cluster applies it) |
| --- | --- | --- |
| **Declarative** (describe the end state) | Host playbooks in V2.0, idempotent in style, run from the operator's machine. Also V1.0's plain manifests applied with `kubectl apply` | V2.0 cluster layer: manifests in git, a reconciler that fetches, applies, prunes and reverts a hand edit |
| **Scripted** (list the steps) | V1.0 for most of what a person did: a Makefile, playbooks and one-off scripts, run by hand. V2.0 first install, the ops agent and the runner alert on the always-on Mac | Nothing in either version today |

### Where V1.0 sat (measured 2026-10-27)

I classified every hand-run step of V1.0 before choosing anything: about 172 make targets and 59 playbooks (the published split sums to 173). 104 are checks, drills and status views, which are not state at all. 24 are host-level automation. 20 are imperative orchestration. 6 are wrappers. Only 19 are declarative applies that a controller could own. So V1.0 sat mostly in **scripted and push**, with a detector added later (a daily read-only diff with an alert, done 2026-10-24). The 19 declarative applies are the way the about 80 plain manifests were put on the cluster (both are declarative and push). Of those 80, 74 matched the live cluster that day and 6 did not; the first daily diff found 6 differences.

The push model also produced its own incidents. An installer dropped a flag and brought a second default storage class back. On 2026-10-21 a deploy pinned a new image in git, and a second deploy two minutes later rolled the cluster **back** to the old one, where it stayed for two days. Nothing was wrong with either command. The cause was that the person running the second one held the only copy of "what should be there", in the shape of a checkout.

### Why V2.0 on top of V1.0

Because the measurement said which cell was the problem, and which was not. The 19 declarative steps could move to declarative and pull. Of the other 154, the 104 checks and the 20 orchestration steps are procedures and stay scripts. The 24 host-level steps are the part V2.0 keeps as playbooks and plans to pull (decision record 7, **planned**). The 6 wrappers go with whatever they wrap. V1.0 improved in four stages, and V2.0 picks up where they stopped:

| Stage | V1.0 | V2.0 |
| --- | --- | --- |
| Detect drift | done 2026-10-24 (a daily diff with an alert) | replaced by revert; the alert is not rebuilt (below) |
| Secrets in git | done 2026-10-25 | declarative and pull: decrypted by the cluster, **proven** 2026-11-10 |
| Roll out from git | not built on V1.0 | **proven** 2026-11-10 |
| Imperative steps as idempotent jobs | not started | **open**, case by case |

### Where V2.0 sits today (read 2026-11-11)

| Piece | What I write | Who applies it | Status |
| --- | --- | --- | --- |
| Cluster layer: manifests, admission policy, tenant pack | Declarative: Kustomize manifests in git, published as an OCI bundle (not signed yet) | **Pull**: the reconciler fetches every few minutes, prunes, and puts a hand edit back | pull **proven** 2026-11-10 and 11; all Kustomizations Ready on 2026-11-11 (19 in one reading, 18 at 07:00 UTC on other pages; the live count is on the status page). That a hand edit is put back was seen once, on one quota, by accident, and is not a deliberate test of any other object. The policy and tenant pack rest on the default-deny probe of 2026-11-10, which is separate from the revert claim |
| Secrets | Declarative: encrypted files in git | **Pull**: the cluster decrypts | **proven** 2026-11-10 |
| Host layer: operating system, install, firewall | Playbooks: idempotent, declarative in style | **Push**, from the operator's machine. A pull timer is decided (decision record 7) and not built | playbooks **built**, the timer **planned** |
| First install (bootstrap script) | Scripted | Push, once, by hand | **built**; ran once, 2026-11-10 |
| Ops agent and runner alert on the always-on Mac | Playbook and script | Push, deployed by hand | **built**; the alert and the agent were deployed 2026-11-11 (the agent still reads the cluster's workloads by SSH, to be replaced) |
| CI gate scripts | Scripted: a test is a procedure | Run by CI | by nature, and that is fine |

Some work cannot be declarative at all: a database major upgrade, realm setup in the login service. The plan is to turn each into an idempotent job, case by case. None is done.

### What stays scripted and pushed, and why

The first install has to exist before anything can pull, so it is pushed once by hand. The hosts are pushed because the thing that would pull for them is a timer on each host, which needs a deploy key and an identity per host that only I can create; it is **planned**, and if built, it will let a bad merge reach every host within one interval. The always-on Mac sits outside the cluster, so the reconciler cannot reach it.

### What V1.0 got right, and V2.0 must not lose

- **It measured before choosing.** The split above is why V2.0 changed one layer and left the rest alone.
- **It added a detector first.** Seeing the 6 differences made the case for the rest.
- **It had a daily drift guard with an alert.** V2.0 has not rebuilt it. The reconciler reverts drift instead, which is stronger for anything git names, and blind to anything git does not mention. Monitoring has run since 2026-11-11, with 12 alert rules that day ({{ hw_ob.alert_rules }} in the generated figures of {{ site.data.stats.generated_at | date: "%Y-%m-%d" }}). One of them, for a Kustomization that has not been Ready for 15 minutes, is written and live (**built**); it was seen pending, not firing, in the power-off drills of 2026-11-19. Alerts reach a chat channel: the node-loss alerts arrived there about 6.5 minutes after a machine went dark on 2026-11-19, and the owner's phone shows them as chat messages. Nothing rings through silent mode, waits for an acknowledgement or escalates. Paging a person, a rule for the reconciler losing its source, and an independent drift check are **open**. V1.0's guard was also red for eight days (2026-11-02 to 2026-11-09) and unread, so an alert nobody reads is no better.

### The honest summary

V2.0 is mostly **declarative and pull** in the cluster, and still **scripted and push** at the edges: the first install, the hosts and the always-on Mac. It is **not fully GitOps yet**. The host pull timer (decision record 7) is the planned fix for the hosts; for the first install and the Mac I have no plan to change it. V1.0 is retired, torn down on 2026-11-10, and described here only as it was on the dates given.

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
| 2026-11-15 | pass: backup 12 s, restore 81 s | The login service's database, from the same store into a scratch cluster beside the live one. The two answered one comparison query identically, row for row; 13 MB. The same day showed that this database had had no completed backup until then: two nightly runs had failed on a missing secret, and were fixed |

### What the drill does not prove

- It does not prove point-in-time recovery. The backup was taken on demand.
- It does not prove a restore from a nightly backup. No nightly backup has been restored.
- It does not prove survival of losing the store. The store is one small Mac with one copy, and
  there is no off-site copy.
- It covers two databases (the reference app's and the login service's), each once, from an
  on-demand backup. "A random database is restored" is the done-when for the step, and the
  second restore of each is still owed (2026-11-20).

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

**Two replicas that failed on timing (2026-11-19, result: fail).** Cluster DNS ran as two replicas on two machines, which reads as highly available. When one machine was switched off at its power button, lookups on the other machines stalled for 51.1 s and two of the probe's writes failed. A pod kill three days earlier had passed. Section 10 has the story and the rule it led to.

**A step merged before its referee was read (2026-11-20).** In the cluster DNS change-over, the next step was merged in the same command that read the previous step's referee, so a small unexplained failure count was seen only after the merge. Section 10 has the details. Lesson: read the referee, then merge.

### V1.0 (retired 2026-11-10)

- **Red guards.** The daily guards were red every day from 2026-11-02 to 2026-11-09 and nobody was looking. That is why I insist on an alert that reaches a person, and on a guard that is independent of the thing it guards.
- **A wipe is not a migration.** Of V1.0's 257 alerts, 74 mechanisms and 16 power-off proofs, 0 have been carried over, and the cutover gate is not passed. The new platform starts with fewer safety nets, and this page lists the ones that are missing.

## 10. Failure scenarios: simulate, then pull the plug

*Added 2026-11-20. The figures are from the run records up to 2026-11-19 and from the live site on 2026-11-20.*

A piece that claims a second instance is only as good as the minute after it loses the first. So failures are caused on purpose, on a ladder of five rungs. Each rung shows something the one below cannot, and none of them replaces the one above.

| Rung | What runs it | What it can show | What it cannot show | Status, 2026-11-20 |
| --- | --- | --- | --- | --- |
| 1. Gates on every pull request | A throwaway cluster of one node in CI | Configuration, admission policies, signatures, a backup and restore round trip, the reference app's contract | Losing a node: there is only one | **built**; runs on every pull request |
| 2. Simulations | Throwaway clusters of several nodes, run in containers on a home machine; a node is "lost" by cutting its network or stopping its container | Node loss, timing, change-overs, rollouts after an outage | Real hardware: network cards, disks, power, the router and switch, the floating address on a real network, the oldest machines' speed | **built** for cluster DNS and monitoring: 4 simulations from 2026-11-11 to 2026-11-19, all pass, plus a log agent outage test. Run by hand. The nightly suite is **planned** (below) |
| 3. Live software drills | On the live site: kill a process, kill a database primary, drain a node, all under the probes below | Each piece's failover time, and whether any acknowledged write was lost | A machine that stops without warning | **proven** per piece: 17 drills on 2026-11-16/17, 15 pass, 2 fail (one fixed and re-run green, one open). Neither failure lost an acknowledged write. They do not count as proof for a single point |
| 4. Live power-off drills | The owner at the machines, one machine held off by its power button, by a written run sheet, least damage first | The only proof that moves a single point to fixed | A mains cut of the whole site; two machines off at once | 2 of 7 run on 2026-11-19: 1 pass, 1 fail. The series starts again from drill 1 |
| 5. Restore drills | A scratch database restored beside the live one, from the backup store alone | The backup can be read back, and how long it takes | The off-site copy, point-in-time recovery, the loss of the whole site | 3 run, all pass: one on V1.0 before it was retired (2026-11-08), and on this platform the reference app's database (2026-11-10) and the login service's (2026-11-15) |

### The referees, and when to stop

A drill is judged by referees that run before, during and after it, not by reading status afterwards:

- **Probes from a machine outside the cluster**, each timed: the cluster API through its floating address, the reference app and the login service through the ingress, and writes through the connection pooler with a fresh name lookup each time, so that a gap in writes and the number of writes kept are both counted.
- **A DNS probe on every node**, counting failed lookups and lookups slower than 1 s.
- **The alerts**, compared with a list of the alerts each drill is expected to raise, written before it starts.

**The stop rule.** A change-over step stops on any failed lookup or any new alert. A drill is aborted, the machine powered back on and the session ended, when a service is not back at twice its target, when an alert fires that was not expected, or when a second machine shows a problem. Two machines are never off at once, because each database instance lives on its own machine's disk.

### The rule, decided 2026-11-20 (planned)

Every failure scenario is first rehearsed on a simulated cluster shaped like home (three servers and three agents, the same manifests as far as a container cluster can carry them), nightly on a home CI host, and never on a pull request, because it is too slow for one. The scope, in order:

1. every piece that claims a second instance (the reference app's pods, its database and the login service's, sign-in, the database operator, the backup plugin, cluster DNS, the ingress, admission, the floating address);
2. the rest of the production path: the database's writes and failover, its object store, the connection pooler, the way in up to the node;
3. the major supporting systems: delivery, monitoring and alerting, the backup path.

**No live drill runs before its simulation has passed**, or the drill's record says why the scenario could not be simulated. Status on 2026-11-20: the rule is written down; of the scenarios in its scope, only the cluster DNS node loss (and its change-over) has been simulated, besides the earlier one-off trials of the monitoring stack and of a drain; the home-shaped cluster and the nightly run do not exist yet. The live drills stay, and become confirmations instead of discoveries.

### Why: highly available on paper, not in a power cut

On 2026-11-19 the second power-off drill held off a worker that ran one of the two cluster DNS replicas. Two replicas, spread over two machines, looked highly available on paper. They were not. A machine that stops without warning is marked NotReady only after about a minute (60 s in this drill), and until then its dead DNS pod stays in the service. Each lookup sent to it waits 5 s, and its retries go to the same dead pod. Lookups on the other machines stalled for 51.1 s, two of the probe's writes failed because a name could not be resolved, and the abort rule ended the session. The users' requests were all answered, because the apps keep their database connections open; any new connection in that minute would have failed as the probe's did.

The software drill three days earlier had killed a DNS pod and passed, because a killed pod is removed from the service at once. A review on paper cannot see timing either. A simulation can: the same day, a four-node throwaway cluster reproduced the stall within minutes, in every one of six runs. It then showed the fix, a DNS server on every node with each node preferring its own, running with no failed lookup, and it found a rollout stall in the fix before the live site met it. Had the simulation come first, the flaw would have been found at no risk. That is the reason for the rule above.

**The fix, built on 2026-11-20.** The change-over runs in five steps, one pull request at a time, each judged by the DNS probe before the next. All five went live on 2026-11-20. During the first step's hour-long soak, one node counted 2 failed lookups out of about 7,600, both fast, with no error in any DNS log; the cause is still unknown. The last three steps waited for a log line per failed lookup and a clean soak, then ran the same day. After the first step the probe on all six nodes counted no failed lookup, and the old DNS add-on stayed gone across four server restarts. The single point stays **open** until a power-off drill passes.

### A process slip, 2026-11-20

The second step of the change-over was merged in the same command that read the first step's referee. The referee had counted those 2 failed lookups; they were read only after the merge, and the reconciler applied the step about half a minute later. Nothing broke: the probe has been clean since. But a referee whose verdict arrives after the decision is not a referee. **Read the referee, then merge.**

**What this does not prove.** That anything here is highly available. Of the single points in the [register](reliability.html), {{ hw_ev.single_points_fixed }} are fixed in the generated figures of {{ site.data.stats.generated_at | date: "%Y-%m-%d" }}, because fixed needs a power-off drill that passed. The simulations run in containers on one machine and stand in for no hardware. The nightly rule is planned, not built, and it will be shown to work only when a simulation fails and stops a live drill.

Related pages: [the delivery chain](platform.html#how-a-change-reaches-the-cluster),
[what I'd do differently](lessons.html), [who reviews, honestly](ai-dev.html#who-reviews-honestly).
