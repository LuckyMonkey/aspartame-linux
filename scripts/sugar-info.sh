#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/sugar-vm.sh"
require_vm
exec ssh "${SSH_OPTS[@]}" "$SSH_TARGET" /usr/local/bin/aspartame-sugar-info
