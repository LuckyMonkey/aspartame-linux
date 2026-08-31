#!/usr/bin/env bash
set -euo pipefail
root=${GTK4_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4}
toolkit="$root/sources/sugar-toolkit-gtk4"; ext="$root/sources/sugar-ext"; venv="$root/venv"
log="$root/logs/gtk4-build-$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$root/logs" "$root/build"; exec > >(tee "$log") 2>&1
test -d "$toolkit/.git" || { echo "missing toolkit checkout: $toolkit"; exit 2; }
test -d "$ext/.git" || { echo "missing sugar-ext checkout: $ext"; exit 2; }
test -x "$venv/bin/python" || { echo "missing preview venv: $venv"; exit 2; }
echo "toolkit: $(git -C "$toolkit" rev-parse HEAD)"; echo "sugar-ext: $(git -C "$ext" rev-parse HEAD)"
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for patch in "$repo"/patches/gtk4-preview/*.patch; do
    [ -f "$patch" ] || continue
    case "$patch" in
        *0001*) target="$toolkit" ;;
        *0002*) target="$ext" ;;
        *) continue ;;
    esac
    if git -C "$target" apply --check "$patch" >/dev/null 2>&1; then
        git -C "$target" apply "$patch"
        echo "applied preview patch: $(basename "$patch")"
    fi
done
PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" "$venv/bin/python" -c 'import sugar4; print("sugar4: PASS", sugar4.__file__)'
ext_build="$root/build/sugar-ext"
if [ ! -f "$ext_build/build.ninja" ]; then meson setup "$ext_build" "$ext" --prefix="$root/prefix" --buildtype=debug; fi
meson compile -C "$ext_build"
echo "GTK4 toolkit and sugar-ext build: PASS"
echo "GTK4 shell: not claimed; run sugar-gtk4-check for shell/configuration status"
