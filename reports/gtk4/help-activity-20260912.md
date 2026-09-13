# GTK4 Help activity runtime evidence — 2026-09-12

The native `org.laptop.HelpActivity` bundle was launched through the live
Journal D-Bus service after fixing the GTK3/GTK4 process boundary.

- Launch result: `org.freedesktop.DBus` returned `boolean true`.
- Child: `/home/aspartame/Development/gtk4-preview/venv/bin/python -c ... sugar4.activity.activityinstance ...`
- Screenshot: `reports/screenshots/sugar-20260912-212558-v0.0.31.png`
- The screenshot visibly shows a fullscreen Sugar activity surface titled
  **Sugar Help**, with the native Sugar top bar and stop control.

Root cause found: the system `sitecustomize.py` imported Gtk 3 before every
child process. The GTK4 launcher now marks its environment with
`ASPARTAME_GTK4_PREVIEW=1`, and the legacy hook skips itself in that process.
The activity constructor also accepts the ActivityHandle required by the
toolkit entrypoint.
