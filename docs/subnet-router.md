---
title: A remote subnet router — an old NAS replaced by a Pi
tldr_what: "A runbook for replacing an old NAS whose only job is to route a remote site into the tailnet with a Raspberry Pi: first on stock Debian, then on the estate's own Yocto image with signed A/B updates. The site's internet is Starlink."
tldr_why: "A box nobody visits for weeks is where an A/B update with rollback pays off, and where its blind spot hurts most: an update that boots fine but breaks the tunnel strands the site, and nothing rolls back."
tldr_use: "The steps for a Tailscale subnet router behind Starlink's carrier-grade NAT, a Yocto recipe and units that keep the node's identity off the A/B slots, and a switch-over that never leaves the site unreachable."
reread: 2026-11-28
body_read: 2026-11-28
summary:
  - "**What it is:** a plan, not a build (2026-11-28). An old NAS at a remote site does one job, advertising the site's LAN into the tailnet. A Raspberry Pi can do it for a fraction of the power, on software that still gets updates."
  - "**Two paths:** stock Debian on a Pi 4 or 5 (an afternoon, and the fall-back), or the estate's own Yocto image with Tailscale added, a read-only root and signed A/B updates."
  - "**Starlink:** the router can't run Tailscale and has little LAN configuration, and IPv4 sits behind carrier-grade NAT. None of that blocks a subnet router: Tailscale connects outward, and source NAT means the LAN needs no return route."
  - "**The design rule:** the node's identity lives on the data partition, not in a slot, and a slot is marked good only once the tunnel is up. Otherwise an update that boots but breaks Tailscale cuts the site off with no rollback."
  - "**The switch-over:** run the Pi beside the NAS, both advertising the same route, and retire the NAS only after the Pi has carried the site alone through a power cut and an update."
---

# A remote subnet router: an old NAS replaced by a Pi

{% include tldr.html %}

{% include in-short.html %}

**Status, 2026-11-28: planned. Nothing is bought, built or running.** Every step below is
written to be done, not reported as done. When a step has been done on hardware, it gets a
date here, the same way as everywhere else on this site.

## Why replace it

The remote site has an old NAS whose only job is to be a Tailscale *subnet router*: it
advertises the site's LAN into the tailnet, so the devices there can be reached from anywhere
without running Tailscale on each of them. It does that job, but:

- **It is old.** Its operating system is at or near the end of its updates, and the Tailscale
  package for it lags behind upstream. This is the box that faces the internet.
- **It is oversized.** A NAS spins up disks and draws roughly 15–30 W to forward packets. A Pi
  draws about 3–5 W.
- **It is a single point.** If it fails, the site is gone until someone travels there.

A subnet router is one of the lightest jobs there is: WireGuard plus forwarding. The site's
uplink (Starlink) is slower than what a Pi 4 or 5 can push through the tunnel, so the board is not
the limit. A Pi 3 B+, the board the [Yocto image](yocto.html) targets, is a different case: its
Ethernet sits behind USB 2.0 and its cores are slow for WireGuard. Expect it to be the bottleneck
at well under 100 Mbit/s. That is plenty for remote access to the devices at the site and poor for
moving large files.

## The network: Starlink

```
  tailnet ──(outbound UDP, NAT traversal or a relay)── Starlink dish/router ── site LAN
                                                                 │
                                                        Pi (subnet router) ── the devices
```

What Starlink changes, and what it doesn't:

- **The Starlink router can't run Tailscale.** It has no packages and little LAN configuration
  in the app. So the router must be a separate box on the LAN, which is the plan anyway.
- **IPv4 is behind carrier-grade NAT,** so nothing reaches the site inbound and port forwarding
  is not an option. Tailscale doesn't need it: the Pi connects outward and uses NAT traversal.
  When traversal fails, traffic goes through Tailscale's relays (DERP). That is slower but still
  works. Run `tailscale netcheck` and `tailscale ping` from the Pi to see which you get. Starlink
  also hands out public IPv6, which can give a direct path to peers that have IPv6 too.
