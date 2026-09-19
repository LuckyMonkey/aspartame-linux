# Copyright (C) 2008-2013 Sugar Labs
# Copyright (C) 2026 Aspartame contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Sugar Home's installed Activity list, using native GTK4 list models."""

import logging
import os
from gettext import gettext as _

from gi.repository import Gdk, Gio, GObject, Gtk, Pango

from sugar4 import profile
from sugar4.activity import activityfactory
from sugar4.datastore import datastore
from sugar4.graphics import style
from sugar4.graphics.alert import Alert
from sugar4.graphics.icon import Icon
from sugar4.graphics.palette import Palette
from sugar4.graphics.palettemenu import PaletteMenuBox, PaletteMenuItem

from jarabe.desktop.activitystate import search_terms_match
from jarabe.desktop import activitypresentation
from jarabe.journal import misc
from jarabe.model import bundleregistry, desktop
from jarabe.util.normalize import normalize_string


def register_target(widget, target_id, **metadata):
    """Attach optional Help metadata without importing GTK3 view modules."""
    widget._sugar_help_target = (target_id, metadata)


def supports_bundle(bundle):
    """Return whether the GTK4 launcher can resolve this bundle command."""
    try:
        activityfactory.get_command(bundle)
    except (AttributeError, RuntimeError, ValueError, TypeError):
        return False
    return True


def explain_unsupported(bundle):
    """Explain why a bundle remains assigned to the Classic Space."""
    try:
        activityfactory.get_command(bundle)
    except Exception as error:
        return str(error)
    return _('This activity is not available in the GTK4 Space.')


def _bundle_icon_file(bundle):
    """Resolve an Activity icon without assuming a particular bundle layout.

    Older bundle implementations return an absolute filename while newer
    metadata readers may return a basename.  Home and palettes must share the
    same resolution path so a layout difference cannot produce a blank icon in
    only one surface.
    """
    value = bundle.get_icon()
    if not value:
        return None
    candidates = [value]
    root = bundle.get_path()
    if not os.path.isabs(value):
        candidates.extend((
            os.path.join(root, value),
            os.path.join(root, value + '.svg'),
            os.path.join(root, 'activity', value),
            os.path.join(root, 'activity', value + '.svg'),
        ))
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    logging.warning('Activity icon is missing: bundle=%s icon=%s',
                    bundle.get_bundle_id(), value)
    return None


def _set_bundle_icon(icon, bundle, color=None):
    """Set a bundle icon, retaining a visible Sugar fallback on bad metadata."""
    icon_file = _bundle_icon_file(bundle)
    if icon_file is not None:
        icon.props.file = icon_file
        if color is not None:
            icon.props.xo_color = color
        return
    icon.props.file = None
    icon.props.icon_name = 'activity-start'
    if color is not None:
        icon.props.xo_color = color


class ActivityItem(GObject.GObject):
    def __init__(self, bundle):
        super().__init__()
        self.bundle = bundle
        self.bundle_id = bundle.get_bundle_id()
        self.name = bundle.get_name()
        self.fields = tuple(normalize_string(str(value or '')) for value in (
            self.name, bundle.get_summary(), ' '.join(bundle.get_tags() or [])))


