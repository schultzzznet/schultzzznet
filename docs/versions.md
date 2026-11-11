---
title: "V1.0 and V2.0: what changed"
description: A dated diff list between the retired cluster (V1.0) and the K3s home site (V2.0), area by area, with a status word on every V2.0 row.
reread: 2026-11-11
body_read: 2026-11-11
summary:
  - "**What it is:** a diff list of V1.0 (the cluster retired on 2026-11-10) against V2.0 (the K3s home site, built on 2026-11-10 and 11), 70 rows in 16 areas, each row dated and given one of four status words."
  - "**Counts, 2026-11-11:** 14 kept, 32 changed, 6 new, 1 dropped, 17 not rebuilt yet. Of the V2.0 sides, 19 are proven, 17 built, 8 planned, 24 open; 2 are unchanged and outside the cluster."
  - "**Where V1.0 was better:** 30 rows, among them a live reference to compare against, replicated storage, one database cluster per app, names on the LAN, an in-cluster registry that needed no internet, read monitoring and alerts, rehearsed upgrades, rollback and restore drills, a public entrance, scans and an audit log. Most of that is not rebuilt yet."
  - "**V1.0 is kept as a diffed reference.** Nothing about it is deleted and every V1.0 fact keeps its date. It is not running; it is never evidence about V2.0."
---

# V1.0 and V2.0: what changed

{% include in-short.html %}

On 2026-11-10 I took V1.0 down and built V2.0 on the same six machines. This page is the diff list: for each area, what V1.0 did, what V2.0 does today, whether that is a change, and how far V2.0 has got. It was read against the system on 2026-11-11 (the live readings at 07:00 UTC), when V2.0 was about a day old, so no row is an uptime claim. Where V1.0 did something better I say so in the row.

## The key

| Word | Meaning |
|---|---|
| **V1.0** | The retired old cluster, torn down on 2026-11-10. It is described only as it was on the dates given. It does not run. |
| **V2.0** | The K3s home site, built on the same six machines on 2026-11-10 and 11. |
| **proven** | Seen working, on the date given in the evidence column. |
| **built** | Written and applied, but not shown to do its job. |
| **planned** | Decided or intended, not built. |
| **open** | Not decided, not done, or a known gap. |

Change types: **kept** (same idea, carried over), **changed** (a different way of doing it), **new** (V1.0 had nothing like it), **dropped** (removed on purpose), **not rebuilt yet** (V1.0 had it, V2.0 does not). Two rows (3D printing source and cost) are unchanged and outside the cluster, so they carry no status word.

## Counts by change type

| Change | Rows |
|---|---|
| kept | 14 |
| changed | 32 |
| new | 6 |
| dropped | 1 |
| not rebuilt yet | 17 |
| **All** | **70** |

| V2.0 status | Rows |
|---|---|
| proven | 19 |
| built | 17 |
| planned | 8 |
| open | 24 |
| no status (outside the cluster) | 2 |

The shape matters more than the totals: most of what V1.0 had for watching, scanning and surviving a lost machine is on the not-rebuilt side, and most of what is new is about how change reaches the cluster and what it is allowed to run.

## The diff list, by area

### Hardware and OS

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Hardware and OS | Six retired laptops: three control-plane servers that also ran workloads, three agents; the oldest from 2011. Ran until 2026-11-10. | The same six machines, wiped and rebuilt as V2.0 on 2026-11-10; same roles. | kept | proven | **Evidence:** All six machines Ready, and none carries a taint, so the three servers still run workloads; read 2026-11-11 07:00 UTC. **Why:** The old hardware is the handicap on purpose: if it runs here it runs on better. |
| Hardware and OS | V1.0 stayed up as the working reference until 2026-11-10. Its own daily guards had been red every day from 2026-11-02 to 2026-11-09 and nobody read them. | Torn down on 2026-11-10, before the new site passed its gates, because the new site needed the same machines. | changed | proven | **Evidence:** Teardown record 2026-11-10; the 2026-11-10 review found V1.0 healthy but unattended, 6 nodes Ready and 6 apps at 2 of 2. **Why:** V1.0 was better here: it was a live thing to compare against. The cost of tearing it down first is that comparisons now rest on notes, and the outside-tool baseline I wanted before the wipe (benchmark, scorecard) was never filed. |
| Hardware and OS | Ubuntu Desktop on the nodes with the desktop stripped by a play; Debian on some CI builders. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | One server distribution on every host, including the CI builders, installed from a stick built from the repository. | changed | proven | **Evidence:** Six blank machines became a Ready site in one supervised session on 2026-11-10. **Why:** One image to maintain. The reason for the single distribution is not written down, and only one distribution has run end to end (a second is open). |
| Hardware and OS | Host rules learned from incidents lived in playbooks: frequency governor and temperature caps, sleep masked, swap off, inotify limits, one stable IPv4 node address, service flags only in config files, time synced before runners start. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | A written host baseline and a host play. On 2026-11-08 the review found most of V1.0's rules missing from it; I have not re-checked rule by rule. | changed | built | **Evidence:** A three-VM rehearsal passed on 2026-11-10 and a second run changed nothing (4 min 11 s); the baseline applied to six real machines the same day. **Why:** Each of those rules cost an incident. Writing the baseline from scratch risks paying for them twice. |
| Hardware and OS | Hard power-off drills existed as a make target, after one real mains cut on 2026-08-20 took two of three servers down for 9 min 12 s. Each control-plane machine's battery, power path, wake-on-LAN limit and disk class were recorded after that incident. | None run on V2.0. 0 of 16 power-off proofs carried over, and none can run until the site is live long enough to cut. Per-machine hardware and power facts are one register row for all six nodes, last looked at on 2026-11-08. | not rebuilt yet | open | **Evidence:** Carry-over register read 2026-11-11: 16 proofs, all open. Hardware-facts review finding open 2026-11-08. **Why:** V1.0 was better: V1.0 had the drills and knew which servers had a battery. The drills are how a lesson stays learned. The 9 min 12 s figure is from the V1.0 incident register of 2026-11-05. |
| Hardware and OS | Supporting machines (workstation, small always-on Mac, an edge board, a probe board, a Yocto build board) each had a role. A home camera recorder also ran on the always-on Mac. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Same machines. The always-on Mac now holds the backup store outside the cluster; the workstation is where host plays and bootstrap run. The edge and probe boards are not part of V2.0 yet. The camera recorder is untouched and declared out of scope for the platform; it is a household service, not something I am learning from. | kept | built | **Evidence:** Backup store reachable and the nightly backup completed, read 2026-11-11. **Why:** Not rebuilt on purpose; the platform changed around them. |
| Hardware and OS | Adding a node: install by hand at the console with a shared install password, add to the inventory, run make. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Build an installer stick, install, add to the inventory, run the host play with check-and-diff first. | changed | open | **Evidence:** Whole blank site proven 2026-11-10; joining one node to a live site not tried. **Why:** The shared install password is gone. |

