---
title: Alerting and monitoring — two models, one human
reread: 2026-10-30
summary:
  - "**What it is:** alerts go straight to chat; a small local model on a separate machine answers questions, writes a morning digest and *proposes* fixes; a large cloud model reads the local one's posts once a day and grades them. Nothing either says is executed: a fixed, allowlisted guardrail layer disposes, and almost every action waits for a named person's click."
  - "**Where the people are:** a click on every action, a monthly graded sample of eight posts, and a guard that goes red after 35 days without one. The cloud model's grades are drafts and cannot satisfy that guard. The first graded sample is due by 2026-11-26."
  - "**What it may do alone:** two rules, both on-demand database backups, and only if auto-apply is switched on. It is not. Everything else is a proposal."
  - "**What changed on 26 October:** a review of its first 96 summaries found inflated severity and a blind data source it never mentioned, and a model-supplied name placed into a command run as root. Arguments are now validated, only approvers count, every executed action is audited, and a quality loop measures what it says."
  - "**What is still weak:** its log-based proposals (five graded, none good), a small model that is not an engineer, one instance, and an approval channel that is a third-party chat service."
---

# An AI ops agent with a narrow, audited write path

{% include in-short.html %}

{% assign skills = 6 %}{% assign rules = 5 %}{% assign restarts = 3 %}{% assign additive = 2 %}{% assign refused = 16 %}{% assign tests = 690 %}
{% capture rr %}{{ rules }} mapped, {{ refused }} refused{% endcapture %}
![model](https://img.shields.io/badge/model-local%2C%20on--prem-black?logo=ollama&logoColor=white)
![skills](https://img.shields.io/badge/skill%20vocabulary-{{ skills }}%20named%2C%20closed-2EA44F)
![rules](https://img.shields.io/badge/alert%20rules-{{ rr | uri_escape }}-24A1C1)
![autoapply](https://img.shields.io/badge/unattended%20auto--apply-off-orange)
![failclosed](https://img.shields.io/badge/chaos%20safety-fail--closed-critical)

There is a lot of "AI for ops" that is a chat window in front of a dashboard. This one has a
write path to a production cluster, which makes the interesting question not *what can it
do* but **what is it allowed to do without asking.**

This is the run-time half of a two-part practice, the production edge. [The dev-time
half](ai-dev.html) is a cloud model as a reviewed engineering peer, deliberately a different
model, in a different place, for a different reason.

*Counts below are read from the agent's source as of 2026-10-27 and will move; they are
typed here, not generated, which is the one weakness of this page. The page was first
written against the agent as it stood on 2026-10-09; the section
[The agent since 2026-10-26](#the-agent-since-2026-10-26) is what changed.*

---

## The loop: two models, one human

Alerting is not one thing, and the models are in only part of it. As read from the deploy
configuration and the host on 2026-10-30:

```mermaid
flowchart LR
  SRC["metrics · logs · workload state"] --> RULES["alert rules"]
  RULES -->|"the moment one fires<br/>no model involved"| CH["chat channel"]
  SRC --> POLL["hourly poll<br/>the post is composed by code"]
  POLL -->|"only if something changed;<br/>repeated after 24 h"| CH
  SRC --> DIG["07:00 digest<br/>written by the local model"]
  DIG --> CH
  CH --> P1["a person: approves or rejects<br/>every action, thumbs a post"]
  POLL --> REC["every post recorded"]
  REC -->|"daily, up to 12 posts"| CLOUD["cloud model<br/>grades them, no tools"]
  CLOUD -.->|"drafts only"| P2
  REC --> P2["a person, monthly:<br/>grades 8 random posts"]
```

- **Alerts** go from the alert rules to chat directly, as they fire and as they resolve. No model
  is in that path; it is the part that must work when everything else does not.
- **The hourly post** is composed by code from the findings: a line saying how urgent it is,
  grouped logins, job ages, a one-line workload count. It is posted only when something
  changed, and repeated after a day. Until 2026-10-28 a local model wrote its headline; it no
  longer does, because it kept repeating what the code had already said. One real post went
  from about 70 lines to 15.
- **The local model** (a small one, on the same machine as the agent) answers questions asked in
  chat, writes the 07:00 digest from a metrics snapshot and phrases proposals. It cannot run
  anything. **The digest is not recorded in the quality loop below, so nobody has graded it**,
  which makes it the weakest-measured thing the model still does.
- **The cloud model** reads, once a day, up to twelve of the agent's recent posts and drafts a
  grade for each: right or wrong, noisy or missed, and separately whether it was clear and
  something a person could act on. It has no tools, so text inside a post can change a grade at
  most. Its drafts go to a separate file on purpose: the guard that insists a person has graded
  a sample counts only a person's grades, **so a model reading another model can never satisfy
  it.** A person adopts a draft by grading the post, or ignores it. It costs roughly $0.12 to
  $0.63 a day.
- **The people** approve or reject every action (a named approver list; an empty list means
  nobody), thumb posts up or down, and about monthly grade eight random posts. A guard goes
  red after 35 days without a graded sample. No sample has been graded yet; the first is due by
  2026-11-26.

**What the second reader has shown so far.** Its first run, on 2026-10-28, graded twelve posts
written before the layout change: it called eleven wrong and one noisy, and seven of the eleven carried
no automatic flag, so the cheap checks had missed them. Five were invented causes. The posts were then redesigned, which is
the intended use: a stronger model finds the failure once, and a rule or a line of code keeps it
fixed. Separately, on five golden prompts run twice each (2026-10-27), the local model passed 8
of 10 and two cloud models passed 10 of 10 each. Those cases test rule-following, not
engineering judgement, so they do not show the cloud models to be better at running a cluster,
and they do not rank one cloud model over the other.

**The same discipline applied to the alerts themselves.** On 2026-10-29 a DNS-slowness alert was
retuned to fire on a share of slow lookups (above 10 percent for ten minutes; the usual level is
about 2) after a raw probe showed the packet loss was not everywhere. Measured over four hours on
2026-10-30, the two oldest machines lose about 7 percent of lookups sent to the service address and the
other four lose under 0.3, while direct queries to the DNS pods from the same two machines are almost
clean. A kernel upgrade on one of them made no difference (7.9 against 7.3 percent), which retired my
first theory. Its cause is still open. A memory alert that fired on a figure including the kernel's file
cache now compares the process's own memory; that change was applied to the cluster the same day, and the
daily drift check that had been failing because it was merged but not applied went green. An alert that cries wolf teaches people to ignore the next one, which is the cost
the quality loop exists to put a number on.

**What this does not show.** It shows the output is measured and the input path is safer. It does
not show that either model reasons well about an incident, and the cloud model's grades are a
second opinion, not ground truth. The model-to-model step adds a third party that sees alert
text; that is a choice I made on 2026-10-27, and it is the reason for the correction below.

---

## It runs outside the cluster, deliberately

> A monitor that dies with the thing it monitors is not a monitor.

The agent does not run as a workload on the cluster it watches. It runs on a separate small
machine, supervised by the host's own service manager, reaching the cluster over the network
like any other client. When the cluster is unhealthy, which is the only time the agent
matters, the agent is still up, still has its history, and can still say so.

The model that does the live work is **local**. Nothing in the alert path, the hourly post, the
digest or an approval calls a vendor's API, so the ops brain does not stop working because
someone else's API is down or has changed its terms. That is a dependency property, and it
used to be a privacy claim as well. **Correction, 2026-10-30:** this page said no cluster
state, logs or alert payloads left the house. That stopped being true on 2026-10-28, when the
daily cloud reader began ([next section](#the-loop-two-models-one-human)): it is sent alert
text and node names (trimmed to 300 characters each), the facts the code computed and the
local model's wording, for up to twelve posts a day. It is not sent logs, credentials or
manifests.

---

## What it reads

```mermaid
flowchart LR
  subgraph IN["read-only inputs"]
    M["metrics"]
    L["logs"]
    A["active alerts"]
    K["node / workload state"]
    C["identity-provider state"]
    P["pull-request health"]
  end
  IN --> AG["correlate · summarise · propose"]
  AG --> ADD["additive action<br/>runs unattended once armed"]
  AG --> DIS["disruptive action<br/>waits for a human"]
  AG --> REP["digest + escalation"]
```

Correlation across those sources is the intent: a pod restart is noise; a pod restart *plus*
a node's disk latency climbing *plus* a recent merged change is a hypothesis worth a human's
attention. Whether the local model actually does that well is a claim I have not measured.

Two things I had listed here and have taken out as of 2026-10-09. Vulnerability findings are
synced to a ticket tracker and announced in chat, but nothing in the code feeds them into the
correlation. The cluster's API audit trail is in the log store, but I found no agent code
that queries it. Specialist collectors feed the rest, and the job is a short list, not a
longer dashboard.

---

## Two paths in, one guardrail authority

A cluster action reaches execution through exactly one of two entry points, and both are
forced through the same builder before anything is allowed to run.

> *I had to be in the driver’s seat. I had to tell it what I wanted, and I had to be the
> reviewer, the auditor of what was coming out.*
> — DHH on the first phase of agentic development, [Lex Fridman Podcast #501](https://lexfridman.com/dhh-2/) (2026)

For this agent that is the permanent design, not a transitional one. The guardrails are not
a stepping stone toward a model that runs unsupervised; they are the point.

### Chat path

A deterministic parser handles ordinary phrasing; an LLM router only takes over when the
parser misses and the text looks like it wants a mutation. Neither one ever produces a
command. Both can only emit a skill name plus typed parameters, chosen from a **closed
vocabulary of {{ skills }}**: scale, restart, drain, activate, rebalance, backup. **Every
chat-triggered action, all {{ skills }} skills with no exceptions, is posted as a dry run and
waits for an explicit human approval.** There is no unattended path from a conversation,
however additive the request looks. An approval that nobody clicks expires after ten minutes. Since 2026-10-26 only people on a named approver list can request or approve one; an empty list means nobody.

### Alert path

A firing alert triggers a lookup, and the model is not in this loop at all. A small,
hand-written table maps specific alerts to one of the same {{ skills }} skills. An alert is
untrusted input, and routing it through an LLM before acting would add exactly the
prompt-injection surface the rest of this design exists to avoid. A lookup is deterministic,
testable, and cannot be talked into anything.

As of 2026-10-27 the table holds **{{ rules }} rules, and {{ refused }} further alert types are explicitly
declared un-actionable, each with a written reason**: a level-based alert that would loop
forever if acted on, a symptom whose "fix" would erase the evidence, a physical fault no
command can touch. Absence is an oversight; a name on that second list is a decision.

Only **{{ additive }} of the {{ rules }}** are additive (an on-demand backup, which adds an
object and touches nothing live). Only those are *eligible* to run unattended, and only once
a separate switch has been deliberately armed. **That switch is still off.** The other
{{ restarts }} are restarts, which are correct but disruptive: a restart can erase the
evidence of what crashed, or cycle replicas that were still serving. They queue through the
identical approval card as the chat path. The fifth rule, a restart for a backup component
that had ended up on the same node as its database primary, was added on 2026-09-16; it
touches no database and is still gated.

> A silent self-heal is not one. Even the unattended path always announces what it did.

### Shared guardrails

Every guardrail lives in the single shared builder, so neither entry point can route around
it by construction: the skill vocabulary, a rule that no service can be scaled to zero, one
permanently protected control-plane node, a five-minute rate limit between any two
executions, and the approval timeout. Even a worst case stays bounded. A hostile instruction
smuggled into a log line the model is summarising can, at most, produce a structured request
like *scale to zero*; the guardrail refuses it, and a human would still have had to click
approve. Three independent stops between suggestion and effect.

Draining a node is instructive on its own: it is frequently *safe* by the quorum arithmetic,
and it is still always on the gated side. Safety is not the criterion, **reversibility** is.
An unnecessary on-demand backup costs one wasted object. A node drained that should not have
been costs an incident.

A third category sits outside even this: whole-cluster operations live behind a flag that
defaults to off and is documented as *leave it there*. Some capabilities should require
editing configuration and thinking about it, not clicking a button while distracted.

Every gated action shows the exact command, who asked for it, and a dry run of its effect
before anyone can approve it, and every executed action is appended to an audit file that survives a restart (since 2026-10-26; before that the log lived in memory). An approval that does
not show you what you are approving is a rubber stamp.

### The refusal list is the load-bearing half

The mapping from alert to action is a **plain dictionary, not a model decision**; the local
model is weakest at exactly the structured extraction that routing requires, so routing
never reaches it. What is more interesting is the second table, which is longer. This is an
abridged excerpt, with the names shortened, the labels left out and the reasons paraphrased:

```python
# Eligible to run unattended: additive only. Creates an object, destroys nothing.
REMEDIATIONS = {
    "BackupStale":      Rule(skill="backup",  auto=True),
    "LastBackupFailed": Rule(skill="backup",  auto=True),
    # Correct, but disruptive: a restart erases the evidence of what crashed.
    "AppPodDown":            Rule(skill="restart", auto=False),
    "AppDeploymentDegraded": Rule(skill="restart", auto=False),
    # ... and the backup-component co-location restart, also auto=False
}

# Refused outright, each with a reason. This table is longer than the one above
# and that ratio is the point.
NEVER_REMEDIATE = {
    "ContainerOOMKilled":
        "level-based stale gauge: the alert stays firing after recovery, so a "
        "restart would re-trigger it forever (verified 2026-08-07)",
    "ClusterLostRedundancy":
        "a replica with an unusable data directory needs a rebuild, not a restart",
    # ... fourteen more
}
```

And a test that pins the property rather than the contents, so the rule cannot be quietly
widened later:

```python
def test_only_additive_skills_may_auto_apply():
    for name, rule in REMEDIATIONS.items():
        if rule.auto:
            assert rule.skill == "backup", (
                f"{name} is marked auto but {rule.skill!r} is not additive"
            )
```

That test was **falsified before it was trusted**: flip a restart rule to `auto=True` and
watch it fail, because a guard nobody has seen fail is not known to be a guard.

**Retraction, 2026-10-09.** This section used to say the refusal list "proved itself in
production" over a database incident, with the agent proposing zero actions across three
days. I cannot back that with a dated log: the incident is undated, the remediation
proposals were not armed in the infrastructure code until 2026-09-29, and the diagnosis the
old text quoted from that incident turned out to be wrong. What I can still stand behind is
smaller. `ContainerRestartingFrequently` is on the refusal list, so a crash-looping database
pod does not get restarted by this agent; a restart rule for it would have cycled a pod
mid-recovery and destroyed the log evidence. On the same day as this note a database replica
that had silently diverged at a failover two weeks earlier crash-looped on its first restart,
and the alerts that now cover that class are alerts for a human. None of them is mapped to an
action.

> Zero false positives over a real incident is a better result than a clever remediation,
> and it is the harder one to demonstrate, because success looks like an empty log. I do not
> yet have the log.

---

## The chaos safety controller, and fail-closed as a default

Scheduled fault injection runs against a staging target on the platform: call it the
resident **provocateur**. Its entire job is manufacturing exactly the kind of trouble
everything else on this site is built to survive. The controller that guards it is the part
worth copying.

It pauses **every** fault schedule when any of these is true:

- the feature is switched off
- the cluster is not in steady state: any alert at or above a severity threshold is firing,
  or a workload is degraded
- **the check itself errored**

That third one is the design decision. "I could not determine whether the cluster is healthy"
is treated identically to "the cluster is unhealthy." A safety control that fails open is
decoration; the whole reason it exists is the case where something unexpected is happening,
and "unexpected" very often means the check broke too.

It also tracks *duration*. A brief blip pauses injection quietly. An injected fault that has
not self-healed inside its recovery budget (five minutes by default) escalates loudly, with
the correct framing: the alarming thing is not the fault, it is that **the automatic
recovery loop is not recovering.**

There are two schedules, a pod kill and a packet-loss fault, each hourly on weekdays in the
daytime, and the controller pauses and re-arms each one as the steady-state check changes. As of
2026-10-27 both are paused, and they last fired on 2026-10-13: the gate vetoes on any
warning-level alert, and two have been firing since the previous morning. That is the controller
doing what it is for, and a reason to read "armed" as a reading of one moment. The ten days before
that, and the two latches that caused them, are on
[the reliability page](reliability.html#fault-injection-is-paused-by-its-own-safety-gate).
The controller was armed in the infrastructure code on 2026-09-22.

**Schedules are discovered, never listed.** The controller enumerates fault schedules from
the live cluster on every tick; it does not read a configured list of things to guard. This
is the same lesson as [deriving vulnerability-scan scope from the cluster](devsecops.md), and
it was learned the same way: an earlier kill switch matched **one hardcoded name**, and a
second class of fault had been added afterwards. The switch reported success and covered half
the system. A hand-maintained list of things to protect drifts in exactly one direction:
smaller than everyone believes. Derived scope means a new fault class is enrolled in its own
safety guard at the moment it exists, not once someone remembers.

---

## The lesson that makes this page honest

The safety controller had **never been deployed to the machine whose only job was to hold
it.** The deployment mechanism copied a directory rather than checking out the repository,
so the host quietly kept an old build, and arming the controller would have been a no-op
that reported success. It was armed for real only after that was found. The copy mechanism
stayed how the agent shipped until 2026-10-26, when it was replaced by a
deploy from a merged commit with a daily drift check ([below](#the-agent-since-2026-10-26)).
The lesson is in the past tense now, and the check that made it so is itself the lesson.

The pattern is identical to [the reboot daemon that never rebooted](reliability.md) and the
fault injector that had never fired: **configured, plausible, and inert.** The
distinguishing field in all three cases is the same one, and it was on no dashboard:

> **When did this last actually run?**

"Armed" and "has fired" are different claims. Only one of them is evidence.

---

## A scar worth keeping

**A process-level watchdog, because libraries wedge.** The messaging socket the agent uses
for approvals can enter a permanent reconnect loop after the host sleeps: connected according
to every log line, delivering nothing. The agent counts broken-pipe errors and, past a
threshold inside a short window, deliberately exits so the host's service manager respawns
it with a fresh connection. Self-healing at the process level, because *the library believed
it was fine* and only the failure rate disagreed.

A smaller one: an automated remediation notice once double-wrapped its own code fences and
rendered as unreadable literal markup. When the message is the interface, formatting is a
correctness bug.

---

## How it is evaluated

Three layers, deliberately:

- **Unit tests**: {{ tests }} test functions across the agent's suite as of 2026-10-27 (a
  static count of definitions, not a pass rate; parametrised cases make the collected count
  higher). They run offline, with no cluster and no model reachable: prompt-router
  regression, command parsing, and every guardrail asserted directly. Those are the
  never-scale-to-zero rule, the protected node, the rate limit, and both recognisers landing
  on the same action for the same request.
- **Integration tests** written to run against the real cluster from the agent's host, over
  its real access path, because a mock cannot tell you that the credential, the route and
  the permissions are all correct simultaneously. They exist in the repository; I have not
  found a schedule that runs them, so I do not claim they run regularly.
- **Live operation, dated.** The agent was first scaffolded in April 2026, but for most of
  that time it answered chat mentions only. Scheduled polling and the daily digest have been
  in the infrastructure code since 2026-09-06, the chaos safety controller since 2026-09-22,
  and approval-gated remediation proposals since 2026-09-29. Unattended auto-apply has never
  been switched on.

**Retraction, 2026-10-09.** This section used to say the agent "has run unsupervised for
months" and that "additive remediations have executed and are logged". The first is true of
the chat loop only. The second I cannot support: the unattended path has never been armed,
and the agent's audit log lived in memory and did not survive a restart, so there was no
trail to point to. (An audit file exists since 2026-10-26; it is one day old.) Its chaos state is served read-only over HTTP for a dashboard, but that
server is off by default, so its liveness is observable only where it has been enabled.

---

## The agent since 2026-10-26

The first outside look at the agent's *output* (not its code) came on 2026-10-26, and it changed
the agent. The account is short because the numbers are the point.

**What the review of 96 hourly summaries found.** "Critical" appeared in 79 of them, with no
critical alert firing in 69. Not one mentioned a data source that had been blind for fourteen
days. Of the 25 summaries that reported out-of-memory kills, 16 did so when no such alert was
active. And the logs kept only the first 200 characters of each post, so the review was
possible at all only because the metrics store remembered what had been firing.

**What the same review found in the code.** A model-supplied namespace was placed into a command
run as root on a cluster host. That had been true since 2026-10-14 and is the sharpest finding the
agent has had. It needed prompt injection and a way to plant text, so it was rated low in
likelihood and critical in impact. Separately, every proposal since 2026-10-09 had been silently
dropped, because the chat channel it was configured to post to did not exist.

**What changed, with the date it landed:**

- **Arguments are validated (2026-10-26).** Tool arguments are validated before anything runs, the approver list gates both requesting and approving, the rate limit is atomic,
  every executed action is appended to an audit file, and the service definition no longer carries
  chat tokens. Channel and approver identities come from a credentials directory that is not in git.
- **It deploys from git, and git is checked (2026-10-26).** The deploy refuses uncommitted changes
  and any commit not on the merged branch, exports that commit, and stamps it on the host. A daily
  check compares the agent's code by checksum, the model server's environment, the declared models
  and the agent's configuration keys. Its first measurement found eight files that differed, a
  context-window setting that had never been applied (and would have been far too large for a model
  of this size on this machine), and about twenty gigabytes of evaluation models that no file
  declared. The same week an edit to the deploy playbook deleted a whole configuration step; neither
  the syntax check nor CI could see it, and the agent kept working only because the sync excludes
  that file. It was found by deploying, which is why the drift check exists.
- **What it says is measured (2026-10-26).** Every model call is recorded: the facts the code
  computed, what the model was given, what it said, its cost in tokens and seconds, and automatic
  flags for the failure classes found so far (severity inflation, an outage claimed as happening, "all
  healthy" next to a blind source, a headline about history). The status line is now written by
  code, not by the model. About monthly, a person grades eight random posts as good, noisy, wrong or
  missed; a daily check goes red when no sample has been graded for 35 days, so "sometimes" happens.
  Golden cases, built from graded failures, are run against the live model before any prompt, rule
  or model change is merged.

**The first turn of that loop, measured** (four cases, two runs each: small, so read the direction,
not the decimals): the old prompt passed 6 of 8; the new one, which carries the facts and four
rules, passed 8 of 8, at about forty percent more thinking time. Switching the model's thinking off
was tried and rejected: the model then wrote its reasoning into the post, was slower, and passed 3
of 8. A first check flagged a correct sample as wrong, was refined after a person read it, and
the earlier runs were re-scored with the refined check for both prompts so the comparison stayed
fair. The human grade is the arbiter; the automatic flags only have to be conservative.

**The first graded sample after the deploy** is the useful humility: the hourly summary was graded
good, and all five of the log-based *proposals* were not (three wrong, two noisy, none good). The
cause is that "no recent logs" fires for a service that simply logs a few lines an hour. The cheapest
fix is in code (compare a service with its own usual rate), not in the prompt, and that is the next
turn of the loop. A one-click thumbs vote under each post, from named approvers only, adds a trend
that is explicitly not a grade of correctness.

**What this does not show.** It shows the agent's *output* is now measured and its *input path* is
safer. It does not show the model reasons well about incidents, which remains the claim this page
has never made. The loop's first review is due by 2026-11-26.

---

## Honest limits

- **It is one instance.** Losing it degrades autonomy, not availability, which is why it is
  ranked below the storage and registry gaps rather than above them.
- **It proposes far more than it applies.** The unattended surface is intentionally the
  boring end of the action space, and that is the design working, not a shortfall. Every call
  and every executed action is recorded since 2026-10-26, so the counts of proposals approved,
  rejected and expired now begin to exist; there are not yet enough days of them to publish.
- **A small local model is not an engineer.** It is good at saying "these three facts are
  related" at 3am. It is not good at deciding whether the related facts justify an outage.
- **None of it proves reachability or intent.** The agent reasons over the same signals a
  human would read, with the same limits those signals have.
- **The approval channel is a third-party messaging service.** If it is down, gated actions
  cannot be approved, and today that means all remediation, because auto-apply is off. Once
  it is armed, additive ones will still run.

---

## Read next

- **[High availability, audited](reliability.md)**: the single-fault inventory and the drain
  that removed its own control surface.
- **[DevSecOps, end to end](devsecops.md)**: the gates, and the derived-scope principle.
- **[AI in development](ai-dev.md)**: the other half, a cloud model as a reviewed peer.

---

<sub>Written for publication. No hostnames, addresses, credential locations or channel
identifiers appear here, and a guard fails the build if they ever do.</sub>

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
