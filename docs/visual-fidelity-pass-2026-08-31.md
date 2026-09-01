# Visual fidelity pass — 2026-08-31

This pass used the SSH deployment and in-guest screenshot workflow. Stable GTK3 Sugar remained the runtime path.

## Five completed goals

1. Activity Manager rows have more consistent vertical rhythm.
2. Activity Manager columns now have deliberate horizontal spacing instead of touching.
3. The reusable five-face rating control has larger, evenly spaced faces.
4. Unselected rating faces retain stronger subdued visibility while the selected face remains fully emphasized.
5. Remove actions are compact and visually secondary.

Additional confirmed fix: the persistent Aspartame version marker now explicitly selects GTK3 before importing GTK APIs. It no longer crashes from a GTK3/GTK4 API mismatch.

## Verification

- Local Python syntax checks: PASS
- make sugar-reload: PASS
- Runtime overlay import: /mnt/aspartame-dev/sugar/src/jarabe/desktop/viewtoolbar.py
- Sugar shell restart: 16904 to 17884
- Metacity: PASS
- Shell D-Bus: PASS
- Home window: PASS
- Guest display: 1920x1080
- Settings panel process: PASS
- Settings screenshot OCR includes Activity Manager and About my Computer
- Version overlay process: running; remaining output is deprecation warnings only

Evidence:

- reports/screenshots/sugar-20260831-215714-v0.0.15.png
- reports/screenshots/sugar-20260831-215536-v0.0.15.png

Known limitation: the current automated launcher opens the Control Panel at its default section; selecting and screenshotting the Activity Manager section still needs a guest-side semantic navigation helper.
