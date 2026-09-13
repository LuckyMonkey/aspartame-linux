# GTK4 Activity focus transfer evidence — 2026-09-13

In the live 1920x1080 QEMU guest, Help Activity PID 64814 was active in the
modern Space.  QEMU function-key events produced this sequence:

1. F3 returned to the GTK4 Home favorites ring.
2. F6 revealed the Sugar Frame; the Help icon was shown as the active running
   Activity.
3. F4 returned to Help, with its focused search field and `Input received: h`
   state intact.

The captures are:

* `sugar-20260912-230633-v0.0.31.png` — Home
* `sugar-20260912-230636-v0.0.31.png` — Frame with active Help
* `sugar-20260912-230638-v0.0.31.png` — Help restored

The authoritative Shell `StopActivity` call returned `true`; PID 64814 then
disappeared and the capture `sugar-20260912-230711-v0.0.31.png` showed Home.
The live shell log contained no `KeyError`, `ValueError`, or traceback after
this stop.
