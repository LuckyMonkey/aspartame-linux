# GTK3/GTK4 Spaces runtime verification — 2026-09-15

The live guest switched to the classic Space and back to the modern Space
without restarting the OS session. `sugar-gtk4-space.sh status` reported
`current=0` with the GTK3 process, then `current=1` with the GTK4 process;
both remained present as distinct Jarabe processes.

Evidence captures:

- GTK3 classic Home: `reports/screenshots/sugar-20260915-080314-v0.0.31.png`
- GTK4 modern Home List: `reports/screenshots/sugar-20260915-080322-v0.0.31.png`

The captures differ in both visual composition and SHA-256, confirming that
workspace switching selected the intended Space rather than merely relabeling
one surface.
