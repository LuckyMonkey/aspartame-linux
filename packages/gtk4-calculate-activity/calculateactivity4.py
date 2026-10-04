"""Native GTK4 Calculate Activity for the modern Sugar Space.

Expressions are parsed with :mod:`ast` and evaluated by a whitelist, never
``eval``.  Closer to GTK3 Calculate than the first port: functions (sqrt,
trigonometry, logarithms, factorial, ...), the constants pi and e, ``ans``,
user variables (``x = 4``), ``^`` for powers, degree/radian modes, a history
list that can be clicked to reuse an expression, and specific error messages.
Plotting, number bases, and collaboration remain unported.

Journal payload history (append-only):

* v1: the plain expression text.  Still written when there is no history and
  no variables, so v1 readers and the guest probe see what they always did.
* v2 (2026-10-02): JSON ``{"version": 2, "expression", "history",
  "variables", "angle"}`` once the session has history or variables.
"""

import ast
import json
import math
import operator
from pathlib import Path

import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


MAX_MAGNITUDE = 1e100
MAX_HISTORY = 50
RESERVED = {"pi", "e", "ans", "tau"}


class CalcError(ValueError):
    """A user-facing explanation of why an expression has no value."""


def _power(base, exponent):
    # Refuse before computing: 2**9999999 would otherwise stall the Activity.
    if base not in (0, 1, -1) and abs(exponent) * math.log10(max(abs(base), 1e-300)) > 100:
        raise CalcError("Result is too large")
    return operator.pow(base, exponent)


def _factorial(value):
    if value != int(value) or value < 0:
        raise CalcError("factorial needs a whole number of 0 or more")
    if value > 69:
        raise CalcError("Result is too large")
    return math.factorial(int(value))


def _division(left, right):
    if right == 0:
        raise CalcError("Division by zero")
    return operator.truediv(left, right)


def _modulo(left, right):
    if right == 0:
        raise CalcError("Division by zero")
    return operator.mod(left, right)


_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub,
           ast.Mult: operator.mul, ast.Div: _division,
           ast.Pow: _power, ast.Mod: _modulo}
_UNOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _functions(angle):
    to_rad = math.radians if angle == "deg" else (lambda x: x)
    from_rad = math.degrees if angle == "deg" else (lambda x: x)
    return {
        "sqrt": math.sqrt, "abs": abs, "round": round,
        "floor": math.floor, "ceil": math.ceil, "exp": math.exp,
        "ln": math.log, "log": math.log10, "factorial": _factorial,
        "sin": lambda x: math.sin(to_rad(x)), "cos": lambda x: math.cos(to_rad(x)),
        "tan": lambda x: math.tan(to_rad(x)),
        "asin": lambda x: from_rad(math.asin(x)), "acos": lambda x: from_rad(math.acos(x)),
        "atan": lambda x: from_rad(math.atan(x)),
    }


def normalize(text):
    """Accept the symbols on the keypad and common typing habits."""
    for symbol, python in (("×", "*"), ("÷", "/"), ("−", "-"), ("^", "**"),
                           ("π", "pi"), ("√", "sqrt"), (",", ".")):
        text = text.replace(symbol, python)
    return text.strip()


def _evaluate(text, variables=None, angle="rad"):
    """Evaluate one expression; returns a number or raises CalcError."""
    names = {"pi": math.pi, "e": math.e, "tau": math.tau}
    names.update(variables or {})
    functions = _functions(angle)
    try:
        tree = ast.parse(normalize(text), mode="eval")
    except SyntaxError:
        raise CalcError("Check the expression: something is missing or extra") from None

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in names:
                return names[node.id]
            raise CalcError("Unknown name: %s" % node.id)
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNOPS:
            return _UNOPS[type(node.op)](visit(node.operand))
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in functions and len(node.args) == 1 and not node.keywords):
            return functions[node.func.id](visit(node.args[0]))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            raise CalcError("Unknown function: %s" % node.func.id)
        raise ValueError("unsupported expression")

    try:
        value = visit(tree)
    except ZeroDivisionError:
        raise CalcError("Division by zero") from None
    except OverflowError:
        raise CalcError("Result is too large") from None
    except (TypeError, ValueError) as error:
        if isinstance(error, CalcError):
            raise
        raise CalcError("That is outside what this function accepts") from None
    if isinstance(value, complex) or abs(value) > MAX_MAGNITUDE:
        raise CalcError("Result is too large")
    return value


