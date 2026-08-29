"""Small, Sugar-native metadata and interaction layer for What's This?."""

from dataclasses import dataclass
import logging
from pathlib import Path


LOG = logging.getLogger(__name__)
MODE_FILE = Path('/tmp/aspartame-whats-this')


@dataclass(frozen=True)
class Target:
    id: str
    title: str
    short_description: str
    explanation: str
    documentation: str | None = None


_TARGETS = {
    'org.aspartame.shell.help': Target(
        'org.aspartame.shell.help', "What's This?",
        'Learn what something on the screen does.',
        'Click an unfamiliar thing to learn what it does without opening it.'),
    'org.aspartame.shell.home': Target(
        'org.aspartame.shell.home', 'Home',
        'See the activities on your computer.',
        'Home is where you choose what you want to do. Your activities and the XO are here.',
        'shell#home'),
    'org.aspartame.shell.journal': Target(
        'org.aspartame.shell.journal', 'Journal',
        "Find things you've worked on.",
        "This is where things you've worked on are remembered. Open something here to continue where you left off.",
        'shell#journal'),
    'org.aspartame.shell.neighborhood': Target(
        'org.aspartame.shell.neighborhood', 'Neighborhood',
        'See people and computers around you.',
        'This shows people and computers around you that Aspartame can interact with.',
        'shell#neighborhood'),
    'org.aspartame.shell.group': Target(
        'org.aspartame.shell.group', 'Group',
        'See the people you are working with.',
        'This shows the people you have deliberately joined for shared work.',
        'shell#group'),
    'org.aspartame.shell.frame': Target(
        'org.aspartame.shell.frame', 'Frame',
        'Reach Sugar navigation and useful actions.',
        'The Frame appears around the edge when you need it. It gives you a way to move through Sugar without covering your activity.',
        'shell#frame'),
    'org.aspartame.count': Target(
        'org.aspartame.count', 'Count',
        'Count things arranged in rows, stacks, and layers.',
        'Draw the boxes you can see and add layers for boxes behind them. Count keeps track of the total automatically.',
        'count#activity'),
    'org.aspartame.count.total': Target(
        'org.aspartame.count.total', 'Total',
        'How many boxes are in the whole stack.',
        "This is the total number of boxes you've drawn across all the layers. Count updates it automatically whenever you add or remove a box.",
        'count#total'),
    'org.aspartame.count.layer.previous': Target(
        'org.aspartame.count.layer.previous', 'Previous layer',
        'Move toward the front of the stack.',
        'Show the layer closer to the front of the stack.',
        'count#previous-layer'),
    'org.aspartame.count.layer.next': Target(
        'org.aspartame.count.layer.next', 'Next layer',
        'Move deeper into the stack.',
        'Show the next row of boxes deeper in the stack.',
        'count#next-layer'),
    'org.aspartame.count.current-layer': Target(
        'org.aspartame.count.current-layer', 'Current layer',
        "See which row of boxes you're editing.",
        "You're editing one row of boxes at a time. For example, layer 2 of 4 is the second row behind the front row.",
        'count#current-layer'),
    'org.aspartame.count.layer.new': Target(
        'org.aspartame.count.layer.new', 'New layer',
        'Add an empty row behind the stack.',
        'Add an empty row of boxes behind the deepest row.',
        'count#new-layer'),
    'org.aspartame.count.layer.copy': Target(
        'org.aspartame.count.layer.copy', 'Copy layer',
        'Make another layer like this one.',
        'Make another layer with the same arrangement of boxes. This is useful when several rows in a stack have the same arrangement.',
        'count#copy-layer'),
}


def register_target(widget, target_id, **metadata):
    """Attach a semantic target to a widget without changing its behavior."""
    target_data = _TARGETS.get(target_id)
    if target_data is None:
        target_data = Target(target_id, metadata.get('title', target_id),
                             metadata.get('short_description', ''),
                             metadata.get('explanation', ''),
                             metadata.get('documentation'))
        _TARGETS[target_id] = target_data
    widget._aspartame_help_id = target_id
    return target_data


def register_activity(activity):
    bundle_id = activity.get('id', 'unknown')
    safe_id = ''.join(char if char.isalnum() else '-'
                      for char in bundle_id).strip('-').lower()
    target_id = 'org.aspartame.activity.' + safe_id
    title = activity.get('name', bundle_id)
    summary = activity.get('summary') or ('Open %s and explore what it can do.' % title)
    explanation = summary.rstrip('.')
    if explanation:
        explanation += '.'
    explanation += ' Open it from Home to begin, or use Journal to resume saved work.'
    _TARGETS[target_id] = Target(
        target_id, title, summary, explanation,
        'activities#' + safe_id)
    return target_id


def target(target_id):
    return _TARGETS.get(target_id)


def all_targets():
    return tuple(_TARGETS.values())


def is_active():
    return MODE_FILE.exists()


def set_active(active):
    if active:
        MODE_FILE.touch()
    else:
        try:
            MODE_FILE.unlink()
        except FileNotFoundError:
            pass


def toggle():
    active = not is_active()
    set_active(active)
    return active


def _show_explanation(widget, target_data):
    from gi.repository import Gio, Gtk
    from sugar3.graphics.palette import Palette, ToolInvoker

    palette = Palette(target_data.title)
    body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    body.set_border_width(12)
    label = Gtk.Label(label=target_data.explanation)
    label.set_line_wrap(True)
    label.set_max_width_chars(42)
    label.set_xalign(0)
    body.pack_start(label, False, False, 0)
    if target_data.documentation:
        more = Gtk.Button(label='See more…')
        more.set_relief(Gtk.ReliefStyle.NONE)
        more.set_halign(Gtk.Align.START)
        more.connect('clicked', _open_documentation, target_data.documentation)
        body.pack_start(more, False, False, 0)
    palette.set_content(body)
    invoker = ToolInvoker()
    invoker.attach_tool(widget)
    palette.props.invoker = invoker
    palette.popup(immediate=True)


def _open_documentation(_button, documentation):
    from gi.repository import Gio
    uri = 'file:///usr/share/aspartame/docs/universal-help.html#' + documentation.split('#', 1)[-1]
    Gio.AppInfo.launch_default_for_uri(uri, None)


def guard(widget, target_id):
    """Intercept pointer activation only while What's This? is active."""
    register_target(widget, target_id)
    widget.add_events(1 << 8)  # GDK_BUTTON_PRESS_MASK; avoids a Gdk import here.
    widget.connect('button-press-event', _guard_button_press)
    return widget


def _guard_button_press(widget, _event):
    if not is_active():
        return False
    target_id = getattr(widget, '_aspartame_help_id', None)
    target_data = target(target_id)
    if target_data is None:
        LOG.warning("No contextual-help metadata for %s", target_id)
        _show_missing(widget)
    else:
        _show_explanation(widget, target_data)
    set_active(False)
    return True


def _show_missing(widget):
    from sugar3.graphics.palette import Palette, ToolInvoker
    palette = Palette("What's This?")
    label = __import__('gi.repository', fromlist=['Gtk']).Gtk.Label(
        label="There isn't an explanation for this yet.")
    label.set_border_width(12)
    palette.set_content(label)
    invoker = ToolInvoker()
    invoker.attach_tool(widget)
    palette.props.invoker = invoker
    palette.popup(immediate=True)


def escape():
    set_active(False)
