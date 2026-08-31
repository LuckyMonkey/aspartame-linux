#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "usage: $0 CHECKOUT [CHECKOUT ...]" >&2
    exit 2
fi

for checkout in "$@"; do
    test -d "$checkout/.git" || {
        echo "not a git checkout: $checkout" >&2
        exit 1
    }
    git -C "$checkout" fetch --prune origin
    printf '%s\t' "$checkout"
    git -C "$checkout" log -1 --format='%H %cs %s'
done
