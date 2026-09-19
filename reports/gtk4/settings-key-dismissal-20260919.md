# GTK4 Settings keyboard dismissal — 2026-09-19

The Settings window's key controller previously ran in the default bubble
phase. A focused search entry and the global key handler could therefore claim
navigation keys before the modal panel saw them. Patch 0164:

- moves the panel controller to GTK4 capture phase;
- treats Escape, F3, and F4 as panel dismissal keys;
- reuses the existing stop/close path so modal ownership is released by the
  0162 repair.

The rebuilt guest applied 0164 and passed the GTK4 runtime check:

```text
runtime-check=ok target=gtk4 pid=88846 desktop=1 window=0xe00005 stable_pid=758 gtk4_pid=88846
```

Source verification confirms the capture controller is installed on the real
GTK4 `ControlPanel`. Physical key injection remains limited by the current
guest/QEMU evdev transport, so this report does not claim a physical Escape
trace. The implementation is deliberately bounded to the modal panel and does
not alter global Spaces or Activity input routing.
