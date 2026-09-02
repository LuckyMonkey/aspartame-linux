# GTK4 race status

Checked 2026-08-31. The preview is isolated on SteamLibrary and cannot overwrite the working GTK3 path.

## Current milestone

🟡 GTK4 Home startup reached: the isolated preview now gets past profile setup,
Home construction, and optional collaboration dependencies. Default Favorites
Home is visible and the shell process remains alive for at least 12 seconds.
List View, Frame interaction, and activity launch are not yet claimed.

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

## Verified FIRST PIXELS checkpoint

On 2026-08-31 the pinned GTK4 Jarabe shell stayed alive for 25 seconds under private Xvfb and a DBus session and produced recognizable Sugar profile UI pixels. Capture: /media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4/logs/first-pixels-12.png. This is not yet Home, shell stability, or activity lifecycle.

The reproducible wrapper is make sugar-gtk4-run / scripts/sugar-gtk4-run.sh. It contains isolated SUGAR_HOME, GSettings schema data, group-label data, GI typelib and library paths, Python path, Xvfb fallback, and DBus setup.

Preview-only compatibility work uses Casilda 0.3 (Casilda-0.1) because host GTK4 4.14 cannot build the current Casilda 1.x API. Activity launch remains explicitly unsupported by the selected toolkit head.


## 2026-09-01 verification

GTK4 checks pass: GTK4/PyGObject loads, 55 toolkit tests pass, sugar-ext native tests pass, and Jarabe starts under private Xvfb/DBus. A recognizable Sugar-rendered screenshot was captured at reports/gtk4/first-pixels-12.png (1280x800). This does not yet prove stable Home, Frame, Journal, or Activity lifecycle. The next blocker is stable Home rendering for 60 seconds. Runtime warnings include software Casilda rendering under Xvfb, Graphene version selection, and private-portal/GVFS noise; these remain visible in the captured run log.

## 2026-09-02 Home startup milestone

The first real Home startup run initially failed in the legacy activity-list
renderer, then in profile-key validation, optional Telepathy initialization, and
missing extension data. Preview-only patches `0005` through `0011` address those
startup boundaries without changing stable GTK3. The final run stayed alive for
12 seconds, produced a 1280x800 screenshot at
`reports/gtk4/home-preview-20260902.png`, and OCR identified the Home search
surface. The same run still reports non-fatal missing UPower/espeak/portal and
network-extension warnings.

Next single blocker: make List View a real GTK4-native view, or explicitly
provide Home search/list behavior without the legacy TreeView compatibility path.

## 2026-09-02 Home search milestone

Home search now initializes the lazy ActivitiesList before applying the query,
so entering a search from Favorites does not dereference an absent list view.
Preview patch `0012-home-lazy-list-search.patch` was applied and checked in the
isolated shell. A real F5 + `calc` input produced the Home search state and the
Jarabe process remained alive. Evidence: `reports/gtk4/home-search-20260902.png`.

The list renderer remains legacy GTK3-style code under the GTK4 preview.
Journal and network startup also still report separate `PaletteMenuItem` API
errors; those are not part of this milestone.
## 2026-09-02 palette and datastore checkpoint

The GTK4 preview toolkit now provides the upstream migration name
`PaletteMenuItem.set_image()` plus a narrow `set_icon_widget()` compatibility
method for shell code that has not yet been ported. This removes the runtime
crashes previously seen in network and Journal toolbox construction. The
pinned sugar-datastore source is staged in the isolated prefix: its small
`metadatareader` extension is compiled for the host Python and its remaining
`env`, `mime`, and `logger` imports use `sugar4`. The preview launcher starts
the service on the private D-Bus session and reports `datastore: ready`.

Journal proceeds farther after this checkpoint but still fails in its legacy
GTK3-style `CellRendererFavorite` (`props` is unavailable under GTK4). That
is the next Journal-specific port blocker, not part of this checkpoint.
