#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/sugar-vm.sh"
require_vm

version_file="$project_root/archiso/aspartame/airootfs/usr/share/aspartame/ui-version"
version=$(tr -d '[:space:]' < "$version_file")
timestamp=$(date +%Y%m%d-%H%M%S)
output_dir=${SCREENSHOT_DIR:-$project_root/reports/screenshots}
output_file="$output_dir/sugar-${timestamp}-v${version}.png"
remote_file="/tmp/sugar-${timestamp}-v${version}.png"
mkdir -p "$output_dir"

resolution=$(vm_ssh "runuser -u aspartame -- env DISPLAY=:0 xrandr --current" |
    awk '/ connected primary / {split($4, mode, "+"); print mode[1]; exit}')
test -n "$resolution" || { echo 'could not determine guest display size' >&2; exit 2; }

vm_ssh "runuser -u aspartame -- env DISPLAY=:0 ffmpeg -hide_banner -loglevel error -f x11grab -video_size '$resolution' -i :0 -frames:v 1 -y '$remote_file'"
vm_scp_from "$remote_file" "$output_file"
vm_ssh rm -f "$remote_file"

test -s "$output_file"
printf 'Screenshot: %s\n' "$output_file"
printf 'Resolution: %s\n' "$resolution"
printf 'SHA-256: %s\n' "$(sha256sum "$output_file" | awk '{print $1}')"
if command -v identify >/dev/null 2>&1; then
    identify "$output_file"
fi

# Keep OCR beside the image as searchable evidence of what was visible.
ocr_file="${output_file%.png}.txt"
if command -v tesseract >/dev/null 2>&1; then
    tesseract "$output_file" "${output_file%.png}" --psm 11 >/dev/null 2>&1 || true
    printf 'OCR text: %s\n' "$ocr_file"
fi

# Capture-only by design. Restarting Sugar belongs to sugar-reload or the
# full-session restart command, never to screenshot collection.
