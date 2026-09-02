"""System-wide Sugar Select-a-Thing interaction layer.

This is deliberately separate from the Help Activity. Jarabe owns selecting
and safely inspecting a visible object; the help registry supplies language
and the Help Activity supplies deeper documentation.
"""

import logging

from gi.repository import Gdk, Gtk

import aspartame_help

LOG = logging.getLogger(__name__)
_SELECTED = None


def _walk(widget):
    yield widget
    children = []
    for method in ('get_children', 'get_child'):
        try:
            value = getattr(widget, method)()
        except (AttributeError, TypeError):
            continue
        if method == 'get_child':
            value = [value] if value is not None else []
        children.extend(value)
    seen = set()
    for child in children:
        if child is not None and id(child) not in seen:
            seen.add(id(child))
            yield from _walk(child)


def _selectable(widget):
    if not getattr(widget, 'get_visible', lambda: True)():
        return False
    if not getattr(widget, 'get_sensitive', lambda: True)():
        return False
    return (getattr(widget, '_aspartame_help_id', None) is not None or
            getattr(widget, 'get_can_focus', lambda: False)())


def _targets(window):
    result = []
    seen = set()
    for widget in _walk(window):
        if _selectable(widget) and id(widget) not in seen:
            result.append(widget)
            seen.add(id(widget))
    return result


def _accessible_text(widget):
    try:
        accessible = widget.get_accessible()
        name = accessible.get_name()
        description = accessible.get_description()
        if name or description:
            return name or 'This control', description or 'This control can be used here.'
    except (AttributeError, TypeError):
        pass
    try:
        text = widget.get_tooltip_text()
        if text:
            return text.split(' - ', 1)[0], text
    except (AttributeError, TypeError):
        pass
    return None, None


def _select(window, widget):
    global _SELECTED
    _SELECTED = widget
    target_id = getattr(widget, '_aspartame_help_id', None)
    if target_id and aspartame_help.target(target_id):
        aspartame_help._explain_widget(widget)
        return
    title, description = _accessible_text(widget)
    if title and description:
        aspartame_help._show_explanation(
            widget, aspartame_help.Target('runtime.accessible', title,
                                          description, description))
    else:
        aspartame_help._show_missing(widget)
    aspartame_help.set_active(False)
    if not title:
        LOG.info('No contextual-help metadata for selected object')


def _move(window, backwards=False):
    global _SELECTED
    widgets = _targets(window)
    if not widgets:
        aspartame_help._show_missing(window)
        return True
    try:
        index = widgets.index(_SELECTED)
    except ValueError:
        index = 0 if backwards else -1
    step = -1 if backwards else 1
    _SELECTED = widgets[(index + step) % len(widgets)]
    try:
        _SELECTED.grab_focus()
    except (AttributeError, TypeError):
        pass
    return True


def _event(window, event):
    if not aspartame_help.is_active():
        return False
    if event.type == Gdk.EventType.KEY_PRESS:
        if event.keyval == Gdk.KEY_Escape:
            aspartame_help.escape()
            return True
        if event.keyval in (Gdk.KEY_Tab, Gdk.KEY_Down, Gdk.KEY_Right):
            return _move(window, bool(event.state & Gdk.ModifierType.SHIFT_MASK))
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
            if _SELECTED is None:
                return _move(window)
            _select(window, _SELECTED)
            return True
        # While selecting, never leak a key into the selected Activity.
        return True
    if event.type == Gdk.EventType.BUTTON_PRESS:
        widget = Gtk.get_event_widget(event)
        if widget is None:
            aspartame_help._show_missing(window)
        else:
            _select(window, widget)
        return True
    return False


def install_window(window):
    """Install Select-a-Thing before child activation on one Sugar window."""
    if getattr(window, '_aspartame_select_a_thing_installed', False):
        return
    window._aspartame_select_a_thing_installed = True
    window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.KEY_PRESS_MASK)
    # Gtk's generic event signal is the capture point. Returning True here
    # prevents an Activity launch/button activation while inspection is active.
    window.connect('event', _event)


def reset():
    global _SELECTED
    _SELECTED = None
