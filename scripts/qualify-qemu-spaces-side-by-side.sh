#!/usr/bin/env bash
set -euo pipefail

project_root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
ssh_port=${SSH_PORT:-2223}
qmp=${ASPARTAME_QEMU_QMP:-/tmp/aspartame-qemu-qmp-headless}
report=${ASPARTAME_SPACES_REPORT:-$project_root/reports/gtk4/spaces-side-by-side-headless-$(date -u +%Y%m%dT%H%M%SZ).log}
case "$report" in
    /*) ;;
    *) report="$project_root/$report" ;;
esac
mkdir -p "$(dirname -- "$report")"
report_dir=$(CDPATH= cd -- "$(dirname -- "$report")" && pwd)
screenshot=${ASPARTAME_SPACES_SCREENSHOT:-$report_dir/spaces-side-by-side.png}
case "$screenshot" in
    /*) ;;
    *) screenshot="$project_root/$screenshot" ;;
esac

{
    echo "spaces-qualification=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "ssh-port=$ssh_port qmp=$qmp"
    echo "screenshot=$screenshot"
    SSH_PORT="$ssh_port" "$project_root/scripts/ssh-asp" \
        'runuser -u aspartame -- env DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000 ASPARTAME_ATSPI_BUS=unix:path=/run/user/1000/aspartame-gtk4/at-spi/bus_0 python3 /mnt/aspartame-dev/scripts/sugar-gtk4-spaces-menu-probe.py'
    (
        cd "$project_root"
        ASPARTAME_QEMU_QMP="$qmp" \
            "$project_root/scripts/qemu-headless-macro.py" \
            "$project_root/macros/qemu/spaces-side-by-side.json"
    )
    framebuffer="$project_root/reports/screenshots/spaces-side-by-side.png"
    test -s "$framebuffer"
    if [ "$screenshot" != "$framebuffer" ]; then
        cp "$framebuffer" "$screenshot"
    fi
    test -s "$screenshot"
    echo "spaces-qualification=PASS report=$report screenshot=$screenshot"
} 2>&1 | tee "$report"
