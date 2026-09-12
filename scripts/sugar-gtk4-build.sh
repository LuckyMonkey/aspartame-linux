#!/usr/bin/env bash
set -euo pipefail
if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This build is guest-only; run it inside the Aspartame development VM.' >&2
    exit 2
fi

# The image's stable-Activity bridge deliberately pins GTK3 from
# sitecustomize. Mark every preview subprocess before Python starts so GTK4
# can be selected in the isolated toolchain without weakening stable Sugar.
export ASPARTAME_GTK4_PREVIEW=1

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export PYTHONPATH="$repo/sugar-overlay/src${PYTHONPATH:+:$PYTHONPATH}"

root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
shell="$root/sources/sugar"
toolkit="$root/sources/sugar-toolkit-gtk4"
ext="$root/sources/sugar-ext"
datastore="$root/sources/sugar-datastore"
casilda="$root/sources/casilda"
log_activity="$root/sources/log-activity"
prefix="$root/prefix"
venv="$root/venv"
log="$root/logs/gtk4-build-$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$root/logs" "$root/build"; exec > >(tee "$log") 2>&1
test -d "$shell/.git" || { echo "missing shell checkout: $shell"; exit 2; }
test -d "$toolkit/.git" || { echo "missing toolkit checkout: $toolkit"; exit 2; }
test -d "$ext/.git" || { echo "missing sugar-ext checkout: $ext"; exit 2; }
test -d "$datastore/.git" || { echo "missing sugar-datastore checkout: $datastore"; exit 2; }
test -d "$casilda/.git" || { echo "missing Casilda checkout: $casilda"; exit 2; }
test -d "$log_activity/.git" || { echo "missing Log Activity checkout: $log_activity"; exit 2; }
test -f "$log_activity/logviewer.py" || { echo "missing Log Activity source: $log_activity"; exit 2; }
if ! test -x "$venv/bin/python"; then
    python3 -m venv --system-site-packages "$venv"
fi
# Expose Empy from the isolated preview venv when Arch omitted its console link.
if ! test -x "$venv/bin/empy" && test -x "$venv/bin/em.py"; then
    ln -sf "$venv/bin/em.py" "$venv/bin/empy"
