# Examples — four things worth stealing

Extracted from a running seven-node bare-metal Kubernetes platform, scrubbed of
hostnames and addresses, and kept as close to the deployed version as scrubbing
allows. Each one exists because something looked correct and was not.

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
the assumptions of the place they came from — Ubuntu hosts, k3s, a Prometheus
Operator install. Read them before running them; the comments explaining *why*
are the valuable part, not the code.