- **The LAN needs no return route.** By default a Linux subnet router source-NATs the traffic it
  forwards, so to a device at the site, a remote connection looks like it comes from the Pi. That
  matters here because the Starlink router can't hold a static route. Keep source NAT on (the
  default; never pass `--snat-subnet-routes=false`).
- **The Pi doesn't need a fixed LAN address.** It only connects outward, so a DHCP lease is
  enough.
- **It needs a wired port.** Use Ethernet, not Wi-Fi. Which Starlink router is at the site
  decides how: recent routers have Ethernet ports, an older one needs Starlink's Ethernet adapter,
  and the Mini's built-in router has no port at all. Check before buying anything.
- **Expect short outages.** The dish reboots now and then for firmware updates and drops out in
  bad weather. Tailscale reconnects by itself. Don't build alerts that page on a two-minute gap.
- **Don't use bypass mode.** It turns off the Starlink router's Wi-Fi and gains nothing for this
  job.
- **On the router itself,** pass `--accept-dns=false` so the Pi keeps resolving through the local
  network.

## Path A: stock Debian (the baseline, and the fall-back)

On a Pi 4 or 5 with Raspberry Pi OS Lite (64-bit), booting from a USB SSD (or NVMe on a Pi 5)
rather than an SD card:

```sh
curl -fsSL https://tailscale.com/install.sh | sh

printf 'net.ipv4.ip_forward = 1\nnet.ipv6.conf.all.forwarding = 1\n' |
  sudo tee /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf

sudo tailscale up \
  --advertise-routes=<site-lan-cidr> \
  --advertise-tags=tag:subnet-router \
  --accept-dns=false
```

Then:

1. In the admin console, approve the route. With the policy below this happens automatically.
   A tagged node also has key expiry turned off. An untagged one doesn't, and would drop off the
   tailnet after 180 days.
2. Turn on `unattended-upgrades`. Tailscale's apt repository is covered once it is listed in the
   allowed origins.
3. Turn on the hardware watchdog: set `RuntimeWatchdogSec=15` in `/etc/systemd/system.conf`.
4. On a Pi 4 or 5, apply Tailscale's recommended UDP offload setting for Linux subnet routers
   (`ethtool -K eth0 rx-udp-gro-forwarding on rx-gro-list off`, made persistent with a
   networkd-dispatcher or udev hook).
5. Use the official power supply. Undervoltage causes most of the strange faults on a Pi.

The policy that tags the router and auto-approves its route (tailnet policy file):

```jsonc
{
  "tagOwners":     { "tag:subnet-router": ["autogroup:admin"] },
  "autoApprovers": { "routes": { "<site-lan-cidr>": ["tag:subnet-router"] } }
}
```

Path A is done in an afternoon and needs nothing from the rest of the estate. That is why it is
the fall-back. If path B isn't ready by the time the NAS has to go, path A goes in.

## Path B: the estate's own Yocto image

The [embedded image](yocto.html) already has what an unvisited box wants: a read-only squashfs
root, a separate data partition, signed A/B updates and a bootloader that falls back to the other
slot by itself. Turning it into a subnet router means adding one recipe, a kernel fragment and two
units. What follows is the design; none of it is in the layer yet.

### The rule that matters: identity on the data partition