class ActivityRow(Gtk.Box):
    """A reusable factory row; actions retain native button semantics."""

    def __init__(self, owner):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL,
                         spacing=style.DEFAULT_SPACING)
        self.owner = owner
        self.item = None
        self.palette = None
        self.set_focusable(True)
        self.set_accessible_role(Gtk.AccessibleRole.BUTTON)
        self.add_css_class('activity-list-row')
        self.set_margin_start(style.DEFAULT_SPACING)
        self.set_margin_end(style.DEFAULT_SPACING)
        self.set_margin_top(style.DEFAULT_PADDING)
        self.set_margin_bottom(style.DEFAULT_PADDING)

        self.favorites = Gtk.Box(spacing=style.DEFAULT_PADDING)
        self.append(self.favorites)
        self.icon = Icon(pixel_size=style.STANDARD_ICON_SIZE)
        self.append(self.icon)
        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        labels.set_hexpand(True)
        self.name = Gtk.Label(xalign=0)
        self.name.set_ellipsize(Pango.EllipsizeMode.END)
        self.summary = Gtk.Label(xalign=0)
        self.summary.set_ellipsize(Pango.EllipsizeMode.END)
        self.summary.add_css_class('dim-label')
        labels.append(self.name)
        labels.append(self.summary)
        self.append(labels)
        # Launch gestures belong to non-interactive content so favorite and
        # action controls retain their own click semantics.
        for target in (self.icon, labels):
            primary = Gtk.GestureClick(button=Gdk.BUTTON_PRIMARY)
            primary.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
            primary.connect('pressed', self._primary_pressed)
            target.add_controller(primary)
        self.status = Gtk.Label(xalign=0)
        self.status.set_width_chars(16)
        self.append(self.status)
        self.version = Gtk.Label(xalign=1)
        self.version.set_width_chars(6)
        self.append(self.version)

        self.actions = Gtk.Button()
        self.actions.set_child(Icon(icon_name='emblem-down',
                                    pixel_size=style.SMALL_ICON_SIZE))
        self.actions.add_css_class('sugar-tool-button')
        self.actions.connect('clicked', self._actions_clicked)
        self.append(self.actions)
        click = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
        click.connect('pressed', self._secondary_pressed)
        self.add_controller(click)
        keys = Gtk.EventControllerKey()
        keys.connect('key-pressed', self._key_pressed)
        self.add_controller(keys)

    def bind(self, item):
        self.unbind()
        self.item = item
        bundle = item.bundle
        self.name.set_text(item.name)
        self.summary.set_text(bundle.get_summary() or '')
        _set_bundle_icon(self.icon, bundle)
        self.version.set_text(str(bundle.get_activity_version()))
        self.actions.update_property([Gtk.AccessibleProperty.LABEL],
                                     [_('Actions for %s') % item.name])
        register_target(self.actions, 'home.activity.actions.' + item.bundle_id,
                        title=_('Activity actions'), explanation=_(
                            'Start or resume this activity, or choose whether '
                            'it appears among your Home favorites.'))
        for view in range(desktop.get_number_of_views()):
            favorite = self.owner.registry.is_bundle_favorite(
                item.bundle_id, bundle.get_activity_version(), view)
            button = Gtk.ToggleButton(active=favorite)
            button.add_css_class('sugar-tool-button')
            image = Icon(icon_name=desktop.get_favorite_icons()[view],
                         pixel_size=style.SMALL_ICON_SIZE)
            if favorite:
                image.props.xo_color = profile.get_color()
            button.set_child(image)
            button.update_property([Gtk.AccessibleProperty.LABEL],
                                   [_('%s: favorite in %s') % (
                                       item.name, desktop.get_view_labels()[view])])
            button.connect('toggled', self._favorite_toggled, view)
            self.favorites.append(button)
        self.refresh_state()

    def unbind(self):
        if self.palette is not None:
            self.palette.popdown(immediate=True)
            if self.palette.get_parent() is not None:
                self.palette.unparent()
            self.palette = None
        while self.favorites.get_first_child() is not None:
            self.favorites.remove(self.favorites.get_first_child())
        self.item = None

    def refresh_state(self):
        if self.item is None:
            return
        state = self.owner.presentation.present(self.icon, self.item.bundle_id)
        description = activitypresentation.STATE_LABELS[state]
        if not supports_bundle(self.item.bundle):
            description = _('Classic Space activity')
        self.status.set_text(description)
        self.update_property([Gtk.AccessibleProperty.LABEL,
                              Gtk.AccessibleProperty.DESCRIPTION],
                             [self.item.name, description])

    def _favorite_toggled(self, button, view):
        if self.item is not None:
            self.owner.registry.set_bundle_favorite(
                self.item.bundle_id, self.item.bundle.get_activity_version(),
                button.get_active(), view)

    def _actions_clicked(self, button):
        self.show_palette()

    def _secondary_pressed(self, gesture, count, x, y):
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)
        self.show_palette()

    def _primary_pressed(self, gesture, count, x, y):
        """Launch a row from a primary pointer click."""
        if count != 1 or self.item is None:
            return
        logging.info('Home List primary activation: %s', self.item.bundle_id)
        self.owner.run_activity(self.item.bundle_id, True)

    def _key_pressed(self, controller, keyval, keycode, modifiers):
        if keyval == Gdk.KEY_Menu or (keyval == Gdk.KEY_F10 and
                                     modifiers & Gdk.ModifierType.SHIFT_MASK):
            self.show_palette()
            return True
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
            if self.item is not None:
                self.owner.run_activity(self.item.bundle_id, True)
                return True
        return False

    def show_palette(self):
        if self.item is None:
            return
        if self.palette is not None:
            self.palette.popdown(immediate=True)
            self.palette.unparent()
        self.palette = ActivityListPalette(self.item.bundle)
        self.palette.connect('erase-activated', self.owner._erase_requested)
        self.palette.set_parent(self.actions)
        self.palette.popup(immediate=True)


