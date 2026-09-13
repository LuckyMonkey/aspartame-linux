# Repeated GTK4 Activity lifecycle — 2026-09-13 (authoritative stop)

Using the live GTK4 Space and its Journal/Shell D-Bus services, three complete
native Help Activity cycles were executed:

```text
cycle=1 launch=(true,) pid=101921 activity_id=722f4b70e8f44d78a72fc6e9e5da6896 stop=(true,) cleanup=PASS
cycle=2 launch=(true,) pid=101942 activity_id=4425e7b3a4644e6eb5e9ed2fb8c47d1a stop=(true,) cleanup=PASS
cycle=3 launch=(true,) pid=101964 activity_id=4a94d0b638fa4c2bb9c77ad3507e2af0 stop=(true,) cleanup=PASS
```

After the final cycle, no `helpactivity4.HelpActivity` child remained and the
GTK4 shell stayed alive:

```text
runtime-check=ok target=gtk4 pid=98527 desktop=1 window=0x1000518 stable_pid=100449 gtk4_pid=98527
```

This closes repeated normal launch/authoritative-stop cleanup for one real
GTK4 Activity. Abnormal-exit testing, additional Activities, and physical
F1–F8 delivery remain separate completion-gate items.
