# GTK4 Activity UX qualification — second batch — 2026-10-03

This pass audited the next sparse GTK4 surfaces at 1920×1080 in the headless
Aspartame QEMU guest. Testing used snapshot disks and did not take the host
pointer or keyboard.

## Changes verified

- Write now presents a full-width, labeled, bordered Document editor.
- Pippy now presents full-width bordered Python program and Output areas.
- Jukebox now presents a full-width labeled Playlist area with visible bounds.
- Color My World now labels the large swatch as Color preview and groups the
  color buttons under Palette.
- Roundtrip helpers used by this batch can select the packaged
  `/usr/lib/aspartame` Python runtime, with the development-tree fallback
  retained.

## Evidence

- Focused source tests: 8 passed.
- Headless visual sweep: 4/4 passed at 1920×1080.
- Pippy, Jukebox, and Color My World: two Journal resume cycles each,
  including visible restore, clean stop, service release, and datastore
  payload checks.
- Write: three launch/activate/stop lifecycle cycles passed.

Screenshots:

- [Color My World](visual-sweep-ux-next-20261003/org.sugarlabs.ColorMyWorldActivity.png)
- [Write](visual-sweep-ux-next-20261003/org.sugarlabs.Write.png)
- [Pippy](visual-sweep-ux-next-20261003/org.laptop.Pippy.png)
- [Jukebox](visual-sweep-ux-next-20261003/org.laptop.sugar.Jukebox.png)

These four are the next modern-Space retirement candidates. As with the first
batch, this qualifies the modern launcher path and bounded offline workflow;
it does not claim full upstream feature parity or remove the GTK3 fallback.
