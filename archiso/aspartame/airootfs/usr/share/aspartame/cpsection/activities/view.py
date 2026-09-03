from gettext import gettext as _
import os
import sys
from xml.sax.saxutils import escape

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GdkPixbuf

from sugar3.graphics import style
from jarabe.controlpanel.sectionview import SectionView
from jarabe.model import bundleregistry

from . import model
from .rating_faces import FaceRating

sys.path.insert(0, '/usr/share/aspartame')
import aspartame_visual
try:
    import aspartame_help
except ImportError:
    aspartame_help = None


class ActivityManager(SectionView):
    """A small, inspectable Activity inventory inside Sugar Settings."""

    def __init__(self, activity_model, alerts):
        SectionView.__init__(self)
        self._model = activity_model
        self._rows = {}
        self.set_border_width(style.DEFAULT_SPACING * 2)
        self.set_spacing(style.DEFAULT_SPACING)
        css = Gtk.CssProvider()
        css.load_from_data(('''
            .aspartame-activity-row {
                border-bottom: 1px solid %s;
                padding: 8px 0;
                min-height: 68px;
            }
            .aspartame-rating-face {
                min-width: 58px;
                min-height: 58px;
                padding: 0;
                border: none;
                border-radius: 29px;
                background: transparent;
                box-shadow: none;
            }
            .aspartame-rating-face.aspartame-rating-selected {
                border: 2px solid %s;
                background-color: %s;
            }
            .aspartame-remove-button {
                min-width: 68px;
                min-height: 28px;
                padding: 1px 8px;
                border: 1px solid %s;
                border-radius: 14px;
                background-color: %s;
                color: %s;
            }
            .aspartame-remove-button label {
                color: %s;
                font-weight: bold;
            }
            .aspartame-remove-button:hover,
            .aspartame-remove-button:active {
                background-color: %s;
                border-color: %s;
                color: %s;
            }
            .aspartame-remove-button:hover label,
            .aspartame-remove-button:active label {
                color: %s;
            }
            .aspartame-table-header {
                background-color: %s;
                border-bottom: 2px solid %s;
            }
        ''' % (aspartame_visual.SHELL_LINE,
               aspartame_visual.SHELL_INK,
               aspartame_visual.SHELL_INK,
               aspartame_visual.SHELL_SURFACE,
               aspartame_visual.SHELL_MUTED_INK,
               aspartame_visual.SHELL_MUTED_INK,
               aspartame_visual.SHELL_INK,
               aspartame_visual.SHELL_INK,
               aspartame_visual.SHELL_WHITE,
               aspartame_visual.SHELL_WHITE,
               aspartame_visual.SHELL_SURFACE,
               aspartame_visual.SHELL_MUTED_INK,
               aspartame_visual.SHELL_BORDER)).encode('utf-8'))
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        title = Gtk.Label()
        title.set_markup('<b>%s</b>' % _('Activity Manager'))
        title.set_xalign(0)
        self.pack_start(title, False, False, 0)

        description = Gtk.Label(label=_('Installed Activities. Rate them to record what needs attention.'))
        description.set_xalign(0)
        description.set_line_wrap(True)
        self.pack_start(description, False, False, 0)

        self._count_label = Gtk.Label()
        self._count_label.set_xalign(0)
        self.pack_start(self._count_label, False, False, 0)

        self._scroller = Gtk.ScrolledWindow()
        self._scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroller.set_min_content_height(420)
        self._scroller.add_events(Gdk.EventMask.SCROLL_MASK)
        self._scroller.connect('scroll-event', self._table_scroll_event)
        self._table_surface = Gtk.EventBox()
        self._table_surface.set_visible_window(False)
        self._table_surface.set_hexpand(True)
        self._table_surface.set_vexpand(True)
        self._table_surface.add_events(Gdk.EventMask.SCROLL_MASK)
        self._table_surface.connect('scroll-event', self._table_scroll_event)
        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.NONE)
        self._list.set_vexpand(True)
        self._list.set_hexpand(True)
        self._list.add_events(Gdk.EventMask.SCROLL_MASK)
        self._list.connect('scroll-event', self._table_scroll_event)
        self._table_surface.add(self._list)
        self._scroller.add(self._table_surface)
        self.pack_start(self._scroller, True, True, 0)

        self._empty = Gtk.Label(label=_('No Activities were found.'))
        self._empty.set_xalign(0)
        self.pack_start(self._empty, False, False, 0)
        self.setup()

    def _table_scroll_event(self, _widget, event):
        adjustment = self._scroller.get_vadjustment()
        if adjustment is None:
            return False

        if event.direction == Gdk.ScrollDirection.SMOOTH:
            _delta_x, delta_y = event.get_scroll_deltas()
            delta = delta_y
        elif event.direction == Gdk.ScrollDirection.DOWN:
            delta = 1.0
        elif event.direction == Gdk.ScrollDirection.UP:
            delta = -1.0
        else:
            return False

        step = max(adjustment.get_step_increment(), 1.0)
        lower = adjustment.get_lower()
        upper = max(lower, adjustment.get_upper() - adjustment.get_page_size())
        value = adjustment.get_value() + delta * step * 3.0
        adjustment.set_value(min(max(value, lower), upper))
        return True

    def setup(self):
        for child in self._list.get_children():
            self._list.remove(child)
        self._rows = {}
        self._column_groups = [Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
                               for _ in range(4)]
        ratings = model.load_ratings()
        activities = model.list_activities()
        self._count_label.set_text(_('%d installed Activities') % len(activities))
        self._empty.set_visible(not activities)
        header = Gtk.Grid()
        header.set_border_width(style.DEFAULT_SPACING)
        header.set_column_spacing(0)
        header.set_hexpand(True)
        header.get_style_context().add_class('aspartame-table-header')
        for column, (text, width, align) in enumerate((
                (_('Version'), 140, 0.5),
                (_('Activity'), 430, 0.0),
                (_('Rating'), 330, 0.5),
                (_('Actions'), 90, 1.0))):
            actual_column = column
            label = Gtk.Label(label=text)
            label.set_xalign(align)
            label.set_halign(Gtk.Align.FILL)
            label.set_hexpand(column == 1)
            label.set_size_request(width, -1)
            header.attach(label, actual_column, 0, 1, 1)
            self._column_groups[column].add_widget(label)
        self._list.add(header)
        for activity in activities:
            help_id = None
            if aspartame_help:
                help_id = aspartame_help.register_activity(activity)
            row = self._make_row(activity, ratings.get(activity['id'], 0), help_id)
            self._list.add(row)
        # Sugar shows the section container, not its child widgets.
        # Explicitly reveal this section so it cannot appear as a blank panel.
        self.show_all()
        self._empty.set_visible(not activities)

    def apply(self):
        for activity_id, face_buttons in self._rows.values():
            rating = next((index for index, button in
                           enumerate(face_buttons, 1)
                           if button.get_active()), 0)
            if rating > 0:
                model.save_rating(activity_id, rating)

    def undo(self):
        self.setup()

    def _make_row(self, activity, rating, help_id=None):
        row = Gtk.ListBoxRow()
        row.get_style_context().add_class('aspartame-activity-row')
        row.set_size_request(-1, 84)
        grid = Gtk.Grid()
        grid.set_size_request(-1, 68)
        grid.set_border_width(style.DEFAULT_SPACING)
        grid.set_column_spacing(style.DEFAULT_SPACING * 2)
        grid.set_hexpand(True)
        row.add(grid)

        identity = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        identity.set_size_request(-1, 52)
        identity.set_hexpand(True)
        identity.set_halign(Gtk.Align.FILL)
        icon_name = activity.get('icon', '')
        icon_path = None
        if icon_name:
            for suffix in ('.svg', '.png'):
                candidate = os.path.join(activity['path'], 'activity', icon_name + suffix)
                if os.path.isfile(candidate):
                    icon_path = candidate
                    break
        if icon_path:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    icon_path, 42, 42, True)
                icon = Gtk.Image.new_from_pixbuf(pixbuf)
            except GLib.Error:
                icon = Gtk.Image.new_from_icon_name(
                    'activity-generic', Gtk.IconSize.DIALOG)
        else:
            icon = Gtk.Image.new_from_icon_name(
                'activity-generic', Gtk.IconSize.DIALOG)
        icon.set_pixel_size(aspartame_visual.ACTIVITY_ICON_SLOT - 10)
        icon.set_tooltip_text(_('Icon for %s') % activity['name'])
        icon.set_halign(Gtk.Align.CENTER)
        icon.set_valign(Gtk.Align.CENTER)
        icon.set_hexpand(False)
        icon.set_vexpand(False)
        icon_slot = Gtk.Box()
        icon_slot.set_size_request(aspartame_visual.ACTIVITY_ICON_SLOT, aspartame_visual.ACTIVITY_ICON_SLOT)
        icon_slot.set_halign(Gtk.Align.CENTER)
        icon_slot.set_valign(Gtk.Align.CENTER)
        icon_slot.pack_start(icon, False, False, 0)
        identity.pack_start(icon_slot, False, False, 0)

        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        labels.set_size_request(-1, 52)
        labels.set_hexpand(True)
        labels.set_halign(Gtk.Align.FILL)
        name = Gtk.Label(label=activity['name'])
        name.set_xalign(0)
        name.set_markup('<b><big>%s</big></b>' % escape(activity['name']))
        name.set_tooltip_text(_('Activity name: %s') % activity['name'])
        if aspartame_help and help_id:
            aspartame_help.guard(name, help_id)
        labels.pack_start(name, False, False, 0)
        summary = activity.get('summary', '')
        detail_text = summary or _('Open this Activity to begin.')
        detail = Gtk.Label(label=detail_text)
        detail.set_xalign(0)
        detail.set_hexpand(True)
        detail.set_halign(Gtk.Align.FILL)
        detail.set_line_wrap(True)
        detail.set_ellipsize(0)
        detail.set_tooltip_text(activity.get('url') or activity['path'])
        labels.pack_start(detail, False, False, 0)
        identity.pack_start(labels, True, True, 0)
        grid.attach(identity, 1, 0, 1, 1)
        self._column_groups[1].add_widget(identity)

        rating_box = FaceRating(rating=rating, context=activity['name'])
        rating_box.set_size_request(330, -1)
        rating_box.set_halign(Gtk.Align.CENTER)
        rating_box.set_margin_start(style.DEFAULT_SPACING * 2)
        rating_box.set_margin_end(style.DEFAULT_SPACING * 2)
        rating_box.connect('rating-changed', self._face_rating_changed, activity['id'])
        if aspartame_help and help_id:
            aspartame_help.guard(rating_box, help_id)
        grid.attach(rating_box, 2, 0, 1, 1)
        self._column_groups[2].add_widget(rating_box)

        version = activity['version'] or _('version unknown')
        detail_version = Gtk.Label()
        detail_version.set_markup('<b><big>%s</big></b>' % escape(version))
        detail_version.set_xalign(0.5)
        detail_version.set_halign(Gtk.Align.FILL)
        detail_version.set_hexpand(False)
        detail_version.set_size_request(140, -1)
        detail_version.set_tooltip_text(activity['path'])
        grid.attach(detail_version, 0, 0, 1, 1)
        self._column_groups[0].add_widget(detail_version)

        if activity['user']:
            action_label = _('Uninstall')
            action_tip = _('Uninstall this Activity and keep its work in the Journal.')
        elif activity.get('hidden'):
            action_label = _('Restore')
            action_tip = _('Show this Activity on Home again.')
        else:
            action_label = _('Hide')
            action_tip = _('Hide this system Activity from Home without deleting it.')
        remove = Gtk.Button(label=action_label)
        remove.get_style_context().add_class('aspartame-remove-button')
        remove.set_tooltip_text(action_tip)
        remove.connect('clicked', self._remove_clicked, activity)
        remove.set_size_request(64, -1)
        remove.set_halign(Gtk.Align.END)
        grid.attach(remove, 3, 0, 1, 1)
        self._column_groups[3].add_widget(remove)

        self._rows[activity['id']] = (activity['id'], rating_box)
        return row

    def _face_rating_changed(self, rating_box, rating, activity_id):
        if rating:
            model.save_rating(activity_id, rating)
        else:
            model.clear_rating(activity_id)

    def _remove_clicked(self, _button, activity):
        if not activity['user']:
            hidden = not activity.get('hidden', False)
            verb = _('Hide') if hidden else _('Restore')
            dialog = Gtk.MessageDialog(
                transient_for=self.get_toplevel(),
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text=_('%s %s?') % (verb, activity['name']))
            if hidden:
                dialog.format_secondary_text(_(
                    'This keeps the system Activity installed, but removes it '
                    'from Home for this user. Your Journal work is unchanged.'))
            else:
                dialog.format_secondary_text(_(
                    'This shows the installed Activity on Home again.'))
            response = dialog.run()
            dialog.destroy()
            if response != Gtk.ResponseType.OK:
                return
            model.set_activity_hidden(activity['id'], activity['version'], hidden)
            try:
                registry = bundleregistry.get_registry()
                registry.set_bundle_favorite(activity['id'],
                                             activity['version'], not hidden)
            except (ValueError, AttributeError):
                # The persisted state is still correct; the next shell start
                # will reload it even if this registry instance is unavailable.
                pass
            self.setup()
            return

        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=_('Uninstall %s?') % activity['name'])
        dialog.format_secondary_text(_(
            'The Activity bundle will be moved to a recoverable local '
            'quarantine. Your Journal work is unchanged.'))
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.OK:
            return
        try:
            model.remove_activity(activity['path'])
        except (OSError, PermissionError, ValueError) as error:
            error_dialog = Gtk.MessageDialog(
                transient_for=self.get_toplevel(),
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE,
                text=_('Activity could not be uninstalled'))
            error_dialog.format_secondary_text(str(error))
            error_dialog.run()
            error_dialog.destroy()
            return
        self.setup()
        success_dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text=_('Activity uninstalled'))
        success_dialog.format_secondary_text(
            _('%s was moved to the recoverable Activity quarantine.') %
            activity['name'])
        success_dialog.run()
        success_dialog.destroy()
