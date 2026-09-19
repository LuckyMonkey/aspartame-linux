# Casilda Alt+Tab surface boundary — 2026-09-19

## Result

The GTK4 shell's Alt+Tab path now walks authoritative Activity model state and
updates the selected Activity. The remaining surface-raise behavior is not
implemented because the public Casilda boundary does not expose a way to raise
an already-mapped Wayland toplevel.

## Evidence

- `patches/gtk4-preview/0151-shell-alt-tab-walks-tracked-activities.patch`
  fixes the GTK3 assumption that every Activity owns a shell-visible Gtk
  window; modern Activities are tracked through their D-Bus services instead.
- The installed `Casilda-1.0.gir` exposes `Compositor.get_client_socket_fd`
  and `Compositor.spawn_async`, but no raise, activation, or focus-toplevel
  method.
- `casilda_compositor_focus_toplevel()` exists only as an internal C helper and
  requires Casilda's private `CasildaCompositorToplevel` object. Jarabe cannot
  name or obtain that object through the supported GI API.
- Therefore `ShellModel.activate_activity()` can truthfully update active
  state and the visible compositor page, but cannot raise a selected prior
  client surface without expanding Casilda's public ABI.

## Boundary

This is an explicit Casilda-owned follow-up, not a GTK4 shell regression. A
future upstreamable change should add a stable compositor API keyed by the
Activity's Wayland identity, then Jarabe can call it from
`activate_activity()`. No private symbol or X11 stacking hack is introduced in
this pass.
