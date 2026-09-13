# GTK4 Control Panel XID boundary — 2026-09-12

The semantic Control Panel action previously passed an empty string to the
legacy X11-compatible constructor. Its realize callback then compared that
string with an integer and logged a `TypeError`. The action now passes numeric
XID `0` and only establishes a transient parent when a real shell window is
available.

After restarting Jarabe, `ShowControlPanel` returned `boolean true`; the
Control Panel rendered and the shell log contained no new `Traceback` or
`TypeError`.

Latest screenshot: `reports/screenshots/sugar-20260912-*.png`.
