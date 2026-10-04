# GTK4 activity UX pass — compact games batch

Date: 2026-10-04
Environment: headless QEMU, 1920×1080, GTK4 preview, no host mouse grab

This batch improved four compact Activities without changing their game state
or Journal formats:

- Number Rush now presents the arithmetic round, answer, score, and actions
  in an expanding `Arithmetic round` surface.
- Stopwatch now presents its controls in an expanding `Elapsed time` surface
  with a clearly readable 64px primary time display.
- BlockParty now presents its blocks in a labeled expanding `Block
  arrangement` surface.
- Memorize now presents its cards in a labeled expanding `Matching cards`
  surface.

The four captured surfaces are in
[`visual-sweep-ux-games2-20261004/`](visual-sweep-ux-games2-20261004/).
The final headless sweep completed `pass=50 fail=0` at 1920×1080. Each target
roundtrip completed `resume=PASS cleanup=PASS`; the AT-SPI cache warnings did
not affect lifecycle results.

This is UX/lifecycle qualification evidence, not a FULL PORT claim. GTK3
remains installed as fallback/reference until the parity, collaboration,
physical-input, and accessibility gates are complete.
