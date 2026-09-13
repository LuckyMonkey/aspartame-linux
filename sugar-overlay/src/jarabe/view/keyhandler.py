"""Workspace-aware GTK3 key handling for the Aspartame Spaces preview.

The packaged GTK3 handler uses ``SugarExt.KeyGrabber`` to receive Sugar's
function keys globally.  That is correct for a single Sugar desktop, but a
global X11 grab steals F1--F6 from the isolated GTK4 Space as soon as both
desktops share the same X server.  Keep the upstream handler and action
semantics, but release its grabs whenever Metacity has selected the modern
workspace.  The grab is restored when the classic workspace becomes active.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import logging
import os
import subprocess
import sys

import gi

gi.require_version("Wnck", "3.0")
from gi.repository import GLib, Wnck


def _load_packaged_handler():
    """Load the distro handler without recursively importing this overlay."""
    current = Path(__file__).resolve()
    for entry in sys.path:
        if not entry:
            continue
        candidate = (Path(entry) / "jarabe/view/keyhandler.py").resolve()
        if not candidate.is_file() or candidate == current:
            continue
        # The Aspartame overlay is present in both /usr/share and the
        # development bind mount.  Neither is the upstream GTK3 handler; if
        # we load either one again this loader recurses until startup crashes.
        # Only accept the distro-installed module from Python's site-packages.
        if "site-packages" not in candidate.parts:
            continue
        spec = spec_from_file_location("_aspartame_packaged_keyhandler", candidate)
        if spec is None or spec.loader is None:
            continue
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ImportError("the packaged Sugar keyhandler is unavailable")


_packaged = _load_packaged_handler()

# Preserve every upstream action table/helper/import except the public factory
# functions and class that need the workspace gate below.
for _name, _value in vars(_packaged).items():
    if not _name.startswith("__") and _name not in {
        "KeyHandler", "setup", "get_instance"
    }:
        globals()[_name] = _value


class KeyHandler(_packaged.KeyHandler):
    """Upstream GTK3 handler with an EWMH workspace ownership gate."""

    def __init__(self, frame):
        super().__init__(frame)
        self._classic_space_active = None
        self._space_watch_id = GLib.timeout_add(100, self._sync_space_grab)
        self._sync_space_grab()

    def _key_pressed_cb(self, grabber, keycode, state, event_time):
        key = grabber.get_key(keycode, state)
        if key in ("F7", "F8"):
            target = "gtk3" if key == "F7" else "gtk4"
            controller = os.environ.get(
                "ASPARTAME_SPACE_SWITCHER",
                "/mnt/aspartame-dev/scripts/sugar-gtk4-space.sh",
            )
            logging.warning("GTK3 semantic Space key: %s", key)
            subprocess.Popen([controller, target], close_fds=True)
            return True
        return super()._key_pressed_cb(grabber, keycode, state, event_time)

    @staticmethod
    def _active_workspace_number():
        screen = Wnck.Screen.get_default()
        if screen is None:
            return None
        screen.force_update()
        workspace = screen.get_active_workspace()
        if workspace is None:
            return None
        return workspace.get_number()

    def _sync_space_grab(self):
        """Own global Sugar keys only while classic Space is selected."""
        workspace = self._active_workspace_number()
        classic_active = workspace is None or workspace == 0
        if classic_active == self._classic_space_active:
            return True

        if classic_active:
            # Recreate the grabber after modern Space releases it.  The
            # SugarExt object owns X11 passive grabs; dropping the object is
            # the reliable ungrab path on versions where grab_keys([]) only
            # updates its requested key list.
            if self._key_grabber is None:
                self._key_grabber = SugarExt.KeyGrabber()
                self._key_grabber.connect('key-pressed',
                                          self._key_pressed_cb)
                self._key_grabber.connect('key-released',
                                          self._key_released_cb)
            # Spaces keys are semantic shell actions, not upstream Sugar
            # actions.  Include them in the passive grab explicitly so the
            # classic Space can hand F8 back to the coordinator (and keep
            # F7 idempotent) while the modern Space is isolated.
            keys = list(_actions_table.keys())
            for space_key in ("F7", "F8"):
                if space_key not in keys:
                    keys.append(space_key)
            self._key_grabber.grab_keys(keys)
        else:
            grabber = self._key_grabber
            self._key_grabber = None
            if grabber is not None:
                grabber.grab_keys([])
                del grabber
        self._classic_space_active = classic_active
        logging.warning(
            "Spaces key ownership: GTK3 %s (workspace=%s)",
            "active" if classic_active else "released",
            workspace,
        )
        return True


_instance = None


def setup(frame):
    global _instance
    _instance = KeyHandler(frame)


def get_instance():
    return _instance
