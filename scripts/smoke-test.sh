#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$root/Makefile"
test -f "$root/archiso/aspartame/profiledef.sh"
test -f "$root/archiso/aspartame/packages.x86_64"
rg -q '^sugar$' "$root/archiso/aspartame/packages.x86_64"
rg -q '^cups$' "$root/archiso/aspartame/packages.x86_64"
rg -q '^networkmanager$' "$root/archiso/aspartame/packages.x86_64"

required_scripts=(
    build-iso.sh run-qemu.sh ssh-asp sugar-info.sh sugar-reload.sh
    sugar-session-restart.sh sugar-logs.sh sugar-screenshot.sh sugar-patch.sh
    sugar-open-control-panel.sh sugar-upstream-sync.sh sugar-gtk4-init.sh sugar-gtk4-build.sh sugar-gtk4-check.sh sugar-gtk4-update.sh sugar-gtk4-smoke.sh
    sugar-modernization-check.sh
    activity-review-inventory.py activity-review-check.sh activity-review-capture.sh activity-contract-check.py
)
for script in "${required_scripts[@]}"; do
    test -x "$root/scripts/$script"
done
find "$root/scripts" -type f -name '*.sh' -print0 |
    xargs -0 -n 1 bash -n

guest_bin="$root/archiso/aspartame/airootfs/usr/local/bin"
guest_shell_tools=(
    aspartame-restart-sugar aspartame-sugar-health
    aspartame-sugar-info aspartame-sugar-logs
    aspartame-sugar-state aspartame-x-session
)
guest_python_tools=(
    aspartame-sugar-imports aspartame-version-overlay
)
for tool in "${guest_shell_tools[@]}" "${guest_python_tools[@]}"; do
    test -x "$guest_bin/$tool"
done
for tool in "${guest_shell_tools[@]}"; do
    bash -n "$guest_bin/$tool"
done
for tool in "${guest_python_tools[@]}"; do
    python3 - "$guest_bin/$tool" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
compile(path.read_text(encoding="utf-8"), str(path), "exec")
PY
done

test -f "$root/docs/SUGAR-DEVELOPMENT.md"
test -f "$root/docs/SUGAR-STYLING.md"
test -f "$root/sugar-overlay/extensions.list"
test -f "$root/sugar-overlay/src/jarabe/select_a_thing.py"
python3 -m py_compile "$root/sugar-overlay/src/jarabe/select_a_thing.py"
test -f "$root/archiso/aspartame/airootfs/usr/share/aspartame/select_a_thing.py"
test -f "$root/sugar-overlay/src/sitecustomize.py"
python3 -m py_compile "$root/sugar-overlay/src/sitecustomize.py"
test -f "$root/archiso/aspartame/airootfs/usr/share/aspartame/sitecustomize.py"
test -f "$root/archiso/aspartame/airootfs/usr/share/glib-2.0/schemas/org.aspartame.clock.gschema.xml"
grep -qx 'exec /usr/local/bin/aspartame-x-session' \
    "$root/archiso/aspartame/airootfs/etc/skel/.xinitrc"

while IFS= read -r relative; do
    test -n "$relative" || continue
    test -f "$root/sugar-overlay/src/$relative"
    python3 - "$root/sugar-overlay/src/$relative" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
compile(path.read_text(encoding="utf-8"), str(path), "exec")
PY
done < "$root/sugar-overlay/files.list"
while IFS= read -r relative; do
    test -n "$relative" || continue
    test -f "$root/archiso/aspartame/airootfs/usr/share/aspartame/$relative"
    python3 - "$root/archiso/aspartame/airootfs/usr/share/aspartame/$relative" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
compile(path.read_text(encoding="utf-8"), str(path), "exec")
PY
done < "$root/sugar-overlay/extensions.list"

for command in sugar-info sugar-reload sugar-session-restart sugar-logs sugar-screenshot sugar-patch-check sugar-open-control-panel sugar-upstream-sync sugar-gtk4-init sugar-gtk4-build sugar-gtk4-run sugar-gtk4-smoke sugar-gtk4-check sugar-gtk4-update sugar-modernization-check activity-review-inventory activity-review-check activity-review-capture activity-contract-check; do
    grep -q "^$command:" "$root/Makefile"
done

source "$root/sugar-overlay/UPSTREAM"
archive=${SUGAR_PACKAGE_ARCHIVE:-${BUILD_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build}/root.x86_64/var/cache/pacman/pkg/$SUGAR_ARCHIVE}
if test -f "$archive"; then
    "$root/scripts/sugar-patch.sh" check
else
    echo "Sugar overlay/patch sync: SKIP (package archive not built yet)"
fi

echo 'static Aspartame profile and Sugar development checks passed'