### Cluster software

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Cluster software | Lightweight Kubernetes, three servers with embedded etcd, a floating address for the API. A virtual IP for the API was live from 2026-10-20. | Same distribution and shape, installed fresh. Flags go only in config files, because the installer once dropped a flag on upgrade. | kept | proven | **Evidence:** Six of six nodes Ready, three control-plane, read 2026-11-11. The floating API address has been in use since 2026-11-10; its pods restarted twice (cause not checked) and failover of the address is not tried. **Why:** I kept the shape and changed what ran on it. |
| Cluster software | Kubernetes upgrade was a playbook: etcd snapshot first, servers one at a time, then agents. Run once, 2026-10-21. | No job. By hand, node by node, snapshot first. Held for next quarter. | not rebuilt yet | open | **Evidence:** Read 2026-11-11: the play warns and does nothing. **Why:** V1.0 was better: the upgrade had a rehearsed script. My reason for skipping it: the nodes are fresh. |
| Cluster software | OS patching: unattended upgrades, reboots gated on a block list of alerts, a host scan, patch alerts. It had stopped silently five different ways, each with a test. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Nothing installs updates or reboots on a schedule. | not rebuilt yet | open | **Evidence:** Review finding open on 2026-11-11; stock behaviour on the six nodes not checked. **Why:** V1.0 was better, and it paid for it in five failures. I have not yet decided what to rebuild. |
| Cluster software | Bundled add-ons were left on; cluster DNS held at two replicas by an autoscaler and a disruption budget. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Bundled service load balancer and ingress turned off in favour of explicit ones; DNS keeps its autoscaler and budget; metrics server stays bundled. | changed | built | **Evidence:** Read from the site folder and the cluster, 2026-11-11. **Why:** Two writers for one object is a fault I have already seen; the replacements have a single owner each. |
| Cluster software | A pod network with no encryption between nodes; a policy controller ran but 0 policies were in force outside the GitOps namespace, because of a belief that was never tested (71 days). *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Encrypted node-to-node tunnel, policy controller enforcing, IPv4 only. These are first-install choices not yet defended. | changed | built | **Evidence:** Default-deny probe on 2026-11-10 blocked steady traffic after about 30 s. **Why:** Encryption at install is cheap; later it is a rebuild. |
| Cluster software | Cluster DNS ran with a measured 3 to 4 percent loss, fixed per pod, and a probe that measured it. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Bundled DNS with autoscaler. The probe and the per-pod fix are not carried. | not rebuilt yet | open | **Evidence:** Carry-over review 2026-11-08: both missing; the new reference app lacks the per-pod fix. **Why:** V1.0 was better: it could measure DNS loss. |

