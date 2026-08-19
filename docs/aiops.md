---
title: The operations agent — what a local model is allowed to do
---

# An AI ops agent with a narrow, audited write path

![model](https://img.shields.io/badge/model-local%2C%20on--prem-black?logo=ollama&logoColor=white)
![placement](https://img.shields.io/badge/placement-outside%20the%20cluster%2C%20on%20purpose-326CE5?logo=kubernetes&logoColor=white)
![skills](https://img.shields.io/badge/skill%20vocabulary-6%20named%2C%20closed-2EA44F)
![autoapply](https://img.shields.io/badge/unattended%20auto--apply-off%20by%20default-orange)
![failclosed](https://img.shields.io/badge/chaos%20safety-fail--closed-critical)
![discovery](https://img.shields.io/badge/fault%20schedules-discovered%2C%20never%20listed-24A1C1)

There is a lot of "AI for ops" that is a chat window in front of a dashboard. This one has a
write path to a production cluster, which makes the interesting question not *what can it
do* but **what is it allowed to do without asking.**

This is the run-time half of a two-part practice; [the dev-time half](ai-dev.md) — a cloud
model as a reviewed engineering peer, not a party trusted with a cluster — is deliberately a
different model, running in a different place, for a different reason.

---

## It runs outside the cluster, deliberately

The agent does not run as a workload on the cluster it watches.

> A monitor that dies with the thing it monitors is not a monitor.

It runs on a separate small machine, supervised by the host's own service manager, reaching
the cluster over the network like any other client. When the cluster is unhealthy — which is
the only time the agent matters — the agent is still up, still has its history, and can
still say so.

The model itself is **local**. No cluster state, no logs, no alert payloads and no
configuration leave the house to be inferred on. That is a privacy property and a
dependency property at once: the ops brain does not stop working because someone else's API
is down or has changed its terms.

---

## What it reads

```mermaid
flowchart LR
  subgraph IN["read-only inputs"]
    M["metrics"]
    L["logs + API audit trail"]
    A["active, non-silenced alerts"]
    K["node / pod / replica state"]
    V["vulnerability findings"]
    C["CI + change metadata"]
  end
  IN --> AG["correlate · summarise · propose"]
  AG --> ADD["additive action<br/>runs unattended"]
  AG --> DIS["disruptive action<br/>waits for a human"]
  AG --> REP["digest + escalation"]
```

Correlation across those sources is the actual product. A pod restart is noise; a pod
restart *plus* a node's disk latency climbing *plus* a change merged forty minutes earlier
is a hypothesis worth a human's attention.

Specialist collectors feed it: one samples application errors out of the log store, one
tracks traffic and capacity trends, one watches build and test failure rates. The agent's job
is to turn those into a short list, not a longer dashboard.

---

## Two paths in, one guardrail authority

A cluster action reaches execution through exactly one of two entry points, and both are
forced through the same builder before anything is allowed to run.

**A human asks for something in chat.** A deterministic parser handles ordinary phrasing;
an LLM router only takes over when the parser misses and the text looks like it wants a
mutation. Neither one ever produces a command. Both can only emit a skill name plus typed
parameters, chosen from a **closed vocabulary of six**: scale, restart, drain, activate,
rebalance, backup. **Every chat-triggered action — all six skills, no exceptions — is posted
as a dry run and waits for an explicit human approval.** There is no unattended path from a
conversation, however additive the request looks.

**A firing alert triggers a lookup — and the model is not in this loop at all.** A small,
hand-written table maps a short list of specific alerts to one of the same six skills. The
model is deliberately excluded here: an alert is untrusted input, and routing it through an
LLM before acting on it would add exactly the prompt-injection surface the rest of this
design exists to avoid — a lookup is deterministic, testable, and cannot be talked into
anything. The table holds **four rules today, and sixteen further alert types are explicitly
declared un-actionable, each with a written reason** — a level-based alert that would loop
forever if acted on, a symptom whose "fix" would erase the evidence, a physical fault no
command can touch. Absence is an oversight; a name on that second list is a decision.

Only **two of those four** rules are additive (an on-demand backup, which adds an object and
touches nothing live) — and only those are *eligible* to run unattended, and only once a
separate switch has been deliberately armed; it defaults off. The other two are restarts,
which are correct but disruptive — a restart can erase the evidence of what crashed, or cycle
replicas that were still serving — so they queue through the identical approval card as the
chat path.

> A silent self-heal is not one. Even the unattended path always announces what it did.

Every guardrail — the skill vocabulary, a rule that no service can be scaled to zero, one
permanently protected control-plane node, a rate limit between any two executions, and a
timeout on an unapproved proposal — lives in that single shared builder, so neither entry
point can route around it by construction. Even a worst case stays bounded: a hostile
instruction smuggled into a log line the model is summarising can, at most, produce a
structured request like *scale to zero* — the scale-to-zero guardrail refuses it, and a human
would still have had to click approve regardless. Three independent stops between suggestion
and effect.

Draining a node is instructive on its own: it is frequently *safe* by the quorum arithmetic,
and it is still always on the gated side. Safety is not the criterion — **reversibility** is.
An unnecessary on-demand backup costs one wasted object. A node drained that should not have
been costs an incident.

A third category sits outside even this: whole-cluster operations live behind a flag that
defaults to off and is documented as *leave it there*. Some capabilities should require
editing configuration and thinking about it, not clicking a button while distracted.

Every gated action shows the exact command, who asked for it, and a dry run of its effect
before anyone can approve it. Every step is logged and attributed. An approval that does not
show you what you are approving is a rubber stamp.

---

## The chaos safety controller, and fail-closed as a default

Scheduled fault injection runs against the platform. The controller that guards it is the
part worth copying.

It pauses **every** fault schedule when any of these is true:

- the feature is switched off
- the cluster is not in steady state — any alert at or above a severity threshold is firing,
  or a workload is degraded
- **the check itself errored**

That third one is the design decision. "I could not determine whether the cluster is healthy"
is treated identically to "the cluster is unhealthy." A safety control that fails open is
decoration; the whole reason it exists is the case where something unexpected is happening,
and "unexpected" very often means the check broke too.

It also tracks *duration*. A brief blip pauses injection quietly. An injected fault that has
not self-healed inside its recovery budget escalates loudly, with the correct framing: the
alarming thing is not the fault, it is that **the automatic recovery loop is not recovering.**

### Schedules are discovered, never listed

The controller enumerates fault schedules from the live cluster on every tick. It does not
read a configured list of things to guard.

This is the same lesson as [deriving vulnerability-scan scope from the cluster](devsecops.md)
instead of maintaining it by hand, and it was learned the same way: an earlier kill switch
matched **one hardcoded name**, and a second class of fault had been added afterwards. The
switch reported success and covered half the system.

> A hand-maintained list of things to protect drifts in exactly one direction: smaller than
> everyone believes.

Derived scope means adding a new fault class enrols it in its own safety guard at the moment
it exists — not once someone remembers.

---

## The lesson that makes this page honest

The safety controller had **never been deployed to the machine whose only job was to hold
it.** The deployment mechanism copied a directory rather than checking out the repository,
so the host quietly kept a months-old build. Arming the controller would have been a no-op
that reported success.

It was armed for real only after that was found. The first fault it actually guarded fired
days later.

The pattern is identical to [the reboot daemon that never rebooted](reliability.md) and the
fault injector that had never fired: **configured, plausible, and inert.** The
distinguishing field in all three cases is the same one, and it was on no dashboard:

> **When did this last actually run?**

"Armed" and "has fired" are different claims. Only one of them is evidence.

---

## Small operational scars worth keeping

Two, because they are the kind of thing that only appears once something runs unattended for
months:

**A process-level watchdog, because libraries wedge.** The messaging socket the agent uses
for approvals can enter a permanent reconnect loop after the host sleeps — connected
according to every log line, delivering nothing. The agent counts broken-pipe errors and,
past a threshold inside a short window, deliberately exits so the host's service manager
respawns it with a fresh connection. Self-healing at the process level, because *the library
believed it was fine* and only the failure rate disagreed.

**Formatting is a correctness bug when the message is the interface.** An automated
remediation notice double-wrapped its own code fences and rendered as unreadable literal
markup. If the only channel through which a human approves a cluster change is garbled, the
control is degraded regardless of how correct the logic behind it is.

---

## How it is evaluated

Three layers, deliberately:

- **Unit tests** — over 300, offline, no cluster and no model reachable — prompt-router
  regression, command parsing, and every guardrail asserted directly: the never-scale-to-zero
  rule, the protected node, the rate limit, and both recognisers landing on the same action
  for the same request.
- **Integration tests that run against the real cluster** from the agent's actual host, over
  its real access path. A mock cannot tell you that the credential, the route and the
  permissions are all correct simultaneously.
- **Live operation.** It has run unsupervised for months. Additive remediations have executed
  and are logged. The safety controller has paused schedules, resumed them, and its state is
  served from an endpoint that a dashboard reads — so *its* liveness is itself observable
  rather than assumed.

---

## Honest limits

- **It is one instance.** Losing it degrades autonomy, not availability — which is why it is
  ranked below the storage and registry gaps rather than above them.
- **It proposes far more than it applies.** The unattended surface is intentionally the
  boring end of the action space, and that is the design working, not a shortfall.
- **A small local model is not an engineer.** It is very good at correlating six data
  sources at 3am and saying "these three facts are related." It is not good at deciding
  whether the related facts justify an outage.
- **None of it proves reachability or intent.** The agent reasons over the same signals a
  human would read, with the same limits those signals have.
- **The approval channel is a third-party messaging service.** If it is down, gated actions
  cannot be approved. Additive ones still run; the escalation path degrades to the alert
  router.

---

## Read next

- **[High availability, audited](reliability.md)** — the single-fault inventory, the drain
  that removed its own control surface, and why the patching loop is the best chaos
  experiment on the platform.
- **[DevSecOps, end to end](devsecops.md)** — the gates, and the derived-scope principle this
  page borrows.
- **[AI in development](ai-dev.md)** — the other half: a cloud model as a reviewed
  engineering peer, and the honest gap in measuring what it actually improves.

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
