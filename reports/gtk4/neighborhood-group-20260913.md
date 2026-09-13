# GTK4 Neighborhood and Group evidence — 2026-09-13

QEMU function-key probes reached the GTK4 top-level capture controller.  The
GTK4 shell log records both `GTK4 semantic key event: F1` and
`GTK4 semantic key event: F2`.

F1 produced the Neighborhood surface with its `Search in Neighborhood` field
and XO center (`sugar-20260912-231915-v0.0.31.png`).  F2 initially exposed a
real `NameError` in `GroupBox` because the localized empty-state label lacked
its gettext import. Patch `0069` fixed that root cause; after restarting the
GTK4 shell, F2 produced the supported empty peer/group state with `Search in
Group` and `No friends are nearby yet.`
(`sugar-20260912-232301-v0.0.31.png`).
With no collaboration peers advertised by the guest, the two empty states are
intentionally visually sparse; this is not evidence of fabricated peer data.
