# GTK3/GTK4 Spaces runtime evidence — 2026-09-15

The guest reports both spaces alive and selectable without restarting the
session:

```text
current=1
count=4
gtk3_pid=531079
gtk4_pid=533252
keys=F7:GTK3,F8:GTK4
```

Semantic `gtk3` then `gtk4` selection produced separate 1920x1080 captures:

- `reports/screenshots/sugar-20260915-092148-v0.0.31.png` — classic GTK3
  Sugar Home with the established artwork/background.
- `reports/screenshots/sugar-20260915-092150-v0.0.31.png` — modern GTK4
  Sugar Home with the GTK4 shell renderer.

Both processes remained alive while switching, and the modern Space retained
its independent GTK4 preview process and private Casilda boundary.
