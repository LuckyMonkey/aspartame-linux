#!/usr/bin/env bash
set -u

root=${GTK4_ROOT:-}
failures=0
printf 'Aspartame GTK4 probe\n'

if [ -n "$root" ] && [ -d "$root" ]; then
    printf 'Toolkit checkout: %s\n' "$root"
else
    echo 'Toolkit checkout: NOT SET (set GTK4_ROOT to an upstream checkout)'
    failures=$((failures + 1))
fi

python3 - <<'PY' || failures=$((failures + 1))
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
print('GTK4 PyGObject: PASS (%d.%d.%d)' % (
    Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version()))
PY

if [ -n "$root" ] && [ -f "$root/pyproject.toml" ]; then
    if PYTHONPATH="$root/src${PYTHONPATH:+:$PYTHONPATH}" python3 - <<'PY'
import sugar4
print('sugar4 import: PASS (%s)' % sugar4.__file__)
PY
    then :; else
        echo 'sugar4 import: FAIL (checkout is not installed or importable)'
        failures=$((failures + 1))
    fi
else
    echo 'sugar4 import: SKIP (no upstream checkout)'
fi

if [ "$failures" -eq 0 ]; then
    echo 'Result: PASS (toolkit probe only; not a GTK4 shell boot claim)'
else
    echo "Result: INCOMPLETE ($failures checks failed or were unavailable)"
fi
exit "$failures"
