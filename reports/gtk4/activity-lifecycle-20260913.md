# GTK4 Activity lifecycle probe — 2026-09-13

Using the live GTK4 shell (`/home/aspartame/Development/gtk4-preview`, PID
39350), the native Help bundle was launched three times through the Journal
D-Bus service. Each call returned `boolean true`; the toolkit reused the
single-process Activity instance (PID 41191) rather than creating an orphan.

The Activity was then terminated and its process disappeared. The shell stayed
alive, demonstrating child-exit containment. Runtime logs are under
`/home/aspartame/Development/gtk4-preview/runtime/home/default/org.laptop.HelpActivity/`.

The visible successful surface is captured at
`reports/screenshots/sugar-20260912-212558-v0.0.31.png`.

Remaining lifecycle coverage: automated stop-button/input traversal and a
second real GTK4 Activity need dedicated probes; this report does not claim
those criteria pass.
