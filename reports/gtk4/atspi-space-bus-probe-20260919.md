# AT-SPI evidence with both Spaces active — 2026-09-19

The guest runs classic GTK3 and modern GTK4 shells concurrently. Each shell
has a private AT-SPI bus, while the X root property names only one bus at a
time. A probe that simply calls `Atspi.get_desktop()` can therefore inspect the
wrong Space and falsely report that a visible Activity is missing.

The Calculate lifecycle and Help accessibility probes now temporarily point
`AT_SPI_BUS` at the modern Space's private bus and restore the original root
property at process exit. This changes evidence collection only; it does not
change shell ownership or Activity behavior.

## Runtime proof

- `python3 scripts/sugar-gtk4-calculate-roundtrip.py 1` — **PASS**
  (`resume=PASS service-release=PASS shell-cleanup=PASS`).
- `python3 scripts/sugar-gtk4-help-visible.py` — **PASS**
  (`help-visible=PASS help-search=PASS`).
- Both probes ran while GTK3 and GTK4 shell processes were present.
- The Help process was stopped through `org.laptop.Shell.StopActivity`; no
  `helpactivity4` process remained.

This closes a qualification-harness ambiguity, not an Activity visual-port
claim. Per-Activity icon/chrome tasks remain in the launch ledger.
