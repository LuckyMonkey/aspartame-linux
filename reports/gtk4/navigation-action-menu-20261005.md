# GTK4 navigation action menu — 2026-10-05

The GTK4 Home toolbar now has a visible `Navigate (F1-F6)` menu alongside
Spaces. It exposes Neighborhood, Group, Home, Activity, Journal, and Frame as
clickable accessible buttons. The callbacks use the existing ShellModel,
Journal, and Frame APIs; no new global key grab or display history was added.

This is the forward UX path for environments where physical F1-F6 delivery
is unreliable. The QEMU/host physical transport qualification remains open
and is documented separately in `docs/runbooks/QEMU_MACROS.md`.

The change is source/build-qualified by the focused repository test; a fresh
guest visual capture will follow the next GTK4 development-share rebuild.
