# GTK4 Activity input evidence — 2026-09-13

The native GTK4 Help Activity was launched through the GTK4 Journal service in
the modern Space.  Its Casilda surface remained alive as PID 64814 and was
captured at:

`reports/screenshots/sugar-20260912-225508-v0.0.31.png`

The QEMU pointer helper focused the Activity's GTK4 search entry, then the HMP
keyboard helper injected `H`.  The resulting capture,
`reports/screenshots/sugar-20260912-230513-v0.0.31.png`, visibly shows:

* the caret in the Search help field,
* the field value `h`, and
* `Input received: h` rendered by the Activity itself.

This proves pointer focus and keyboard delivery reached the real GTK4 Activity
surface.  The QMP helper was corrected to consume the initial greeting before
processing command replies.