def format_number(value):
    if isinstance(value, float):
        if value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return "%.12g" % value
    return str(value)


def parse_assignment(text):
    """Split ``name = expression``; returns (name or None, expression)."""
    if "=" in text and "==" not in text:
        name, _, expression = text.partition("=")
        name = name.strip()
        if name.isidentifier() and name not in RESERVED:
            return name, expression
        raise CalcError("Use a simple name on the left of =")
    return None, text


class CalculateActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Calculate")
        self.variables = {}
        self.history = []
        self.angle = "rad"
        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        root.set_margin_top(30); root.set_margin_bottom(30)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Calculate"])
        root.set_accessible_role(Gtk.AccessibleRole.GROUP)
        root.set_hexpand(True)
        root.set_vexpand(True)
        root.set_halign(Gtk.Align.FILL)
        root.set_valign(Gtk.Align.FILL)
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main.set_hexpand(True)
        main.set_vexpand(True)
        title = Gtk.Label(label="Calculate", xalign=0)
        title.add_css_class("title-1"); main.append(title)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter an expression, for example 2^10 or x = 4")
        self.entry.set_hexpand(True)
        self.entry.update_property([Gtk.AccessibleProperty.LABEL], ["Expression"])
        self.entry.connect("activate", self._calculate)
        main.append(self.entry)
        self.result = Gtk.Label(label="", xalign=0, selectable=True)
        self.result.add_css_class("calculate-result")
        self.result.update_property([Gtk.AccessibleProperty.LABEL], ["Result"])
        main.append(self.result)
        grid = Gtk.Grid(row_spacing=8, column_spacing=8)
        grid.set_hexpand(True)
        grid.set_vexpand(True)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        keys = ("7", "8", "9", "/", "(", "4", "5", "6", "*", ")",
                "1", "2", "3", "-", "^", "0", ".", "=", "+", "%")
        for index, label in enumerate(keys):
            grid.attach(self._key(label, label), index % 5, index // 5, 1, 1)
        for column, (label, text, name) in enumerate((("√", "sqrt(", "Square root"),
                                                      ("π", "pi", "Pi"),
                                                      ("ans", "ans", "Last answer"),
                                                      ("x²", "^2", "Square"),
                                                      ("⌫", None, "Delete last character"))):
            grid.attach(self._key(label, text, name), column, 4, 1, 1)
        main.append(grid)
        functions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for name in ("sin", "cos", "tan", "log", "ln", "factorial"):
            functions.append(self._key(name, name + "(", name))
        keypad = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        keypad.set_hexpand(True)
        keypad.set_vexpand(True)
        keypad.append(grid)
        keypad.append(functions)
        keypad_frame = Gtk.Frame(label="Keypad")
        keypad_frame.set_hexpand(True)
        keypad_frame.set_vexpand(True)
        keypad_frame.set_child(keypad)
        main.append(keypad_frame)
        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.angle_button = Gtk.ToggleButton(label="Radians")
        self.angle_button.set_tooltip_text("Switch trigonometry between radians and degrees")
        self.angle_button.update_property([Gtk.AccessibleProperty.LABEL], ["Angle unit"])
        self.angle_button.connect("toggled", self._angle_toggled)
        bottom.append(self.angle_button)
        clear = Gtk.Button(label="Clear")
        clear.connect("clicked", lambda *_: self._clear())
        bottom.append(clear)
        main.append(bottom)
        root.append(main)

        side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        heading = Gtk.Label(label="History", xalign=0); heading.add_css_class("heading")
        side.append(heading)
        self.history_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        self.history_list.set_activate_on_single_click(True)
        self.history_list.update_property([Gtk.AccessibleProperty.LABEL], ["Calculation history"])
        self.history_list.connect("row-activated", self._history_activated)
        scroll = Gtk.ScrolledWindow(); scroll.set_child(self.history_list)
        scroll.set_vexpand(True); scroll.set_hexpand(True); scroll.set_size_request(260, -1)
        side.append(scroll)
        clear_history = Gtk.Button(label="Clear history")
        clear_history.connect("clicked", lambda *_: self._set_history([]))
        side.append(clear_history)
        root.append(side)
        surface = Gtk.Frame(label="Calculator")
        surface.set_hexpand(True)
        surface.set_vexpand(True)
        surface.set_child(root)
        self.set_canvas(surface)
        self._install_css()

    def _key(self, label, text, name=None):
        button = Gtk.Button(label=label)
        button.set_size_request(64, 48)
        button.set_hexpand(True)
        button.set_vexpand(True)
        button.update_property([Gtk.AccessibleProperty.LABEL], [name or label])
        button.connect("clicked", self._button_clicked, label if text == label else text)
        return button

    def _install_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b".calculate-result { font-size: 28px; font-weight: bold; color: #2f88bd; } .calculate-error { color: #c0392b; font-size: 18px; } button { min-height: 38px; border-radius: 18px; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _button_clicked(self, _button, label):
        if label == "=":
            self._calculate()
            return
        if label is None:
            text = self.entry.get_text()
            self.entry.set_text(text[:-1])
        else:
            # Gtk.Editable.insert_text takes (text, position). Passing a
            # separate length raised TypeError inside the clicked handler on
            # every press, so the keypad silently inserted nothing.
            self.entry.insert_text(label, self.entry.get_text_length())
        self.entry.grab_focus()
        self.entry.set_position(-1)

    def _show(self, text, error=False):
        self.result.set_text(text)
        if error:
            self.result.add_css_class("calculate-error")
        else:
            self.result.remove_css_class("calculate-error")

    def _compute(self, text):
        name, expression = parse_assignment(text)
        variables = dict(self.variables)
        if self.history:
            variables["ans"] = self.history[-1][2]
        value = _evaluate(expression, variables, self.angle)
        if name:
            self.variables[name] = value
        return name, value

    def _calculate(self, *_args, record=True):
        text = self.entry.get_text().strip()
        if not text:
            return
        try:
            name, value = self._compute(text)
        except CalcError as error:
            self._show(str(error), error=True)
            return
        except ValueError:
            self._show("Invalid expression", error=True)
            return
        shown = format_number(value)
        self._show("%s = %s" % (name, shown) if name else shown)
        if record:
            self._set_history((self.history + [[text, shown, value]])[-MAX_HISTORY:])

    def _set_history(self, history):
        self.history = history
        while (row := self.history_list.get_row_at_index(0)) is not None:
            self.history_list.remove(row)
        for expression, shown, _value in reversed(self.history):
            row = Gtk.ListBoxRow()
            row.expression = expression
            label = Gtk.Label(label="%s = %s" % (expression, shown), xalign=0, wrap=True)
            row.set_child(label)
            row.update_property([Gtk.AccessibleProperty.LABEL], ["%s equals %s" % (expression, shown)])
            row.set_tooltip_text("Use this expression again")
            self.history_list.append(row)

    def _history_activated(self, _list, row):
        self.entry.set_text(row.expression)
        self.entry.grab_focus()
        self.entry.set_position(-1)

    def _angle_toggled(self, button):
        self.angle = "deg" if button.get_active() else "rad"
        button.set_label("Degrees" if self.angle == "deg" else "Radians")

    def _clear(self):
        self.entry.set_text(""); self._show(""); self.entry.grab_focus()

    # -- Journal -------------------------------------------------------

    def write_file(self, file_path):
        expression = self.entry.get_text()
        if not self.history and not self.variables and self.angle == "rad":
            payload = expression
        else:
            payload = json.dumps({"version": 2, "expression": expression,
                                  "history": self.history, "variables": self.variables,
                                  "angle": self.angle}, sort_keys=True) + "\n"
        with open(file_path, "w", encoding="utf-8") as stream:
            stream.write(payload)

    def read_file(self, file_path):
        """Restore the expression and calculate it from a Journal object."""
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            text = ""
        state = None
        if text.lstrip().startswith("{"):
            try:
                state = json.loads(text)
            except ValueError:
                state = None
        if isinstance(state, dict) and state.get("version") == 2:
            expression = str(state.get("expression") or "")
            self.variables = {str(k): v for k, v in (state.get("variables") or {}).items()
                              if str(k).isidentifier() and isinstance(v, (int, float)) and not isinstance(v, bool)} \
                if isinstance(state.get("variables"), dict) else {}
            history = state.get("history") if isinstance(state.get("history"), list) else []
            self._set_history([[str(h[0]), str(h[1]), h[2]] for h in history
                               if isinstance(h, list) and len(h) == 3 and isinstance(h[2], (int, float))
                               and not isinstance(h[2], bool)][-MAX_HISTORY:])
            self.angle_button.set_active(state.get("angle") == "deg")
        else:
            expression = text.strip()
        self.entry.set_text(expression)
        self._show("")
        if expression:
            # Recalculating on resume is not a new calculation; keep history as saved.
            self._calculate(record=False)
