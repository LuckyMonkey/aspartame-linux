# GTK4 Markdown UX pass — 2026-10-04

## Result

The packaged GTK4 sweep showed Markdown with its source and preview panes
effectively absent. Markdown now opens with useful starter content in a
responsive side-by-side source/preview workspace, so the activity explains
itself immediately and the primary editing surfaces are visible at normal
Sugar dimensions.

The qualification pass also caught and fixed an initialization crash: the
preview was being updated before the preview widget existed. The starter
buffer is now populated only after both widgets are constructed, and the
preview mirrors it on first launch.

## Verification

Focused host and harness checks:

```text
pytest -q tests/test_gtk4_markdown_activity.py
2 passed

PYTHONPATH=tests/gtk4_harness python3 tests/gtk4_harness/roundtrip.py packages/gtk4-markdown-activity
{"package": "gtk4-markdown-activity", "checks": {"construct": true, "buttons_clicked": 1, "persistent": true, "roundtrip_stable": true, "malformed_tolerated": true}, "errors": []}
```

The rebuilt writable GTK4 guest preview passed:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Markdown launched through Journal and was explicitly activated in the
headless GTK4 shell. The 1920x1080 capture showed the starter source mirrored
in Preview; its SHA-256 was
`4bfecd6cae137edba7bf29d2e8c9429522317f3255523d0b40888330302173ac`.

## Boundary

Markdown remains a `FUNCTIONAL PORT`, not a `FULL PORT`. Full Markdown parser
and rendering breadth remain open. No GTK3 package was removed.
