# FULL PORT receipts — 2026-10-23

Abacus, Finance, Jukebox, Write and Portfolio were ported to their GTK3
core workflows (see the verdict table in
`docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md`). All seven
retirement candidates then passed `scripts/sugar-gtk4-fullport-receipt.py`
on the packaged ISO.

## Image

`aspartame-2026.10.23-x86_64.iso`, sha256
`c0d0a5fc4dfc3de356f9cdbc3b63b152938b962835353e131e697099e7aca4b4`, built
by `make iso` from the unchanged runtime export `ccce1187…`; the five
Activities come from `packages/` at build time. Booted headless in
snapshot mode with `QEMU_DEV_SHARE_MOUNT=0`; nothing was copied into the
guest except the receipt probe in `/tmp`.

## Receipts

Every keystroke went through QEMU's virtual keyboard. `guard` writes
corrupt bytes into the saved object, relaunches, and compares sha256.

| Candidate | Workflow driven by keys | input | persist | guard | a11y |
| --- | --- | --- | --- | --- | --- |
| Markdown | type source, see preview | PASS | PASS | PASS | PASS (4) |
| Pippy | type program, Ctrl+Tab to Run, see 42 | PASS | PASS | PASS | PASS (10) |
| Abacus | choose Soroban in the type list, type 3.25, Up arrow on a bead rod → 3.2500001 | PASS | PASS | PASS | PASS (9) |
| Finance | add a Food expense, open Budget, set a 10.00 monthly budget | PASS | PASS | PASS | PASS (13) |
| Jukebox | add a Journal tone and a Journal video, play, see progress, Next, see the 320×240 video play | PASS | PASS | PASS | PASS (14) |
| Write | Heading 1 from the style list, Ctrl+B bold, export PDF to the Journal; saved as RTF | PASS | PASS | PASS | PASS (33) |
| Portfolio | slides from two starred entries, Next, retitle a slide, Save as PDF; the title reaches the entry | PASS | PASS | PASS | PASS (15) |

(a11y count = visible interactive controls checked, all named.)

## Regression on the same image

| Check | Result |
| --- | --- |
| `sugar-gtk4-runtime-check.sh gtk4` | `runtime-check=ok` |
| GTK4 lifecycle probe, 3 cycles | `lifecycle-probe=PASS` |
| GTK3 lifecycle probe, 3 cycles | `lifecycle-probe=PASS` |
| Activity matrix, 1 cycle | `activity-matrix=PASS` (51 lifecycle PASS lines) |
| Host suite | 633 passed |

## Found and fixed while qualifying

- Arch's gtk4 ships no media module, so `Gtk.MediaFile` could not play.
  Jukebox now drives GStreamer `playbin`, with video frames as textures.
- Adding a track made it current, so Play started the last one added.
- Portfolio's `self.show` shadowed `Gtk.Widget.show()`; the window never
  appeared. The host harness now fails such shadowing.
- Focus landed on FlowBox cells and list rows that ignored Space; pickers
  and thumbnails are now activatable rows.
- Portfolio's description field took Tab as text; it now moves focus.
- Abacus's bead area had no accessible role or name.

## Gate

`scripts/sugar-gtk4-retirement-gate.sh` → `gtk4-retirement=PASS`. Color My
World left the candidate list: it has no GTK3 version to compare. The gate
removes nothing; GTK3 packages stay installed until a separate decision.
