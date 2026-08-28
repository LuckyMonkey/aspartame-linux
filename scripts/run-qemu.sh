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
AUDIO_BACKEND=${AUDIO_BACKEND:-none}
SERIAL_LOG=${SERIAL_LOG:-/media/freezer/SteamLibrary/vms/aspartame-build/runtime/aspartame-serial.log}

test -f "$ISO" || { echo "missing ISO: $ISO" >&2; exit 2; }
mkdir -p "$(dirname "$DISK")"
if ! test -f "$DISK"; then
    qemu-img create -f qcow2 "$DISK" 32G
fi

ACCEL=(-accel tcg,thread=multi -cpu max)
if test -r /dev/kvm && test -w /dev/kvm; then
    ACCEL=(-enable-kvm -cpu host)
fi

exec qemu-system-x86_64 \
    "${ACCEL[@]}" -machine q35 -m "$RAM" -smp "$CPUS" \
    -drive "file=$DISK,if=virtio,format=qcow2" \
    -cdrom "$ISO" -boot menu=on \
    -device virtio-vga -display gtk,gl=off \
    -serial "file=$SERIAL_LOG" \
    -nic user,model=virtio-net-pci \
    -audiodev "driver=$AUDIO_BACKEND,id=a0" -device AC97,audiodev=a0 \
    -device qemu-xhci -device usb-tablet \
    -name Aspartame
