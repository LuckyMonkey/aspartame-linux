#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$root/Makefile"
test -f "$root/archiso/aspartame/profiledef.sh"
test -f "$root/archiso/aspartame/packages.x86_64"
rg -q '^sugar$' "$root/archiso/aspartame/packages.x86_64"
rg -q '^cups$' "$root/archiso/aspartame/packages.x86_64"
rg -q '^networkmanager$' "$root/archiso/aspartame/packages.x86_64"
test -x "$root/scripts/build-iso.sh" && test -x "$root/scripts/run-qemu.sh"
echo "static Aspartame profile checks passed"

