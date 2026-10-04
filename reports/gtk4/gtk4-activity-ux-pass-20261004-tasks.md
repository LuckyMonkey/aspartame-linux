# GTK4 activity UX pass — task workflow

Date: 2026-10-04
Environment: headless QEMU, 1920×1080, GTK4 preview, no host mouse grab

Get Things Done now has a clear horizontal task-entry row, a labeled
expanding `Tasks` surface, and an empty-state layout that communicates where
tasks will appear without changing its JSON Journal format or task behavior.

The captured surface is in
[`visual-sweep-ux-tasks-20261004/`](visual-sweep-ux-tasks-20261004/).
The full headless sweep completed `pass=50 fail=0` at 1920×1080. The targeted
roundtrip completed two Journal cycles with `resume=PASS`,
`service-release=PASS`, and `shell-cleanup=PASS`.

This is UX/lifecycle qualification evidence, not a FULL PORT claim. GTK3
remains installed as fallback/reference until the parity, collaboration,
physical-input, and accessibility gates are complete.