class ActivitiesList(Gtk.Box):
    __gtype_name__ = 'SugarActivitiesList'
    __gsignals__ = {'clear-clicked': (GObject.SignalFlags.RUN_FIRST, None, ())}

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.registry = bundleregistry.get_registry()
        self.presentation = activitypresentation.get_model()
        self._query = ''
        self._rows = set()
        self._alert = None
        self._store = Gio.ListStore.new(ActivityItem)
        self._filter = Gtk.CustomFilter.new(self._matches)
        self._filtered = Gtk.FilterListModel.new(self._store, self._filter)
        self._selection = Gtk.SingleSelection.new(self._filtered)
        self._selection.set_autoselect(True)

        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self._setup_row)
        factory.connect('bind', self._bind_row)
        factory.connect('unbind', self._unbind_row)
        factory.connect('teardown', self._teardown_row)
        self._list_view = Gtk.ListView.new(self._selection, factory)
        self._list_view.set_single_click_activate(True)
        self._list_view.set_show_separators(True)
        self._list_view.connect('activate', self._activated)
        self._list_view.update_property([Gtk.AccessibleProperty.LABEL],
                                        [_('Installed activities')])
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_child(self._list_view)

        self._result_status = Gtk.Label(xalign=0)
        self._result_status.add_css_class('dim-label')
        self._result_status.set_margin_start(style.DEFAULT_SPACING)
        self._result_status.set_margin_top(style.DEFAULT_PADDING)
        self._result_status.update_property(
            [Gtk.AccessibleProperty.LABEL], [_('Activity list status')])

        self._empty = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                              spacing=style.DEFAULT_SPACING,
                              halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        self._empty.append(Gtk.Label(label=_('No matching activities')))
        clear = Gtk.Button(label=_('Clear search'))
        clear.connect('clicked', lambda button: self.emit('clear-clicked'))
        self._empty.append(clear)
        self._stack = Gtk.Stack(vexpand=True)
        self._stack.add_named(scrolled, 'list')
        self._stack.add_named(self._empty, 'empty')
        self.append(self._result_status)
        self.append(self._stack)
        self._filtered.connect('items-changed', self._results_changed)
        for signal in ('bundle-added', 'bundle-changed', 'bundle-removed'):
            self.registry.connect(signal, self._registry_changed)
        desktop.get_model().connect('desktop-view-icons-changed',
                                     self._registry_changed)
        self.presentation.connect('changed', self._state_changed)
        self._reload()

    def _setup_row(self, factory, list_item):
        row = ActivityRow(self)
        self._rows.add(row)
        list_item.set_child(row)

    def _bind_row(self, factory, list_item):
        list_item.get_child().bind(list_item.get_item())

    def _unbind_row(self, factory, list_item):
        # GTK4 can unset the child before these run while it recycles rows,
        # so the factory callbacks have to tolerate an absent one.
        row = list_item.get_child()
        if row is not None:
            row.unbind()

    def _teardown_row(self, factory, list_item):
        row = list_item.get_child()
        if row is None:
            return
        row.unbind()
        self._rows.discard(row)

    def _registry_changed(self, *args):
        self._reload()

    def _reload(self):
        selected = self._selection.get_selected_item()
        selected_id = selected.bundle_id if selected is not None else None
        items = []
        for bundle in self.registry:
            try:
                if bundle.get_show_launcher() and bundle.get_bundle_id() != 'org.laptop.JournalActivity':
                    items.append(ActivityItem(bundle))
            except (AttributeError, TypeError, ValueError, OSError):
                logging.exception('Invalid Activity metadata in Home inventory: %r', bundle)
        items.sort(key=lambda item: (normalize_string(item.name), item.bundle_id))
        self._store.splice(0, self._store.get_n_items(), items)
        if selected_id is not None:
            for position in range(self._filtered.get_n_items()):
                if self._filtered.get_item(position).bundle_id == selected_id:
                    self._selection.set_selected(position)
                    break
        self._results_changed()

    def _matches(self, item):
        return search_terms_match(self._query, item.fields)

    def set_filter(self, query):
        self._query = normalize_string(query.strip())
        self._filter.changed(Gtk.FilterChange.DIFFERENT)
        self._results_changed()
        return self._filtered.get_n_items()

    def _results_changed(self, *args):
        count = self._filtered.get_n_items()
        total = self._store.get_n_items()
        if self._query:
            self._result_status.set_text(
                _('%d matching activities (of %d)') % (count, total))
        else:
            self._result_status.set_text(
                _('%d installed activities') % total)
        self._stack.set_visible_child_name('list' if count else 'empty')

    def _state_changed(self, presentation):
        for row in self._rows:
            row.refresh_state()

    def _activated(self, view, position):
        item = self._filtered.get_item(position)
        if item is not None:
            self.run_activity(item.bundle_id, True)

    def grab_focus(self):
        if self._filtered.get_n_items():
            return self._list_view.grab_focus()
        return self._empty.child_focus(Gtk.DirectionType.TAB_FORWARD)

    def get_activities_selected(self):
        return [{'name': self._filtered.get_item(index).name,
                 'bundle_id': self._filtered.get_item(index).bundle_id}
                for index in range(self._filtered.get_n_items())]

    def run_activity(self, bundle_id, resume_mode):
        bundle = self.registry.get_bundle(bundle_id)
        if bundle is None:
            self._reload()
            return
        if not supports_bundle(bundle):
            self._show_error(_('Open in the Classic Space'),
                             explain_unsupported(bundle))
            return
        if self.presentation.activate_running(bundle_id):
            return
        if not resume_mode:
            misc.launch(bundle)
            return

        # Each request owns its bundle id; overlapping async replies cannot
        # resume the wrong Activity after a second keyboard activation.
        def reply(entries, total_count):
            matching = [entry for entry in entries
                        if entry.get('activity') == bundle_id]
            if matching:
                misc.resume(matching[0], bundle_id)
            else:
                misc.launch(bundle)

        def failed(error):
            logging.error('Home could not read recent Journal entry: %s', error)
            self._show_error(_('Cannot resume activity'), str(error))

        datastore.find({'activity': bundle_id}, sorting=['-timestamp'], limit=1,
                       properties=['uid', 'title', 'icon-color', 'activity',
                                   'activity_id', 'mime_type', 'mountpoint'],
                       reply_handler=reply, error_handler=failed)

    def add_alert(self, alert):
        self.remove_alert()
        self._alert = alert
        self.prepend(alert)

    def remove_alert(self):
        if self._alert is not None:
            self.remove(self._alert)
            self._alert = None

    def _show_error(self, title, message):
        alert = Alert()
        alert.props.title = title
        alert.props.msg = message
        alert.add_button(Gtk.ResponseType.CLOSE, _('Close'),
                         Icon(icon_name='dialog-cancel'))
        alert.connect('response', lambda *args: self.remove_alert())
        self.add_alert(alert)

    def _erase_requested(self, palette, bundle_id):
        bundle = self.registry.get_bundle(bundle_id)
        if bundle is None or not bundle.is_user_activity():
            return
        alert = Alert()
        alert.props.title = _('Remove activity')
        alert.props.msg = _('Uninstall %s? Your Journal entries will be kept.') % bundle.get_name()
        alert.add_button(Gtk.ResponseType.CANCEL, _('Keep'), Icon(icon_name='dialog-cancel'))
        alert.add_button(Gtk.ResponseType.OK, _('Remove'), Icon(icon_name='list-remove'))

        def response(alert, response_id):
            self.remove_alert()
            if response_id != Gtk.ResponseType.OK:
                return
            current = self.registry.get_bundle(bundle_id)
            if current is not None and current.is_user_activity():
                try:
                    self.registry.uninstall(current, delete_profile=False)
                except (OSError, ValueError, RuntimeError) as error:
                    logging.exception('Activity uninstall failed: %s', bundle_id)
                    self._show_error(_('Could not remove activity'), str(error))
        alert.connect('response', response)
        self.add_alert(alert)


