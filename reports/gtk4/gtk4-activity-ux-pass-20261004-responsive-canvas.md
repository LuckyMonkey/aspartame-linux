# GTK4 activity UX pass — responsive canvases

Date: 2026-10-04

## Scope

Count, Connect the Dots, Planets, Reversi, Game of Life, and Grid Paint still
imposed desktop-sized canvas minimums or fixed board cells. That made the work
surface depend on a large desktop allocation and could clip, stretch, or crowd
the activity on smaller Sugar surfaces.

## Change

- Removed fixed body/frame size requests from all six Activities.
- Added GTK4 `Gtk.AspectFrame` containers so each canvas/board expands while
  preserving its intended drawing ratio.
- Used the GTK4 four-argument constructor form, verified against the guest
  preview runtime; the GTK3 label argument is not valid in GTK4.
- Kept a smaller natural content size for initial allocation.
- Made Count's cells and layer overlays homogeneous and derived drag cell
  selection from the allocated grid rather than a fixed pixel width.
- Made the Reversi, Game of Life, and Grid Paint boards homogeneous with
  expanding cells instead of fixed cell dimensions.
- Scaled Planets' orbit geometry with the allocated canvas.
- Scaled Connect the Dots markers and hit targets without reducing the
  pointer target below an accessible size.
- Journal payloads and activity identities are unchanged.

## Verification

```text
python3 -m py_compile packages/gtk4-count-activity/countactivity4.py packages/gtk4-connect-the-dots-activity/connectthedotsactivity4.py packages/gtk4-planets-activity/planetsactivity4.py packages/gtk4-reversi-activity/reversiactivity4.py packages/gtk4-gameoflife-activity/gameoflifeactivity4.py packages/gtk4-gridpaint-activity/gridpaintactivity4.py
pytest -q tests/test_gtk4_count_activity.py tests/test_gtk4_connectthedots_activity.py tests/test_gtk4_planets_activity.py tests/test_gtk4_reversi_activity.py tests/test_gtk4_gameoflife_activity.py tests/test_gtk4_gridpaint_activity.py tests/test_gtk4_visual_layout.py
..............                                                           [100%]
14 passed in 0.08s
```

This is source and focused-test evidence. A packaged headless visual receipt
for these two activities remains to be collected in the next visual sweep.
The GTK3 fallback/reference bundles remain installed.
