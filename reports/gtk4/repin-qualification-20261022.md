# Upstream re-pin qualification — 2026-10-22

Pins: sugar PR #1106 `beaae56`, sugar-toolkit-gtk4 main `9d86a31`, with
series 0300/0301 plus seven datastore/ext/Log/Casilda patches. Built in
the development guest (October 17 image, snapshot mode); the GTK4 Space
ran from `/home/aspartame/Development/gtk4-preview`.

| Check | Result |
| --- | --- |
| Host replay (`sugar-gtk4-series-check`) | exact=9 fuzz=0 failed=0 skipped=1 |
| Host suite | 575 passed |
| Guest build | `preview build: PASS` |
| `sugar-gtk4-runtime-check.sh gtk4` | `runtime-check=ok` |
| GTK4 lifecycle probe, 3 cycles | `lifecycle-probe=PASS` |
| GTK3 lifecycle probe, 3 cycles | `lifecycle-probe=PASS` |
| Settings probe (full) | 3 close/reopen cycles PASS, `settings-aboutcomputer=PASS refresh=PASS` |
| Activity matrix, 1 cycle | `activity-matrix=PASS` (51 lifecycle PASS lines) |

Fixed during qualification:
- **Duplicate shell actions.** `service.py` defined `ShowNeighborhood`,
  `ShowGroup` and `ShowControlPanel` twice. The later copies won, so they
  skipped closing Settings.
- **Theme lookup.** Upstream's `setup_theme` looks for the theme only in
  `/usr/share`. With it missing, the shell fell back to Adwaita, and
  palettes showed white text on white (the XO buddy palette looked
  empty). Theme lookup now searches the XDG data dirs.
- **Settings tile activation.** Tiles are now real buttons. The About
  Computer AT-SPI activation (HANDOFF item 3) now passes.
- **About inventory.** Commands are bounded by a timeout, the inventory is
  collected asynchronously once per refresh, and the Refresh button stays
  in place across refreshes.
- **Settings keys.** The CAPTURE-phase key handler now handles only
  navigation keys and main-page type-ahead. All shell navigation dismisses
  Settings through `actions.dismiss_settings()`.

Screenshot: `about-computer-20261022.png`. The XO palette was checked
visually: themed black, showing the nick, Shutdown, Restart, Logout, My
Settings and Register.

Not covered: the packaged ISO (needs host sudo for `make iso`), the
two-guest share/join run, and the guest datastore byte comparison for
failed loads.

## Later the same day: Snakepit, Chirality, Journal

Host suite: 582 passed. Guest results on the same build:

| Check | Result |
| --- | --- |
| Chirality activity round-trip | `chirality-activity-roundtrip=PASS active-sequence=left,right,left` |
| Chirality object round-trip | `chirality-object-roundtrip=PASS ... payload=utf8 cleanup=PASS` |
| Chirality crash round-trip | `chirality-crash-roundtrip=PASS crashed=right preserved=left` |
| Chirality replacement round-trip | `chirality-resume-roundtrip=PASS ... state-clean=PASS` |
| Shell-restart session resume (Calculate + Clock seeded) | `chirality-resume=PASS restored=left:4f0c…,right:a625… skipped=none failed=none` |

After resume, the state directory contained only `chirality.json` and its
`.lock` file: there was no fixed `.resume-tmp` and no stray temporary
files.

## Packaged ISO

`aspartame-2026.10.22-x86_64.iso`, sha256 `f9dff8b7…a41733`, built by
`make iso` from the staged 20261022 runtime export. The embedded
`STANDALONE-MANIFEST` reads `eae0e392…`, which matches the export. The
0300/0301 freshness gate passed during the build. The VM was booted
headless in snapshot mode with `QEMU_DEV_SHARE_MOUNT=0` (no 9p mount), and
every check ran from `/usr/lib/aspartame/gtk4-preview`.

| Check | Result |
| --- | --- |
| `sugar-gtk4-runtime-check.sh gtk4` | `runtime-check=ok` |
| Settings probe (full) | 3 close/reopen cycles PASS, `settings-aboutcomputer=PASS refresh=PASS` |
| GTK4 lifecycle probe, 3 cycles | `lifecycle-probe=PASS` |
| GTK3 lifecycle probe, 3 cycles | `lifecycle-probe=PASS` |
| Activity matrix, 1 cycle | `activity-matrix=PASS` |
| Chirality activity / object / crash / resume round-trips | all PASS, `state-clean=PASS` |

Screenshot: `about-computer-iso-20261022.png` (Image 2026.10.22, themed XO
palette).

Not run on the ISO: the two-guest share/join, which passed on the dev
build with the same 0300/0301. One build warning was seen: the
`archiso_pxe_nfs` hook lacks `nfsmount`, which affects only PXE/NFS boot.
