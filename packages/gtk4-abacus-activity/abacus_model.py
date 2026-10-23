"""Abacus types and bead arithmetic, independent of GTK.

The type table follows the GTK3 reference (sugarlabs/abacus,
abacus_window.py): every rod has beads above the bar ("top", each worth
``factor`` units) and beads below it ("bottom", each worth one unit), and a
place value. Fraction rods (Caacupé, Cuisenaire) are tristate: their beads
can also be pushed down to count negatively.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Rod:
    top: int
    bottom: int
    factor: int
    place: Fraction
    tristate: bool = False

    @property
    def maximum(self):
        return self.top * self.factor + self.bottom


@dataclass(frozen=True)
class AbacusType:
    name: str
    label: str
    rods: tuple
    fractional: bool = False   # show values as mixed fractions
    colored: bool = False      # Cuisenaire colours, one per rod


def _positional(rods, top, bottom, factor, base, units=None):
    """A place-value abacus; ``units`` is the index of the ones rod."""
    units = rods - 1 if units is None else units
    return tuple(Rod(top, bottom, factor, Fraction(base) ** (units - i)) for i in range(rods))


def _listed(counts, places, tristate=False):
    return tuple(Rod(0, count, 1, Fraction(place), tristate) for count, place in zip(counts, places))


_FRACTION_COUNTS = (10, 10, 10, 10, 10, 10, 2, 3, 4, 5, 6, 8, 9, 10, 12)
_FRACTION_PLACES = (100000, 10000, 1000, 100, 10, 1, Fraction(1, 2), Fraction(1, 3),
                    Fraction(1, 4), Fraction(1, 5), Fraction(1, 6), Fraction(1, 8),
                    Fraction(1, 9), Fraction(1, 10), Fraction(1, 12))

TYPES = {t.name: t for t in (
    AbacusType("suanpan", "Suanpan", _positional(15, 2, 5, 5, 10)),
    AbacusType("soroban", "Soroban", _positional(15, 1, 4, 5, 10, units=7)),
    AbacusType("decimal", "Decimal", _positional(10, 0, 10, 1, 10)),
    AbacusType("nepohualtzintzin", "Nepohualtzintzin", _positional(13, 3, 4, 5, 20)),
    AbacusType("hexadecimal", "Hexadecimal", _positional(15, 1, 7, 8, 16)),
    AbacusType("binary", "Binary", _positional(15, 0, 1, 1, 2)),
    AbacusType("schety", "Schety", _listed(
        (10,) * 10 + (4, 10, 10, 10, 10),
        tuple(10 ** (9 - i) for i in range(10)) + (Fraction(1, 4), Fraction(1, 10),
                                                   Fraction(1, 100), Fraction(1, 1000),
                                                   Fraction(1, 10000)))),
    AbacusType("caacupe", "Caacupé", _listed(_FRACTION_COUNTS, _FRACTION_PLACES, True),
               fractional=True),
    AbacusType("cuisenaire", "Rods", _listed(
        range(1, 11), [Fraction(1, n) for n in range(1, 11)], True),
        fractional=True, colored=True),
)}
CUSTOM_LIMITS = {"rods": (1, 20), "top": (0, 4), "bottom": (1, 15), "factor": (1, 16),
                 "base": (2, 36)}
CUSTOM_DEFAULT = {"rods": 15, "top": 2, "bottom": 5, "factor": 5, "base": 10}


def custom_type(rods, top, bottom, factor, base):
    values = {"rods": rods, "top": top, "bottom": bottom, "factor": factor, "base": base}
    for key, value in values.items():
        low, high = CUSTOM_LIMITS[key]
        if not isinstance(value, int) or not low <= value <= high:
            raise ValueError("custom %s must be %d to %d" % (key, low, high))
    return AbacusType("custom", "Custom", _positional(rods, top, bottom, factor, base))


TYPE_ORDER = tuple(TYPES) + ("custom",)
LABELS = {name: TYPES[name].label for name in TYPES} | {"custom": "Custom"}


class Abacus:
    """Bead state for one abacus. Each rod holds ``[top, bottom]`` counts:
    beads pushed against the bar. A tristate rod's bottom count is signed."""

    def __init__(self, kind="suanpan", custom=None):
        self.custom = dict(CUSTOM_DEFAULT if custom is None else custom)
        self.set_type(kind)

    def set_type(self, kind):
        if kind == "custom":
            self.type = custom_type(**self.custom)
        elif kind in TYPES:
            self.type = TYPES[kind]
        else:
            raise ValueError("unknown abacus type %r" % kind)
        self.rods = [[0, 0] for _ in self.type.rods]

    def clear(self):
        self.rods = [[0, 0] for _ in self.type.rods]

    def count(self, index):
        top, bottom = self.rods[index]
        return top * self.type.rods[index].factor + bottom

    def set_count(self, index, count):
        """Set a rod to ``count`` units, filling top beads first."""
        rod = self.type.rods[index]
        low = -rod.bottom if rod.tristate else 0
        count = max(low, min(rod.maximum, count))
        if count < 0:
            self.rods[index] = [0, count]
            return
        top = min(rod.top, count // rod.factor) if rod.top else 0
        self.rods[index] = [top, min(rod.bottom, count - top * rod.factor)]

    def set_beads(self, index, top, bottom):
        rod = self.type.rods[index]
        low = -rod.bottom if rod.tristate else 0
        if not (0 <= top <= rod.top and low <= bottom <= rod.bottom):
            raise ValueError("rod %d out of range: %r" % (index, (top, bottom)))
        self.rods[index] = [top, bottom]

    def click_bead(self, index, region, bead, down=False):
        """Move bead ``bead`` (0 = nearest the bar) the way a finger would.

        On a tristate rod beads are numbered from the top, and ``down``
        pushes a resting bead below the rest line.
        """
        rod = self.type.rods[index]
        top, bottom = self.rods[index]
        if region == "top":
            top = bead if bead < top else bead + 1
        elif not rod.tristate:
            bottom = bead if bead < bottom else bead + 1
        elif bottom > 0 and bead < bottom:
            bottom = bead
        elif bottom < 0 and bead >= rod.bottom + bottom:
            bottom = -(rod.bottom - bead - 1)
        elif down:
            bottom = -(rod.bottom - bead)
        else:
            bottom = bead + 1
        self.set_beads(index, top, bottom)

    def value(self):
        return sum((self.count(i) * rod.place for i, rod in enumerate(self.type.rods)), Fraction(0))

    def maximum(self):
        return sum((rod.maximum * rod.place for rod in self.type.rods), Fraction(0))

    def set_value(self, number):
        """Show ``number`` on the abacus, greedily from the largest rod."""
        number = Fraction(number)
        if number < 0 or number > self.maximum():
            raise ValueError("%s does not fit on this abacus" % format_value(number))
        self.clear()
        for index, rod in enumerate(self.type.rods):
            count = min(rod.maximum, int(number // rod.place))
            self.set_count(index, count)
            number -= self.count(index) * rod.place
        if number:
            raise ValueError("%s cannot be shown exactly on this abacus" % format_value(self.value() + number))

    def value_text(self):
        return format_value(self.value(), self.type.fractional)

    def to_payload(self):
        return {"format": "aspartame-abacus-v2", "type": self.type.name,
                "custom": dict(self.custom), "rods": [list(r) for r in self.rods]}

    @classmethod
    def from_payload(cls, payload):
        if not isinstance(payload, dict):
            raise ValueError("abacus payload must be an object")
        if "values" in payload and "format" not in payload:
            # GTK4 Abacus 1: five decimal place-value rods.
            values = payload["values"]
            if not isinstance(values, list) or len(values) != 5 or \
                    not all(isinstance(v, int) and 0 <= v <= 9 for v in values):
                raise ValueError("values must contain five digits")
            abacus = cls("decimal")
            for offset, digit in enumerate(values):
                abacus.set_count(5 + offset, digit)
            return abacus
        if payload.get("format") != "aspartame-abacus-v2":
            raise ValueError("unsupported abacus format %r" % payload.get("format"))
        custom = payload.get("custom", CUSTOM_DEFAULT)
        if not isinstance(custom, dict) or set(custom) != set(CUSTOM_DEFAULT):
            raise ValueError("custom settings are malformed")
        custom_type(**custom)
        abacus = cls(payload.get("type"), custom)
        rods = payload.get("rods")
        if not isinstance(rods, list) or len(rods) != len(abacus.rods):
            raise ValueError("rod count does not match the abacus type")
        for index, pair in enumerate(rods):
            if not (isinstance(pair, list) and len(pair) == 2 and
                    all(isinstance(v, int) and not isinstance(v, bool) for v in pair)):
                raise ValueError("rod %d is malformed" % index)
            abacus.set_beads(index, *pair)
        return abacus


def format_value(value, fractional=False):
    """Exact text for a value: decimals where they terminate, else fractions."""
    value = Fraction(value)
    sign = "−" if value < 0 else ""
    value = abs(value)
    whole, part = divmod(value, 1)
    denominator = part.denominator
    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    if part == 0:
        return sign + "{:,}".format(int(whole))
    if fractional or denominator != 1:
        fraction = "%d/%d" % (part.numerator, part.denominator)
        return sign + (fraction if whole == 0 else "{:,} {}".format(int(whole), fraction))
    digits = 0
    while (part * 10 ** digits).denominator != 1:
        digits += 1
    text = "{:,}".format(int(whole)) + ("%.*f" % (digits, part))[1:]
    return sign + text


def parse_value(text):
    """Parse ``12``, ``0.25``, ``3/4`` or ``2 1/3`` into an exact Fraction."""
    text = text.strip().replace(",", "").replace("−", "-")
    if not text:
        raise ValueError("enter a number")
    parts = text.split()
    try:
        if len(parts) == 2 and "/" in parts[1]:
            whole = Fraction(parts[0])
            part = Fraction(parts[1])
            return whole + part if whole >= 0 else whole - part
        if len(parts) == 1:
            return Fraction(parts[0])
    except (ValueError, ZeroDivisionError):
        pass
    raise ValueError("%r is not a number" % text)
