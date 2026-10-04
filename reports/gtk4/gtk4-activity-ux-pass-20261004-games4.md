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
are source-qualified by 10 focused tests and Python compilation. Packaged
1920x1080 visual evidence is intentionally pending the next standalone ISO
rebuild; the prior immutable packaged image remains qualified at 50/50.
