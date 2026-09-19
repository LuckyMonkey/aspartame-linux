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

## Current reality (2026-09-15, reconciled)

- `master` and `origin/master` are synchronized at `54f2e0b` (the README and
  planning-runbook documentation continued in subsequent documentation-only
  commits).
- Host regression suite: 265 GTK4 tests passed. The guest preview build applies and
  validates patch 0015 and boots the GTK4 shell.
- Fifty modern Activities have live Casilda launch/stop coverage, including
  Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log,
  and the additional native GTK4 ports listed in the status matrix. The
  2026-09-15 one-cycle matrix passed every registered bundle; this remains
  coverage evidence, not a FULL PORT claim.
- Remaining parity work is user-visible: physical QEMU function-key transport,
  peer-backed Neighborhood/Group behavior, and individual ports for the
  remaining legacy Activity catalog. No additional keybinding or Spaces
  abstraction is justified by current evidence.
- Later on 2026-09-15, the live guest was found with the classic GTK3 shell
  placed on the modern Space's workspace (a bare `python3 -m jarabe.main`
  restart bypassing `sugar-gtk4-space.sh`'s placement step); reconciled with
  `sugar-gtk4-space.sh setup`. The same session found and fixed a shared
  AT-SPI bus-discovery collision between the two Spaces (GTK4-023) and used
  the fix to root-cause the open Tab/Shift+Tab/Space gate item down to a
  missing Casilda keyboard-focus handoff (GTK4-024); see `BLOCKERS.md`.

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
- [x] Physical function keys in the modern Space. Closed 2026-09-15: F1/F3/F5
      reach Neighborhood/Home/Journal, F6 reveals the Frame and Escape
      dismisses it, and physical F7/F8 switch Spaces across two round trips.
      Root cause was `SugarKeyGrabber` never releasing its X11 passive grabs,
      fixed in `patches/system/0001-sugar-toolkit-gtk3-keygrabber-release.patch`;
      see `reports/gtk4/fkey-grab-resolved-20260915.md`. It ships as a rebuilt
      package, `packages/sugar-toolkit-gtk3/PKGBUILD`, installed from the
      profile's `[aspartame]` repository; one ISO build remains to exercise
      that path.
- [ ] Neighborhood/Group peer actions (empty state is verified; peer requires a
      second collaboration participant)
- [x] Settings, Activity Manager, approval and contextual Help
- [x] Physical-event Tab/Shift+Tab/Space. Closed 2026-09-15: physical typing,
      Tab, Shift+Tab, Enter and Space all reach a real GTK4 Activity launched
      without pointer assistance. Four faults in series were removed - the
      overlay owned window focus (0140), nothing then claimed it (0136), the
      shell's duplicate-dispatch guard swallowed unhandled keys (0139), and
      Casilda applied modifiers one keystroke late (0138), on top of
      keyboard focus at map time (0137). Physical F7/F8 remains open and is
      tracked as a separate X11/Metacity transport frontier, not a Sugar gap;
      see `reports/gtk4/keyboard-delivery-20260915.md`.
- [x] Accessible names, roles and states on important controls
- [x] GTK CSS/build validation, no fatal GTK4 tracebacks or orphaned Activities
- [x] Regression invariants and lifecycle stability run (repeat this pass as
      routine tooling; it is not a one-time milestone)
- [x] Durable screenshots, runtime logs, commands, architecture and runbooks
- [x] Verified coherent commits pushed to GitHub

No unchecked item is an external blocker merely because it requires more work.
