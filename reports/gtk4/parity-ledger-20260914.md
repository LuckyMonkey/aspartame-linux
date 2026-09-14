# GTK4 parity ledger — 2026-09-14

## Closed gap

GTK4 Frame exposes a stable accessible `Frame` label and `GROUP` role. The
current-source patch sequence handles historical hunk drift without hiding
runtime failures.

## Current evidence

- Guest preview build passes beyond patch 0015.
- GTK4 runtime check passes on desktop 1 (`pid=183604`).
- GTK3 runtime check passes on desktop 0 (`pid=33761`).
- The modern Space is restored after the comparison and passes again.
- Full host suite: 162 tests passed (`pytest -q`, 2026-09-14).
- Fresh guest lifecycle probe (2026-09-14): GTK4 Count launched/stopped for
  three consecutive cycles (PIDs `222220`, `222242`, `222263`), each reporting
  `cleanup=PASS`; final result `lifecycle-probe=PASS`.
- Fresh guest rebuild (2026-09-14): all preview patches applied or semantically
  verified through 0123, including 0015; toolkit import, Casilda 1.0,
  sugar-ext, Jarabe, and datastore metadata checks all passed.
- Native Calculate Activity (2026-09-14): staged into the rebuilt GTK4
  registry, launched through Journal (`org.aspartame.Calculate`), exposed its
  private `WAYLAND_SOCKET`, passed the GTK4 runtime check, and stopped cleanly.
- Calculate repeated lifecycle (2026-09-14): three live launch/stop cycles
  passed with PIDs `231101`, `231124`, and `231145`; every cycle reported
  `cleanup=PASS` and the probe ended `lifecycle-probe=PASS`.
- Image Viewer (2026-09-14): the pinned GTK4 source was staged, launched
  through Journal (`org.laptop.ImageViewerActivity`, PID `233782`), and stopped
  cleanly with the shell reporting the expected successful StopActivity call.
- Image Viewer repeated lifecycle (2026-09-14): three live launch/stop cycles
  passed with PIDs `246325`, `246348`, and `246369`; each reported
  `cleanup=PASS` and the probe ended `lifecycle-probe=PASS`.
- Terminal (2026-09-14): installed the guest `vte4` package after repairing
  pacman trust, rebuilt the GTK4 prefix, launched `org.laptop.Terminal` (PID
  `249258`) through Journal, and stopped it cleanly (`terminal-stop=PASS`).

## Ranked remaining gaps

1. Physical F1–F6 delivery remains below the QEMU/evdev transport. Semantic
   `ShowHome`, `ShowJournal`, `ShowFrame`, `ShowNeighborhood`, `ShowGroup`, and
   `ShowControlPanel` actions are reliable, so no additional keybinding layer
   is justified until keyboard events reach the guest device.
2. Neighborhood/Group peer actions need a real collaboration peer. The empty
   state and accessible roots are verified; inventing peers would not prove
   Sugar collaboration behavior.
3. More individual Activities still require GTK4 ports (Browse remains a
   known GTK3/WebKit-era example). Help and Log provide the verified real
   GTK4 Activity lifecycle path.

## Complexity policy

No new Spaces, launcher, datastore, or input abstraction is introduced by the
Frame fix. GTK3 remains a separate process and behavioral reference.