fi
export PATH="$venv/bin:$PATH"
echo "toolkit: $(git -C "$toolkit" rev-parse HEAD)"; echo "sugar-ext: $(git -C "$ext" rev-parse HEAD)"
patch_dir=${GTK4_PATCH_DIR:-$repo/patches/gtk4-preview}
patch_state="$root/build/applied-patches"
mkdir -p "$patch_state"
for patch in "$patch_dir"/*.patch; do
    [ -f "$patch" ] || continue
    case "$patch" in
        *0001*|*0004*|*0006*|*0013*|*0015*|*0016*|*0017*|*0018*|*0020*|*0022*|*0023*|*0024*|*0025*|*0026*|*0028*|*0030*|*0032*|*0033*|*0035*) target="$toolkit" ;;
        *0029*) target="$log_activity" ;;
        *0002*) target="$ext" ;;
        *0014*) target="$root/sources/sugar-datastore" ;;
        *0003*) echo "skipping legacy Casilda 0.1 compatibility patch"; continue ;;
        *0005*|*0007*|*0008*|*0009*|*0010*|*0011*|*0012*|*0019*|*0021*|*0027*|*0031*|*0034*|*0036*) target="$root/sources/sugar" ;;
        *) echo "unrouted GTK4 preview patch: $patch" >&2; exit 2 ;;
    esac
    patch_name=$(basename "$patch")
    patch_digest=$(sha256sum "$patch" | cut -d " " -f 1)
    stamp="$patch_state/$patch_name.sha256"
    if [[ "$patch_name" == *0004* ]] && grep -q "def get_environment" "$toolkit/src/sugar4/activity/activityfactory.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified superseded preview patch: $patch_name"
        continue
    fi
    # The pinned toolkit already contains the launch and D-Bus service
    # surfaces introduced by these early preview patches.
    if [[ "$patch_name" == *0022* ]] &&
        grep -q "def create(bundle, handle)" "$toolkit/src/sugar4/activity/activityfactory.py" 2>/dev/null &&
        grep -q "subprocess.Popen(" "$toolkit/src/sugar4/activity/activityfactory.py" 2>/dev/null &&
        grep -q 'command.extend(\["--activity-id", handle.activity_id\])' "$toolkit/src/sugar4/activity/activityfactory.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Activity launch contract: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0023* ]] &&
        grep -q "class ActivityService" "$toolkit/src/sugar4/activity/activityservice.py" 2>/dev/null &&
        grep -q "def SetActive" "$toolkit/src/sugar4/activity/activityservice.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified superseded preview patch: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0030* ]] &&
        grep -q 'launcher_name == "sugar-activity3"' "$toolkit/src/sugar4/activity/activityfactory.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing GTK3 launcher guard: $patch_name"
        continue
    fi
    # Later homebox fixes extend the lazy-list hunk from 0008. Accept that
    # already-applied semantic result even when the additional toolbar and
    # query wiring changes the original patch context.
    if [[ "$patch_name" == *0008* ]] &&
        grep -q 'self\._list_view = None' "$shell/src/jarabe/desktop/homebox.py" 2>/dev/null &&
        grep -q 'def _ensure_list_view' "$shell/src/jarabe/desktop/homebox.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing lazy Home list result: $patch_name"
        continue
    fi
    # 0016 later changes CellRendererIcon's class and adds native GObject
    # properties, but intentionally retains every behavior introduced by
    # 0015. Recognize that complete semantic result when patch context has
    # moved, while still applying 0015 on a pristine checkout.
    if [[ "$patch_name" == *0015* ]] &&
        grep -q 'class CellRendererIcon(Gtk.CellRenderer):' "$toolkit/src/sugar4/graphics/icon.py" 2>/dev/null &&
        grep -q 'self\.props = _CellRendererIconProps(self)' "$toolkit/src/sugar4/graphics/icon.py" 2>/dev/null &&
        grep -q 'def connect(self, signal_name, callback, \*user_data):' "$toolkit/src/sugar4/graphics/icon.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing CellRendererIcon property/signal contract: $patch_name"
        continue
    fi
    # 0029's GTK4 ListBox implementation is already present in the pinned
    # Log Activity source. Its later edits changed surrounding helpers, so
    # the historical wholesale replacement no longer applies mechanically.
    if [[ "$patch_name" == *0029* ]] &&
        grep -q 'class MultiLogView(Gtk.Paned):' "$log_activity/logviewer.py" 2>/dev/null &&
        grep -q 'self\._listbox = Gtk.ListBox()' "$log_activity/logviewer.py" 2>/dev/null &&
        ! grep -q 'Gtk\.TreeView' "$log_activity/logviewer.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing GTK4 Log ListBox result: $patch_name"
        continue
    fi
    # 0032 intentionally adjusts the toolbar snapshot hunk from 0028. The
    # surrounding Sugar interaction changes remain present; verify their
    # semantic markers rather than replaying the superseded context.
    if [[ "$patch_name" == *0028* ]] &&
        grep -q 'click_gesture\.set_button(1)' "$toolkit/src/sugar4/graphics/icon.py" 2>/dev/null &&
        grep -q 'class _PaletteWindowWidget(Gtk.Popover):' "$toolkit/src/sugar4/graphics/palettewindow.py" 2>/dev/null &&
        grep -q 'Gtk\.Widget\.do_snapshot(self, snapshot)' "$toolkit/src/sugar4/graphics/toolbarbox.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Sugar interaction/snapshot result: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0033* ]] &&
        grep -q 'object_id = activity_id.replace("-", "_")' "$toolkit/src/sugar4/activity/activityservice.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing encoded Activity service path: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0034* ]] &&
        grep -q 'def _get_service_path(self):' "$shell/src/jarabe/model/shell.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing encoded shell Activity path: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0035* ]] &&
        grep -q 'command.extend(\["--activity-id", handle.activity_id\])' "$toolkit/src/sugar4/activity/activityfactory.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Activity ID propagation: $patch_name"
        continue
    fi
    if [ -f "$stamp" ] &&
        grep -qx "$patch_digest" "$stamp" &&
        git -C "$target" apply --reverse --check "$patch" >/dev/null 2>&1; then
        echo "verified preview patch: $patch_name"
    elif git -C "$target" apply --check "$patch" >/dev/null 2>&1; then
        git -C "$target" apply "$patch"
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied preview patch: $patch_name"
    elif git -C "$target" apply --reverse --check "$patch" >/dev/null 2>&1; then
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "verified existing preview patch: $patch_name"
    elif [[ "$patch_name" == *0029* || "$patch_name" == *0033* || "$patch_name" == *0034* || "$patch_name" == *0035* || "$patch_name" == *0036* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied compatibility preview patch: $patch_name"
    else
        echo "GTK4 preview patch drift: $patch_name" >&2
        echo "target: $target" >&2
        exit 2
    fi
done
PYTHONPATH="$toolkit/src${PYTHONPATH:+:$PYTHONPATH}" "$venv/bin/python" -c 'import sugar4; print("sugar4: PASS", sugar4.__file__)'

install -m 0755 "$repo/scripts/sugar-activity4" "$venv/bin/sugar-activity4"
test -x "$venv/bin/sugar-activity4"

activity_dir="$prefix/share/sugar/activities"
test -f "$log_activity/activity/activity.info" || {
    echo "missing pinned Log Activity bundle: $log_activity" >&2
    exit 2
}
mkdir -p "$activity_dir"
if test -e "$activity_dir/Log.activity" && test ! -L "$activity_dir/Log.activity"; then
    echo "refusing to replace a real Log.activity directory" >&2
    exit 2
fi
ln -sfn "$log_activity" "$activity_dir/Log.activity"

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

# sugar-artwork currently ships GTK3 CSS only.  Install the GTK4 port under
# the canonical Sugar theme names so both Jarabe and Activities resolve it
# through their existing gtk-theme-name setting.
for sugar_theme in sugar-72 sugar-100; do
    install -d "$prefix/share/themes/$sugar_theme/gtk-4.0"
    install -m 0644 "$repo/assets/gtk4/sugar.css" \
        "$prefix/share/themes/$sugar_theme/gtk-4.0/gtk.css"
done

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
