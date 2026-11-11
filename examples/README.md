# Examples — four things worth stealing

**Previous platform records, as of 2026-11-11.** The four examples were extracted from the
previous platform's running system, a six-node bare-metal Kubernetes platform that ran until it
was torn down on 2026-11-10. They are scrubbed of hostnames and addresses and kept as close to the
deployed version as scrubbing allows. Each one exists because something looked correct and was not.

What still applies, as read on 2026-11-11:

- **The reboot-daemon example (`kured-args.yaml`)** describes a component that does not run on the
  new cluster. No reboot daemon pod runs there (checked 2026-11-11); the host baseline still lists
  one as a rule, not yet built.
- **The alert-rule example (`duty-cycle-alert.yaml`)** is a rule for the Prometheus operator, which
  is not installed on the new cluster. Monitoring there is merged (2026-11-11) but not running, so no
  rule is evaluated. The idea (a metric that sawtooths across its threshold) is independent of the
  tool.
- **The host-level timer example (`systemd-oneshot-timer.md`)** still applies. The new platform's
  host layer ships a daily disk-wear timer paired with a `Type=oneshot` service. I read the service template on 2026-11-11: it
  does not set `RemainAfterExit`, so it avoids the trap the example documents; I have not shown the
  timer firing on the hosts (not measured yet).
- **The scanner example (`trivy-kernel-ab-split.sh`)** is about host scanning, not the cluster. I
  have not re-run it against the new hosts (not measured yet).

They are here because [the site](https://schultzzznet.github.io/schultzzznet/)
describes these mechanisms in prose, and prose is not a thing you can run.

| File | The bug it exists because of | Steal it if |
|---|---|---|
| [`trivy-kernel-ab-split.sh`](trivy-kernel-ab-split.sh) | A fully-patched host still reported ~1,800 findings, forever | You scan host filesystems with Trivy and the count never reaches zero |
| [`duty-cycle-alert.yaml`](duty-cycle-alert.yaml) | A node sat 23% of every day above 90 °C and no alert ever fired | You have a metric that sawtooths across its threshold |
| [`kured-args.yaml`](kured-args.yaml) | The reboot daemon read a path inside its own container and concluded, hourly, that nothing needed rebooting | You run kured, or any drain-and-reboot coordinator |
| [`systemd-oneshot-timer.md`](systemd-oneshot-timer.md) | A timer fired exactly once per boot instead of every five minutes | You pair a `Type=oneshot` service with a `.timer` |

---

## Licence

MIT. No warranty, and none of these are a substitute for understanding the
system you are pointing them at.

## A caveat worth reading first

These were extracted from a working system, not written as a library. They carry
the assumptions of the place they came from, as of their extraction (the previous platform,
until 2026-11-10): Ubuntu hosts, k3s, a Prometheus Operator install. Read them before running them; the comments explaining *why*
are the valuable part, not the code.
