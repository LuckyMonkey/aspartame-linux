# Count Activity

Count is a small Sugar Activity for counting filled cells in editable 2D
layers. It is intentionally an Activity, not a conventional desktop app:
its document is saved and resumed through the Sugar Journal.

The authoritative bundle is `Count.activity/`. The ISO profile contains the
same bundle under `/usr/share/sugar/activities/Count.activity`.

For the live QEMU development VM:

```bash
make count-deploy
```

Launch it through Sugar with `sugar-launch org.aspartame.Count` from the
active session. The current version supports cell toggling, dimensions,
multiple layers, duplicate/delete/clear, undo/redo, total counts, and JSON
Journal persistence. Isometric rendering and richer Activity metadata remain
future work.
