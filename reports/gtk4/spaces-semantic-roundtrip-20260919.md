# Spaces semantic round trip — 2026-09-19

The live guest was checked with the existing Space controller while both
shells remained running:

```text
initial: current=1 count=4 gtk3_pid=758 gtk4_pid=108601
gtk3:    current=0 count=4 gtk3_pid=758 gtk4_pid=108601
gtk4:    current=1 count=4 gtk3_pid=758 gtk4_pid=108601
```

Both processes stayed alive, their ownership remained distinct, and the
controller reported `keys=F7:GTK3,F8:GTK4` throughout. This proves the semantic
workspace handoff; it does not replace a physical F7/F8 QEMU key-delivery test.
