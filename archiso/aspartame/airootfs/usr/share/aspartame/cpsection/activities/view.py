from gettext import gettext as _
import sys
from xml.sax.saxutils import escape

from gi.repository import Gtk

from sugar3.graphics import style
from jarabe.controlpanel.sectionview import SectionView

from . import model

sys.path.insert(0, '/usr/share/aspartame')
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
        css.load_from_data(b'''
            .aspartame-activity-row {
                border-bottom: 1px solid #c8d3d8;
                padding: 5px 0;
            }
            .aspartame-rating-face {
                font-size: 36px;
                font-family: "Noto Color Emoji", "Noto Emoji", sans-serif;
                min-width: 56px;
                min-height: 56px;
                padding: 0;
                border: none;
                border-radius: 28px;
                background: transparent;
                box-shadow: none;
            }
            .aspartame-rating-face.aspartame-rating-selected {
                border: 2px solid #30383c;
                background-color: #e6eef1;
            }
            .aspartame-remove-button {
                min-width: 92px;
                min-height: 38px;
                padding: 4px 14px;
                border: 0;
                border-radius: 20px;
                background-color: #202b31;
                color: #ffffff;
            }
            .aspartame-remove-button label {
                color: #ffffff;
                font-weight: bold;
            }
            .aspartame-table-header {
                background-color: #e6eef1;
                border-bottom: 2px solid #8fa3ad;
            }
        ''')
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
        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.NONE)
        self._list.set_vexpand(True)
        self._scroller.add(self._list)
        self.pack_start(self._scroller, True, True, 0)

        self._empty = Gtk.Label(label=_('No Activities were found.'))
        self._empty.set_xalign(0)
        self.pack_start(self._empty, False, False, 0)
        self.setup()

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
                (_('Version'), 120, 0.5),
                (_('Activity'), 360, 0.0),
                (_('Rating'), 250, 0.5),
                (_('Actions'), 100, 1.0))):
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
        grid = Gtk.Grid()
        grid.set_border_width(style.DEFAULT_SPACING)
        grid.set_column_spacing(0)
        grid.set_hexpand(True)
        row.add(grid)

        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        labels.set_size_request(360, -1)
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
        detail_text = summary or (_('%s, version %s') %
                                  (activity['name'],
                                   activity['version'] or _('unknown')))
        detail = Gtk.Label(label=detail_text)
        detail.set_xalign(0)
        detail.set_hexpand(True)
        detail.set_halign(Gtk.Align.FILL)
        detail.set_line_wrap(True)
        detail.set_ellipsize(0)
        detail.set_tooltip_text(activity.get('url') or activity['path'])
        labels.pack_start(detail, False, False, 0)
        grid.attach(labels, 1, 0, 1, 1)
        self._column_groups[1].add_widget(labels)

        rating_box = Gtk.Box(spacing=2)
        rating_box.set_size_request(250, -1)
        rating_box.set_hexpand(False)
        rating_box.set_halign(Gtk.Align.CENTER)
        faces = ('\U0001f62b', '\U0001f61f', '\U0001f610', '\U0001f642', '\U0001f604')
        labels_for_faces = ('Broken', 'Bad', 'Needs work', 'Good', 'Perfect')
        group = None
        face_buttons = []
        for index, (face, face_label) in enumerate(zip(faces, labels_for_faces), 1):
            if group is None:
                face_button = Gtk.RadioButton.new_with_label(None, face)
                group = face_button
            else:
                face_button = Gtk.RadioButton.new_with_label_from_widget(group, face)
            face_button.set_mode(False)
            face_button.set_relief(Gtk.ReliefStyle.NONE)
            face_button.set_can_focus(False)
            face_button.get_style_context().add_class('aspartame-rating-face')
            face_label_widget = face_button.get_child()
            if isinstance(face_label_widget, Gtk.Label):
                face_label_widget.set_family('Noto Color Emoji')
                face_label_widget.set_markup('<span size="xx-large">%s</span>' % face)
            face_button.set_tooltip_text(_('%s: %s') % (face_label, activity['name']))
            face_button.set_active(rating == index)
            face_button.connect('toggled', self._face_toggled,
                                activity['id'], index)
            if aspartame_help and help_id:
                aspartame_help.guard(face_button, help_id)
            face_buttons.append(face_button)
            rating_box.pack_start(face_button, False, False, 0)
        self._refresh_face_appearance(face_buttons)
        grid.attach(rating_box, 2, 0, 1, 1)
        self._column_groups[2].add_widget(rating_box)

        version = activity['version'] or _('version unknown')
        detail_version = Gtk.Label()
        detail_version.set_markup('<b><big>%s</big></b>' % escape(version))
        detail_version.set_xalign(0.5)
        detail_version.set_halign(Gtk.Align.FILL)
        detail_version.set_hexpand(False)
        detail_version.set_size_request(120, -1)
        detail_version.set_tooltip_text(activity['path'])
        grid.attach(detail_version, 0, 0, 1, 1)
        self._column_groups[0].add_widget(detail_version)

        remove = Gtk.Button(label=_('Remove'))
        remove.get_style_context().add_class('aspartame-remove-button')
        remove.set_tooltip_text(_('Remove this Activity for this user.'))
        remove.set_sensitive(activity['user'])
        if not activity['user']:
            remove.set_tooltip_text(_('System Activities cannot be removed from this user session.'))
        remove.connect('clicked', self._remove_clicked, activity)
        remove.set_size_request(100, -1)
        remove.set_halign(Gtk.Align.END)
        grid.attach(remove, 3, 0, 1, 1)
        self._column_groups[3].add_widget(remove)

        self._rows[activity['id']] = (activity['id'], face_buttons)
        return row

    def _refresh_face_appearance(self, buttons):
        for face_button in buttons:
            label = face_button.get_child()
            if isinstance(label, Gtk.Label):
                label.set_opacity(1.0 if face_button.get_active() else 0.38)
            context = face_button.get_style_context()
            if face_button.get_active():
                context.add_class('aspartame-rating-selected')
            else:
                context.remove_class('aspartame-rating-selected')

    def _face_toggled(self, button, activity_id, rating):
        self._refresh_face_appearance(button.get_parent().get_children())
        if button.get_active():
            model.save_rating(activity_id, rating)

    def _remove_clicked(self, _button, activity):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=_('Remove %s?') % activity['name'])
        dialog.format_secondary_text(_('The Activity will be moved to a recoverable local quarantine.'))
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
                text=_('Activity could not be removed'))
            error_dialog.format_secondary_text(str(error))
            error_dialog.run()
            error_dialog.destroy()
            return
        self.setup()
