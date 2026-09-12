# GTK4 Activity lifecycle probe — 2026-09-12

Environment: Aspartame QEMU guest, GTK4 Space, GTK 4.22.4, Casilda 1.5.0,
private socket `wayland-sugar`.

Probe: launched `Log.activity` directly through `sugar-activity4` with
`SUGAR_ACTIVITY_ID=probe-log2` semantics and the GTK4/Wayland environment.

Evidence:

- Activity process remained alive as PID 1970.
- The private D-Bus session owned `org.laptop.Activityprobe-log2`.
- The encoded object path `/org/laptop/Activity/probe_log2` responded to
  `org.freedesktop.DBus.Introspectable.Introspect`.
- The introspection included the `org.laptop.Activity` interface and its
  lifecycle methods.
- Calling `org.laptop.Activity.Close` returned successfully; PID 1970 and the
  Activity bus name disappeared afterward.

Result: D-Bus registration and clean stop are proven. The Activity GTK surface
was not visible in the shell screenshot, so Casilda surface mapping/first paint
and real pointer/keyboard delivery remain open gates.
