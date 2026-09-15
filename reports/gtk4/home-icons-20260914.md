# Home icon references repaired

27 repository-owned modern Activity metadata files named a missing SVG,
for example icon=abacus while the file was activity-abacus.svg. This caused
blank document placeholders throughout the Home ring. Corrected metadata
to reference the existing artwork; no renderer or SVG artwork changes.

Live evidence after dev-sync and modern-shell restart:

- Before: home-icons-before-20260914.png (1920x1080).
- After: home-icons-after-20260914.png (1920x1080).
- Fresh GTK4 PID 471271; zero "Failed to load icon file" messages in its
  /tmp/aspartame-gtk4-current.log.
- All 46 repository-owned Activity icon paths exist and parse as SVG.
- Host suite: 271 passed.

The ring still shows fixed-color artwork and needs visual parity evaluation
against GTK3; this fix addresses missing files only. The earlier process
matrix does not establish full Activity startup or behavioral parity.

NEW COMPLEXITY INTRODUCED: none in the runtime; one metadata asset check.
NEXT HIGHEST-VALUE GAP: verify GTK3 Activity input/stop and strengthen actual
startup proof before relying on the Activity matrix.
