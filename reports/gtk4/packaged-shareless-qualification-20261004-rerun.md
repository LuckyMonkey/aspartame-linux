# Packaged/shareless GTK4 qualification rerun — 2026-10-04

## Result

PASS after the GTK4 Get Things Done cleanup fix. The fresh packaged ISO
booted without `/mnt/aspartame-dev`; GTK4 became the active modern Space and
the complete Journal visual sweep passed 50/50 at 1920×1080.

## Artifact

- ISO: `aspartame-2026.10.04-x86_64.iso`
- SHA-256: `7afdc058cbb6e196f587ea9c77524b377dd50ff65e18c4f0ad79c2361f797fec`
- QEMU: `QEMU_HEADLESS=1 QEMU_DISPLAY=none QEMU_SNAPSHOT=1 QEMU_DEV_SHARE_MOUNT=0`
- Runtime: `/usr/lib/aspartame/gtk4-preview`

## Results

- `aspartame-sugar-health`: PASS after graphical-session startup.
- `sugar-gtk4-runtime-check.sh gtk4`: PASS on desktop 1, with the GTK3
  fallback shell still present on desktop 0.
- Get Things Done: two Journal launch/stop/resume cycles passed, including
  `service-release=PASS` and `shell-cleanup=PASS`.
- Complete catalog visual sweep: `pass=50 fail=0`, 1920×1080.
- The prior `49/50` result was reproduced before the fix: GTD cleanup called
  `get_child()` on the ListBox placeholder `Gtk.Label`. The Activity now
  enumerates actual rows with `get_row_at_index()` for summary, resume, and
  save paths.

## Boundary

This is packaged visual/lifecycle evidence, not a FULL PORT claim. GTK3
remains installed as fallback/reference while feature parity, collaboration,
mounted-file handling, and physical-input gates remain open.