### Networking and ingress

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Networking and ingress | Ingress behind one small edge machine on a public tunnel service. A public name existed; an outside probe read 99.95 percent over 7 days on 2026-10-27. Public exposure was attacked on a schedule (exposure contracts, a template scanner, a pentest whose findings were fixed on 2026-11-01). | No public entrance and no public name. Ingress is reachable inside only. Nothing public exists to attack, so no exposure scan runs. | not rebuilt yet | planned | **Evidence:** Read 2026-11-11: no public path. The outside probe monitors were paused on 2026-11-10. **Why:** V1.0 was better: it had a real front door. My reason for waiting: nothing needs a front door yet. The 99.95 percent figure is a V1.0 note of 2026-10-27; I did not find the probe record itself in the old repository on 2026-11-11. |
| Networking and ingress | The ingress controller ran on the cluster. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Same controller, class-selected, behind the floating address, plain HTTP only. The certificate manager is installed but no certificate is issued from it. | kept | built | **Evidence:** Ingress and load-balancer Kustomizations applied, three certificate-manager pods Running, read 2026-11-11. **Why:** TLS and names are the open parts. A running controller with no certificate issued proves nothing. |
| Networking and ingress | V1.0 had working names from a LAN DNS service and mDNS host names. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | V2.0 has no names yet: the DNS plan for a home zone is not decided. Pods cannot use mDNS, so the backup store is addressed by IP, learned from a fault on 2026-11-10. | not rebuilt yet | open | **Evidence:** Decision register 2026-11-11, DNS plan row open. **Why:** V1.0 was better: names worked. A refusal in the bootstrap script now stops the same mistake. |
| Networking and ingress | One switch carried every etcd and storage host; one router held the DHCP reservations. Both accepted as single points. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Same switch, router and internet line, because the machines are the same. | kept | open | **Evidence:** Single-points register read 2026-11-11: 22 rows, 13 accepted, 9 open. **Why:** Nothing was fixed here; the 2026-11-08 review found the switch was missing from the register. |

### Storage and databases

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Storage and databases | Replicated block storage kept three copies of volumes across all six nodes. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Node-local volumes only. A volume dies with its machine; durability comes from three database instances on three nodes. | changed | built | **Evidence:** One default storage class, read back 2026-11-11. **Why:** V1.0 was better: a machine could die without losing a volume. Dropped as a reviewed trade, to keep the first site simple (my reason). |
| Storage and databases | Operator-managed PostgreSQL, 13 clusters on 2026-10-27, 8 healthy on 2026-11-10 after the old major version was retired; each app and service could have its own cluster, so one failure stayed in one place. | One cluster of three instances behind a pooler; its shape is enforced by a check. | changed | proven | **Evidence:** Cluster healthy, 3 of 3 ready, read 2026-11-11. **Why:** V1.0 was better on isolation: one cluster is one failure domain for every app that moves to it. My reason for one: only one app has moved. |
| Storage and databases | Quorum synchronous commit was read back on each primary on 2026-10-09, after I found it silently dropped for 23 days. | Asked for in the spec, but not read back; the failover-quorum safety check is off. | changed | built | **Evidence:** Spec read 2026-11-11; no primary has been asked. **Why:** V1.0 learned that a spec is not a reading. I have not asked. |
| Storage and databases | Major-version upgrade without downtime: a parallel cluster by logical replication, then a pause of the pooler; 87 to 142 s, no errors (2026-09). A guard failed when a successor did not mirror its predecessor. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | None. The new cluster starts on the current major, and no mirror guard exists. | not rebuilt yet | open | **Evidence:** Carry-over register: mechanism open, read 2026-11-11. **Why:** V1.0 was better: the procedure was scripted and measured. |
| Storage and databases | Push delivery, so nothing pruned database objects; the Flux handover was partial (12 of 17 Kustomizations suspended on 2026-11-08). | Prune is on for every Kustomization, including database objects. A path refactor could delete a database and its disk. | new | open | **Evidence:** Carry-over review finding, 2026-11-08; still a design risk on 2026-11-11. **Why:** The reconciler gives revert but takes away a safety net. |
| Storage and databases | Durable identity provider on its own replicated database. The apps signed people in on the provider's own page (authorization code with PKCE). *(V1.0, as of 2026-11-05 to 2026-11-10.)* | One pod in development mode on an in-memory database. Users and sessions do not survive a restart. A sign-in by an app through the new provider has not been shown. | changed | open | **Evidence:** Read 2026-11-10 and 2026-11-11. **Why:** V1.0 was better: users survived a restart. The placeholder is listed, not hidden. |

### Backup and restore

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Backup and restore | In-cluster object store plus a nightly mirror to a NAS: two copies. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | An S3-compatible store on one always-on Mac outside the cluster: one machine, one copy. Whether the NAS returns is open. | changed | open | **Evidence:** Nightly backup completed, read 2026-11-11. No second copy exists. **Why:** V1.0 was better: it survived the loss of one machine's disk. A store outage was found on 2026-11-08 to fill the database disk with logs; the finding is closed by a merge, a store-outage proof is still open. |
| Backup and restore | Weekly rotating restore drills of 8 databases. 3 of 8 passed on 2026-11-08. | One manual drill of one database, a few MB, about 60 s, passed on 2026-11-10. | changed | proven | **Evidence:** Restore from the store alone, 2026-11-10; a marker row and six tables came back. **Why:** V1.0 was better on coverage: it ran more drills, and only 3 of 8 databases passed. Not shown: real size, point in time, the scheduled backup. |
| Backup and restore | Backup of the registry and the signing keys on timers, each with a verifying check. The in-cluster registry also kept images available with no internet. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | The signing key has one local copy; a second home in a password manager is open. No registry to back up, and image pulls now need the internet. | not rebuilt yet | open | **Evidence:** Mechanisms open in the register, 2026-11-11. **Why:** V1.0 was better: keys had timed, checked backups and images did not depend on the internet. Key custody is still one disk. |
| Backup and restore | Rebuilding the platform from blank was never run before the teardown. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | One supervised bring-up from blank machines, about 4.5 hours merge to converged, three faults fixed on the way. | new | proven | **Evidence:** Bring-up record 2026-11-10; a second host-layer run changed nothing. **Why:** Not yet one command and not timed from power-on. |
| Backup and restore | RPO of zero was documented while the database was asynchronous. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | RPO and RTO numbers proposed in the decision record; none decided, none measured. | changed | open | **Evidence:** Decision register 2026-11-11, RPO/RTO row open. **Why:** The V1.0 claim was wrong for 23 days, so I do not repeat a number. |

