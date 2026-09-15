# GTK4-024 — Activity toplevels now receive Wayland keyboard focus — 2026-09-15

`focus-transfer-frontier-20260915.md` root-caused why a physical Tab never
reaches an Activity's own widgets. This report records the fix that closes
the first half of that gap, and states plainly what is still open.

## Defect

`casilda_compositor_focus_toplevel()` is the only code path in Casilda that
calls `wlr_seat_keyboard_notify_enter()`. In `xdg_toplevel_map()` it was
reached from a single `else` branch — a fresh, plain, non-maximized map.
Two other branches fell through without it:

- a toplevel that maps `requested.fullscreen || requested.maximized`, which
  is every Sugar Activity filling the compositor viewport;
- a toplevel remapped from previously saved state.

So an Activity's Wayland surface was never told it had keyboard focus. Only
`on_click_gesture_pressed` — a pointer click — could establish it.

## Evidence before

Full AT-SPI dump of a running, visible Help Activity (pid 25376), taken
through the GTK4-023 bus-pinning probe:

    - application '-c' focused=False
      - frame 'Sugar Help' focused=False
        ...
            - text 'Search help' focused=False focusable=True
            - scroll pane '' focused=False focusable=True
              - button 'How Sugar is organized' focused=False focusable=True
              - button 'Keyboard and accessibility' focused=False focusable=True
              ... every node focused=False ...

A complete, correctly labeled, fully focusable widget tree in which nothing
was ever focused.

## Fix

`patches/gtk4-preview/0137-casilda-focus-toplevel-on-map.patch` calls
`casilda_compositor_focus_toplevel()` unconditionally at the end of
`xdg_toplevel_map()`. The function already returns early when the surface is
already focused or when the toplevel owns child toplevels, so the
unconditional call adds no new state machine.

`patches/gtk4-preview/0136-shell-focus-activity-compositor.patch` is the
shell-side companion: `ShellModel` switched its stack to the "activity" page
without giving the compositor widget GTK keyboard focus, so the focused
widget stayed wherever Home or Journal left it.

Casilda was rebuilt from the pinned checkout with meson and reinstalled into
the preview prefix; the shell was restarted to pick it up.

## Evidence after

A Help Activity launched through `org.laptop.Journal.LaunchBundle` with **no
pointer click and no AT-SPI interaction of any kind**, then probed:

    launched pid=28703 activity=273fbc568c40498b9b1ff5da815eec10
    focused=1 pid=28121 role=panel name='' path=Sugar < python
    focused=1 pid=28703 role=text name='Search help' path=panel < panel < panel < panel < Sugar Help < -c

The Activity's own default widget now holds keyboard focus at map time. Both
patches reverse-check cleanly against the live guest sources, and
`sugar-gtk4-build.sh` routes 0136 to the shell checkout and 0137 to the
Casilda checkout so a full rebuild reproduces this.

## Still open

Per-keystroke delivery into the embedded client is **not** fixed. With both
patches live, physical `BackSpace`/`z`/`q` still leave the Help search
entry's text unchanged (read back through AT-SPI as `'Journal'`, the value
set programmatically beforehand). The shell's own top-level key handler logs
every one of those keys, so QEMU→evdev→GTK transport is fine; what does not
happen is Casilda's own per-widget `key_controller` firing to call
`wlr_seat_keyboard_notify_key()`. A temporary `g_warning` inside
`casilda_compositor_seat_key_notify()` confirmed that function is never
entered for those presses. That controller only fires when the compositor
widget is the GTK window's actual focus widget, and `grab_focus()` on it was
not sufficient to make that so.

The Tab/Shift+Tab/Space completion-gate item therefore stays unchecked. The
next investigation is why the compositor widget does not become the GTK
window's focus widget despite being focusable and being handed
`grab_focus()` — likely `gtk_window_set_focus`/`GtkRoot` semantics for a
widget whose content lives in another process.
