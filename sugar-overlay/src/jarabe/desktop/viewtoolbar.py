# Copyright (C) 2006-2007 Red Hat, Inc.
# Copyright (C) 2009 Tomeu Vizoso, Simon Schampijer
# Copyright (C) 2009-2012 One Laptop per Child
# Copyright (C) 2010 Collabora Ltd. <http://www.collabora.co.uk/>
# Copyright (C) 2008-2013 Sugar Labs
# Copyright (C) 2013 Daniel Francis
# Copyright (C) 2013 Walter Bender
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
from datetime import datetime
import locale
import logging
import sys

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import GdkPixbuf

from sugar3.graphics import style
from sugar3.graphics import iconentry
from sugar3.graphics.radiotoolbutton import RadioToolButton

from jarabe.desktop import favoritesview
from jarabe.model import desktop

sys.path.insert(0, '/usr/share/aspartame')
import aspartame_help
import aspartame_visual

_AUTOSEARCH_TIMEOUT = 1000


class ViewToolbar(Gtk.Toolbar):
    __gtype_name__ = 'SugarViewToolbar'

    __gsignals__ = {
        'query-changed': (GObject.SignalFlags.RUN_FIRST, None,
                          ([str])),
        'view-changed': (GObject.SignalFlags.RUN_FIRST, None,
                         ([object])),
    }

    def __init__(self):
        Gtk.Toolbar.__init__(self)
        aspartame_help.set_active(False)
        self.set_style(Gtk.ToolbarStyle.BOTH_HORIZ)

        self._favorites_views_indicies = []
        for i in range(desktop.get_number_of_views()):
            self._favorites_views_indicies.append(i)
        self._list_view_index = self._favorites_views_indicies[-1] + 1

        self._desktop_model = desktop.get_model()
        self._desktop_model.connect('desktop-view-icons-changed',
                                    self.__desktop_view_icons_changed_cb)

        self._query = None
        self._autosearch_timer = None

        self._add_separator()

        tool_item = Gtk.ToolItem()
        self.insert(tool_item, -1)
        tool_item.show()

        self.search_entry = iconentry.IconEntry()
        self.search_entry.set_icon_from_name(iconentry.ICON_ENTRY_PRIMARY,
                                             'entry-search')
        self.set_placeholder_text_for_view(_('Home'))
        self.search_entry.add_clear_button()
        self.search_entry.set_width_chars(25)
        self.search_entry.connect('activate', self._entry_activated_cb)
        self.search_entry.connect('changed', self._entry_changed_cb)
        tool_item.add(self.search_entry)
        self.search_entry.show()

        # Use an expanding, centered tool item rather than a ToolButton.
        # ToolButton aligns its label from the left and makes the clock appear
        # displaced when the surrounding controls change width.
        self._clock_item = Gtk.ToolItem()
        self._clock_item.set_expand(True)
        clock_box = Gtk.Box()
        clock_box.set_hexpand(True)
        clock_box.set_halign(Gtk.Align.FILL)
        self._clock_render_label = Gtk.Label(label="--:--")
        self._clock_render_label.set_hexpand(True)
        self._clock_render_label.set_halign(Gtk.Align.CENTER)
        self._clock_render_label.set_valign(Gtk.Align.CENTER)
        self._clock_render_label.set_can_focus(False)
        self._clock_render_label.get_style_context().add_class(
            'aspartame-clock-button')
        clock_box.pack_start(self._clock_render_label, True, True, 0)
        self._clock_item.add(clock_box)
        self.insert(self._clock_item, -1)
        self._clock_item.show_all()
        self._clock_button = self._clock_render_label
        clock_css = Gtk.CssProvider()
        clock_css.load_from_data(b'''
            .aspartame-clock-button,
            .aspartame-clock-button:hover,
            .aspartame-clock-button:active,
            .aspartame-clock-button:checked,
            .aspartame-clock-button:focus {
                background: transparent;
                background-image: none;
                border: 0;
                box-shadow: none;
                outline-width: 0;
            }
        ''')
        self._clock_button.get_style_context().add_provider(
            clock_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._clock_render_label.set_margin_top(0)
        self._clock_render_label.set_margin_bottom(0)
        self._clock_settings = Gio.Settings.new("org.aspartame.clock")
        self._clock_settings.connect("changed::format",
                                     self.__clock_format_changed_cb)
        self.__update_clock_cb()
        GLib.timeout_add_seconds(30, self.__update_clock_cb)

        self._button_box = Gtk.HBox()
        self._favorites_buttons = []
        for i in range(desktop.get_number_of_views()):
            self._add_favorites_button(i)
        toolitem = Gtk.ToolItem()
        toolitem.add(self._button_box)
        self.insert(toolitem, -1)
        self._button_box.show()
        toolitem.show()

        self._list_button = RadioToolButton(icon_name='view-list')
        self._list_button.props.group = self._favorites_buttons[0]
        self._list_button.props.tooltip = _('List view')
        self._list_button.props.accelerator = \
            _('<Ctrl>%d' % (len(self._favorites_views_indicies) + 1))
        self._list_view_toggle_id = self._list_button.connect(
            'toggled', self.__view_button_toggled_cb, self._list_view_index)
        self.insert(self._list_button, -1)

        help_css = Gtk.CssProvider()
        help_css.load_from_data(('''
            .aspartame-help-button,
            .aspartame-help-button:hover,
            .aspartame-help-button:focus,
            .aspartame-help-button:active {
                min-width: %dpx;
                min-height: %dpx;
                padding: 0;
                border-radius: 999px;
                border: 2px solid %s;
                background: transparent;
                background-image: none;
                box-shadow: none;
            }
            button.aspartame-help-button label.aspartame-help-glyph {
                color: %s;
                margin: 0;
                padding: 0;
                font-size: 27px;
                font-weight: bold;
            }
            .aspartame-help-button.aspartame-help-active {
                background: %s;
                border-color: %s;
            }
            button.aspartame-help-button.aspartame-help-active label.aspartame-help-glyph {
                color: %s;
            }
        ''' % (aspartame_visual.HELP_BUTTON_DIAMETER,
               aspartame_visual.HELP_BUTTON_DIAMETER,
               aspartame_visual.SHELL_WHITE,
               aspartame_visual.SHELL_FOCUS,
               aspartame_visual.SHELL_WHITE,
               aspartame_visual.SHELL_WHITE,
               aspartame_visual.SHELL_FOCUS)).encode('utf-8'))

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), help_css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._help_button = Gtk.Button()
        self._help_button.get_style_context().add_class(
            'aspartame-help-button')
        self._help_button.set_relief(Gtk.ReliefStyle.NONE)
        self._help_button.set_focus_on_click(True)
        self._help_button.set_size_request(aspartame_visual.HELP_BUTTON_DIAMETER, aspartame_visual.HELP_BUTTON_DIAMETER)
        self._help_button.set_tooltip_text(
            "What is this? - Learn what something on the screen does.")
        aspartame_help.register_target(
            self._help_button, 'org.aspartame.shell.help')
        self._help_button.connect('button-press-event',
                                  self.__help_clicked_cb)
        # Reuse the installed Help Activity's canonical Sugar artwork.
        help_icon = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            '/usr/share/sugar/activities/Help.activity/activity/activity-help.svg',
            24, 24, True)
        help_image = Gtk.Image.new_from_pixbuf(help_icon)
        help_image.set_halign(Gtk.Align.CENTER)
        help_image.set_valign(Gtk.Align.CENTER)
        help_image.set_tooltip_text(
            'What is this? Learn what something on the screen does.')
        self._help_button.add(help_image)
        help_toolitem = Gtk.ToolItem()
        help_toolitem.set_border_width(0)
        help_toolitem.add(self._help_button)
        # Keep contextual Help beside the Home search field, not among the
        # view selectors.  It is a search/understanding affordance.
        self.insert(help_toolitem, 2)
        help_toolitem.show_all()
        GLib.idle_add(self._install_help_key_handler)

        aspartame_help.guard(self._list_button, 'org.aspartame.shell.list')

        self._add_separator()

    def __help_clicked_cb(self, _button, _event):
        active = aspartame_help.toggle()
        self._set_help_button_active(active)
        return True

    def _set_help_button_active(self, active):
        context = self._help_button.get_style_context()
        if active:
            context.add_class('aspartame-help-active')
            self._help_button.set_tooltip_text(
                "What is this? - Click something to learn what it does.")
        else:
            context.remove_class('aspartame-help-active')
            self._help_button.set_tooltip_text(
                "What is this? - Learn what something on the screen does.")
        self._help_button.queue_draw()

    def _install_help_key_handler(self):
        window = self.get_toplevel()
        if isinstance(window, Gtk.Window):
            aspartame_help.install_window(window)
            window.connect('key-press-event', self.__help_key_press_cb)
        return False

    def __help_key_press_cb(self, _window, event):
        if event.keyval == Gdk.KEY_Escape and aspartame_help.is_active():
            aspartame_help.escape()
            self._set_help_button_active(False)
            return True
        return False

    def _add_favorites_button(self, i):
        logging.debug('adding FavoritesButton %d' % (i))
        self._favorites_buttons.append(FavoritesButton(i))
        self._favorites_buttons[i].connect('toggled',
                                           self.__view_button_toggled_cb,
                                           self._favorites_views_indicies[i])
        if i > 0:
            self._favorites_buttons[i].props.group = self._favorites_buttons[0]
        self._button_box.add(self._favorites_buttons[i])
        self._favorites_buttons[i].show()

    def show_view_buttons(self):
        for i in range(desktop.get_number_of_views()):
            self._favorites_buttons[i].show()
        self._list_button.show()

    def hide_view_buttons(self):
        for i in range(desktop.get_number_of_views()):
            self._favorites_buttons[i].hide()
        self._list_button.hide()

    def __find_clock_label(self, widget):
        if isinstance(widget, Gtk.Label):
            return widget
        if isinstance(widget, Gtk.Container):
            for child in widget.get_children():
                label = self.__find_clock_label(child)
                if label is not None:
                    return label
        return None


    def __clock_format_changed_cb(self, settings, key):
        self.__update_clock_cb()

    def __update_clock_cb(self):
        locale.setlocale(locale.LC_TIME, "")
        clock_format = self._clock_settings.get_string("format")
        if clock_format:
            text = datetime.now().strftime(clock_format)
        else:
            time_format = locale.nl_langinfo(locale.T_FMT)
            if "%I" in time_format or "%p" in time_format:
                text = datetime.now().strftime("%I:%M %p").lstrip("0")
            else:
                text = datetime.now().strftime("%H:%M")
        escaped_text = GLib.markup_escape_text(text)
        if self._clock_render_label is not None:
            self._clock_render_label.set_markup(
                "<span size=\"xx-large\" weight=\"bold\">%s</span>" %
                escaped_text)
        return True


    def clear_query(self):
        self.search_entry.props.text = ''

    def set_placeholder_text_for_view(self, view_name):
        text = _('Search in %s') % view_name
        self.search_entry.set_placeholder_text(text)

    def _add_separator(self, expand=False):
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        if expand:
            separator.set_expand(True)
        else:
            separator.set_size_request(style.GRID_CELL_SIZE,
                                       style.GRID_CELL_SIZE)
        self.insert(separator, -1)
        separator.show()

    def _entry_activated_cb(self, entry):
        if self._autosearch_timer:
            GLib.source_remove(self._autosearch_timer)
            self._autosearch_timer = None
        new_query = entry.props.text
        if self._query != new_query:
            self._query = new_query
            if isinstance(self._query, bytes):
                self._query = self._query.decode()
            self.emit('query-changed', self._query)

    def _entry_changed_cb(self, entry):
        if not entry.props.text:
            entry.activate()
            return

        if self._autosearch_timer:
            GLib.source_remove(self._autosearch_timer)
        self._autosearch_timer = GLib.timeout_add(_AUTOSEARCH_TIMEOUT,
                                                  self._autosearch_timer_cb)

    def _autosearch_timer_cb(self):
        logging.debug('_autosearch_timer_cb')
        self._autosearch_timer = None
        self.search_entry.activate()
        return False

    def __view_button_toggled_cb(self, button, view):
        if button.props.active:
            self.emit('view-changed', view)

    def __desktop_view_icons_changed_cb(self, model):
        number_of_views = desktop.get_number_of_views()

        if len(self._favorites_views_indicies) < number_of_views:
            for i in range(number_of_views -
                           len(self._favorites_views_indicies)):
                n = len(self._favorites_views_indicies)
                self._favorites_views_indicies.append(n)
                self._add_favorites_button(n)
                self._favorites_buttons[n].show()
        elif number_of_views < len(self._favorites_views_indicies):
            for i in range(len(self._favorites_views_indicies) -
                           number_of_views):
                n = len(self._favorites_views_indicies) - 1
                logging.debug('removing FavoritesButton %d' % (n))
                button = self._favorites_buttons[n]
                self._favorites_buttons.remove(button)
                button.destroy()
                self._favorites_views_indicies.remove(
                    self._favorites_views_indicies[n])
        self._button_box.show()

        self._list_view_index = number_of_views
        self._list_button.props.accelerator = \
            _('<Ctrl>%d' % (len(self._favorites_views_indicies) + 1))
        self._list_button.disconnect(self._list_view_toggle_id)
        self._list_view_toggle_id = self._list_button.connect(
            'toggled', self.__view_button_toggled_cb, self._list_view_index)
        self._list_button.show()


