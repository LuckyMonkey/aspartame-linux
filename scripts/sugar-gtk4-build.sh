#!/usr/bin/env bash
set -euo pipefail
root=${GTK4_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4}
toolkit="$root/sources/sugar-toolkit-gtk4"; ext="$root/sources/sugar-ext"; datastore="$root/sources/sugar-datastore"; venv="$root/venv"
log="$root/logs/gtk4-build-$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$root/logs" "$root/build"; exec > >(tee "$log") 2>&1
test -d "$toolkit/.git" || { echo "missing toolkit checkout: $toolkit"; exit 2; }
test -d "$ext/.git" || { echo "missing sugar-ext checkout: $ext"; exit 2; }
test -d "$datastore/.git" || { echo "missing sugar-datastore checkout: $datastore"; exit 2; }
test -x "$venv/bin/python" || { echo "missing preview venv: $venv"; exit 2; }
echo "toolkit: $(git -C "$toolkit" rev-parse HEAD)"; echo "sugar-ext: $(git -C "$ext" rev-parse HEAD)"
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
for patch in "$repo"/patches/gtk4-preview/*.patch; do
    [ -f "$patch" ] || continue
    case "$patch" in
        *0001*|*0004*|*0006*|*0013*|*0015*) target="$toolkit" ;;
        *0002*) target="$ext" ;;
        *0014*) target="$root/sources/sugar-datastore" ;;
        *0003*|*0005*|*0007*|*0008*|*0009*|*0010*|*0011*) target="$root/sources/sugar" ;;
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

# The GTK4 Journal still consumes the upstream datastore D-Bus service.
# Build its small native metadata reader into the preview prefix only.
datastore_build="$root/build/sugar-datastore"
datastore_site="$root/prefix/lib/python3.12/site-packages"
mkdir -p "$datastore_build/carquinyol" "$datastore_site/carquinyol"
python_include=$(python3 -c 'import sysconfig; print(sysconfig.get_config_var("INCLUDEPY"))')
python_ext_suffix=$(python3 -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
gcc -shared -fPIC -O2 -I"$python_include" \
    -o "$datastore_build/carquinyol/metadatareader$python_ext_suffix" \
    "$datastore/src/carquinyol/metadatareader.c"
cp "$datastore"/src/carquinyol/*.py "$datastore_site/carquinyol/"
PYTHONPATH="$datastore_site:$toolkit/src" python3 -c \
    'import carquinyol.metadatareader; print("datastore metadata reader: PASS")'
echo "GTK4 toolkit, sugar-ext, and datastore preview build: PASS"
echo "GTK4 shell: not claimed; run sugar-gtk4-check for shell/configuration status"
