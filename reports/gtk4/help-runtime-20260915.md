# GTK4 Help runtime verification — 2026-09-15

The real `org.laptop.HelpActivity` bundle was launched in the modern Space,
explicitly activated through the Shell service, and found in the guest AT-SPI
tree as `Sugar Help`. The 1920×1080 capture shows the dark Sugar Help surface,
Help icon/stop control, search field, and English topic list covering Home,
Activities, Journal, Frame, Neighborhood, keyboard/accessibility, and further
reading. The earlier white icon-only captures were launch placeholders taken
before `ActivateActivity`; they are not runtime evidence for the Help UI.

Evidence: `reports/screenshots/sugar-20260915-092840-v0.0.31.png` and OCR
sidecar. Probe output: `help-visible=PASS` (AT-SPI surface/name discovery).
