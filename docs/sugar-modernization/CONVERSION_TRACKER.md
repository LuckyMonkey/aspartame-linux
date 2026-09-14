# GTK4 conversion execution record

This is the active steering document for the full conversion requested on
2026-09-11. Historical first-pixels notes and the root engineering backlog are
not completion claims. The conversion is **in progress**, not complete.

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

## Current reality (2026-09-14)

- `master` and `origin/master` are synchronized at `e8ffe45`.
- Host regression suite: 174 tests passed. Guest GTK4 toolkit suite: 55 tests
  passed. The guest preview build applies/validates patch 0015 and boots the
  GTK4 shell.
- Nine modern Activities have live Casilda launch/stop evidence: Help, Count,
  Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, and Log.
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
- [ ] GTK4 startup/reload and GTK namespace isolation
- [ ] Home Favorites/List/search/clear/XO and real running state
- [ ] Real GTK4 Activity launch/input/active/stop repeated three times
- [ ] Abnormal exit cleanup: process, service, surface, shell state
- [ ] Home/Activity switching and semantic classic/modern Spaces
- [ ] Frame, palettes, notifications, clipboard and DnD
- [ ] Journal entries/search/resume/details/delete and datastore persistence
- [ ] Neighborhood/Group at the current supported network level
- [ ] Settings, Activity Manager, approval and contextual Help
- [ ] Pointer and physical-event Tab/Shift+Tab/Enter/Space/Escape
- [ ] Accessible names, roles and states on important controls
- [ ] GTK CSS parser validation, no fatal warnings/tracebacks/orphans
- [ ] PASS2 regressions and performance/stability run
- [ ] Durable screenshots, runtime logs, commands, architecture and runbooks
- [ ] Verified coherent commits pushed to GitHub

No unchecked item is an external blocker merely because it requires more work.
