#!/usr/bin/env bash
set -u
export ASPARTAME_GTK4_PREVIEW=1
project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export PYTHONPATH="$project_root/sugar-overlay/src${PYTHONPATH:+:$PYTHONPATH}"
root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
toolkit="$root/sources/sugar-toolkit-gtk4"; venv="$root/venv"; fail=0
# GTK tests must use the Sugar session bus/display, not a root caller's
# `/run/user/0` environment.  This keeps the checker safe to invoke via sudo
# while preserving the same GTK4 process boundary as the live shell.
sugar_user=${SUGAR_USER:-aspartame}
if [ -d "/run/user/$(id -u "$sugar_user" 2>/dev/null || echo 0)" ]; then
    sugar_uid=$(id -u "$sugar_user")
    export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$sugar_uid}"
fi
if [ -z "${DISPLAY:-}" ] && [ -S /tmp/.X11-unix/X0 ]; then
    export DISPLAY=:0
fi
echo "Aspartame GTK4 preview checks"
[ -f "$root/PINS.tsv" ] && echo "pins: PASS" || { echo "pins: FAIL"; fail=$((fail+1)); }
if [ -x "$venv/bin/python" ]; then PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" "$venv/bin/python" -c 'import gi; gi.require_version("Gtk", "4.0"); from gi.repository import Gtk; import sugar4; print("GTK4/PyGObject/sugar4: PASS", "%d.%d.%d" % (Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version()), sugar4.__file__)' || fail=$((fail+1)); else echo "preview venv: FAIL"; fail=$((fail+1)); fi
if [ -d "$toolkit/.git" ] && [ -x "$venv/bin/python" ]; then
    if [ "$(id -u)" -eq 0 ]; then
        runuser -u "$sugar_user" -- env DISPLAY="${DISPLAY:-:0}" \
            XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" \
            PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" \
            "$venv/bin/python" -m pytest -q \
            "$toolkit/tests/test_icon.py" "$toolkit/tests/test_iconentry.py" || fail=$((fail+1))
    else
        PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" \
            "$venv/bin/python" -m pytest -q \
            "$toolkit/tests/test_icon.py" "$toolkit/tests/test_iconentry.py" || fail=$((fail+1))
    fi
elif [ -d "$toolkit/.git" ]; then
    echo "preview venv: FAIL"
    fail=$((fail+1))
else
    echo "toolkit checkout: FAIL"
    fail=$((fail+1))
fi
[ -f "$root/build/sugar-ext/build.ninja" ] && echo "sugar-ext configured: PASS" || echo "sugar-ext configured: NOT YET"
grep -q 'PKG_CHECK_MODULES(SHELL, gtk4)' "$root/sources/sugar/configure.ac" 2>/dev/null && echo "shell GTK4 configure gate: PASS" || { echo "shell GTK4 configure gate: FAIL"; fail=$((fail+1)); }
if pgrep -u "${SUGAR_USER:-aspartame}" -f '/sources/sugar/src/jarabe/main.py' >/dev/null 2>&1; then
    echo "GTK4 preview shell boot: PASS"
else
    echo "GTK4 preview shell boot: NOT RUNNING"
fi
echo "full GTK4 replacement gate: NOT CLAIMED (see reports/gtk4/runtime-matrix-20260913.md)"
exit "$fail"
