#!/usr/bin/env bash
set -euo pipefail

# Regenerate the rebased shell/toolkit patches (0300/0301) from the pinned
# guest checkouts after editing them in place. The checkouts must sit at the
# SHAs pinned in sugar-gtk4-init.sh; everything that differs from that SHA,
# including new untracked source files, becomes the downstream delta.
#
# To move to a newer upstream head: rebase the delta in a scratch clone
# (git rebase --onto NEW OLD), resolve conflicts there, record the decisions
# in the patch header, update the pins in sugar-gtk4-init.sh, then run
# make sugar-gtk4-init sugar-gtk4-build and this script.

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
patch_dir=$repo/patches/gtk4-preview

regenerate() {
    local name=$1 number=$2 src
    src="$root/sources/$name"
    local patch_file
    patch_file=$(ls "$patch_dir/$number"-*.patch)
    local header
    header=$(sed '/^diff --git /,$d' "$patch_file")
    git -c safe.directory="$src" -C "$src" add -N -- 'src/*.py'
    {
        printf '%s\n' "$header"
        git -c safe.directory="$src" -C "$src" diff --binary HEAD -- . \
            ':(exclude)*.orig' ':(exclude)*.rej' ':(exclude)src/jarabe/config.py'
    } > "$patch_file.new"
    mv "$patch_file.new" "$patch_file"
    echo "regenerated $(basename "$patch_file")"
}

regenerate sugar 0300
regenerate sugar-toolkit-gtk4 0301
