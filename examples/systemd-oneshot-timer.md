# The `RemainAfterExit` trap: a timer that fires exactly once, then never again

A short one, because it is small, silent, and it will get you.

## The symptom

A `.timer` with `OnUnitActiveSec=5min` paired with a `Type=oneshot` service. It
runs once at boot and then never again. `systemctl list-timers` shows it as
active and scheduled. No error anywhere. Nothing in the journal but the single
successful run.

Found here fleet-wide: every node's timer had run **exactly once since boot**,
across nine machines, for as long as the unit had existed.

## The cause

```ini
[Service]
Type=oneshot
RemainAfterExit=yes     # <-- this line
```

`RemainAfterExit=yes` tells systemd to consider the unit **active** after the
process exits. That is normally what you want for a oneshot that establishes
some state — it makes `systemctl status` report "active (exited)" rather than
"inactive (dead)", so the state it set up is represented honestly.

But a timer's job is to **start** its unit. Starting a unit that systemd already
considers active is a no-op. So every subsequent trigger is silently discarded.
The timer fires correctly, forever, at a unit that will never run again.

The two settings are individually reasonable and jointly useless.

## The fix

Drop `RemainAfterExit` from any oneshot that a timer drives:

```ini
# backlight-off.service
[Unit]
Description=Blank the built-in LCD backlight on this headless node
After=multi-user.target

[Service]
Type=oneshot
# No RemainAfterExit: with it set, the paired timer's OnUnitActiveSec= never
# re-fires — the unit is always already "active", so each retrigger is a no-op.
ExecStart=/bin/sh -c 'for b in /sys/class/backlight/*/bl_power; do echo 4 > "$b" 2>/dev/null || true; done; for f in /sys/class/graphics/fb*/blank; do echo 4 > "$f" 2>/dev/null || true; done'

[Install]
WantedBy=multi-user.target
```

```ini
# backlight-off.timer
[Unit]
Description=Periodically re-blank the built-in LCD backlight

[Timer]
OnBootSec=3min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

## Two things that will waste your time afterwards

**Restarting the timer does not fix an already-stuck service.** After you correct
the unit file and `daemon-reload`, the *service* is still sitting in
`active (exited)` from before the change. The timer will go on no-opping against
it. You have to restart the **service**, not the timer:

```sh
systemctl daemon-reload
systemctl restart backlight-off.service   # the service, not the timer
```

**Enabling a timer well after boot leaves `NEXT` as `n/a`.** If the timer only
has `OnBootSec=` and `OnUnitActiveSec=`, and boot was hours ago with the unit
never having run, there is no anchor to compute the next elapse from. It looks
broken and is not; restart the timer once and it schedules normally.

## How to check it, rather than believe it

```sh
# LAST should advance between runs. If it never moves, you have this bug.
systemctl list-timers backlight-off.timer

# SubState should be "dead" — i.e. restartable. "exited" means the timer
# has nothing it can start.
systemctl show backlight-off.service -p SubState -p ActiveState
```

And verify the *effect*, not the unit state, because on some hardware the write
succeeds and does nothing:

```sh
# read the connector's real power state back
for c in /sys/class/drm/card*-*/; do
  [ "$(cat "$c/status")" = connected ] && echo "$(basename "$c")=$(cat "$c/dpms")"
done
```

On 2011-era Apple panels here, `bl_power` accepted the write, read back the value
it was given, and the screen stayed visibly lit — the only honest signal was the
DRM connector's own `dpms` attribute. A sysfs write returning success is not
evidence that anything happened.
