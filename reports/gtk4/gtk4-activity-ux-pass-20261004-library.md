# GTK4 activity UX pass — library and word surfaces

Date: 2026-10-04  
Environment: headless QEMU, 1920×1080, GTK4 preview, no host mouse grab

This pass corrected three functional GTK4 Activities whose useful content was
otherwise compressed into a thin top strip:

- **Get Books** now uses a bounded, labeled horizontal catalog/details split,
  selects the first available book on initial load, and keeps the read action
  in a dedicated action row.
- **Jukebox** now uses a labeled playlist/player split with a visible
  now-playing state; playlist selection, play/stop, local-file addition, and
  Journal state remain intact.
- **Words** now presents its task in a centered, bounded “Word explorer” card
  instead of stretching the input and action across the entire display.

Evidence:

- targeted visual sweep: `pass=3 fail=0`, 1920×1080;
- all three bundles launched through the GTK4 Journal/D-Bus route, painted,
  were captured, and stopped cleanly;
- two Journal resume/stop cycles passed for each bundle, including seeded
  Get Books selection, Jukebox playlist, and Words lookup payloads;
- `sugar-gtk4-runtime-check.sh gtk4` returned `runtime-check=ok` after the
  probes;
- focused source tests: 7 passed;
- generated captures: [`visual-sweep-ux-library-20261004/`](visual-sweep-ux-library-20261004/).

This is a presentation and interaction hierarchy improvement, not a parity
claim. The GTK3 bundles remain available as fallback/reference until the
Activity runbook’s behavior, input, storage, and collaboration gates pass.
