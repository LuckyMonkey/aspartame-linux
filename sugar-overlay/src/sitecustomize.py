"""Aspartame runtime hook for Jarabe Select-a-Thing.

This is loaded only when the Aspartame development/image path is on
PYTHONPATH. It bridges Sugar toolkit Window construction to Jarabe's
selector without modifying individual Activities.
"""

import logging

_LOG = logging.getLogger(__name__)

try:
    import gi
    gi.require_version("Gdk", "3.0")
    gi.require_version("Gtk", "3.0")

    from sugar3.graphics import window as sugar_window

    _original_init = sugar_window.Window.__init__

    def _window_init(self, *args, **kwargs):
        _original_init(self, *args, **kwargs)
        try:
            from jarabe import select_a_thing
            select_a_thing.install_window(self)
        except (ImportError, AttributeError, TypeError):
            _LOG.debug("Select-a-Thing is unavailable for this window",
                       exc_info=True)

    if not getattr(sugar_window.Window,
                   '_aspartame_select_a_thing_hooked', False):
        sugar_window.Window.__init__ = _window_init
        sugar_window.Window._aspartame_select_a_thing_hooked = True
except (ImportError, AttributeError, TypeError):
    # The hook must never prevent a Sugar process from starting.
    _LOG.debug("Sugar Window hook is unavailable", exc_info=True)
