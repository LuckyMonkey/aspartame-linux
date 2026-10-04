# GTK4 headless visual qualification — 2026-10-02

## Result

- Full GTK4 activity lifecycle/render sweep: **50 pass, 0 fail** at 1920×1080.
- Filtered runtime check for Calculate and Finance: **2 pass, 0 fail**.
- Captures were taken inside the guest X display over SSH; the host QEMU
  window was never mapped, activated, or given the host mouse.
- Contact sheet: `visual-sweep-headless-20261002-contact-sheet.png`.

## UX fixes verified

- Calculate now centers a bounded content surface and expands its keypad into
  a readable, homogeneous grid.
- Finance now presents Description and Amount as aligned columns, including
  the empty-state layout.

## Automation status

- `scripts/qemu-headless-macro.py` passed the side-by-side spaces macro and
  produced normal PNG framebuffer captures through QMP.
- The default QMP absolute pointer path is qualified by the deterministic
  Calculate `7+8=15` macro; button press and release are sent separately.
- The GTK4 Home Spaces button and its accessible “Compare Spaces side by
  side” action are qualified headlessly. The 2026-10-03 framebuffer capture
  shows the GTK3 and GTK4 panes side by side at 960×1080 each:
  `spaces-button-headless-20261003.png`.
- QMP F7/F8 delivery remains open: the F8 event reaches X11, but the live
  workspace remains unchanged. This is tracked as input/Metacity transport,
  not as a failure of the semantic controller or button path.
- GTK3 retirement is not claimed from this report; the packaged ISO still
  needs a rebuild to include the latest side-by-side window-hint fix.

No commit or GitHub push was performed.
