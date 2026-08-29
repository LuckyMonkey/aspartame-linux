#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/sugar-vm.sh"
source "$project_root/sugar-overlay/UPSTREAM"
overlay_root="$project_root/sugar-overlay/src"
files_list="$project_root/sugar-overlay/files.list"
extension_files_list="$project_root/sugar-overlay/extensions.list"
extension_root="$project_root/archiso/aspartame/airootfs/usr/share/sugar/extensions"
clock_schema="$project_root/archiso/aspartame/airootfs/usr/share/glib-2.0/schemas/org.aspartame.clock.gschema.xml"
version_file="$project_root/archiso/aspartame/airootfs/usr/share/aspartame/ui-version"
marker_file="$project_root/archiso/aspartame/airootfs/usr/local/bin/aspartame-version-overlay"
share_root=${DEV_SHARE:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev}
report_dir="$project_root/reports/reloads"
timestamp=$(date +%Y%m%d-%H%M%S)
mkdir -p "$report_dir"
exec > >(tee "$report_dir/sugar-reload-$timestamp.log") 2>&1

revision=$(git -C "$project_root" describe --always --dirty)
ui_version=$(tr -d '[:space:]' < "$version_file")
printf '%s\n\n' 'Aspartame Sugar reload'
printf 'Source:\n  %s\n  git %s\n  UI v%s\n\n' "$overlay_root" "$revision" "$ui_version"

printf '%s\n' 'Validation:'
while IFS= read -r relative; do
    test -n "$relative" || continue
    python3 - "$overlay_root/$relative" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
compile(path.read_text(encoding="utf-8"), str(path), "exec")
PY
done < "$files_list"
while IFS= read -r relative; do
    test -n "$relative" || continue
    python3 - "$extension_root/$relative" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
compile(path.read_text(encoding="utf-8"), str(path), "exec")
PY
done < "$extension_files_list"
printf '  Date & Time extension syntax ... PASS\n'

printf '  Python syntax ........ PASS\n'
"$project_root/scripts/sugar-patch.sh" check >/dev/null
printf '  overlay/patch sync ... PASS\n'
require_vm
printf '  VM SSH ............... PASS\n'

guest_version=$(vm_ssh pacman -Q "$SUGAR_PACKAGE" | awk '{print $2}')
if test "$guest_version" != "$SUGAR_VERSION"; then
    printf '  guest package ........ FAIL (expected %s, got %s)\n' "$SUGAR_VERSION" "$guest_version" >&2
    exit 10
fi
printf '  guest package ........ PASS (%s %s)\n' "$SUGAR_PACKAGE" "$guest_version"

printf '\nHost write access:\n'
printf '  sudo is used only for %s\n' "$share_root"
sudo -v

vm_ssh env EXPECTED_SUGAR_VERSION="$SUGAR_VERSION" bash -s <<'REMOTE'
set -euo pipefail
share=/mnt/aspartame-dev/sugar
mountpoint -q /mnt/aspartame-dev
current=$(pacman -Q sugar | awk '{print $2}')
test "$current" = "$EXPECTED_SUGAR_VERSION"
if test -f "$share/.base-package"; then
    test "$(cat "$share/.base-package")" = "sugar $current" || {
        echo 'runtime Sugar base does not match guest package; refusing to overwrite it' >&2
        exit 20
    }
elif test -f "$share/src/jarabe/__init__.py"; then
    printf 'sugar %s\n' "$current" > "$share/.base-package"
else
    site=$(PYTHONPATH= python3 - <<'PY'
import importlib.util
spec = importlib.util.find_spec("jarabe")
print(next(iter(spec.submodule_search_locations)))
PY
)
    install -d "$share/src/jarabe"
    cp -a "$site/." "$share/src/jarabe/"
    printf 'sugar %s\n' "$current" > "$share/.base-package"
fi
REMOTE

while IFS= read -r relative; do
    test -n "$relative" || continue
    sudo install -D -m 0644 "$overlay_root/$relative" "$share_root/sugar/src/$relative"
done < "$files_list"

sudo install -m 0644 "$files_list" "$share_root/sugar/files.list"
sudo install -m 0644 "$extension_files_list" "$share_root/extensions.list"
while IFS= read -r relative; do
    test -n "$relative" || continue
    sudo install -D -m 0644 "$extension_root/$relative" "$share_root/extensions/$relative"
done < "$extension_files_list"
sudo install -D -m 0644 "$clock_schema" "$share_root/schemas/org.aspartame.clock.gschema.xml"
sudo install -D -m 0644 "$version_file" "$share_root/ui-version"
sudo install -D -m 0755 "$project_root/archiso/aspartame/airootfs/etc/skel/.xinitrc" "$share_root/tools/aspartame-xinitrc"
sudo install -D -m 0755 "$marker_file" "$share_root/tools/aspartame-version-overlay"
for tool in aspartame-sugar-info aspartame-sugar-health aspartame-sugar-logs aspartame-sugar-state aspartame-sugar-imports aspartame-x-session aspartame-restart-sugar; do
    sudo install -D -m 0755 \
        "$project_root/archiso/aspartame/airootfs/usr/local/bin/$tool" \
        "$share_root/tools/$tool"
