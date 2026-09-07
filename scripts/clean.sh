#!/usr/bin/env bash
set -euo pipefail

build_root=${BUILD_ROOT:-/media/freezer/SteamLibrary/vms/aspartame-build}
rm -rf -- "$build_root/artifacts/out" "$build_root/artifacts/work"
