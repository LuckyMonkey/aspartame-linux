#!/usr/bin/env bash
set -euo pipefail

: "${PROFILE:?PROFILE is required}"
: "${OUT_DIR:?OUT_DIR is required}"
: "${WORK_DIR:?WORK_DIR is required}"

if ! command -v mkarchiso >/dev/null 2>&1; then
    echo "error: mkarchiso is required; run this from an Arch build environment" >&2
    exit 2
fi

mkdir -p "$OUT_DIR" "$WORK_DIR"
mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$PROFILE"

