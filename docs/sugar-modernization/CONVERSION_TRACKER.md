# GTK4 conversion execution record

This is the active steering document for the full conversion requested on
2026-09-11. Historical first-pixels notes and the root engineering backlog are
not completion claims. The conversion is **in progress**, not complete.

Activity checkboxes below record implementation and runtime coverage history;
they do not claim behavioral parity. The authoritative per-Activity status is
`ACTIVITY_PORT_CLASSIFICATION.md`, which distinguishes FULL PORT, FUNCTIONAL
PORT, COVERAGE IMPLEMENTATION, and PLACEHOLDER.

## Starting reality (historical)

- Starting branch `master`, HEAD/origin `601ffc6`; origin fetched 2026-09-11.
- No Git submodules. Dependencies are separate, pinned guest checkouts recorded
  in `/home/aspartame/Development/gtk4-preview/PINS.tsv`.
- Python 3.14.7; GTK3 3.24.52; GTK4 4.22.4; Casilda 1.5.0;
  wlroots 0.20.2. Sugar `f84a2d5`, toolkit `74f6a05`, Casilda `cecb869`,
  datastore `7aa97e7`, Log `b4c43c4`.
- QEMU was stopped. Reopened the existing September 4 ISO and existing disks.
  `/home/aspartame` is the existing `/dev/vdb` ext4 home volume.
- The outer desktop is X11/Metacity; GTK4 Jarabe embeds Casilda for private
  Wayland clients. This is not a complete Wayland host/session migration.
- Both GTK3 and GTK4 can start. Live launch revealed the preview wrapper never
  calls the Activity console-script entrypoint. A clean exit is not a launch.
- Casilda initially exposes no public surface lifecycle; Gtk.Application's
  window-added signal cannot observe separate Wayland client windows.
- GTK4 Home list/Journal still contain GTK3 TreeView assumptions. Historical
  compatibility and process-liveness tests do not prove parity.
- Runtime share initially lacked current scripts. This was corrected during the
  2026-09-14 deployment; current runtime evidence is maintained in
  `reports/gtk4/runtime-matrix-20260914.md` and the parity ledger.

## Current reality (2026-09-14, reconciled)

- `master` and `origin/master` are synchronized at `12e2c26`.
- Host regression suite: 205 tests passed. The guest preview build applies and
  validates patch 0015 and boots the GTK4 shell.
- Thirty-nine modern Activities have live Casilda launch/stop evidence, including
  Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log,
  and the 30 additional native GTK4 ports listed in the status matrix.
- Remaining parity work is user-visible: physical QEMU function-key transport,
  peer-backed Neighborhood/Group behavior, and individual ports for the
  remaining legacy Activity catalog. No additional keybinding or Spaces
  abstraction is justified by current evidence.

## Execution and ownership

1. Root: build/deploy reproducibility, launcher, Casilda surface lifecycle,
   Jarabe state, semantic Spaces, regression and live integration.
2. Home/Frame: native list/search, real running icon state, Frame input/focus.
3. Journal: native list/model/details/chooser, datastore search/resume/actions.
4. Settings/Neighborhood/Help: native forms, real peer models, contextual Help.

Author native shell replacements under `gtk4-overlay/src/jarabe/`; keep
upstream-layer fixes in owner-labelled patches. Do not edit stable GTK3 through
the modern overlay. Only the root integration process deploys/restarts the
visible VM; isolated widget probes use separate displays/profiles/buses.

## Completion gate (all require runtime proof)

- [ ] GTK3 Home, Activity launch/input/stop and regression invariants
- [x] GTK4 startup/reload and GTK namespace isolation
- [x] Home Favorites/List/search/clear/XO and real running state
- [x] Real GTK4 Activity launch/input/active/stop repeated three times (99-cycle
      matrix; physical input transport remains separate)
- [x] Abnormal exit cleanup: process, service, surface, shell state
- [x] Home/Activity switching and semantic classic/modern Spaces
- [x] Frame, palettes, notifications, clipboard and DnD at the supported level
- [x] Journal entries/search/resume/details/chooser and datastore persistence
- [ ] Neighborhood/Group peer actions (empty state is verified; peer requires a
      second collaboration participant)
- [x] Settings, Activity Manager, approval and contextual Help
- [ ] Physical-event Tab/Shift+Tab/Enter/Space/Escape (semantic actions are
      tested; guest evdev transport is not delivering physical F-keys)
- [x] Accessible names, roles and states on important controls
- [x] GTK CSS/build validation, no fatal GTK4 tracebacks or orphaned Activities
- [x] PASS2 regressions and lifecycle stability run
- [x] Durable screenshots, runtime logs, commands, architecture and runbooks
- [x] Verified coherent commits pushed to GitHub

No unchecked item is an external blocker merely because it requires more work.
