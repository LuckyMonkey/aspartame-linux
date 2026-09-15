# GTK4 Help depth and runtime evidence — 2026-09-15

## Change

The native Help Activity now documents the Sugar shell, XO identity, saving
and resuming Journal objects, Classic/modern Spaces, and recovery when an
Activity will not open.  Topics remain searchable and are presented as native
GTK4 `Gtk.Expander` sections on the dark Sugar surface.

The introductory section is expanded from an idle callback after its child is
attached.  This avoids the GTK4 allocation ordering that previously rendered
every body collapsed even though the first expander had been marked expanded.

## Verification

- `pytest -q tests/test_gtk4_help_content.py tests/test_gtk4_activity_activation.py`
  — 33 passed.
- Guest `scripts/sugar-gtk4-build.sh` — PASS through the complete preview build;
  patch 0106 is recognized by semantic result and the build advances beyond
  the former 0134 drift frontier.
- Guest process: `helpactivity4.HelpActivity` launched through Journal with a
  real Activity ID and was stopped through its D-Bus `Close()` method.
- Screenshot: `reports/screenshots/sugar-20260915-150121-v0.0.31.png`
  (1920×1080, SHA-256
  `dc15d39e093d4f2456c5119dcd83402572f86c4271d1d209a59b210b263ef314`).

The screenshot proves the dark native surface and searchable topic list.  The
updated idle-expansion behavior is included in the next guest restart; no
claim is made here that this screenshot proves every section's body is open.

