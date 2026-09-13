# GTK4 Activity abnormal-exit probe — 2026-09-13

The native Help Activity was launched through `org.laptop.Journal.LaunchBundle`
and then its child process was terminated with `SIGKILL` to bypass the normal
stop path.

```text
(true,)
abnormal_pid=102304
remaining=0
runtime-check=ok target=gtk4 pid=98527 desktop=1 window=0x1000518 stable_pid=100449 gtk4_pid=98527
```

The child disappeared and the GTK4 shell remained healthy. This verifies
process cleanup and shell containment for an abnormal Activity exit; visual
state inspection after a crash and additional Activity types remain open
completion-gate work.
