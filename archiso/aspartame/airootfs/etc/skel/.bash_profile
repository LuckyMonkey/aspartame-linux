if [[ -z "${DISPLAY:-}" && "$(tty 2>/dev/null)" == "/dev/tty1" ]]; then
    startx >/tmp/aspartame-startx.log 2>&1
    startx_status=$?
    printf '\n--- startx exited (%s) ---\n' "$startx_status"
    cat /tmp/aspartame-startx.log
    exit "$startx_status"
fi
