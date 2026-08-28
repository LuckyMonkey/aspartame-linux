#!/bin/sh
export XDG_CURRENT_DESKTOP=Sugar
export XDG_SESSION_DESKTOP=sugar
exec dbus-run-session -- sugar