### Identity

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Identity | Every cluster write came from one admin identity; the admin kubeconfig sat on the workstation and the deploy runner. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | No CI job holds a cluster credential. The admin kubeconfig remains on the workstation for emergencies. Tenant identities have no cluster rights. | changed | built | **Evidence:** Workflow read 2026-11-11; tenant identity proven on a local test cluster 2026-11-09. **Why:** No per-person cluster identity exists in either. |

### Secrets

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Secrets | Secrets in git encrypted with SOPS and age from 2026-10-25, applied by make targets; plaintext in the cluster. | SOPS and age, two recipients, applied by the cluster's own decryptor, one unit per namespace. | kept | proven | **Evidence:** Four secrets live, applied by the reconciler, 2026-11-10 to 2026-11-11. **Why:** The tool carried; the one-unit-per-namespace split came from a deadlock found on first bring-up. |
| Secrets | Key rotation was an open task and the recovery key had no safe second home. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Same: the recovery key is not yet off the workstation, a decrypt with the workstation off has not been tried, and the key itself has not been rotated. | kept | open | **Evidence:** Decision register row open, 2026-11-11. **Why:** Owed, by me. |
| Secrets | A signing key file sat on the deploy runner. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | The signing key is in an environment limited to the main branch; one local copy; rotated 2026-11-08. A plaintext Secret is refused by the publish step. | changed | built | **Evidence:** Environment settings and workflow read 2026-11-11. **Why:** A pull-request run could once read the key; that is closed. |

### Delivery

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Delivery | Push: a person or a runner holding admin credentials ran make (about 150 to 190 targets) and ansible (about 65 playbooks) at the cluster. A partial Flux handover had 12 of 17 Kustomizations suspended on 2026-11-08. | Pull for the cluster layer: merge, a hosted workflow publishes an OCI artifact, the reconciler in the cluster fetches it every 2 minutes, applies, prunes. No CI credential reaches the cluster. | changed | proven | **Evidence:** Pull proven 2026-11-10; six publish runs 2026-11-11 at 18 to 28 s. All 19 Kustomizations Ready on 2026-11-11 07:00 UTC (14 of 18 at 06:42 UTC, before the monitoring fix landed). **Why:** Drift is reverted, no deploy machine is needed and no credential sits in CI. |
| Delivery | A daily guard compared manifests and charts with the cluster and posted; it ran red every day from 2026-11-02 to 2026-11-09 unread. | The reconciler reverts a hand edit. No independent check for what git does not mention. | changed | proven | **Evidence:** Hand patches reverted within minutes on 2026-11-10 (by accident). **Why:** Revert is stronger than report. An unmanaged object is invisible to it. |
| Delivery | Operators and add-ons installed through Helm by make. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Installed once by a script from the workstation, outside the reconciler. Five bootstrap objects made by hand. | kept | built | **Evidence:** Ran once, 2026-11-10. **Why:** A dependency bump will reach the repository and never the cluster. Open as a design. |
| Delivery | Hosts changed by ansible from the workstation. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Same. A pull timer for hosts is decided but not built. | kept | planned | **Evidence:** Decision record accepted but not built, read 2026-11-11. **Why:** If built, a bad merge reaches every host within one interval. |
| Delivery | Roll back: undo the rollout or revert the pin and ship. A health gate with a canary was drilled but report-only in CD. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Git revert, merge, wait 3 to 10 minutes. No health-gated rollback; procedure never rehearsed. | changed | open | **Evidence:** Operations comparison 2026-11-11. **Why:** V1.0 was better: rollback was quick and drilled. |
| Delivery | Change and see in seconds with a direct apply. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Every change is a pull request and a gate of 10 to 33 minutes. Direct edits are reverted. | changed | proven | **Evidence:** First real pull request at home took 33 min 12 s, 2026-11-10. The local-cluster gate itself is flaky: last 30 runs 22 green, 5 red, 3 cancelled (2026-11-10); retries are in, counting them is open. **Why:** A slow loop is the cost of one door. Keeping direct work to the throwaway cluster. |
| Delivery | After a green build, CD wrote the new image reference back to the repository. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | A person reads the signed digest and opens a second pull request. Nothing orders digests. | changed | open | **Evidence:** Operations comparison 2026-11-11, open question 1. **Why:** V1.0 was better. The owner of this step is not named. |
| Delivery | A guard refused to deploy an older build. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Image tags are commit hashes that cannot be ordered, so the guard is not built. | not rebuilt yet | open | **Evidence:** Operations comparison 2026-11-11. **Why:** V1.0 was better: it prevented the stale-checkout rollback of 2026-10-21. |
| Delivery | Images came from an in-cluster registry with its own backup. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | A hosted registry. The in-cluster one was dropped. | dropped | proven | **Evidence:** Image and artifact pulls worked, 2026-11-10 to 2026-11-11. **Why:** V1.0 was better on independence: its registry needed no internet and had its own backup. V2.0 has fewer things to run but depends on the hosted registry being reachable. |
| Delivery | The deliverable was a signed image. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | The artifact the reconciler pulls is unsigned and read through a moving tag. Whoever can write that package can change the cluster. | new | open | **Evidence:** Source read 2026-11-11: no verification set. **Why:** The largest risk of the pull model. |
| Delivery | Maintenance mode: make targets started and ended a maintenance window, silenced alerts and recorded a reason. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | None, since no alert exists to silence. A suspended Kustomization during an incident must be recorded by hand. | not rebuilt yet | open | **Evidence:** Runbook written, never rehearsed on the home site, 2026-11-11. **Why:** V1.0 was better. It comes back with alerts. |

