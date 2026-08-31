#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
overlay="$root/sugar-overlay/src"
stable_profile="$root/archiso/aspartame/packages.x86_64"
failures=0

echo 'Aspartame Sugar modernization guardrails'
grep -q '^SUGAR_VERSION=' "$root/sugar-overlay/UPSTREAM" || {
    echo 'FAIL: stable Sugar pin is missing'; failures=$((failures + 1)); }
grep -qx 'sugar-toolkit-gtk3' "$stable_profile" || {
    echo 'FAIL: stable GTK3 toolkit pin is missing'; failures=$((failures + 1)); }
if rg -n 'require_version\(.+Gtk.+4\.0|from sugar4|import sugar4' "$overlay" >/dev/null; then
    echo 'FAIL: GTK4 code entered the stable GTK3 overlay'; failures=$((failures + 1))
else
    echo 'stable GTK4 contamination: PASS'
fi

if rg -n 'Gdk\.Screen|Gtk\.Menu|pack_start|add_events|Gtk\.Clipboard' "$overlay" >/dev/null; then
    echo 'legacy GTK3 APIs: REVIEW (existing stable code; do not mass-convert)'
else
    echo 'legacy GTK3 APIs: none found'
fi

if rg -n 'GdkX11|Gtk\.Window\.get_window|xrandr|DISPLAY' "$overlay" >/dev/null; then
    echo 'X11-sensitive code: REVIEW (expected in stable session)'
else
    echo 'X11-sensitive code: none found'
fi

printf 'stable pin: '
sed -n 's/^SUGAR_VERSION=//p' "$root/sugar-overlay/UPSTREAM"
printf 'host Python: '
python3 --version

if [ "$failures" -eq 0 ]; then
    echo 'Result: PASS (stable path remains isolated)'
else
    echo "Result: FAIL ($failures guardrails)"
fi
exit "$failures"
