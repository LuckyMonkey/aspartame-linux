#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=scripts/lib/sugar-vm.sh
source "$script_dir/lib/sugar-vm.sh"

require_vm

vm_ssh 'bash -s' <<'REMOTE'
set -eu

shell_pid=$(pgrep -u aspartame -f '^python3 -m jarabe\.main$' | head -n1 || true)
if [ -z "$shell_pid" ]; then
    echo "Sugar shell is not running; refusing to launch Control Panel." >&2
    exit 1
fi

if pgrep -u aspartame -f 'jarabe\.controlpanel\.gui|ControlPanel' >/dev/null 2>&1; then
    echo "Control Panel is already running in the Sugar session."
    exit 0
fi

getenv() {
    tr '\0' '\n' < "/proc/$shell_pid/environ" |
        sed -n "s/^$1=//p" | head -n1
}

log=/tmp/aspartame-control-panel.log
runuser -u aspartame -- env \
    DISPLAY="$(getenv DISPLAY)" \
    DBUS_SESSION_BUS_ADDRESS="$(getenv DBUS_SESSION_BUS_ADDRESS)" \
    XAUTHORITY="$(getenv XAUTHORITY)" \
    XDG_RUNTIME_DIR="$(getenv XDG_RUNTIME_DIR)" \
    PYTHONPATH="/usr/share/sugar/extensions:$(getenv PYTHONPATH)" \
    SUGAR_HOME="$(getenv SUGAR_HOME)" \
    SUGAR_PROFILE="$(getenv SUGAR_PROFILE)" \
    SUGAR_SCALING="$(getenv SUGAR_SCALING)" \
    SUGAR_MIME_DEFAULTS="$(getenv SUGAR_MIME_DEFAULTS)" \
    SUGAR_ACTIVITIES_HIDDEN="$(getenv SUGAR_ACTIVITIES_HIDDEN)" \
    SUGAR_GROUP_LABELS="$(getenv SUGAR_GROUP_LABELS)" \
    GTK2_RC_FILES="$(getenv GTK2_RC_FILES)" \
    XDG_CURRENT_DESKTOP="$(getenv XDG_CURRENT_DESKTOP)" \
    XDG_SESSION_DESKTOP="$(getenv XDG_SESSION_DESKTOP)" \
    nohup python3 -c 'import dbus.mainloop.glib; dbus.mainloop.glib.DBusGMainLoop(set_as_default=True); from gi.repository import Gtk; from jarabe import config; settings=Gtk.Settings.get_default(); settings.set_property("gtk-theme-name", "sugar-100" if "SUGAR_SCALING" in __import__("os").environ and __import__("os").environ["SUGAR_SCALING"] == "100" else "sugar-72"); settings.set_property("gtk-icon-theme-name", "sugar"); Gtk.IconTheme.get_default().append_search_path(config.data_path + "/icons"); settings.set_property("gtk-button-images", True); from jarabe.controlpanel.gui import ControlPanel; panel=ControlPanel(); panel.show_all(); Gtk.main()' >"$log" 2>&1 < /dev/null &
echo "Graphical Control Panel launched with Sugar's ControlPanel class."
echo "Guest log: $log"
REMOTE
