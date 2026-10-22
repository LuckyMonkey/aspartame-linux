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
