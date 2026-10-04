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
`reports/gtk4/visual-sweep-games4-dev-20261004/` and from the final shareless
image under
[`visual-sweep-games4-packaged-20261004/`](visual-sweep-games4-packaged-20261004/).

The rebuilt standalone ISO used preview archive SHA-256
`5e196b1ef3908fb17054e279f3a6b4cdbf39c4958133977aa1bbf28a990f4978` and ISO
SHA-256 `f7537f7e02fbb813a72c1d852545c1d322c2adf1f466a556582c820870f15428`.
The packaged sweep passed `8/8` at `1920x1080`; its manifest SHA-256 is
`e30ba7cf282d2d2a00c1f418f4add576946888473789c60cb7c00bec90554fc8`.

The complete packaged GTK4 catalog regression sweep then passed `50/50` at
`1920x1080`, followed by another GTK4 runtime ownership check. Its durable
manifest is [`visual-sweep-packaged-games4-full-20261004/manifest.tsv`](visual-sweep-packaged-games4-full-20261004/manifest.tsv)
with SHA-256
`57e318ea983b079725225818fce34ebe52c7432b6e34d28119144538e8ee59d2`.
