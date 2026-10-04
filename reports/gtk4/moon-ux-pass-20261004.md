# GTK4 Moon UX pass — 2026-10-04

## Result

The packaged GTK4 visual sweep exposed a layout regression in Moon: the
activity showed its title, phase text, and controls, but the phase canvas was
allocated at zero height. The existing drawing code therefore had no visible
surface.

Moon now puts the phase surface directly in the expandable Activity root. The
canvas has a compact minimum size, a labeled `Moon phase` frame, a dark
illustration surface, and responsive navigation controls. This preserves the
existing eight-phase model and Journal payload while making the primary visual
learning surface visible at 1920x1080.

## Verification

Focused host checks:

```text
pytest -q tests/test_gtk4_moon_activity.py
2 passed

PYTHONPATH=tests/gtk4_harness python3 tests/gtk4_harness/roundtrip.py packages/gtk4-moon-activity
{"package": "gtk4-moon-activity", "checks": {"construct": true, "buttons_clicked": 3, "persistent": true, "roundtrip_stable": true, "malformed_tolerated": true}, "errors": []}
```

The rebuilt writable GTK4 guest preview passed:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Moon launched through the real Journal D-Bus path in the headless GTK4 shell.
The initial 1920x1080 capture showed the labeled phase frame and new-moon
surface; its SHA-256 was
`e7c24d0b14e88ccdaae4e89f9c81a2c01a345d711d233d949e69d23e69caf214`.

A headless QEMU pointer click on `Next` changed both the phase label and the
rendered illustration to waxing crescent. The follow-up 1920x1080 capture
checksum was
`1fbf21a8e79ac76b1a228fbf0be187e06885a04d731a456e6b2ccb1ed336eca6`.

## Boundary

Moon remains a `FUNCTIONAL PORT`, not a `FULL PORT`. Full astronomical
simulation and collaboration behavior remain open. No GTK3 package was
removed, and no persistent display history was introduced.
