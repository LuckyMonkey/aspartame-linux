# Spaces round-trip and GTK3 startup — 2026-09-13

F7 initially selected workspace 0 but showed a black screen because the
classic shell crashed during import. The startup log identified recursive
loading between the two Aspartame overlay copies:

`/usr/share/aspartame/jarabe/view/keyhandler.py` ↔
`/mnt/aspartame-dev/sugar/src/jarabe/view/keyhandler.py`

The overlay loader now accepts only the distro handler under Python
`site-packages`, preventing it from loading another overlay copy. After
deploying the fix, GTK3 started normally and rendered the Home ring in
`sugar-20260912-234118-v0.0.31.png`.

Live Space checks then showed:

- F8 selected GTK4 (`current=1`) and rendered the GTK4 Frame in
  `sugar-20260912-234136-v0.0.31.png`.
- F7 selected GTK3 (`current=0`) with the GTK3 Home ring visible.
- Both processes remained present in the controller status.