class ActivityListPalette(Palette):
    __gsignals__ = {'erase-activated': (GObject.SignalFlags.RUN_FIRST, None, (str,))}

    def __init__(self, bundle):
        palette_icon = Icon(xo_color=profile.get_color(),
                            pixel_size=style.STANDARD_ICON_SIZE)
        _set_bundle_icon(palette_icon, bundle, profile.get_color())
        super().__init__(primary_text=bundle.get_name(),
                         icon=palette_icon)
        box = PaletteMenuBox()
        self.set_content(box)
        supported = supports_bundle(bundle)
        start = PaletteMenuItem(_('Start new'), icon_name='activity-start')
        start.set_sensitive(supported)
        start.connect('activate', lambda item: misc.launch(bundle))
        box.append_item(start)
        if not supported:
            self.set_secondary_text(explain_unsupported(bundle))
        registry = bundleregistry.get_registry()
        for view in range(desktop.get_number_of_views()):
            favorite = registry.is_bundle_favorite(bundle.get_bundle_id(),
                                                   bundle.get_activity_version(), view)
            label = (_('Remove favorite from %s') if favorite else _('Make favorite in %s'))
            item = PaletteMenuItem(label % desktop.get_view_labels()[view],
                                   icon_name=desktop.get_favorite_icons()[view])
            item.connect('activate', self._favorite, registry, bundle, view, not favorite)
            box.append_item(item)
        if bundle.is_user_activity():
            remove = PaletteMenuItem(_('Remove'), icon_name='list-remove')
            remove.set_sensitive(os.access(bundle.get_path(), os.W_OK) and
                                 not registry.is_activity_protected(bundle.get_bundle_id()))
            remove.connect('activate', lambda item: self.emit('erase-activated', bundle.get_bundle_id()))
            box.append_item(remove)

    def _favorite(self, item, registry, bundle, view, favorite):
        registry.set_bundle_favorite(bundle.get_bundle_id(),
                                     bundle.get_activity_version(), favorite, view)
        self.popdown(immediate=True)
