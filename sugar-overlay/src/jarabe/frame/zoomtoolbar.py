# Copyright (C) 2006-2007 Red Hat, Inc.
# Copyright (C) 2009 Simon Schampijer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from gettext import gettext as _
import logging
import sys

from gi.repository import Gdk

from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GObject

from sugar3.graphics import style
from sugar3.graphics.palette import Palette
from sugar3.graphics.radiotoolbutton import RadioToolButton

from jarabe.journal import journalactivity
from jarabe.frame.frameinvoker import FrameWidgetInvoker
from jarabe.model import shell

sys.path.insert(0, '/usr/share/aspartame')
import aspartame_help


class ZoomToolbar(Gtk.Toolbar):
    __gsignals__ = {
        'level-clicked': (GObject.SignalFlags.RUN_FIRST, None,
                          ([]))
    }

    def __init__(self):
        Gtk.Toolbar.__init__(self)
        aspartame_help.set_active(False)

        # we shouldn't be mirrored in RTL locales
        self.set_direction(Gtk.TextDirection.LTR)
        self.set_style(Gtk.ToolbarStyle.BOTH_HORIZ)

        # ask not to be collapsed if possible
        self.set_size_request(4 * style.GRID_CELL_SIZE, -1)

        self._mesh_button = self._add_button('zoom-neighborhood',
                                             _('Neighborhood'),
                                             _('F1'),
                                             shell.ShellModel.ZOOM_MESH)
        self._groups_button = self._add_button('zoom-groups',
                                               _('Group'),
                                               _('F2'),
                                               shell.ShellModel.ZOOM_GROUP)
        self._home_button = self._add_button('zoom-home',
                                             _('Home'),
                                             _('F3'),
                                             shell.ShellModel.ZOOM_HOME)
        self._activity_button = \
            self._add_button('zoom-activity',
                             _('Activity'),
                             _('F4'),
                             shell.ShellModel.ZOOM_ACTIVITY)

        self._journal_button = Gtk.ToolButton.new(None, _('Journal'))
        self._journal_button.set_icon_name('activity-journal')
        self._journal_button.set_is_important(True)
        self._journal_button.set_tooltip_text(_('Journal'))
        self._journal_button.connect('clicked', self.__journal_clicked_cb)
        self.add(self._journal_button)
        self._journal_button.show()

        spacer = Gtk.SeparatorToolItem()
        spacer.set_expand(True)
        self.add(spacer)
        spacer.show()
        self._help_button = Gtk.ToolButton.new(None, '?')
        self._help_button.set_is_important(True)
        self._help_button.set_tooltip_text("What is this? - Learn what something on the screen does.")
        self._help_button.connect('button-press-event', self.__help_clicked_cb)
        self.add(self._help_button)
        self._help_button.show()
        GLib.idle_add(self._install_help_key_handler)

        aspartame_help.guard(self._mesh_button, 'org.aspartame.shell.neighborhood')
        aspartame_help.guard(self._groups_button, 'org.aspartame.shell.group')
        aspartame_help.guard(self._home_button, 'org.aspartame.shell.home')
        aspartame_help.guard(self._activity_button, 'org.aspartame.shell.frame')
        aspartame_help.guard(self._journal_button, 'org.aspartame.shell.journal')

        shell_model = shell.get_model()
        self._set_zoom_level(shell_model.zoom_level)
        shell_model.zoom_level_changed.connect(self.__zoom_level_changed_cb)

    def _add_button(self, icon_name, label, accelerator, zoom_level):
        if self.get_children():
            group = self.get_children()[0]
        else:
            group = None

        button = RadioToolButton(icon_name=icon_name, group=group,
                                 accelerator=accelerator)
        Gtk.RadioToolButton.set_label(button, label)
        button.props.label_widget = None
        button.connect('clicked', self.__level_clicked_cb, zoom_level)
        self.add(button)
        button.show()

        palette = Palette(GLib.markup_escape_text(label))
        palette.props.invoker = FrameWidgetInvoker(button)
        palette.set_group_id('frame')
        button.set_palette(palette)

        return button

    def __help_clicked_cb(self, _button, _event):
        active = aspartame_help.toggle()
        self._help_button.set_tooltip_text(
            "What is this? - Click something to learn what it does."
            if active else
            "What is this? - Learn what something on the screen does.")
        return True

    def _install_help_key_handler(self):
        window = self.get_toplevel()
        if isinstance(window, Gtk.Window):
            window.connect('key-press-event', self.__help_key_press_cb)
        return False

    def __help_key_press_cb(self, _window, event):
        if event.keyval == Gdk.KEY_Escape and aspartame_help.is_active():
            aspartame_help.escape()
            self._help_button.set_tooltip_text("What is this? - Learn what something on the screen does.")
            return True
        return False

    def __level_clicked_cb(self, button, level):
        if not button.get_active():
            return

        shell.get_model().set_zoom_level(level)
        self.emit('level-clicked')

    def __journal_clicked_cb(self, _button):
        journalactivity.get_journal().show_journal()


    def __zoom_level_changed_cb(self, **kwargs):
        self._set_zoom_level(kwargs['new_level'])

    def _set_zoom_level(self, new_level):
        logging.debug('new zoom level: %r', new_level)
        if new_level == shell.ShellModel.ZOOM_MESH:
            self._mesh_button.props.active = True
        elif new_level == shell.ShellModel.ZOOM_GROUP:
            self._groups_button.props.active = True
        elif new_level == shell.ShellModel.ZOOM_HOME:
            self._home_button.props.active = True
        elif new_level == shell.ShellModel.ZOOM_ACTIVITY:
            self._activity_button.props.active = True
        else:
            raise ValueError('Invalid zoom level: %r' % (new_level))