### CI and runners

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| CI and runners | Self-hosted Mac runners holding the admin kubeconfig, SSH to the control plane and the signing key; hard resets, a full disk, a locked keychain. Hosted CI was cut in August 2026 by a billing gap. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Hosted runners for anything holding a key. Secret-free heavy jobs run on a fresh VM per job on two old Ubuntu desktops at home. The Mac runners were retired on 2026-11-10. | changed | proven | **Evidence:** First real gate at home 2026-11-10; both builders took jobs in parallel 2026-11-11, gates started not passed. **Why:** Smaller blast radius from a stolen runner token. |
| CI and runners | Almost all CI on my own machines from 2026-08-26. | Included hosted minutes ran out on 2026-11-09. A $20 budget is being spent, about $0.15 per hosted gate. | changed | proven | **Evidence:** Budget runbook and tally, 2026-11-09 to 2026-11-10. **Why:** V1.0 was better on cost. The home path is built to save it; saving not measured. |
| CI and runners | Private repo on the free plan: nothing enforceable. 112 of 133 commits had a pull request by 2026-10-27. | Main protected: pull request, two required checks, linear history, no force push, admins bound. 0 approvals required. 76 of the first 77 commits through a pull request. | changed | built | **Evidence:** Setting read back 2026-11-11; protection on main itself never tested. **Why:** The aggregate gate is not required yet: a cancelled red run beat a green re-run in a test. |

### Admission and security policy

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Admission and security policy | No admission control. First-party images were checked by scripts: 6 of 7 verified on 2026-10-27. | Vendor images only from a closed, digest-pinned list, enforced in refuse mode by a validating admission policy. | new | proven | **Evidence:** One real refusal of an off-list image on 2026-11-10; the policy is Ready, read 2026-11-11 07:00 UTC. **Why:** A list I wrote is only as good as its upkeep. |
| Admission and security policy | Same: signatures on first-party images were checked by scripts, not by the cluster. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Own images need the CI signature, enforced by an image-validating admission policy in refuse mode. | new | built | **Evidence:** The policy is Ready, read 2026-11-11 07:00 UTC. The signature check on the home site is not on record, only on a test cluster. **Why:** Built is the honest word until a signed image is admitted and an unsigned one refused here. |
| Admission and security policy | Network policies absent outside one namespace. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Default-deny in the four tenant namespaces and a tenant pack of quotas and rules. | new | built | **Evidence:** Probe 2026-11-10 failed: a new pod is open for about 1 to 3 s. Ingress denial and DNS egress not tested. **Why:** A clean stop of the admission engine fails open; nothing alerts on it. |
| Admission and security policy | Nightly SBOM scans, a vulnerability tracker with triage, host and edge scans. 61 third-party images scanned. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | None. No tracker, no SBOM job, no host scan. | not rebuilt yet | planned | **Evidence:** Compliance page, 2026-11-11. **Why:** V1.0 was better. Triage and the security response process were barely carried (2026-11-08 review). |
| Admission and security policy | Kubernetes API audit log at metadata level to a log store. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Not configured. | not rebuilt yet | open | **Evidence:** Operations comparison 2026-11-11. **Why:** V1.0 was better, though every write looked like one admin. |
| Admission and security policy | Secret scanning at commit and by sweeps. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Pre-commit scan of the full history; 62 hooks run locally and again in CI. | kept | built | **Evidence:** Hooks counted 2026-11-11. **Why:** No evidence a leaked value has not reached a history. |

