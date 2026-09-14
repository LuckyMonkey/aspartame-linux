"""Small native GTK4 calculator Activity for the modern Sugar Space."""

import ast
import operator

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub,
           ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.Pow: operator.pow}
_UNOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _evaluate(text):
    tree = ast.parse(text, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNOPS:
            return _UNOPS[type(node.op)](visit(node.operand))
        raise ValueError("unsupported expression")

    value = visit(tree)
    if abs(value) > 1e100:
        raise ValueError("result is too large")
    return value


class CalculateActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Calculate")
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        root.set_margin_top(30); root.set_margin_bottom(30)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Calculate"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        title = Gtk.Label(label="Calculate", xalign=0)
        title.add_css_class("title-1"); root.append(title)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter an expression")
        self.entry.set_hexpand(True)
        self.entry.update_property([Gtk.AccessibleProperty.LABEL], ["Expression"])
        self.entry.connect("activate", self._calculate)
        root.append(self.entry)
        self.result = Gtk.Label(label="", xalign=0)
        self.result.add_css_class("calculate-result")
        self.result.update_property([Gtk.AccessibleProperty.LABEL], ["Result"])
        root.append(self.result)
        grid = Gtk.Grid(row_spacing=8, column_spacing=8)
        for index, label in enumerate(("7", "8", "9", "/", "4", "5", "6", "*",
                                       "1", "2", "3", "-", "0", ".", "=", "+")):
            button = Gtk.Button(label=label)
            button.set_size_request(74, 52)
            button.update_property([Gtk.AccessibleProperty.LABEL], [label])
            button.connect("clicked", self._button_clicked, label)
            grid.attach(button, index % 4, index // 4, 1, 1)
        root.append(grid)
        clear = Gtk.Button(label="Clear")
        clear.connect("clicked", lambda *_: self._clear())
        root.append(clear)
        self.set_canvas(root)
        self._install_css()

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b".calculate-result { font-size: 28px; font-weight: bold; color: #2f88bd; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _button_clicked(self, _button, label):
        if label == "=":
            self._calculate()
        else:
            self.entry.insert_text(label, self.entry.get_text_length(), None)
            self.entry.grab_focus()

    def _calculate(self, *_args):
        try:
            value = _evaluate(self.entry.get_text().strip())
            self.result.set_text(str(value))
        except (SyntaxError, ValueError, ZeroDivisionError):
            self.result.set_text("Invalid expression")

    def _clear(self):
        self.entry.set_text(""); self.result.set_text(""); self.entry.grab_focus()

    def write_file(self, file_path):
        with open(file_path, "w", encoding="utf-8") as stream:
            stream.write(self.entry.get_text())
