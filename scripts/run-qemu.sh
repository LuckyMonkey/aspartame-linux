#!/usr/bin/env bash
set -euo pipefail

ISO=${ISO:-"$(dirname "$0")/../out/aspartame-x86_64.iso"}
RAM=${RAM:-4096}
CPUS=${CPUS:-4}
DISK=${DISK:-"$(dirname "$0")/../runtime/aspartame-test.qcow2"}

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
    -nic user,model=virtio-net-pci \
    -audiodev driver=none,id=a0 -device AC97,audiodev=a0 \
    -device qemu-xhci -device usb-tablet \
    -name Aspartame

