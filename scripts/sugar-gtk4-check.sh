#!/usr/bin/env bash
set -u
export ASPARTAME_GTK4_PREVIEW=1
project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export PYTHONPATH="$project_root/sugar-overlay/src${PYTHONPATH:+:$PYTHONPATH}"
root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
toolkit="$root/sources/sugar-toolkit-gtk4"; venv="$root/venv"; fail=0
echo "Aspartame GTK4 preview checks"
[ -f "$root/PINS.tsv" ] && echo "pins: PASS" || { echo "pins: FAIL"; fail=$((fail+1)); }
if [ -x "$venv/bin/python" ]; then PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" "$venv/bin/python" -c 'import gi; gi.require_version("Gtk", "4.0"); from gi.repository import Gtk; import sugar4; print("GTK4/PyGObject/sugar4: PASS", "%d.%d.%d" % (Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version()), sugar4.__file__)' || fail=$((fail+1)); else echo "preview venv: FAIL"; fail=$((fail+1)); fi
if [ -d "$toolkit/.git" ] && [ -x "$venv/bin/python" ]; then
    PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" "$venv/bin/python" -m pytest -q "$toolkit/tests/test_icon.py" "$toolkit/tests/test_iconentry.py" || fail=$((fail+1))
elif [ -d "$toolkit/.git" ]; then
    echo "preview venv: FAIL"
    fail=$((fail+1))
else
    echo "toolkit checkout: FAIL"
    fail=$((fail+1))
fi
[ -f "$root/build/sugar-ext/build.ninja" ] && echo "sugar-ext configured: PASS" || echo "sugar-ext configured: NOT YET"
grep -q 'PKG_CHECK_MODULES(SHELL, gtk4)' "$root/sources/sugar/configure.ac" 2>/dev/null && echo "shell GTK4 configure gate: PASS" || { echo "shell GTK4 configure gate: FAIL"; fail=$((fail+1)); }
echo "shell boot: NOT CLAIMED (migration branch remains experimental)"; exit "$fail"
