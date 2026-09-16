# Bounded five-fix pass — 2026-09-15

Five independent defects found by using the modern Space, each reproduced
before any code changed.

## 1 — The Journal rendered blank

- **Reproduction:** press F5. An empty white surface, no toolbar, search or
  entries (9063-byte capture).
- **Root cause:** `show_main_view()` opens with a correct compound guard,
  skip the rebuild when MAIN is both the active view and the canvas, followed
  by six identical bare `if self._active_view == JournalViews.MAIN: return`
  copies. `_active_view` starts as MAIN, so the first call during `_setup()`
  returned before `set_canvas(self._main_view)`.
- **Fix:** patch 0144 removes the bare duplicates.
- **Evidence:** the Journal renders "697 Journal entries" with search and row
  actions (67409-byte capture, OCR confirms).

## 2 — About my Computer claimed the build was unknown

- **Reproduction:** Settings → About my Computer showed `Build: Not available`.
- **Root cause:** `get_build_number()` probes `/boot/olpc_build`,
  `/etc/redhat-release` and `lsb_release`. None exist here, and os-release is
  never consulted, although it says `IMAGE_ID=aspartame`.
- **Fix:** patch 0145 falls back to os-release.
- **Evidence:** the model returns `aspartame 2026.09.04` and the live section
  renders it. Serial Number and Wireless Firmware still read "Not available"
  on a VM, which is honest.

## 3 — The Favorites ring could not be used from the keyboard

- **Reproduction:** on Home, Tab cycled between the search entry and two
  toolbar buttons. No Activity icon ever took focus, so nothing could be
  launched without a pointer.
- **Root cause, two parts.** `FavoritesView` called `set_can_focus(False)`;
  in GTK3 that only stopped the container being a focus stop, but GTK4's
  can-focus gates whether focus may enter the widget *or any child*, so the
  whole ring was excluded. With focus able to enter, Enter still did nothing
  because `CanvasIcon` emits `activate` only from its click gesture while
  `ActivityIcon` advertises `AccessibleRole.BUTTON`.
- **Fix:** patches 0146 and 0147.
- **Evidence:** Tab stops on `Planets` then `PlayGo`; Enter on `Planets`
  starts `Planets.activity planetsactivity4.PlanetsActivity`.

## 4 — Sugar tool buttons were anonymous to assistive technology

- **Reproduction:** Home's two view switchers reported `name=''` over AT-SPI.
- **Root cause:** `ToolButton.set_tooltip()` deliberately clears the GTK
  tooltip because the Sugar palette is the tooltip, and nothing then supplied
  an accessible name.
- **Fix:** patch 0148 sets the accessible label from the same string.
- **Evidence:** the switchers now report `Favorites view` and `List view`.

## 5 — Home's List View raised on every row recycle

- **Reproduction:** switch Home to List View and interact; the shell log fills
  with `AttributeError: 'NoneType' object has no attribute 'unbind'` from
  `activitieslist.py:288`.
- **Root cause:** `_teardown_row` and `_unbind_row` call
  `list_item.get_child().unbind()` unconditionally, but GTK4 may unset the
  child before those callbacks run while recycling rows.
- **Fix:** guard both callbacks in `gtk4-overlay`.
- **Evidence:** repeated Favorites/List switching now produces zero unbind
  errors, and the shell stays healthy.

## Deferred

Reproduced, understood, and deliberately not pursued.

- **F5 does not open the Journal.** `show_journal()` calls `reveal()`, which
  uses top-level window semantics, and never moves the shell's view state.
  Poking the stack directly was tried and reverted: it left F3 unable to
  return Home, which is worse than the original. The coherent fix drives the
  shell's zoom and active-activity state. The Journal is reachable from the
  Frame in the meantime.
- **Journal list rows render their palette inline** as three full-width bars
  per entry, so about four of 697 entries fit on screen. The fault is in the
  GTK4 list-row/palette-invoker port.
- **The Settings window does not cover the screen,** leaving Home's toolbar
  and a second search entry visible above it. `fullscreen()` on the window had
  no effect, making this window management between the shell and a transient
  modal under Metacity.

## Checked and found correct

Recorded so they are not re-investigated: Neighborhood and Group empty states,
Journal entry rename, Home List View favourite toggling and its persistence,
Escape closing the control panel, and F1-F6 suppression while a modal is open
(`_non_modal_action_keys`, deliberate upstream behaviour).
