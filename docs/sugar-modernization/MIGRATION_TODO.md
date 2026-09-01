# GTK4 migration backlog

## P0 — boot/session startup

- [ ] Identify an upstream GTK4 shell branch that can start a complete Sugar
  session. Scope: shell/session. Depends on Sugar shell migration. Test with
  an isolated VM. Completion: Home, D-Bus, and clean shutdown work.
- [ ] Remove any GTK3-only shell import from the selected upstream branch.
  Downstream only until upstream has a supported pattern.

## P1 — major shell functionality

- [ ] Frame, Home, Journal, and Activity launch smoke tests on GTK4.
- [ ] Verify Sugar theme/icon behavior without GTK3-only CSS assumptions.

## P2 — Journal / Neighborhood / Frame / clipboard / palettes

- [ ] Port clipboard and palette behavior using upstream GTK4 APIs.
- [ ] Verify datastore and D-Bus boundaries remain unchanged.

## P3 — core activities / Fructose

- [ ] Test upstream Calculate and Log GTK4 ports first; then inventory other
  Fructose activities. Keep each activity a separate reviewable change.

## P4 — Wayland/backend neutrality

- [ ] Test the upstream Casilda/Wayland path when shell support exists.
- [ ] Remove accidental new X11 dependencies from migrated code.

## P5 — cleanup and packaging

- [ ] Track Python/GTK API deprecations and Arch package drift.
- [ ] Add matching GTK4 package profile only when upstream shell is bootable.

## P6 — optional modernization

- [ ] AI-assisted mechanical ports with upstream references.
- [ ] Typing, documentation, and accessibility improvements after behavior is
  stable.

- [x] Confirm GTK4 Jarabe remains alive for 60 seconds under isolated Xvfb/DBus. Verified 2026-09-01 with no traceback, crash, SIGILL, or fatal marker. This closes process liveness only; Home/Frame/input still require runtime interaction tests.
