# GTK4 Activity UX pass — games/form batch 4

Date: 2026-10-04

This source pass gives the remaining compact game/form surfaces explicit
Sugar-style work areas instead of relying on implicit child allocation:

- BallAndBrick: expanding labelled game board around the drawing surface.
- Implode: expanding labelled block board with centred blocks.
- Last One Loses: expanding labelled token pile with centred tokens.
- Maze: expanding labelled maze board with centred grid and controls.
- Poll: expanding labelled choice region containing the editable rows.
- Reversi: expanding labelled board with centred 8x8 grid.
- Clock, JAMClock, and Read: explicit expanding root canvases.

The changes preserve the existing Activity behavior and Journal payloads. They
are source-qualified by 10 focused tests and Python compilation. The rebuilt
headless development guest then passed:

- GTK4 runtime ownership check from the rebuilt preview root;
- targeted visual sweep `8/8` at `1920x1080`;
- Journal resume/cleanup for BallAndBrick, Implode, Last One Loses, Maze,
  Poll, and Reversi (`6/6`).

Screenshots and the manifest are retained in the development share under
`reports/gtk4/visual-sweep-games4-dev-20261004/`. Packaged 1920x1080 evidence
is intentionally pending the next standalone ISO rebuild; the prior
immutable packaged image remains qualified at `50/50`.