### Observability and alerting

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Observability and alerting | 124 of 124 scrape targets, 227 rules (78 written in the repo), 31 dashboards on 2026-10-27 (V1.0 owner notes; I did not find the probe record in the old repository on 2026-11-11); 257 alerts counted in the V1.0 incident register capture of 2026-11-08. | Written as plain manifests, 12 rule tests pass offline. Applied on 2026-11-11, with 18 of 18 targets up and 12 alert rules when read: metrics, alert manager, dashboard and state-metrics pods Running (about nine minutes old at 07:00 UTC) and the node exporter on all six machines. 0 of 257 alerts carried over. | changed | built | **Evidence:** First live run failed on a missing namespace 2026-11-10 to 2026-11-11 (14 of 18 Kustomizations Ready at 06:42 UTC); the one-line fix landed and all 18 were Ready at 07:00 UTC. Read the same day: 18 of 18 scrape targets up, 12 alert rules, no dashboards, about an hour of history; no alert is known to reach a person. **Why:** V1.0 was better: 124 targets, 227 rules, 31 dashboards and a long history, against 18 targets, 12 rules, no dashboards and an hour. Running pods alone would not notice a failure. |
| Observability and alerting | Alerts went to chat, a dead-man heartbeat, and a small model answered them. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Chat is a window: no acknowledgement, no escalation. Nothing reaches a person. | changed | open | **Evidence:** Owner decision open since 2026-11-07. **Why:** V1.0 was better. |
| Observability and alerting | Outside monitors graded the public endpoint and scheduled jobs. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | None; paused 2026-11-10. | not rebuilt yet | planned | **Evidence:** No monitors, 2026-11-11. **Why:** V1.0 was better. The status page now says not measured yet. |
| Observability and alerting | A log store with its own alert rules, and 31 dashboards. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | No logs, no dashboards. Git is the list of what runs. | not rebuilt yet | planned | **Evidence:** Read 2026-11-11. **Why:** V1.0 was better. The pull model is quiet when it breaks; logs and alerts matter more. |
| Observability and alerting | Fault injection ran hourly on weekdays until it stopped on 2026-10-13, with a synthetic load generator. | Neither on V2.0. One tracing pod runs; no trace read. | not rebuilt yet | planned | **Evidence:** Read 2026-11-11. **Why:** V1.0 was better: it had fault injection and load. Without load nothing can be called stable. |
| Observability and alerting | Seeing what ran: make verify, make endpoints, Grafana, a container manager UI, a console and a portal. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Git is the list. flux get and kubectl get are the readers. No UI; the portal and console are proposed for retirement, owner undecided. | changed | proven | **Evidence:** Read 2026-11-11. **Why:** A person must know the commands; V1.0 had more places to look. |

### AI ops agent

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| AI ops agent | A small local model in chat answered questions, wrote a digest and proposed fixes. An allowlist and a click decided. A cloud model graded its posts. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | None. The local model is not part of V2.0. No alert feeds an agent. | not rebuilt yet | planned | **Evidence:** The reviewer agent has no account yet (2026-11-11). **Why:** V1.0 was better: its quality loop found inflated severity in its first 96 summaries (2026-10-26). |
| AI ops agent | V1.0 had a cloud model as my engineering peer on every repository. *(As of 2026-11-05 to 2026-11-10.)* | Same, held to the same checks. All 101 commits carry the AI co-author line. | kept | proven | **Evidence:** Counted 2026-11-11. **Why:** Review approvals are 0; the merge-approval scheme is Proposed. |

### Apps

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Apps | Six apps at 2 of 2 replicas with synthetic load, plus a satellite app from another repository. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | One reference app (3 database instances, pods Running). The other two clients not moved, the satellite not redeployed. | changed | proven | **Evidence:** 7 pods Running in its namespace, 2026-11-11. **Why:** V1.0 was better: six apps with synthetic load exercised more than one app with none. My reason for one: I moved the smallest first. The three Flutter clients are unchanged and none is in an app store. |
| Apps | The app framework was at the previous major. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Current major with contract fuzzing: eight faults found in the first run. | changed | proven | **Evidence:** Fuzz run 2026-11-07 to 2026-11-08; one more fault open 2026-11-11. **Why:** The app standard has not met a hard case. |

### 3D printing and embedded

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| 3D printing and embedded | Printing as source, OpenSCAD and Python. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Unchanged. The preview gallery pod on V1.0 is gone. | kept | - | **Evidence:** Parts list dated 2026-10-27; newer frame, plate and marker holder not listed. **Why:** Mechanical work is outside the cluster. |
| 3D printing and embedded | Signed A/B over-the-air updates for a Pi with a bill of materials. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Unchanged. The tracker it fed was inside V1.0 and is gone. A new one is planned. | kept | planned | **Evidence:** Yocto page, 2026-11-11. **Why:** The heartbeat from devices to the cluster is also planned. |