A Tailscale node *is* its state file: the machine key, the node key, and its settings (the
advertised routes and tags). The October work on the test rig found that every freshly installed
slot generates its own SSH host keys
([the embedded page](yocto.html#the-same-path-on-a-different-machine-october-2026)). If Tailscale's
state lived in the slot, every update would show up in the tailnet as a new, unapproved machine,
which would cut the site off with every update. So the state goes on the data partition, which no
update touches:

```ini
# tailscaled.service (installed by the recipe; /data is wherever the layer mounts its data partition)
[Unit]
Description=Tailscale node agent
Wants=network-pre.target
After=network-pre.target systemd-networkd.service
RequiresMountsFor=/data

[Service]
Type=notify
RuntimeDirectory=tailscale
ExecStart=/usr/sbin/tailscaled --statedir=/data/tailscale --socket=/run/tailscale/tailscaled.sock --port=41641
ExecStopPost=/usr/sbin/tailscaled --cleanup
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### First join without baking a key into the image

An auth key in the image would end up in every bundle and on the artefact server. Instead,
enrolment is a one-shot unit that runs only if a key file is present on the data partition. You
put the key there once, by hand, over the LAN or by writing to the SD card. The unit then deletes
it. After that, the state file carries the node's identity and settings through every update.

```ini
# tailscale-enroll.service
[Unit]
Description=Join the tailnet once, from a key left on the data partition
After=tailscaled.service
Requires=tailscaled.service
ConditionPathExists=/data/tailscale/enroll.key

[Service]
Type=oneshot
EnvironmentFile=/data/tailscale/enroll.conf
ExecStart=/usr/bin/tailscale up --auth-key=file:/data/tailscale/enroll.key \
  --advertise-routes=${ROUTES} --advertise-tags=tag:subnet-router --accept-dns=false
ExecStartPost=/bin/rm -f /data/tailscale/enroll.key

[Install]
WantedBy=multi-user.target
```

`enroll.conf` holds one line, `ROUTES=<site-lan-cidr>`, so the image says nothing about which site
it is for. Use a pre-approved, tagged, single-use key: a key that is leaked after first use is then
worth nothing.

### The recipe

The simplest recipe that works packages Tailscale's static release binaries, which are pinned by
version and checksum, like every other input to the layer. It is sketched for the 64-bit build.
For a 32-bit build, use the `arm` tarball and its checksum.

```bitbake
# recipes-connectivity/tailscale/tailscale_<version>.bb
SUMMARY = "Tailscale node agent and CLI, from the static release binaries"
HOMEPAGE = "https://tailscale.com"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/BSD-3-Clause;md5=<checksum of the common licence file>"

SRC_URI = "https://pkgs.tailscale.com/stable/tailscale_${PV}_arm64.tgz;subdir=ts \
           file://tailscaled.service \
           file://tailscale-enroll.service \
           file://90-subnet-router.conf"
SRC_URI[sha256sum] = "<from pkgs.tailscale.com, checked by hand when the version is bumped>"
COMPATIBLE_HOST = "aarch64.*-linux"

S = "${UNPACKDIR}/ts/tailscale_${PV}_arm64"

inherit systemd
SYSTEMD_SERVICE:${PN} = "tailscaled.service tailscale-enroll.service"

do_install() {
    install -Dm0755 ${S}/tailscaled ${D}${sbindir}/tailscaled
    install -Dm0755 ${S}/tailscale  ${D}${bindir}/tailscale
    install -Dm0644 ${UNPACKDIR}/tailscaled.service        ${D}${systemd_system_unitdir}/tailscaled.service
    install -Dm0644 ${UNPACKDIR}/tailscale-enroll.service  ${D}${systemd_system_unitdir}/tailscale-enroll.service
    # forwarding on; read-only root is fine, sysctl.d is read at boot
    install -Dm0644 ${UNPACKDIR}/90-subnet-router.conf     ${D}${sysconfdir}/sysctl.d/90-subnet-router.conf
}

# Prebuilt Go binaries: already stripped, not linked with the distro's flags.
INSANE_SKIP:${PN} = "already-stripped ldflags"
RDEPENDS:${PN} = "iptables"
```

And a kernel fragment, `tailscale.cfg`, for the TUN device and the netfilter pieces that the
forwarding and source NAT use:

```
CONFIG_TUN=y
CONFIG_NETFILTER=y
CONFIG_NF_CONNTRACK=y
CONFIG_NF_NAT=y
CONFIG_IP_NF_IPTABLES=y
CONFIG_IP_NF_FILTER=y
CONFIG_IP_NF_NAT=y
CONFIG_IP_NF_TARGET_MASQUERADE=y
```

Two things to check before trusting this:

- **Size.** The two static binaries add tens of megabytes. Each slot has a hard ceiling, and the
  embedded page records a 224 MB runtime that didn't fit a 213 MB slot. Measure the image before
  and after. If it doesn't fit, build from source with Tailscale's build tags for a smaller,
  combined binary, at the cost of a Go toolchain in the build.
- **The kernel goes with the slot, the boot partition doesn't.** The embedded page's lesson
  applies directly: the boot partition is shared and isn't part of an update. So the first image
  with this fragment is a re-flash, not an over-the-air update.

### Marking a slot good: the tunnel is the health check

This is the part that the A/B design gets wrong for this job unless it is changed on purpose. The
bootloader falls back when a boot *fails*. An update that boots cleanly but breaks Tailscale (a
bad unit, a missing kernel option, state that can't be read) is a successful boot. The slot is
marked good, and the site is cut off, with no rollback and nobody there.

So for this image, the unit that marks the slot good must wait for the tunnel: `tailscale status`
reports the node as running, and a peer elsewhere in the tailnet answers `tailscale ping`. If that
doesn't happen within a few minutes, the unit doesn't mark the slot good and reboots, the
bootloader counts down that slot's attempts, and the old slot comes back.

The other half is power. The [October rig](yocto.html#the-same-path-on-a-different-machine-october-2026)
used up a slot's three boot attempts through power cuts during boot, and fell back by itself. At a
site with unreliable power, that is a real risk, so two things must be known before the box is
left there:

- what the bootloader does when *both* slots run out of attempts;
- whether the health check above adds enough time to boot to make that more likely.

Test both by pulling the plug, not by reasoning about them.

### Updates over the tunnel

Once it is running, updates reach the Pi the same way as on the rig: a signed bundle, streamed onto
the inactive slot, this time over the tailnet. With the health check above, a bad bundle comes back
on its own. Without it, path A's plain package updates are the safer choice.

Two more notes:

- **The clock.** The board has no battery-backed clock, so right after boot TLS fails with
  "certificate is not yet valid" until the time is synced. Tailscale retries until it is. Make the
  update job wait for `time-sync.target`.
- **The watchdog.** Set `RuntimeWatchdogSec` in systemd, as on path A. The read-only root already
  reboots after a kernel panic.

## The switch-over: never unreachable

Tailscale supports more than one router advertising the same subnet, and fails over between them.
That makes the switch-over safe:

1. **Before the trip,** check what else the NAS does, and move each job somewhere else or decide
   to drop it. A NAS that "only" routes often also turns out to be a backup target, a time source,
   a UPS monitor or a file share someone uses.
2. **At the site,** plug the Pi in beside the NAS, enrol it, and advertise the same route from
   both.
3. **Prove failover:** stop Tailscale on the NAS, check that the site can still be reached from
   outside through the Pi, then start it again.
4. **Prove the Pi on its own,** for at least a few weeks with the NAS as standby, including one
   power cut (pull the plug) and, on path B, one over-the-air update.
5. **Retire the NAS:** remove its route advertisement, remove it from the tailnet, power it off.
   Leave it on the shelf for a season before wiping it.

## Open questions

- Which Starlink router is at the site, and does it have a free Ethernet port?
- Path B on the Pi 3 B+, or a Pi 4/5? The layer targets the 3 B+. A newer board means a new
  machine in the layer, and a newer board is what makes the tunnel faster than the uplink.
- What exactly does the NAS do besides routing? (Step 1 of the switch-over.)
- Is a small UPS or a supercapacitor HAT worth it, given the boot-attempt arithmetic above?
