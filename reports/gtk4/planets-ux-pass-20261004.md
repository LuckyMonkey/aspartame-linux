# GTK4 Planets UX pass — 2026-10-04

## Result

The Planets surface now presents an actual exploration workspace instead of a
title and a row of controls above an undifferentiated blank area. The canvas
has a labeled `Solar system` frame, deterministic stars, orbit rings, a sun,
planet color markers, and a visible highlight/name for the selected planet.
The selection panel explains the current planet, while the five planet
buttons remain centered and keyboard/AT-SPI addressable.

The existing five-planet selection model and JSON Journal payload are
unchanged. The drawing surface remains responsive and uses its live
allocation; no fixed desktop-sized canvas was reintroduced.

## Verification boundary

Focused host source checks:

```text
pytest -q tests/test_gtk4_planets_activity.py
2 passed

PYTHONPATH=tests/gtk4_harness python3 tests/gtk4_harness/roundtrip.py packages/gtk4-planets-activity
{"package": "gtk4-planets-activity", "checks": {"construct": true, "buttons_clicked": 5, "persistent": true, "roundtrip_stable": true, "malformed_tolerated": true}, "errors": []}
```

The rebuilt development guest passed its GTK4 build and a Journal/Casilda
visual sweep (`pass=1 fail=0`, 1920x1080). The captured screenshot is
[`org.sugarlabs.Planets.png`](planets-ux-pass-20261004/org.sugarlabs.Planets.png)
with SHA-256
`e47b7faaaec36c07184f1d19ba26f5751d4efd4df854212962ddc18c9561850e`.

The existing one-cycle guest Journal probe also passed:

```text
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
planets-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

Planets remains a `FUNCTIONAL PORT`, not a `FULL PORT`: the complete upstream
astronomical simulation and collaboration behavior remain open, and no GTK3
package is removed by this pass.
