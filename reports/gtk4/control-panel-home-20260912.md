# GTK4 Control Panel from Home — 2026-09-12

The modern shell was tested from Home with the semantic Sugar shortcut
Alt+Shift+M (QEMU HMP `shift-alt-m`). The fullscreen GTK4 Control Panel opened
with its black Sugar surface, search field, close control, and settings
sections (About Me, About my Computer, Activity Manager, Background, Backup,
Date & Time, Frame, Keyboard, Language, Modem, Network, and Web Services).

Evidence screenshot:

`reports/screenshots/sugar-20260912-205522-v0.0.31.png`

The fix preserves Activity-owned shell windows when an Activity is active and
uses the shell main window as the transient owner when opening from Home.
