# Packaged/shareless GTK4 qualification — 2026-10-04

This is the first qualification run with the development 9p share omitted.
The guest used only the installed ISO runtime and its packaged helper scripts.

## Artifact

- ISO: `aspartame-2026.10.04-x86_64.iso`
- SHA-256: `d3f7d56eab9f2732deaece66d7c0480185f27d3715f3899607e2c6c3f62c1655`
- QEMU: `QEMU_HEADLESS=1 QEMU_DISPLAY=none QEMU_SNAPSHOT=1 QEMU_DEV_SHARE_MOUNT=0`
- Guest display: 1920×1080
- Development mount: absent; only the persistent `/dev/vdb` home disk was mounted

## Results

- `aspartame-sugar-health`: PASS — Sugar, Metacity, shell D-Bus, Home window,
  packaged import path, and fatal-log check.
- GTK4 runtime check: `runtime-check=ok` after selecting GTK4 Space.
- Full visual sweep: `pass=50 fail=0` at 1920×1080. Evidence is in
  [`visual-sweep-packaged-20261004-shareless-final/`](visual-sweep-packaged-20261004-shareless-final/).
- Get Books and Pippy: two Journal launch/activate/stop/cleanup cycles each,
  all PASS.
- Spaces menu: `button=Spaces compare-action=PASS`; geometry is GTK3
  `960x1080+0+0` and GTK4 `960x1080+960+0`.
- Datastore: the installed GTK3/GTK4 shared service contains the malformed
  numeric-metadata guard; the prior `ValueError: invalid literal for int()
  with base 10: b''` no longer reaches the shell.

## Interpretation

The packaged GTK4 presentation path is now usable for the current MVP gate:
the activities render at the intended viewport, launch through Journal, clean
up, and can be qualified without host-window or development-share coupling.
This does not yet authorize removing GTK3: feature parity, collaboration,
mounted-file handling, persistence, and physical-input gates remain open.

The intentional comparison action remains a side-by-side presentation. The
Spaces primitive itself remains the semantic Space controller used to select
GTK3 or GTK4; Chirality's future milestone must build on that abstraction,
not turn comparison geometry into the window manager.
