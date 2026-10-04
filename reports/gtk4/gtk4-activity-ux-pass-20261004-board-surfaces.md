# GTK4 board and instrument UX pass — 2026-10-04

Mastermind, Mancala, and Level no longer impose fixed work-surface sizes:

- Mastermind's six-by-four code board uses homogeneous expanding rows and
  columns; pegs grow with the available Activity surface.
- Mancala's stores and pits use an expanding homogeneous board; pit controls
  retain accessible CSS touch sizing without fixed pixel dimensions.
- Level's drawing surface now uses its live allocation for all geometry rather
  than a 700×260 content request.

The Activity models, Journal payloads, and single-surface Sugar contract are
unchanged. This is source/harness qualification; a packaged visual receipt is
still separate.
