# GTK4 native activity qualification — 2026-10-04 native batch

This receipt closes the stale review gap for five native GTK4 Activities on
the shareless packaged image:

- FotoToon: two launch/stop/resume cycles; seeded caption and panel state
  restored through Journal.
- IQ: seeded round 2 restored as `Puzzle 2 of 3`; clean stop and service
  release passed.
- Portfolio: two launch/stop/resume cycles; seeded title/body restored.
- TurtleBlocks: seeded position, heading, and line state restored.
- Maze: seeded position `[2, 1]` restored as `Position: 3, 2`.

The probes used AT-SPI to locate the real Activity surface, Journal D-Bus to
launch/resume, and the shell stop action to verify process and bus cleanup.
All five completed with `resume=PASS cleanup=PASS`; FotoToon and Portfolio
also completed two cycles each.

The packaged image was the standalone ISO with SHA-256
`0ba689624f6418e0cb0c5c5d1a3b064174640dbadc13a25fbe3e06c87b602363`, carrying
preview archive SHA-256
`5e196b1ef3908fb17054e279f3a6b4cdbf39c4958133977aa1bbf28a990f4978`.
The catalog visual sweep already recorded PASS captures for all five in
[`visual-sweep-packaged-games4-full-20261004/manifest.tsv`](visual-sweep-packaged-games4-full-20261004/manifest.tsv).

These rows are promoted to `testing`, not `pass`: the evidence proves a
bounded native workflow, persistence, accessibility discovery, and cleanup;
it does not prove complete upstream feature breadth, peer collaboration, or
GTK3 behavioral parity.

Nonfatal AT-SPI cache startup warnings appeared while the probes connected;
they did not prevent discovery, resume, or cleanup and caused no GTK4 fatal
traceback.