class FavoritesButton(RadioToolButton):
    __gtype_name__ = 'SugarFavoritesButton'

    def __init__(self, favorite_view):
        RadioToolButton.__init__(self)

        self.props.tooltip = desktop.get_view_labels()[favorite_view]
        self.props.accelerator = _('<Ctrl>%d' % (favorite_view + 1))
        self.props.group = None
        self.props.icon_name = desktop.get_view_icons()[favorite_view]
        view_help_ids = {
            'zoom-neighborhood': 'org.aspartame.shell.neighborhood',
            'zoom-groups': 'org.aspartame.shell.group',
            'zoom-home': 'org.aspartame.shell.home',
            'zoom-activity': 'org.aspartame.shell.activity',
        }
        help_id = view_help_ids.get(self.props.icon_name)
        if help_id:
            aspartame_help.guard(self, help_id)

        favorites_settings = favoritesview.get_settings(favorite_view)
        self._layout = favorites_settings.layout

        # someday, this will be a Gtk.Table()
        layouts_grid = Gtk.HBox()
        layout_item = None
        for layoutid, layoutclass in sorted(favoritesview.LAYOUT_MAP.items()):
            layout_item = RadioToolButton(icon_name=layoutclass.icon_name,
                                          group=layout_item, active=False)
            if layoutid == self._layout:
                layout_item.set_active(True)
            layouts_grid.pack_start(layout_item, True, False, 0)
            layout_item.connect('toggled', self.__layout_activate_cb,
                                layoutid, favorite_view)
        layouts_grid.show_all()
        self.props.palette.set_content(layouts_grid)

    def __layout_activate_cb(self, menu_item, layout, favorite_view):
        if not menu_item.get_active():
            return
        if self._layout == layout and self.props.active:
            return

        if self._layout != layout:
            self._layout = layout

            favorites_settings = favoritesview.get_settings(favorite_view)
            favorites_settings.layout = layout

        if not self.props.active:
            self.props.active = True
        else:
            self.emit('toggled')
