# GTK4 JAMClock parity pass — 2026-10-04

## Result

`org.laptop.JAMClock` no longer presents as a two-label placeholder. The
native GTK4 Activity now provides the core workflow of the GTK3/Pygame
Activity in a responsive layout:

- Scalable analog clock with colour-coded hands and hour numbers.
- Native GTK4 Calendar with month/year navigation.
- Alarm hour and minute controls with wraparound spin buttons.
- Alarm enable/disable button and visible scheduled/ringing status.
- Accessible labels and expandable card surfaces; no fixed 800x600 canvas.
- JSON Journal persistence for alarm time and enabled state.
- Safe defaults for malformed or wrong-shaped Journal objects.

## Verification

Host harness:

```text
{"package": "gtk4-jamclock-activity", "checks": {"construct": true, "buttons_clicked": 9, "persistent": true, "roundtrip_stable": true, "malformed_tolerated": true}, "errors": []}
```

The rebuilt writable GTK4 guest preview passed the complete toolkit preview
build and launched JAMClock through the real Journal D-Bus path. A 1920x1080
headless screenshot showed the analog face, calendar, and alarm card. A QMP
macro incremented the alarm hour/minute and enabled the alarm; the follow-up
capture showed `Alarm on` and `Alarm set for 01:01`.

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
qemu-headless-macro=PASS steps=4 repeats=1 qmp=/tmp/aspartame-qemu-qmp
```

The alarm qualification capture checksum was
`081a0d992e2ab488f476903f16ca246b2ee43d350b249f8722d834292d06f15b`.

## Boundary

JAMClock remains a `FUNCTIONAL PORT`, not a `FULL PORT`. The original
Pygame-specific decorative artwork and bundled ticking/alarm audio are not
reproduced; they remain explicit follow-up work rather than being hidden
behind the GTK4 identity.