done

vm_ssh bash -s <<'REMOTE'
set -euo pipefail
for tool in aspartame-sugar-info aspartame-sugar-health aspartame-sugar-logs aspartame-sugar-state aspartame-sugar-imports aspartame-x-session aspartame-restart-sugar; do
    install -m 0755 "/mnt/aspartame-dev/tools/$tool" "/usr/local/bin/$tool"
done
if ! grep -qx 'exec /usr/local/bin/aspartame-x-session' /home/aspartame/.xinitrc 2>/dev/null; then
    if test -f /home/aspartame/.xinitrc && test ! -e /home/aspartame/.xinitrc.pre-aspartame-system-session; then
        cp -p /home/aspartame/.xinitrc /home/aspartame/.xinitrc.pre-aspartame-system-session
    fi
    install -o aspartame -g aspartame -m 0755 /mnt/aspartame-dev/tools/aspartame-xinitrc /home/aspartame/.xinitrc
fi
install -m 0755 /mnt/aspartame-dev/tools/aspartame-version-overlay \
    /usr/local/bin/aspartame-version-overlay
install -m 0644 /mnt/aspartame-dev/schemas/org.aspartame.clock.gschema.xml /usr/share/glib-2.0/schemas/org.aspartame.clock.gschema.xml
while IFS= read -r relative; do
    test -n "$relative" || continue
    install -D -m 0644 "/mnt/aspartame-dev/extensions/$relative" "/usr/share/sugar/extensions/$relative"
done < /mnt/aspartame-dev/extensions.list
glib-compile-schemas /usr/share/glib-2.0/schemas
install -d -o aspartame -g aspartame /home/aspartame/.cache
pkill -u aspartame -f /usr/local/bin/aspartame-version-overlay || true
runuser -u aspartame -- sh -c \
    'DISPLAY=:0 nohup /usr/local/bin/aspartame-version-overlay >/home/aspartame/.cache/aspartame-version-overlay.log 2>&1 </dev/null &'
REMOTE

host_manifest=$(while IFS= read -r relative; do
    test -n "$relative" || continue
    printf '%s  %s\n' "$(sha256sum "$overlay_root/$relative" | awk '{print $1}')" "$relative"
done < "$files_list")
remote_manifest=$(vm_ssh bash -s <<'REMOTE'
set -euo pipefail
while IFS= read -r relative; do
    test -n "$relative" || continue
    printf '%s  %s\n' "$(sha256sum "/mnt/aspartame-dev/sugar/src/$relative" | awk '{print $1}')" "$relative"
done < /mnt/aspartame-dev/sugar/files.list
REMOTE
)
if test "$host_manifest" != "$remote_manifest"; then
    echo '  source hashes ......... FAIL' >&2
    diff -u <(printf '%s\n' "$host_manifest") <(printf '%s\n' "$remote_manifest") || true
    exit 11
fi
printf '  source hashes ........ PASS\n'
host_extension_manifest=$(while IFS= read -r relative; do
    test -n "$relative" || continue
    printf '%s  %s\n' "$(sha256sum "$extension_root/$relative" | awk '{print $1}')" "$relative"
done < "$extension_files_list")
remote_extension_manifest=$(vm_ssh bash -s <<'REMOTE'
set -euo pipefail
while IFS= read -r relative; do
    test -n "$relative" || continue
    printf '%s  %s\n' "$(sha256sum "/mnt/aspartame-dev/extensions/$relative" | awk '{print $1}')" "$relative"
done < /mnt/aspartame-dev/extensions.list
REMOTE
)
if test "$host_extension_manifest" != "$remote_extension_manifest"; then
    echo '  extension hashes ....... FAIL' >&2
    diff -u <(printf '%s\n' "$host_extension_manifest") <(printf '%s\n' "$remote_extension_manifest") || true
    exit 13
fi
printf '  extension hashes ...... PASS\n'


old_state=$(vm_ssh /usr/local/bin/aspartame-sugar-state)
printf '\nPrevious runtime:\n  %s\n' "$old_state"
printf 'Restart method:\n  SIGTERM jarabe.main; .xinitrc respawns the Sugar D-Bus island\n'
vm_ssh /usr/local/bin/aspartame-restart-sugar

health=''
for _ in $(seq 1 30); do
    if health=$(vm_ssh /usr/local/bin/aspartame-sugar-health 2>&1); then
        break
    fi
    sleep 0.5
done
if ! grep -q '^Result: PASS$' <<<"$health"; then
    printf '%s\n' "$health" >&2
    echo 'Sugar failed health checks; run make sugar-logs' >&2
    exit 12
fi
new_state=$(vm_ssh /usr/local/bin/aspartame-sugar-state)
printf '\nNew runtime:\n  %s\n\n' "$new_state"
printf '%s\n' "$health"
printf '\nRuntime imports:\n'
vm_ssh /usr/local/bin/aspartame-sugar-info | sed -n '/^Runtime imports$/,/^Styling$/p'
printf 'Result:\n  PASS\n'
printf 'Report:\n  %s\n' "$report_dir/sugar-reload-$timestamp.log"
