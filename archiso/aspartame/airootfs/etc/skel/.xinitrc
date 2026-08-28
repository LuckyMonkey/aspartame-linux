#!/bin/sh
export XDG_CURRENT_DESKTOP=Sugar
export XDG_SESSION_DESKTOP=sugar
dbus-run-session -- sugar-session >/tmp/aspartame-sugar.log 2>&1
sugar_status=$?
printf '\n--- sugar-session exited (%s) ---\n' "$sugar_status" >>/tmp/aspartame-startx.log
cat /tmp/aspartame-sugar.log >>/tmp/aspartame-startx.log
exit "$sugar_status"
