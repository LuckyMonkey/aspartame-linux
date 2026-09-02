# GTK4 race status

Checked 2026-09-02. The active preview runs only inside the Aspartame QEMU
development guest. Its source, prefix, profile, D-Bus session, and runtime are
isolated from package-owned GTK3 Sugar.

## Current milestone

🟡 **SHELL STABILITY + HOME SEARCH (Arch VM):** pinned GTK4 Jarabe now renders
the real Favorites wheel and XO after initializing its corrected private D-Bus,
datastore, profile, and embedded Casilda compositor.

An AT-SPI editable-text action entered `terminal` in the GTK4 Home search field.
The List View rendered its real empty-result state, clearing the query returned
to Favorites, and the same Jarabe process remained alive beyond 60 seconds with
no fatal traceback. Casilda's private `wayland-sugar` socket remained healthy.

This proves a stable GTK4 Home render/search/return loop and semantic input into
the search control. It does not prove a complete GTK4 desktop: Frame, Journal,
and Activity lifecycle remain unclaimed. The preview has pinned Activity source
checkouts but no GTK4 Activity bundle is installed or registered yet, so launch
cannot be tested honestly. Stable GTK3 continues behind the isolated preview.
After GTK4 installation exposed an ambiguous GI default, the GTK3-only
Select-a-Thing startup hook was made explicit about GTK/GDK 3; a fresh Terminal
Activity then launched and rendered normally.

## Pinned heads

See the guest pin file: `/home/aspartame/Development/gtk4-preview/PINS.tsv`.
The selected shell is Sugar PR #1106 head `f84a2d514dbbcab6e30c810b00088f47870e04a5`; toolkit is PR #35 head `74f6a05a4921c27d0892bc22845fd4d4a60f4119`.
Casilda is pinned to `cecb869ce390e13ebdecdca9953731d3a3f3aa73`.

## Scorecard

| Area | Upstream main | Aspartame preview |
|---|---|---|
| GTK4 toolkit import | ✅ | ✅ |
| Toolkit icon tests | 🧪 | ✅ 55/55 |
| sugar-ext build/tests | 🧪 | ✅ build/install and 5 native tests |
| Casilda compositor | 🧪 PR work | ✅ 1.5.0 socket and protocols live |
| Shell startup | ❌ incomplete | ✅ Home process stable beyond 60 seconds |
| Home | 🧪 PR work | 🧪 Favorites/search/return visibly exercised |
| Frame/Journal | 🧪 PR work | ❌ not usable yet |
| GTK4 activity lifecycle | 🧪 PR work | ❌ not runtime-tested |

“More code” is not counted as “ahead” until it runs in a session.

## Verified 2026-09-02 Arch VM FIRST PIXELS checkpoint

Evidence: `reports/gtk4/first-pixels-arch-vm-20260902.png` (1920x1080,
SHA-256 `c93ff7a0cdb38a72a27b42c77ccb9714f4061f47d395d73e9cb47932a916095f`).

Runtime versions: Python 3.14.7, GTK 4.22.4, PyGObject 3.56.3,
GLib 2.88.3, Wayland 1.26.0, wlroots 0.20.2, Meson 1.12.0, and
Casilda 1.5.0. The outer preview window uses the guest's existing X11 desktop;
Casilda is the embedded compositor for Sugar's private Wayland activity
surfaces. No Wayland package or service was installed on the host.

The screenshot boundary is also useful for future transitions: Casilda renders
embedded clients through its GTK4 snapshot path. Internal GSK opacity,
clipping, and transforms are compatible with that boundary; Aspartame must not
depend on transparent native top-level windows. No transition work is part of
this checkpoint.

The older `reports/gtk4/first-pixels-12.png` Xvfb result is retained as
historical evidence only. The VM-native Casilda 1.5 result supersedes its host
dependency assumptions.

## Verified 2026-09-02 SHELL STABILITY / Home interaction checkpoint

Evidence:

- `reports/gtk4/home-search-stable-arch-vm-20260902.png` — search query and
  GTK4 empty-result view, SHA-256
  `2c0b84ed164b3e667f633406787077ec1898a7c5054f4aae158a7b691a6fcfab`.
- `reports/gtk4/home-return-stable-arch-vm-20260902.png` — same process returned
  to the Favorites wheel, SHA-256
  `d8479f76fca8266fad448afd43a530f363acc759af0c4852b0285d4e313980ca`.

Preview patches `0018` through `0021` resolve the datastore contract, private
bus environment, Favorites icon sizing, renderer scrolling contract, and lazy
Home toolbar state. The shell stayed alive for 63 seconds after search and
return; Jarabe, datastore, Casilda, and the Wayland socket were all live.

Input was exercised through the GTK4 search object's AT-SPI `EditableText`
interface. This validates semantic control exposure and the resulting Jarabe
behavior. Keyboard event synthesis remains unproven because the managed X11
wrapper does not raise when AT-SPI activates the nested search object; do not
misreport that harness limitation as successful keyboard navigation.

Next milestone: build/register the simplest pinned GTK4 Activity and complete
Home → launch → active Activity → stop → Home. The empty search result is
currently correct for the preview's empty Activity registry.

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
`metadatareader` extension is compiled for the preview Python and its remaining
`env`, `mime`, and `logger` imports use `sugar4`. The preview launcher starts
the service on the private D-Bus session, but the service currently owns the
GTK3 name while `sugar4` asks for the GTK4 name.

Journal proceeds farther after this checkpoint but still fails in its legacy
GTK3-style `CellRendererFavorite` (`props` is unavailable under GTK4). That
is the next Journal-specific port blocker, not part of this checkpoint.