### Process

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Process | V1.0 had 42 decision records (41 counted on 2026-10-27; 42 files, numbered 0000 to 0041, in the old repository on 2026-11-11) and 113 incident records kept in a register (V1.0 incident register, 2026-11-05). | 13 decision records: 3 accepted, 10 proposed. A decision register. | changed | built | **Evidence:** Read 2026-11-11. **Why:** Several proposed records already run things. |
| Process | A maturity ladder, a radar of 3.47 (V1.0 platform recap, snapshot 2026-08-06), 7 of 13 failure domains. | 11 objectives, 109 rules: 3 built, 19 partly, 87 not. The quarter's page is a Draft with no start date. | changed | open | **Evidence:** Move review 2026-11-10 and decision register 2026-11-11. **Why:** Count did not change across the last forty commits. |
| Process | V1.0 had lessons from 113 incident records (V1.0 incident register, 2026-11-05). | All 113 are in a lessons file by failure class. 0 of 257 alerts, 0 of 74 mechanisms, 0 of 16 proofs carried. 72 of 188 findings closed. | changed | open | **Evidence:** Carry-over register, 2026-11-11. **Why:** Closed means a rule is written, not that something acts. |
| Process | Learnings in session notes outside the repository. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Learnings must be in the same pull request. 35 run records, 26 pass, 9 fail, never edited. | changed | built | **Evidence:** Records counted 2026-11-11; counting files shows the habit exists, not that it changes what I do. **Why:** Red records are kept. |

### Cost and power

| Area | V1.0 | V2.0 | Change | V2.0 status | Evidence and why |
|---|---|---|---|---|---|
| Cost and power | Retired hardware, free licences. *(V1.0, as of 2026-11-05 to 2026-11-10.)* | Same. | kept | - | **Evidence:** Index page, 2026-11-11. **Why:** Constraint kept. |
| Cost and power | One measured saving of 13.1 W from fixing the frequency governor on the two busiest nodes (2026-10). | Not re-measured. No power figure claimed. | not rebuilt yet | open | **Evidence:** Read 2026-11-11. **Why:** V1.0 was better: energy was measured, not estimated. The 13.1 W figure is from the V1.0 incident register of 2026-11-05. |

## What V1.0 did better

I count 30 rows where my own note says V1.0 was better, by the words "V1.0 was better" in the row's last column. This list is cut by that judgement; the next list is cut by change type (rows V2.0 does not rebuild yet), so they overlap but differ: a row can be rebuilt differently and still worse, and a row can be missing without V1.0 having been better at it.

- **Hardware and OS.** V1.0 stayed up as the working reference until 2026-11-10. Its own daily guards had been red every day from 2026-11-02 to 2026-11-09 and nobody read them. *(V2.0: proven)*
- **Hardware and OS.** Hard power-off drills existed as a make target, after one real mains cut on 2026-08-20 took two of three servers down for 9 min 12 s. Each control-plane machine's battery, power path, wake-on-LAN limit and disk class were recorded after that incident. *(V2.0: open)*
- **Cluster software.** Kubernetes upgrade was a playbook: etcd snapshot first, servers one at a time, then agents. Run once, 2026-10-21. *(V2.0: open)*
- **Cluster software.** OS patching: unattended upgrades, reboots gated on a block list of alerts, a host scan, patch alerts. It had stopped silently five different ways, each with a test. *(V2.0: open)*
- **Cluster software.** Cluster DNS ran with a measured 3 to 4 percent loss, fixed per pod, and a probe that measured it. *(V2.0: open)*
- **Networking and ingress.** Ingress behind one small edge machine on a public tunnel service. A public name existed; an outside probe read 99.95 percent over 7 days on 2026-10-27. Public exposure was attacked on a schedule (exposure contracts, a template scanner, a pentest whose findings were fixed on 2026-11-01). *(V2.0: planned)*
- **Networking and ingress.** V1.0 had working names from a LAN DNS service and mDNS host names. *(V2.0: open)*
- **Storage and databases.** Replicated block storage kept three copies of volumes across all six nodes. *(V2.0: built)*
- **Storage and databases.** Operator-managed PostgreSQL, 13 clusters on 2026-10-27, 8 healthy on 2026-11-10 after the old major version was retired; each app and service could have its own cluster, so one failure stayed in one place. *(V2.0: proven)*
- **Storage and databases.** Major-version upgrade without downtime: a parallel cluster by logical replication, then a pause of the pooler; 87 to 142 s, no errors (2026-09). A guard failed when a successor did not mirror its predecessor. *(V2.0: open)*
- **Storage and databases.** Durable identity provider on its own replicated database. The apps signed people in on the provider's own page (authorization code with PKCE). *(V2.0: open)*
- **Backup and restore.** In-cluster object store plus a nightly mirror to a NAS: two copies. *(V2.0: open)*
- **Backup and restore.** Weekly rotating restore drills of 8 databases. 3 of 8 passed on 2026-11-08. *(V2.0: proven)*
- **Backup and restore.** Backup of the registry and the signing keys on timers, each with a verifying check. The in-cluster registry also kept images available with no internet. *(V2.0: open)*
- **Delivery.** Roll back: undo the rollout or revert the pin and ship. A health gate with a canary was drilled but report-only in CD. *(V2.0: open)*
- **Delivery.** After a green build, CD wrote the new image reference back to the repository. *(V2.0: open)*
- **Delivery.** A guard refused to deploy an older build. *(V2.0: open)*
- **Delivery.** Images came from an in-cluster registry with its own backup. *(V2.0: proven)*
- **Delivery.** Maintenance mode: make targets started and ended a maintenance window, silenced alerts and recorded a reason. *(V2.0: open)*
- **CI and runners.** Almost all CI on my own machines from 2026-08-26. *(V2.0: proven)*
- **Admission and security policy.** Nightly SBOM scans, a vulnerability tracker with triage, host and edge scans. 61 third-party images scanned. *(V2.0: planned)*
- **Admission and security policy.** Kubernetes API audit log at metadata level to a log store. *(V2.0: open)*
- **Observability and alerting.** 124 of 124 scrape targets, 227 rules (78 written in the repo), 31 dashboards on 2026-10-27 (V1.0 owner notes; I did not find the probe record in the old repository on 2026-11-11); 257 alerts counted in the V1.0 incident register capture of 2026-11-08. *(V2.0: built)*
- **Observability and alerting.** Alerts went to chat, a dead-man heartbeat, and a small model answered them. *(V2.0: open)*
- **Observability and alerting.** Outside monitors graded the public endpoint and scheduled jobs. *(V2.0: planned)*
- **Observability and alerting.** A log store with its own alert rules, and 31 dashboards. *(V2.0: planned)*
- **Observability and alerting.** Fault injection ran hourly on weekdays until it stopped on 2026-10-13, with a synthetic load generator. *(V2.0: planned)*
- **AI ops agent.** A small local model in chat answered questions, wrote a digest and proposed fixes. An allowlist and a click decided. A cloud model graded its posts. *(V2.0: planned)*
- **Apps.** Six apps at 2 of 2 replicas with synthetic load, plus a satellite app from another repository. *(V2.0: proven)*
- **Cost and power.** One measured saving of 13.1 W from fixing the frequency governor on the two busiest nodes (2026-10). *(V2.0: open)*

