#!/usr/bin/env bash
set -euo pipefail
if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This build is guest-only; run it inside the Aspartame development VM.' >&2
    exit 2
fi

root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
shell="$root/sources/sugar"
toolkit="$root/sources/sugar-toolkit-gtk4"
ext="$root/sources/sugar-ext"
datastore="$root/sources/sugar-datastore"
casilda="$root/sources/casilda"
prefix="$root/prefix"
venv="$root/venv"
log="$root/logs/gtk4-build-$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$root/logs" "$root/build"; exec > >(tee "$log") 2>&1
test -d "$shell/.git" || { echo "missing shell checkout: $shell"; exit 2; }
test -d "$toolkit/.git" || { echo "missing toolkit checkout: $toolkit"; exit 2; }
test -d "$ext/.git" || { echo "missing sugar-ext checkout: $ext"; exit 2; }
test -d "$datastore/.git" || { echo "missing sugar-datastore checkout: $datastore"; exit 2; }
test -d "$casilda/.git" || { echo "missing Casilda checkout: $casilda"; exit 2; }
if ! test -x "$venv/bin/python"; then
    python3 -m venv --system-site-packages "$venv"
fi
echo "toolkit: $(git -C "$toolkit" rev-parse HEAD)"; echo "sugar-ext: $(git -C "$ext" rev-parse HEAD)"
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
patch_dir=${GTK4_PATCH_DIR:-$repo/patches/gtk4-preview}
for patch in "$patch_dir"/*.patch; do
    [ -f "$patch" ] || continue
    case "$patch" in
        *0001*|*0004*|*0006*|*0013*|*0015*|*0016*|*0017*) target="$toolkit" ;;
        *0002*) target="$ext" ;;
        *0014*) target="$root/sources/sugar-datastore" ;;
        *0003*) echo "skipping legacy Casilda 0.1 compatibility patch"; continue ;;
        *0005*|*0007*|*0008*|*0009*|*0010*|*0011*|*0012*) target="$root/sources/sugar" ;;
        *) continue ;;
    esac
    if git -C "$target" apply --check "$patch" >/dev/null 2>&1; then
        git -C "$target" apply "$patch"
        echo "applied preview patch: $(basename "$patch")"
    fi
done
PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" "$venv/bin/python" -c 'import sugar4; print("sugar4: PASS", sugar4.__file__)'

for dep in 'gtk4 >= 4.22.2' 'wlroots-0.20 >= 0.20'; do
    pkg-config --exists "$dep" || { echo "missing guest build dependency: $dep"; exit 2; }
done

casilda_build="$root/build/casilda"
if [ -f "$casilda_build/build.ninja" ]; then
    meson setup --reconfigure "$casilda_build" "$casilda" --prefix="$prefix" --libdir=lib -Ddocumentation=false -Dvapi=false
else
    meson setup "$casilda_build" "$casilda" --prefix="$prefix" --libdir=lib --buildtype=debug -Ddocumentation=false -Dvapi=false
fi
meson compile -C "$casilda_build"
meson install -C "$casilda_build"
GI_TYPELIB_PATH="$prefix/lib/girepository-1.0" \
LD_LIBRARY_PATH="$prefix/lib" \
    "$venv/bin/python" -c 'import gi; gi.require_version("Casilda", "1.0"); from gi.repository import Casilda; print("Casilda 1.0: PASS", Casilda._version)'

ext_build="$root/build/sugar-ext"
if [ -f "$ext_build/build.ninja" ]; then
    meson setup --reconfigure "$ext_build" "$ext" --prefix="$prefix" --libdir=lib
else
    meson setup "$ext_build" "$ext" --prefix="$prefix" --libdir=lib --buildtype=debug
fi
meson compile -C "$ext_build"
meson install -C "$ext_build"

# Generate Jarabe's configuration with guest-local paths.  The GTK4 shell is
# Python, so stage its runtime data directly rather than invoking the currently
# broken upstream icon-distribution target (which references absent SVG files).
(
    cd "$shell"
    ./autogen.sh --prefix="$prefix" --disable-update-mimedb
)
install -d "$prefix/share/sugar/data" "$prefix/share/sugar/extensions"
cp -a "$shell/data/." "$prefix/share/sugar/data/"
cp -a "$shell/extensions/." "$prefix/share/sugar/extensions/"
test -f "$shell/src/jarabe/config.py"
grep -Fq "data_path = '$prefix/share/sugar/data'" "$shell/src/jarabe/config.py"

# Keep mutable profile and schema state outside the source and prefix trees.
runroot="$root/runtime"
mkdir -p "$runroot/schemas"
cp "$shell/data/org.sugarlabs.gschema.xml" "$runroot/schemas/"
glib-compile-schemas "$runroot/schemas"
cp "$shell/data/group-labels.defaults" "$runroot/group-labels.json"

# The GTK4 Journal still consumes the upstream datastore D-Bus service.
# Build its small native metadata reader into the preview prefix only.
datastore_build="$root/build/sugar-datastore"
python_version=$($venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
datastore_site="$prefix/lib/python$python_version/site-packages"
mkdir -p "$datastore_build/carquinyol" "$datastore_site/carquinyol"
python_include=$($venv/bin/python -c 'import sysconfig; print(sysconfig.get_config_var("INCLUDEPY"))')
python_ext_suffix=$($venv/bin/python -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
gcc -shared -fPIC -O2 -I"$python_include" \
    -o "$datastore_build/carquinyol/metadatareader$python_ext_suffix" \
    "$datastore/src/carquinyol/metadatareader.c"
install -m 0755 "$datastore_build/carquinyol/metadatareader$python_ext_suffix" \
    "$datastore_site/carquinyol/"
cp "$datastore"/src/carquinyol/*.py "$datastore_site/carquinyol/"
PYTHONPATH="$datastore_site:$toolkit/src" "$venv/bin/python" -c \
    'import carquinyol.metadatareader; print("datastore metadata reader: PASS")'
echo "GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS"
echo "Wayland socket will be owned by embedded Casilda at runtime"
