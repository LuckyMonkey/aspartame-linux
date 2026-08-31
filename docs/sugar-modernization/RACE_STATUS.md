# GTK4 race status

Checked 2026-08-31. The preview is isolated on SteamLibrary and cannot overwrite the working GTK3 path.

## Current milestone

✅ Official GTK4 PyGObject 4.14.5 loads. ✅ `sugar4` imports from the pinned toolkit checkout. ✅ `sugar-ext` C libraries, GIR generation, and five Meson tests build/pass after a local gtk-doc correction. ❌ A complete GTK4 Sugar shell has not booted.

## Pinned heads

See the external preview pin file: `/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4/PINS.tsv`.
The selected shell is Sugar PR #1106 head `f84a2d514dbbcab6e30c810b00088f47870e04a5`; toolkit is PR #35 head `74f6a05a4921c27d0892bc22845fd4d4a60f4119`.

## Scorecard

| Area | Upstream main | Aspartame preview |
|---|---|---|
| GTK4 toolkit import | ✅ | ✅ |
| Toolkit icon tests | 🧪 | ✅ 55/55 |
| sugar-ext build/tests | 🧪 | 🧪 C build/tests pass; typelib correction local |
| Shell startup/Home/Frame/Journal | ❌ incomplete | ❌ not yet attempted successfully |
| Activities/Wayland | 🧪 PR work | ❌ not yet runtime-tested |

“More code” is not counted as “ahead” until it runs in a session.
