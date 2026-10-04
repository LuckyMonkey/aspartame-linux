# GTK4 activity UX pass — games 3 — 2026-10-04

## Result

PASS for the GTK4 development runtime on the headless 1920×1080 QEMU
display. PlayGo, Mancala, and Mastermind now present their primary game
surface as a centered, expanding, labeled board area instead of a small
top-aligned widget island. No host pointer or keyboard input was used.

## Evidence

- The GTK4 preview rebuilt successfully from the synchronized development
  share after the source changes.
- Focused source/layout tests passed: `7 passed`.
- `playgo-roundtrip=PASS resume=PASS cleanup=PASS`.
- `mancala-roundtrip=PASS resume=PASS cleanup=PASS`.
- `mastermind-roundtrip=PASS resume=PASS cleanup=PASS`.
- Headless QMP macros passed for all three launches and screenshots:
  - [`org.laptop.PlayGo.png`](ux-games-20261004/org.laptop.PlayGo.png)
  - [`mulawa.Mancala.png`](ux-games-20261004/mulawa.Mancala.png)
  - [`org.laptop.Mastermind.png`](ux-games-20261004/org.laptop.Mastermind.png)

## Changes

- PlayGo uses an expanding `Go board` frame with a centered 5×5 board.
- Mancala uses an expanding `Mancala board` frame with a centered two-row
  board and stores.
- Mastermind uses an expanding `Code board` frame with a centered six-row
  guess grid; controls remain grouped at the bottom of the Activity.
- The GTK4 builder now recognizes the already-correct 0175 Favorites source
  state during an idempotent rebuild, avoiding a false reverse-patch failure
  after source whitespace changes.
- Headless screenshot macros are reusable and QMP-only; they do not add frame
  history or interact with the host pointer.

## Boundary

This is development-share evidence, not a new packaged ISO qualification.
The GTK3 bundles remain installed as fallback/reference until the broader
behavior, collaboration, and physical-input parity gates are complete.
