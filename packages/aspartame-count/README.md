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
active session. The current version supports cell toggling, multiple layers, duplicate and
delete, total counts, and JSON Journal persistence. Layers share one XY grid:
the selected layer is opaque and editable, while other layers are painted first
as translucent neutral-grey context. The side rail places Back layer and Forward layer arrows
next to the voxel canvas so layer number and edit target stay visible. Delete layer is a single direct button, not a two-step menu.