The live comparison itself belongs on that list. I tore V1.0 down before V2.0 passed its gates, so the comparisons on this page rest on notes and dated readings, and the outside-tool baseline I wanted before the wipe was never filed.

## Not rebuilt yet

V1.0 had these and V2.0 does not, on 2026-11-11 (17 rows). Each keeps the status word it has in the table above.

- **Hardware and OS.** Hard power-off drills existed as a make target, after one real mains cut on 2026-08-20 took two of three servers down for 9 min 12 s. Each control-plane machine's battery, power path, wake-on-LAN limit and disk class were recorded after that incident. *(V2.0: open)*
- **Cluster software.** Kubernetes upgrade was a playbook: etcd snapshot first, servers one at a time, then agents. Run once, 2026-10-21. *(V2.0: open)*
- **Cluster software.** OS patching: unattended upgrades, reboots gated on a block list of alerts, a host scan, patch alerts. It had stopped silently five different ways, each with a test. *(V2.0: open)*
- **Cluster software.** Cluster DNS ran with a measured 3 to 4 percent loss, fixed per pod, and a probe that measured it. *(V2.0: open)*
- **Networking and ingress.** Ingress behind one small edge machine on a public tunnel service. A public name existed; an outside probe read 99.95 percent over 7 days on 2026-10-27. Public exposure was attacked on a schedule (exposure contracts, a template scanner, a pentest whose findings were fixed on 2026-11-01). *(V2.0: planned)*
- **Networking and ingress.** V1.0 had working names from a LAN DNS service and mDNS host names. *(V2.0: open)*
- **Storage and databases.** Major-version upgrade without downtime: a parallel cluster by logical replication, then a pause of the pooler; 87 to 142 s, no errors (2026-09). A guard failed when a successor did not mirror its predecessor. *(V2.0: open)*
- **Backup and restore.** Backup of the registry and the signing keys on timers, each with a verifying check. The in-cluster registry also kept images available with no internet. *(V2.0: open)*
- **Delivery.** A guard refused to deploy an older build. *(V2.0: open)*
- **Delivery.** Maintenance mode: make targets started and ended a maintenance window, silenced alerts and recorded a reason. *(V2.0: open)*
- **Admission and security policy.** Nightly SBOM scans, a vulnerability tracker with triage, host and edge scans. 61 third-party images scanned. *(V2.0: planned)*
- **Admission and security policy.** Kubernetes API audit log at metadata level to a log store. *(V2.0: open)*
- **Observability and alerting.** Outside monitors graded the public endpoint and scheduled jobs. *(V2.0: planned)*
- **Observability and alerting.** A log store with its own alert rules, and 31 dashboards. *(V2.0: planned)*
- **Observability and alerting.** Fault injection ran hourly on weekdays until it stopped on 2026-10-13, with a synthetic load generator. *(V2.0: planned)*
- **AI ops agent.** A small local model in chat answered questions, wrote a digest and proposed fixes. An allowlist and a click decided. A cloud model graded its posts. *(V2.0: planned)*
- **Cost and power.** One measured saving of 13.1 W from fixing the frequency governor on the two busiest nodes (2026-10). *(V2.0: open)*

Related pages: [the estate](index.html), [status](status.html), [how we work](how-we-work.html), [what I'd do differently](lessons.html).
