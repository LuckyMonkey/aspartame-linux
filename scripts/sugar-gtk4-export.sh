#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "usage: GTK4_ROOT=/path/to/gtk4-preview $0 /path/to/gtk4-preview-standalone.tar.gz" >&2
    exit 2
fi

root=$(realpath -- "${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}")
archive=$(realpath -m -- "$1")
for required in PINS.tsv sources prefix venv runtime/schemas/gschemas.compiled \
                runtime/group-labels.json; do
    test -e "$root/$required" || {
        echo "missing built GTK4 input: $root/$required; run sugar-gtk4-build.sh first" >&2
        exit 2
    }
done

mkdir -p -- "$(dirname "$archive")"
partial=$(mktemp "${archive}.partial.XXXXXX")
trap 'rm -f -- "$partial"' EXIT

# Select build outputs explicitly: never export a developer's Journal/profile,
# dconf, portal mounts, Wayland sockets, logs, or stale runtime Activity copies.
# Retain source Git metadata because the runner reports the upstream revisions.
# Transform member/hardlink names only; relative symlink targets must stay as-is.
tar -C "$root" --sort=name --owner=0 --group=0 --numeric-owner \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='*.log' \
    --transform='flags=rh;s#^#gtk4-preview/#' \
    -czf "$partial" PINS.tsv sources prefix venv \
    runtime/schemas runtime/group-labels.json
mv -f -- "$partial" "$archive"
sha256sum -- "$archive"
