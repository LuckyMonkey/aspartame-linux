# GTK4 Help dark-mode evidence — 2026-09-13

The native Help Activity now uses an application-priority GTK4 CSS provider
with a dark `help-root`, white reading text, and a white high-contrast search
entry.  The live 1920x1080 capture
`reports/screenshots/sugar-20260912-231834-v0.0.31.png` visibly confirms the
dark page, readable text, Sugar top bar, and stop control.

The provider uses GTK CSS nodes and `Gtk.StyleContext.add_provider_for_display`;
no browser-only layout properties are involved.
