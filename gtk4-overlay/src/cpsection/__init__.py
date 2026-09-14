"""GTK4-only Control Panel extensions supplied by Aspartame.

The installed Sugar extensions live in a second ``cpsection`` directory.  Use
a namespace path so this overlay does not hide the standard Settings tiles.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
