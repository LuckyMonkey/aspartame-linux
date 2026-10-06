# Color My World GTK4 map pass — 2026-10-05

The next UX slice turns the large preview into a bounded offline world-region
map. Learners see named region boundaries before making a choice, choose a
palette color, click a named region, see the selected region outlined, and can
clear the map with one explicit action. The existing `{"name": "Violet"}`
Journal payload remains valid; new saves add an optional `regions` color map.

Focused checks:

```text
pytest -q tests/test_gtk4_colormyworld_activity.py
2 passed
cycle=1 ... resume=PASS service-release=PASS shell-cleanup=PASS
colormyworld-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The map geometry is intentionally compact and dependency-free. Country-level
geometry/data, flags, richer artwork tools, and collaboration remain open, so
this is progress toward parity and not a FULL PORT claim.
