# GTK4 activity UX pass — responsive canvases

Date: 2026-10-04

## Scope

Connect the Dots and Planets still imposed 980–1000 pixel canvas minimums.
That made the work surface depend on a large desktop allocation and could
clip or crowd the activity on smaller Sugar surfaces.

## Change

- Removed fixed body/frame size requests from both Activities.
- Added GTK4 `Gtk.AspectFrame` containers so each canvas expands while
  preserving its intended drawing ratio.
- Kept a smaller natural content size for initial allocation.
- Scaled Planets' orbit geometry with the allocated canvas.
- Scaled Connect the Dots markers and hit targets without reducing the
  pointer target below an accessible size.
- Journal payloads and activity identities are unchanged.

## Verification

```text
python3 -m py_compile packages/gtk4-connect-the-dots-activity/connectthedotsactivity4.py packages/gtk4-planets-activity/planetsactivity4.py
pytest -q tests/test_gtk4_connectthedots_activity.py tests/test_gtk4_planets_activity.py tests/test_gtk4_visual_layout.py
.....                                                                    [100%]
5 passed in 0.04s
```

This is source and focused-test evidence. A packaged headless visual receipt
for these two activities remains to be collected in the next visual sweep.
The GTK3 fallback/reference bundles remain installed.
