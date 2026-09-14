#!/usr/bin/env bash
set -euo pipefail

if test -z "${ISO:-}"; then
    ISO=$(find /media/freezer/SteamLibrary/vms/aspartame-build/artifacts/out \
        -maxdepth 1 -type f -name 'aspartame-*.iso' -printf '%T@ %p\n' |
        sort -nr | head -n1 | cut -d' ' -f2-)
fi
RAM=${RAM:-4096}
CPUS=${CPUS:-4}
DISK=${DISK:-"/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-test.qcow2"}
DATA_DISK=${DATA_DISK:-"/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-data.qcow2"}
AUDIO_BACKEND=${AUDIO_BACKEND:-none}
SERIAL_LOG=${SERIAL_LOG:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-serial.log}
DEV_SHARE=${DEV_SHARE:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-dev}
QEMU_MONITOR=${QEMU_MONITOR:-/tmp/aspartame-qemu-monitor}
QEMU_QMP=${QEMU_QMP:-/tmp/aspartame-qemu-qmp}
# Keep the window floating while automatically forwarding keyboard/pointer
# events when the pointer is over the guest.  Without the grab, GTK4's
# fullscreen shell can look focused on the host but QEMU never delivers F1-F8
# to the USB keyboard.  Set QEMU_GRAB_ON_HOVER=off only for pointer-only runs.
QEMU_GRAB_ON_HOVER=${QEMU_GRAB_ON_HOVER:-on}
# The GTK frontend initially sizes itself from the firmware's low-resolution
# mode.  Keep the VM floating/resizable, but grow it to a useful 16:9 viewport
# once the host window appears.  Set either value to 0 to disable this helper.
QEMU_WINDOW_WIDTH=${QEMU_WINDOW_WIDTH:-1600}
QEMU_WINDOW_HEIGHT=${QEMU_WINDOW_HEIGHT:-900}

test -f "$ISO" || { echo "missing ISO: $ISO" >&2; exit 2; }
mkdir -p "$(dirname "$DISK")"
mkdir -p "$DEV_SHARE"
if ! test -f "$DISK"; then
    qemu-img create -f qcow2 "$DISK" 32G
fi
if ! test -f "$DATA_DISK"; then
    qemu-img create -f qcow2 "$DATA_DISK" 16G
fi

ACCEL=(-accel tcg,thread=multi -cpu max)
if test -r /dev/kvm && test -w /dev/kvm; then
    ACCEL=(-enable-kvm -cpu host)
fi

qemu-system-x86_64 \
    "${ACCEL[@]}" -machine q35 -m "$RAM" -smp "$CPUS" \
    -drive "file=$DISK,if=virtio,format=qcow2" \
    -drive "file=$DATA_DISK,if=virtio,format=qcow2" \
    -cdrom "$ISO" -boot menu=on \
    -device virtio-vga,xres=1920,yres=1080 -display "gtk,gl=off,zoom-to-fit=on,grab-on-hover=$QEMU_GRAB_ON_HOVER" \
    -monitor "unix:$QEMU_MONITOR,server,nowait" \
    -qmp "unix:$QEMU_QMP,server=on,wait=off" \
    -serial "file:$SERIAL_LOG" \
    -nic user,model=virtio-net-pci,hostfwd=tcp:127.0.0.1:2222-:22 \
    -audiodev "driver=$AUDIO_BACKEND,id=a0" -device AC97,audiodev=a0 \
    -device qemu-xhci -device usb-tablet -device usb-kbd \
    -virtfs "local,path=$DEV_SHARE,mount_tag=aspartame-dev,security_model=none" \
    -name Aspartame &
qemu_pid=$!

# Resize only the named QEMU window; this is deliberately best-effort so the
# launcher remains usable on SSH/headless hosts and under other window managers.
if test "$QEMU_WINDOW_WIDTH" -gt 0 && test "$QEMU_WINDOW_HEIGHT" -gt 0 \
        && command -v xdotool >/dev/null 2>&1; then
    for _attempt in $(seq 1 50); do
        qemu_window=$(xdotool search --name '^QEMU \(Aspartame\)$' 2>/dev/null | head -n1 || true)
        if test -n "$qemu_window"; then
            xdotool windowsize "$qemu_window" "$QEMU_WINDOW_WIDTH" \
                "$QEMU_WINDOW_HEIGHT" >/dev/null 2>&1 || true
            break
        fi
        sleep 0.1
    done
fi
wait "$qemu_pid"
