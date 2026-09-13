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

Follow-up shell-mediated launch (2026-09-12 11:55 EDT) closed the stale probe,
launched `org.laptop.Log` through `org.laptop.Journal.LaunchBundle`, switched to
the GTK4 Space, and captured a visible Log Activity surface at
`reports/screenshots/sugar-20260912-115540-v0.0.31.png` (1920x1080). The
Casilda compositor is receiving and painting the Activity surface; the earlier
Home screenshot was the inactive GTK3 Space, not a failed map. Real pointer and
keyboard evidence still requires a guest input path that delivers events to
`/dev/input/event*` (QMP/USB injection currently returns success but produces no
guest kernel events).

The same instance was then closed through `org.laptop.Activity.Close`; the
process exited and the GTK4 shell returned to Home. Capture:
`reports/screenshots/sugar-20260912-115619-v0.0.31.png` (1920x1080).

Repeated lifecycle probe (2026-09-12 11:57 EDT) launched and closed `Log`
three times through `org.laptop.Journal.LaunchBundle`. Each cycle produced a
new Activity PID and ID, then left zero `activityinstance` processes. A fourth
instance was terminated with `SIGKILL`; after three seconds its process count
was zero and no `org.laptop.Activity*` name remained on the session bus. The
GTK4 shell was back at Home in
`reports/screenshots/sugar-20260912-115727-v0.0.31.png` (1920x1080).

Semantic Journal action (2026-09-12 20:04 EDT) called
`org.laptop.Shell.ShowJournal` on the rebuilt GTK4 shell and received boolean
`true`. The resulting 1920x1080 capture,
`reports/screenshots/sugar-20260912-200432-v0.0.31.png`, visibly shows the
GTK4 Journal surface with the Sugar toolbar, `Search in Journal` field,
activity/device controls, and project list surface. This proves shell-owned
Journal construction and presentation through the GTK4 stack; Journal search,
resume/open, and complete GTK3 parity remain separate gates.
