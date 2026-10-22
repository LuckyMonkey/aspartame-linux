# Settings window ownership

The upstream-derived GTK4 `jarabe.controlpanel.gui.ControlPanel` is a
separate undecorated, modal `Gtk.Window`, transient for the shell's main
window. A separate Settings window is intentional in this implementation;
its placement and dimensions are integration concerns. Patch 0167 requests
the full monitor geometry. Multi-monitor placement and comparison-mode
sizing still need dedicated runtime coverage.

`UIService.ShowControlPanel()` must retain the panel in `_control_panel` and
return `True` after opening it. Modal ownership prevents duplicate panels.
The shared `_close_control_panel()` path destroys the retained window and
releases its modal count, allowing Settings to reopen after `ShowHome()`.
Sections keep their existing accept/cancel and restart-alert navigation.

The original 0058 patch declared two fewer added lines than it contained.
GNU patch therefore omitted window retention and the success return while
reporting success. The October 17 image contains that truncated method.
The patch now has the correct hunk length. Both the preview build and ISO
staging run `scripts/repair-gtk4-controlpanel-action.py` so old exports also
receive the repair. The helper accepts the known truncated implementation,
leaves complete implementations unchanged, and rejects unfamiliar endings.

## Acceptance

Copy `scripts/sugar-gtk4-settings-probe.py` to an idle test guest, then run:

```sh
python3 /tmp/sugar-gtk4-settings-probe.py /tmp/settings-aboutcomputer.png
```

Use `--lifecycle-only` to run only the qualified Settings lifecycle checks.
The full About Computer path currently times out after tile activation in
the test image; its visual/refresh acceptance remains open.

The probe adopts the modern shell environment, verifies three semantic
open/close/reopen cycles and duplicate-panel refusal, then opens About my
Computer and refreshes its local inventory. It returns Home on completion.
It uses AT-SPI actions where available and an accessibility-generated mouse
click at the reported bounds for the custom section tile. This does not
qualify physical keyboard transport, Escape, or all other Settings sections.

## Applying changes

- About Computer inventory is read-only; Refresh requires no restart.
- Changes to shell Python code require restarting the affected shell.
- Existing section restart prompts invoke the session manager's logout
  path; they are not requests to reboot the computer.
- A complete per-setting restart/reboot matrix remains unfinished.
