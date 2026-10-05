# GTK4 navigation action menu — 2026-10-05

The GTK4 Home toolbar now has a visible `Navigate (F1-F6)` menu alongside
Spaces. It exposes Neighborhood, Group, Home, Activity, Journal, and Frame as
clickable accessible buttons. The callbacks use the existing ShellModel,
Journal, and Frame APIs; no new global key grab or display history was added.

This is the forward UX path for environments where physical F1-F6 delivery
is unreliable. The QEMU/host physical transport qualification remains open
and is documented separately in `docs/runbooks/QEMU_MACROS.md`.

Qualification:

- focused repository checks: 72 passed;
- guest `sugar-gtk4-build.sh`: PASS, including 136 active patch inputs and
  `0202-home-navigation-action-menu.patch`;
- guest source checks: 0185 and 0202 both pass `git apply --check`.

A fresh guest screenshot/AT-SPI action capture is still pending: the
development guest restarted the GTK4 process, but its current Casilda/X11
surface is not published as a managed X11 window, so the side-by-side probe
cannot safely capture it. This does not change the full-parity retirement
gate.
