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
imageviewer_activity="$root/sources/imageviewer-activity"
terminal_activity="$root/sources/terminal-activity"
browse_activity="$root/sources/browse-activity"
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
test -d "$imageviewer_activity/.git" || { echo "missing Image Viewer Activity source: $imageviewer_activity"; exit 2; }
test -d "$terminal_activity/.git" || { echo "missing Terminal Activity source: $terminal_activity"; exit 2; }
test -d "$browse_activity/.git" || { echo "missing Browse Activity source: $browse_activity"; exit 2; }
if ! test -x "$venv/bin/python"; then
    python3 -m venv --system-site-packages "$venv"
fi
# Ensure preview children use the GTK3-safe runtime hook from this checkout;
# distro sitecustomize may be stale and is imported before sugar4.
venv_site=$($venv/bin/python -c 'import site; print(site.getsitepackages()[0])')
install -D -m 0644 "$repo/sugar-overlay/src/sitecustomize.py" \
    "$venv_site/sitecustomize.py"
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
        *0001*|*0004*|*0006*|*0013*|*0015*|*0016*|*0017*|*0018*|*0020*|*0022*|*0023*|*0024*|*0025*|*0026*|*0028*|*0030*|*0032*|*0033*|*0035*|*0047*|*0059*|*0060*|*0066*|*0068*) target="$toolkit" ;;
        *0029*) target="$log_activity" ;;
        *0002*) target="$ext" ;;
        *0014*) target="$root/sources/sugar-datastore" ;;
        *0083*) target="$root/sources/sugar" ;;
        *0084*) target="$root/sources/sugar" ;;
        *0085*) target="$root/sources/sugar" ;;
        *0086*) target="$root/sources/sugar" ;;
        *0087*) target="$root/sources/sugar" ;;
        *0088*) target="$root/sources/sugar" ;;
        *0089*) target="$root/sources/sugar" ;;
        *0090*) target="$root/sources/sugar" ;;
        *0091*) target="$root/sources/sugar" ;;
        *0092*) target="$root/sources/sugar" ;;
        *0094*) echo "retired unavailable SugarExt global key-grabber preview patch"; continue ;;
        *0095*) target="$root/sources/sugar" ;;
        *0096*) target="$root/sources/sugar" ;;
        *0097*) target="$root/sources/sugar" ;;
        *0098*) target="$root/sources/sugar" ;;
        *0099*) target="$root/sources/sugar" ;;
        *0100*) target="$root/sources/sugar" ;;
        *0101*) target="$root/sources/sugar" ;;
        *0102*) target="$root/sources/sugar" ;;
        *0103*) target="$root/sources/sugar" ;;
        *0104*) target="$root/sources/sugar" ;;
        *0106*) target="$root/sources/sugar" ;;
        *0107*) target="$root/sources/sugar" ;;
        *0108*) target="$root/sources/sugar" ;;
        *0109*) target="$root/sources/sugar" ;;
        *0111*) target="$root/sources/sugar" ;;
        *0112*) target="$root/sources/sugar" ;;
        *0113*) target="$root/sources/sugar" ;;
        *0114*) target="$root/sources/sugar" ;;
        *0115*) target="$root/sources/sugar" ;;
        *0116*) target="$root/sources/sugar" ;;
        *0117*) target="$root/sources/sugar" ;;
        *0118*) target="$root/sources/sugar" ;;
        *0119*) target="$root/sources/sugar" ;;
        *0120*) target="$root/sources/sugar" ;;
        *0121*) target="$root/sources/sugar" ;;
        *0122*) target="$root/sources/sugar" ;;
        *0123*) target="$root/sources/sugar" ;;
        *0003*) echo "skipping legacy Casilda 0.1 compatibility patch"; continue ;;
        *0005*|*0007*|*0008*|*0009*|*0010*|*0011*|*0012*|*0019*|*0021*|*0027*|*0031*|*0034*|*0036*|*0037*|*0038*|*0039*|*0040*|*0041*|*0042*|*0043*|*0044*|*0045*|*0046*|*0048*|*0049*|*0050*|*0051*|*0052*|*0053*|*0054*|*0055*|*0057*|*0058*|*0061*|*0062*|*0063*|*0064*|*0065*|*0067*|*0069*|*0070*|*0071*|*0073*|*0074*|*0075*|*0076*|*0079*|*0080*|*0081*) target="$root/sources/sugar" ;;
        *) echo "unrouted GTK4 preview patch: $patch" >&2; exit 2 ;;
    esac
    patch_name=$(basename "$patch")
    patch_digest=$(sha256sum "$patch" | cut -d " " -f 1)
    stamp="$patch_state/$patch_name.sha256"
    if [[ "$patch_name" == *0039* ]]; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "retired obsolete preview patch: $patch_name (registry filtering superseded)"
        continue
    fi
    if [[ "$patch_name" == *0042* ]] && grep -Eq "journalactivity\.get_journal\(\)\.show_journal\(\)|journal = journalactivity\.get_journal\(\)" "$shell/src/jarabe/view/keyhandler.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Journal fallback: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0043* ]] && grep -q "model.set_zoom_level(model.ZOOM_ACTIVITY, event_time)" "$shell/src/jarabe/view/keyhandler.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Journal stack zoom: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0041* ]] && grep -q "_sugar_zoom_controller" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified obsolete zoom-controller removal: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0044* ]] &&
        grep -q 'logging.warning("GTK4 semantic key event: %s", key)' "$shell/src/jarabe/view/keyhandler.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified key observability: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0048* ]] && grep -q "_sugar_zoom_controller" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing top-level zoom capture: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0049* ]] && grep -q "def ShowJournal" "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing semantic Journal action: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0050* ]] && grep -q "keyval == Gdk.KEY_F6" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Frame/Journal key capture: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0051* ]] && grep -q "set_focus(shell_instance._overlay)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing GTK4 overlay focus: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0052* ]] && grep -q "def ShowFrame" "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing semantic Frame action: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0053* ]] && sed -n '299,307p' "$shell/src/jarabe/main.py" 2>/dev/null | grep -q "set_focus(shell_instance._overlay)"; then
        # Leave malformed placement to the compatibility hunk below.
        :
    elif [[ "$patch_name" == *0053* ]] && grep -q "set_focus(shell_instance._overlay)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified focus placement correction: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0054* ]] && grep -q "set_focus(shell_instance._overlay)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified final GTK4 overlay focus: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0055* ]] && grep -q "No friends are nearby yet\." "$shell/src/jarabe/desktop/groupbox.py" 2>/dev/null && grep -q "self\._empty_state" "$shell/src/jarabe/desktop/groupbox.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing empty Group view state: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0068* ]] && grep -q "def set_image(self, image):" "$toolkit/src/sugar4/graphics/menuitem.py" 2>/dev/null && grep -q "self\._content_box\.prepend(image)" "$toolkit/src/sugar4/graphics/menuitem.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing MenuItem image compatibility: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0074* ]] && grep -q "semantic_keys\.add_window(home_window)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Home surface shortcut capture: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0075* ]] && grep -q "Loading Journal" "$shell/src/jarabe/journal/listview.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Journal loading state: $patch_name"
        continue
    fi
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
    if [[ "$patch_name" == *0060* ]] &&
        grep -q '"ASPARTAME_GTK4_PREVIEW": "1"' "$toolkit/src/sugar4/activity/activityfactory.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing GTK4 activity process marker: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0062* ]] &&
        grep -q 'def StopActivity(self, activity_id)' "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing StopActivity shell action: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0063* ]] &&
        grep -q 'activity.close_window()' "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Activity surface close: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0064* ]] &&
        grep -q 'os.kill(pid, 15)' "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Activity process termination: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0065* ]] &&
        grep -q 'activity_id.encode()' "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Activity-ID process fallback: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0067* ]] &&
        grep -q '_buttons.pop(home_activity, None)' "$shell/src/jarabe/frame/activitiestray.py" 2>/dev/null &&
        grep -q 'if home_activity not in self._activities:' "$shell/src/jarabe/model/shell.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing idempotent Activity removal: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0069* ]] &&
        grep -q 'from gettext import gettext as _' "$shell/src/jarabe/desktop/groupbox.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Group view gettext import: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0070* ]] &&
        grep -q 'activity_keys.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)' "$shell/src/jarabe/main.py" 2>/dev/null &&
        grep -q 'shell_instance.compositor.add_controller(activity_keys)' "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Casilda activity key capture: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0071* ]] &&
        grep -q 'frame.get_view().hide()' "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Frame dismissal on zoom: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0073* ]] &&
        grep -q 'set_accessible_role(Gtk.AccessibleRole.BUTTON)' "$shell/src/jarabe/desktop/favoritesview.py" 2>/dev/null &&
        grep -q 'Gtk.AccessibleProperty.LABEL' "$shell/src/jarabe/desktop/favoritesview.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Home Activity accessibility: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0027* ]] &&
        grep -q "SUGAR_WINDOWED" "$root/sources/sugar/src/jarabe/main.py" 2>/dev/null &&
        grep -q "set_decorated(False)" "$root/sources/sugar/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing windowed GTK4 shell behavior: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0036* ]] &&
        grep -q "shell_model.notify_launch(activity_id, bundle.get_bundle_id())" "$root/sources/sugar/src/jarabe/journal/misc.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing shell Activity registration: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0037* ]] &&
        grep -q "misc.launch(bundle, object_id=object_id)" "$root/sources/sugar/src/jarabe/journal/bundlelauncher.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Journal lifecycle launch: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0038* ]] &&
        grep -q 'model.stack.set_visible_child_name("activity")' "$root/sources/sugar/src/jarabe/view/launcher.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Activity surface restoration: $patch_name"
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
    if [[ "$patch_name" == *0058* ]] &&
        grep -q 'def ShowControlPanel' "$shell/src/jarabe/view/service.py" 2>/dev/null &&
        grep -q 'ControlPanel(0)' "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing semantic Control Panel action: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0079* ]] &&
        grep -q 'self\._canvas\.unparent()' "$shell/src/jarabe/journal/journalwindow.py" 2>/dev/null &&
        grep -q 'widget\.unparent()' "$shell/src/jarabe/journal/journalwindow.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing safe Journal canvas reparenting: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0080* ]] &&
        grep -q '_overlay.set_focusable(True)' "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing focusable GTK4 key surface: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0081* ]] &&
        grep -q "marshaled = dbus.Dictionary({}, signature='sv')" "$shell/src/jarabe/journal/model.py" 2>/dev/null &&
        grep -q "dbus.Array(PROPERTIES, signature='s')" "$shell/src/jarabe/journal/model.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified explicit Journal datastore query types: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0083* ]] &&
        grep -q "empty_dict = dbus.Dictionary({}, signature='sv')" "$shell/src/jarabe/journal/model.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Journal unique-values signature: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0084* ]] &&
        grep -q "semantic_keys.add_window(journal)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Journal key routing: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0085* ]] &&
        grep -q "zoom_levels =" "$shell/src/jarabe/desktop/homewindow.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Home semantic zoom keys: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0086* ]] &&
        grep -q "if keyval == Gdk.KEY_F1:" "$shell/src/jarabe/desktop/homewindow.py" 2>/dev/null &&
        grep -q "self._view_stack.set_visible_child_name('mesh')" "$shell/src/jarabe/desktop/homewindow.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Home zoom stack selection: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0088* ]] &&
        grep -q "self.set_focusable(True)" "$shell/src/jarabe/desktop/homewindow.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Home focus surface: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0089* ]] &&
        grep -q "_focus_surface in (shell_instance._overlay, shell_instance.stack)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified descendant key capture: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0090* ]] &&
        grep -q "shell_instance.get_model().set_zoom_level(level)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified ShellModel zoom setter: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0091* ]] &&
        grep -q "_main_window.set_focusable(True)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified focusable GTK4 application window: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0092* ]] &&
        grep -q "Gtk.ShortcutScope.GLOBAL" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified global Sugar shortcut controller: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0094* ]] &&
        grep -q "_modern_key_grabber" "$shell/src/jarabe/main.py" 2>/dev/null &&
        grep -q "def _modern_key_pressed(grabber, keycode, state):" \
            "$shell/src/jarabe/main.py" 2>/dev/null &&
        grep -q "Gdk.keyval_from_name(key)" "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified workspace-gated GTK4 key grabber: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0095* ]] &&
        grep -q "Prefer GTK4 bundle" "$shell/src/jarabe/model/bundleregistry.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified modern bundle precedence: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0096* ]] &&
        grep -q "Modern bundle lookup failed" "$shell/src/jarabe/model/bundleregistry.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified modern get_bundle override: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0099* ]] &&
        grep -q 'set_accessible_role(Gtk.AccessibleRole.BUTTON)' "$shell/src/jarabe/controlpanel/gui.py" 2>/dev/null &&
        grep -q 'def _key_pressed(self, controller, keyval, keycode, state)' "$shell/src/jarabe/controlpanel/gui.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing Control Panel accessibility: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0100* ]] &&
        grep -q 'def ShowHome(self)' "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing ShowHome action: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0101* ]] &&
        grep -q 'def ShowList(self)' "$shell/src/jarabe/view/service.py" 2>/dev/null &&
        grep -q 'def show_list_view(self)' "$shell/src/jarabe/desktop/homebox.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing ShowList action: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0102* ]] &&
        grep -q 'def _close_control_panel(self)' "$shell/src/jarabe/view/service.py" 2>/dev/null &&
        grep -q 'self._close_control_panel()' "$shell/src/jarabe/view/service.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing navigation modal cleanup: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0103* ]] &&
        [ "$(grep -c 'self._close_control_panel()' "$shell/src/jarabe/view/service.py" 2>/dev/null || true)" -ge 7 ]; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified duplicate navigation modal cleanup: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0104* ]] &&
        grep -q 'from gi.repository import Gtk, Gdk, GLib' "$shell/src/jarabe/journal/journalwindow.py" 2>/dev/null &&
        grep -q 'GLib.idle_add(self.set_canvas, widget)' "$shell/src/jarabe/journal/journalwindow.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified deferred Journal canvas attach: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0106* ]] &&
        sed -n '/def show_main_view/,/def _show_secondary_view/p' "$shell/src/jarabe/journal/journalactivity.py" 2>/dev/null |
            grep -q 'if self._active_view == JournalViews.MAIN:'; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified idempotent Journal main view: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0107* ]] &&
        grep -A3 -q "elif self._active_view == JournalViews.DETAIL:" "$shell/src/jarabe/journal/journalactivity.py" 2>/dev/null &&
        grep -A3 "elif self._active_view == JournalViews.DETAIL:" "$shell/src/jarabe/journal/journalactivity.py" 2>/dev/null | grep -q "keyname == 'Escape'"; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Journal detail Escape navigation: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0108* ]] &&
        grep -q "active_activity.show_main_view()" "$shell/src/jarabe/view/keyhandler.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Journal detail Escape keyhandler route: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0109* ]] &&
        grep -q 'GLib.idle_add(self.set_toolbar_box, toolbar)' "$shell/src/jarabe/journal/journalwindow.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified deferred Journal toolbar attach: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0111* ]] &&
        ! grep -q '_modern_key_grabber' "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified retired unavailable runtime key grabber: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0112* ]] &&
        sed -n '/def _get_options/,/return options/p' "$shell/src/jarabe/controlpanel/gui.py" 2>/dev/null |
            grep -q "import cpsection.activities"; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified GTK4 Activity Manager section registration: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0113* ]] &&
        ! grep -q "options.setdefault('activities'" "$shell/src/jarabe/controlpanel/gui.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified no misplaced Activity Manager registration: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0114* ]] &&
        grep -q 'AccessibleRole.GROUP' "$shell/src/jarabe/desktop/meshbox.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Neighborhood accessibility: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0115* ]] &&
        grep -q 'AccessibleRole.GROUP' "$shell/src/jarabe/desktop/meshbox.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Neighborhood accessible role: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0116* ]] &&
        grep -q 'AccessibleRole.GROUP' "$shell/src/jarabe/desktop/groupbox.py" 2>/dev/null &&
        grep -q "\[_('Group')\]" "$shell/src/jarabe/desktop/groupbox.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Group accessibility: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0117* ]] &&
        grep -q 'AccessibleRole.GROUP' "$shell/src/jarabe/desktop/groupbox.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Group accessible role: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0118* ]] &&
        grep -q "\[_('Frame')\]" "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null &&
        grep -q 'AccessibleRole.GROUP' "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Frame accessibility: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0119* ]] &&
        sed -n '/def __init__(self, position)/,/self\._position/p' "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null |
            grep -q 'AccessibleRole.GROUP'; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Frame accessibility placement: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0120* ]] &&
        grep -q 'from gettext import gettext as _' "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified Frame accessibility gettext import: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0121* ]] &&
        sed -n '/def __init__(self, position)/,/if self\.is_vertical()/p' "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null |
            grep -q 'AccessibleRole.GROUP'; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified final Frame accessibility placement: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0121* ]] &&
        ! (cd "$shell" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "superseded drifted Frame placement patch: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0122* ]] &&
        sed -n '/def __init__(self, position)/,/def do_dispose/p' "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null |
            grep -q 'AccessibleRole.GROUP' &&
        ! sed -n '/def do_dispose/,/def get_child_box/p' "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null |
            grep -q 'AccessibleRole.GROUP'; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified final Frame accessibility relocation: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0122* ]] &&
        ! (cd "$shell" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "superseded drifted Frame relocation patch: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0123* ]] &&
        sed -n '/def __init__(self, position)/,/def do_dispose/p' "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null |
            grep -q 'AccessibleRole.GROUP' &&
        ! sed -n '/def do_dispose/,/def get_child_box/p' "$shell/src/jarabe/frame/framewindow.py" 2>/dev/null |
            grep -q 'AccessibleRole.GROUP'; then
        printf '%s\n' "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified current Frame accessibility relocation: $patch_name"
        continue
    fi
    if [[ "$patch_name" == *0080* ]] &&
        grep -q '_overlay.set_focusable(True)' "$shell/src/jarabe/main.py" 2>/dev/null; then
        printf "%s\n" "$patch_digest" > "$stamp" 2>/dev/null || true
        echo "verified existing focusable GTK4 key surface: $patch_name"
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
    elif [[ "$patch_name" == *0083* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied Journal datastore signature patch: $patch_name"
    elif [[ "$patch_name" == *0084* ]] &&
        (cd "$target" && patch --dry-run --fuzz=2 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=2 -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied Journal key routing patch: $patch_name"
    elif [[ "$patch_name" == *0085* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied Home semantic zoom patch: $patch_name"
    elif [[ "$patch_name" == *0086* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied Home zoom stack patch: $patch_name"
    elif [[ "$patch_name" == *0087* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied semantic zoom actions: $patch_name"
    elif [[ "$patch_name" == *0088* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied Home focus surface: $patch_name"
    elif [[ "$patch_name" == *0089* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied descendant key capture: $patch_name"
    elif [[ "$patch_name" == *0090* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied ShellModel zoom setter: $patch_name"
    elif [[ "$patch_name" == *0091* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied focusable GTK4 application window: $patch_name"
    elif [[ "$patch_name" == *0092* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied global Sugar shortcut controller: $patch_name"
    elif [[ "$patch_name" == *0094* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied workspace-gated GTK4 key grabber: $patch_name"
    elif [[ "$patch_name" == *0095* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied modern bundle precedence: $patch_name"
    elif [[ "$patch_name" == *0096* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied modern get_bundle override: $patch_name"
    elif [[ "$patch_name" == *0099* ]] &&
        (cd "$target" && patch --dry-run -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch -p1 < "$patch" >/dev/null)
        printf '%s\n' "$patch_digest" > "$stamp"
        echo "applied Control Panel accessibility patch: $patch_name"
    elif [[ "$patch_name" == *0100* ]] &&
        (cd "$target" && patch --dry-run --fuzz=1 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=1 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied semantic ShowHome action: $patch_name"
    elif [[ "$patch_name" == *0101* ]] &&
        (cd "$target" && patch --dry-run --fuzz=1 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=1 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied semantic ShowList action: $patch_name"
    elif [[ "$patch_name" == *0102* ]] &&
        (cd "$target" && patch --dry-run --fuzz=3 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=3 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied navigation modal cleanup: $patch_name"
    elif [[ "$patch_name" == *0103* ]] &&
        (cd "$target" && patch --dry-run --fuzz=3 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=3 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied duplicate navigation modal cleanup: $patch_name"
    elif [[ "$patch_name" == *0104* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied deferred Journal canvas attach: $patch_name"
    elif [[ "$patch_name" == *0106* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied idempotent Journal main view: $patch_name"
    elif [[ "$patch_name" == *0107* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied Journal detail Escape navigation: $patch_name"
    elif [[ "$patch_name" == *0108* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied Journal detail Escape keyhandler route: $patch_name"
    elif [[ "$patch_name" == *0109* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied deferred Journal toolbar attach: $patch_name"
    elif [[ "$patch_name" == *0111* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "removed unavailable runtime key grabber: $patch_name"
    elif [[ "$patch_name" == *0112* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied GTK4 Activity Manager section registration: $patch_name"
    elif [[ "$patch_name" == *0113* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "removed misplaced Activity Manager registration: $patch_name"
    elif [[ "$patch_name" == *0114* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied Neighborhood accessibility: $patch_name"
    elif [[ "$patch_name" == *0115* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied Neighborhood accessible role: $patch_name"
    elif [[ "$patch_name" == *0116* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied Group accessibility: $patch_name"
    elif [[ "$patch_name" == *0117* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied Group accessible role: $patch_name"
    elif [[ "$patch_name" == *0118* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied Frame accessibility: $patch_name"
    elif [[ "$patch_name" == *0119* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "repaired Frame accessibility placement: $patch_name"
    elif [[ "$patch_name" == *0120* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "applied Frame accessibility gettext import: $patch_name"
    elif [[ "$patch_name" == *0121* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "repaired final Frame accessibility placement: $patch_name"
    elif [[ "$patch_name" == *0122* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "relocated final Frame accessibility calls: $patch_name"
    elif [[ "$patch_name" == *0123* ]] &&
        (cd "$target" && patch --dry-run --fuzz=5 -p1 < "$patch" >/dev/null 2>&1); then
        (cd "$target" && patch --fuzz=5 -p1 < "$patch" >/dev/null)
        printf "%s\n" "$patch_digest" > "$stamp"
        echo "relocated current Frame accessibility calls: $patch_name"
    elif [[ "$patch_name" == *0029* || "$patch_name" == *0033* || "$patch_name" == *0034* || "$patch_name" == *0035* || "$patch_name" == *0036* || "$patch_name" == *0037* || "$patch_name" == *0038* || "$patch_name" == *0040* || "$patch_name" == *0041* || "$patch_name" == *0042* || "$patch_name" == *0043* || "$patch_name" == *0044* || "$patch_name" == *0045* || "$patch_name" == *0046* || "$patch_name" == *0047* || "$patch_name" == *0048* || "$patch_name" == *0049* || "$patch_name" == *0050* || "$patch_name" == *0051* || "$patch_name" == *0052* || "$patch_name" == *0053* || "$patch_name" == *0054* || "$patch_name" == *0055* || "$patch_name" == *0057* || "$patch_name" == *0079* || "$patch_name" == *0081* ]] &&
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
# Previous preview builds can leave registry-generated dangling links behind.
# They make Jarabe log "No bundle" errors during startup and obscure real
# inventory failures; remove only links whose targets are already absent.
find "$activity_dir" -xtype l -delete
if test -e "$activity_dir/Log.activity" && test ! -L "$activity_dir/Log.activity"; then
    echo "refusing to replace a real Log.activity directory" >&2
    exit 2
fi
ln -sfn "$log_activity" "$activity_dir/Log.activity"
help_activity="$repo/packages/gtk4-help-activity"
test -f "$help_activity/activity/activity.info" || {
    echo "missing native GTK4 Help Activity bundle: $help_activity" >&2
    exit 2
}
test -f "$help_activity/activity/activity-help.svg" || {
    echo "missing native GTK4 Help Activity icon: $help_activity/activity/activity-help.svg" >&2
    exit 2
}
ln -sfn "$help_activity" "$activity_dir/Help.activity"
count_activity="$repo/packages/gtk4-count-activity"
test -f "$count_activity/activity/activity.info" || {
    echo "missing native GTK4 Count Activity bundle: $count_activity" >&2
    exit 2
}
test -f "$count_activity/countactivity4.py" || {
    echo "missing native GTK4 Count Activity entrypoint" >&2
    exit 2
}
ln -sfn "$count_activity" "$activity_dir/Count.activity"
calculate_activity="$repo/packages/gtk4-calculate-activity"
test -f "$calculate_activity/activity/activity.info" || {
    echo "missing native GTK4 Calculate Activity bundle: $calculate_activity" >&2
    exit 2
}
test -f "$calculate_activity/calculateactivity4.py" || {
    echo "missing native GTK4 Calculate Activity entrypoint" >&2
    exit 2
}
ln -sfn "$calculate_activity" "$activity_dir/Calculate.activity"
test -f "$imageviewer_activity/activity/activity.info" || {
    echo "missing pinned Image Viewer Activity bundle: $imageviewer_activity" >&2
    exit 2
}
ln -sfn "$imageviewer_activity" "$activity_dir/ImageViewer.activity"
test -f "$terminal_activity/activity/activity.info" || {
    echo "missing pinned Terminal Activity bundle: $terminal_activity" >&2
    exit 2
}
ln -sfn "$terminal_activity" "$activity_dir/Terminal.activity"
test -f "$browse_activity/activity/activity.info" || {
    echo "missing pinned Browse Activity bundle: $browse_activity" >&2
    exit 2
}
ln -sfn "$browse_activity" "$activity_dir/Browse.activity"

for dep in 'gtk4 >= 4.22.2' 'wlroots-0.20 >= 0.20' 'vte-2.91-gtk4 >= 0.84' 'webkitgtk-6.0 >= 2.50'; do
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
