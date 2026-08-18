---
title: How the platform builds and ships things
---

# The delivery chain

An application does not have to live in the platform's repository to run on it. It can sit
in its own repo and deploy over a small published contract. This is how that works, and why
it is shaped the way it is.

---

## Why the pipeline is split across two kinds of runner

This is the single most load-bearing fact about the whole chain, and it is invisible unless
you read every `runs-on:` line.

**The house internet connection is behind carrier-grade NAT.** There is no inbound path
from the internet to the cluster and no port forward to open. So GitHub's own hosted
runners — which live in the cloud — *cannot reach the cluster at all*.

Everything that only needs the source code runs in the cloud. Everything that touches the
image registry, the signing key or the Kubernetes API server has to run on a self-hosted
runner sitting on the same LAN as the cluster.

Measured split: **49 job references on cloud runners, 13 on the self-hosted one.**

```mermaid
flowchart LR
  subgraph GH["GitHub-hosted runners · 49 job refs"]
    A["lint · CodeQL · secret scan<br/>unit + contract tests<br/>DAST · nightly · dependency bumps"]
  end
  subgraph LAN["Self-hosted runner · 13 job refs<br/>on the same LAN as the cluster"]
    B["container build + push<br/>sign + verify<br/>release gate<br/>rollout"]
  end
  A --> OK["needs only the repo — done in the cloud"]
  B --> REG[("in-cluster image registry")]
  B --> API["Kubernetes API server"]
  GH -. "no inbound path (CGNAT)" .-> LAN
```

There is an honest weakness here worth stating plainly: that self-hosted runner is a single
machine. Every deploy — including the satellite repositories that call in — stops when it is
off. It is the one part of the delivery path with no redundancy.

---

## The contract an application has to meet

The platform provides the registry, the signing chain, the reusable deploy workflow, the
runtime, ingress, replicated storage, identity, metrics and logs.

The application brings exactly two things:

1. **A `Dockerfile`** that builds for `linux/amd64`.
2. **A Kubernetes manifest** with resource requests and limits, health probes, a disruption
   budget and topology spread.

A signed image plus a conformant manifest is the entire handoff. Everything else is
convention.

---

## What a deploy actually does

```mermaid
flowchart TD
  P["push / release in the application repo"] --> C["its own CI (cloud runner)"]
  C --> U["calls the platform's reusable deploy workflow"]
  U --> D["job: deploy — self-hosted runner"]
  D --> S1["1 · check out the application repo"]
  S1 --> S2["2 · build the artifact (only if the stack needs it)"]
  S2 --> S3["3 · build + push image<br/>immutable git-SHA tag, provenance, SBOM"]
  S3 --> S4["4 · sign, then verify the signature"]
  S4 --> S5["5 · render the manifest and apply it"]
  S5 --> S6["6 · wait on the rollout"]
```

Two details that matter more than they look:

**The image tag is the git SHA, never a floating `latest`.** A floating tag means a rollout
can quietly pull a cached older layer and report success. Immutable tags make "what is
actually running" answerable.

**The signature is verified, not just created.** Signing something and never checking the
signature is a ceremony, not a control. The verify step is what makes it a control.

---

## The gate, and who it does not protect

Applications that live inside the platform repository go through a policy gate between
resolving the release and deploying it:

```mermaid
flowchart LR
  T["release triggered"] --> R["resolve (cloud runner)"]
  R --> G{"release gate<br/>is this commit's CI green?"}
  G -- pass --> K["deploy to Kubernetes"]
  G -- pass --> W["deploy to the legacy runtime"]
  G -- fail --> X["stop — no rollout"]
  K --> V["rollout status + smoke test"]
```

**Satellite repositories do not pass through that gate.** The reusable deploy workflow is a
single job with no policy step, so a satellite's own CI is the only thing between a commit
and a rollout.

That is a deliberate consequence of keeping the contract small — but it is an asymmetry
worth knowing when deciding what belongs in a satellite repository versus the platform
itself.

---

## Supply chain

Every image carries a signature, build provenance and an SBOM. The SBOMs are continuously
re-evaluated against new vulnerability data, so a component that was clean at build time
gets flagged when the world changes rather than at the next release.

One lesson from doing this in anger: **a vulnerability scanner only matches what it can
identify.** An SBOM whose components carry only generic package identifiers produces zero
findings even when real vulnerabilities exist — not because the software is clean, but
because nothing matched. Zero findings and "nothing was evaluated" look identical on a
dashboard. Check that components resolve to real ecosystem identifiers before believing a
clean report.

---

<sub>Machines, addresses, hostnames and topology are deliberately absent. This page was
written for publication, not scrubbed after the fact.</sub>

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
