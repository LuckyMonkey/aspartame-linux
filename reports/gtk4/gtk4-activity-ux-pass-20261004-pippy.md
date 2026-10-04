# GTK4 Pippy UX follow-up

Date: 2026-10-04

The Pippy two-column editor/output workspace was already structurally sound,
but its empty output panel gave no guidance before the first run. The output
surface now shows `Run the program to see output.` on launch and after Reset or
Journal restore, then replaces that prompt with the real result as before.

The focused headless development-guest visual sweep passed:

```text
visual-sweep=COMPLETE pass=1 fail=0 resolution=1920x1080
```

The execution path, timeout behavior, and UTF-8 Journal payload are unchanged.
