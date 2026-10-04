# GTK4 activity UX pass — learning games batch

Date: 2026-10-04
Environment: headless QEMU, 1920×1080, GTK4 preview, no host mouse grab

This batch improved four learning Activities without changing their puzzle
state or Journal formats:

- IQ now presents its sequence, answers, status, and next action inside a
  responsive `Sequence puzzle` panel.
- Jumble now presents the scrambled word, answer entry, actions, and status
  inside a responsive `Word puzzle` panel.
- Appel Haken now has a labeled `Colour regions` surface with visible color
  semantics for the four region controls.
- Across and Down now has a labeled expanding `Answer grid` surface that
  separates the puzzle from letter entry and actions.

All four screenshots are in
[`visual-sweep-ux-games-20261004/`](visual-sweep-ux-games-20261004/).
The full headless sweep completed `pass=50 fail=0` at 1920×1080. Each targeted
roundtrip completed `resume=PASS cleanup=PASS`; the AT-SPI cache warnings were
observed again but did not affect lifecycle results.

This is UX/lifecycle qualification evidence, not a FULL PORT claim. GTK3
remains installed as fallback/reference until the parity, collaboration,
physical-input, and accessibility gates are complete.
