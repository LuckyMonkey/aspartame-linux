# GTK4 Settings language and modal-state repair — 2026-09-19

## Findings

Two independent Settings defects were closed without changing the GTK3
reference shell:

1. The Language section raised `KeyError: 'English'` on the minimal guest
   because `locale -av` supplied no parseable UTF-8 language rows.
2. Closing Settings through `ShowHome()` left ShellModel's modal counter set,
   so the next `ShowControlPanel()` call was refused even though the window was
   no longer visible.

## Changes

- `0161-language-fallback-locale.patch` creates a locale-independent
  English/USA `C.UTF-8` row only when the image has no usable locale metadata.
- `0162-controlpanel-close-modal-state.patch` mirrors the existing stop-button
  modal release in the semantic shell close path. The panel's ownership flag is
  cleared before close, preventing a double decrement if GTK later emits its
  callback.
- `scripts/sugar-gtk4-language-settings.py` is a real GTK4 construction smoke
  probe. It re-execs with the guest shell environment, instantiates the actual
  `cpsection.language.view.Language`, and verifies the fallback row.

## Verification

```text
exact=83 fuzz=33 failed=0 skipped=1 uncompilable=0
Result: PASS (a clean rebuild compiles)

GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS

language-settings=PASS fallback-row=English country=USA

Semantic Settings reopen sequence after the rebuild also returned four
successful calls in order: `ShowHome=true`, `ShowControlPanel=true`,
`ShowHome=true`, `ShowControlPanel=true`.
```

The GTK4 Settings overview was captured at 1920×1080 after the rebuild; the
Language tile is present in the native black Sugar surface:
`reports/screenshots/sugar-20260919-132849-v0.0.31.png`.

## Deliberate scope boundary

This closes construction and modal ownership. It does not claim the remaining
Settings findings are solved: the window still needs a bounded full-screen
coverage pass, and keyboard Escape/F3/F4 dismissal requires a separate input
workflow. Those stay in the qualification deck rather than being hidden by
this fix.
