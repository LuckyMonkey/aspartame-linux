# GTK3/GTK4 side-by-side qualification — 2026-10-04

## Result

The live headless GTK4 guest entered the comparison action through
`sugar-gtk4-space.sh side-by-side` and placed both full Sugar surfaces on
workspace 0 at 1920×1080, each 960×1080. The controller stopped the existing
fullscreen GTK4 shell, restarted it windowed, applied both geometries twice
after map, and returned:

```text
Sugar Spaces side by side: GTK3=960x1080 GTK4=960x1080
```

The first runtime probe exposed and fixed an invocation-boundary defect: when
called through the root SSH helper, the probe inherited `/run/user/0` and
looked for the marker in the wrong runtime directory. It now derives
`XDG_RUNTIME_DIR` from the effective desktop UID before reading comparison
state. This preserves the semantic Spaces boundary and does not add panes,
window history, or display-state history.

## Boundary

This receipt qualifies the developer comparison workflow's process/window
placement. It does not claim GTK3 retirement, Activity parity, or peer
collaboration; those remain separate gates.
