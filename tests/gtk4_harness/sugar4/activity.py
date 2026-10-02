"""Headless ``SimpleActivity`` stub; see the package docstring."""

import os
import tempfile

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class SimpleActivity(Gtk.Window):
    def __init__(self, activity_handle=None):
        super().__init__()
        self.handle = activity_handle
        self.metadata = {}
        self._canvas = None

    def set_canvas(self, canvas):
        self._canvas = canvas
        self.set_child(canvas)

    def get_canvas(self):
        return self._canvas

    def save(self):
        """Stand-in for Journal save: exercise ``write_file`` into a scratch file."""
        with tempfile.TemporaryDirectory() as scratch:
            self.write_file(os.path.join(scratch, "journal-object"))

    def read_file(self, file_path):
        raise NotImplementedError

    def write_file(self, file_path):
        raise NotImplementedError
