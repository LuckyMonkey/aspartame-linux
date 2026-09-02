# GTK4 migration backlog

## P0 — boot/session startup

- [x] Select and pin Sugar PR #1106 and reach real Jarabe pixels in the
  Aspartame VM with embedded Casilda 1.5. This proves startup, not a complete
  session.
- [ ] Align the toolkit/datastore D-Bus service contract.
- [ ] Propagate locale and runtime-directory state before private D-Bus starts.
- [ ] Hold the corrected Home shell alive for 60 seconds without fatal
  tracebacks.
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

- [x] Build Casilda 1.5 against guest Arch wlroots 0.20 and verify the private
  `wayland-sugar` socket/protocol registry.
- [ ] Remove accidental new X11 dependencies from migrated code.

## P5 — cleanup and packaging

- [ ] Track Python/GTK API deprecations and Arch package drift.
- [x] Add the guest-only GTK4/Casilda build dependencies to the ISO profile.

## P6 — optional modernization

- [ ] AI-assisted mechanical ports with upstream references.
- [ ] Typing, documentation, and accessibility improvements after behavior is
  stable.

- [x] Confirm GTK4 Jarabe remains alive for 60 seconds under isolated Xvfb/DBus. Verified 2026-09-01 with no traceback, crash, SIGILL, or fatal marker. This closes process liveness only; Home/Frame/input still require runtime interaction tests.
