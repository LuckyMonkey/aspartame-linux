"""Small GTK4 Activity D-Bus lifecycle service.

This keeps the established Sugar shell contract while GTK4 activities use
Gtk.Application rather than legacy X windows.
"""

import dbus
import dbus.service

from gi.repository import GLib


class ActivityService(dbus.service.Object):
    """Advertise one Activity instance to Jarabe and accept lifecycle calls."""

    def __init__(self, activity):
        self._activity = activity
        self._bus = dbus.SessionBus()
        activity_id = activity.get_id()
        self._bus_name = dbus.service.BusName(
            "org.laptop.Activity" + activity_id, bus=self._bus
        )
        super().__init__(
            self._bus_name, "/org/laptop/Activity/" + activity_id
        )

    @dbus.service.method("org.laptop.Activity", in_signature="b")
    def SetActive(self, active):
        self._activity.set_active(bool(active))

    @dbus.service.method("org.laptop.Activity")
    def Close(self):
        # Return from D-Bus dispatch before close tears down this service.
        GLib.idle_add(self._close_activity)

    def _close_activity(self):
        if self._activity is not None:
            self._activity.close()
        return GLib.SOURCE_REMOVE

    def close(self):
        """Release the well-known instance name during normal shutdown."""
        self.remove_from_connection()
        self._activity = None
        self._bus_name = None
        self._bus = None
