# GTK4 activity UX pass — canvas batch

Date: 2026-10-04
Environment: headless QEMU, 1920×1080, GTK4 preview, no host mouse grab

This batch tightened the layout of six canvas-heavy Activities:

- Gears: labeled, expanding canvas with centered controls.
- Moon: labeled expanding phase surface with clear navigation controls.
- Paint: labeled fill canvas, visible drawing boundary, centered palette,
  and a fill-aligned body so the canvas does not sit in a large top gap.
- FotoToon: labeled caption canvas with a usable full-width preview and
  caption entry.
- Game Of Life: expanding labeled board with cells that fill the available
  Activity area.
- Abacus: labeled place-value surface with full-width rods and accessible
  value controls.

## Evidence

The six captured surfaces are in
[`visual-sweep-ux-canvas-20261004/`](visual-sweep-ux-canvas-20261004/).
All six were captured at 1920×1080 and passed the visual sweep. The final
headless sweep completed `pass=50 fail=0`; the six current source modules were
overlaid into the packaged GTK4 preview before capture.

The six Activity lifecycle probes each completed two cycles with:

`resume=PASS service-release=PASS shell-cleanup=PASS`

The probes also verified the real AT-SPI input path and seeded datastore
payloads. The repeated dbind AT-SPI cache warnings did not affect pass/fail
results and are retained as a follow-up environment issue.

## Runtime probe repair

The roundtrip scripts no longer assume Claude's development-only interpreter
path (`/home/aspartame/Development/gtk4-preview/venv/bin/python`). They accept
`GTK4_PYTHON` and otherwise use the packaged interpreter, allowing the same
probes to run in the standalone QEMU image and the shared development tree.

This is UX/lifecycle qualification evidence, not a FULL PORT claim. GTK3
remains installed as fallback/reference until the per-Activity parity,
collaboration, physical-input, and accessibility gates are satisfied.
