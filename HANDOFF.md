# Aspartame handoff — 2026-10-22

This file holds the current state only. Earlier checkpoints are in git
history.

## State
- **Upstream pins:** sugar PR #1106 `beaae56`; sugar-toolkit-gtk4 main
  `9d86a31`.
  - Aspartame's changes are `0300` (sugar) and `0301` (toolkit), plus
    seven datastore/ext/Log/Casilda patches.
  - Older patches are kept in `patches/gtk4-preview/folded/` for history
    and intent tests.
  - Procedure: `docs/sugar-modernization/UPSTREAM_SYNC.md`.
- **ISO:**
  - `aspartame-build/artifacts/out/aspartame-2026.10.22-x86_64.iso`
    (sha256 `f2efc04e…`) carries the runtime export `eae0e392…`.
  - Every receipt check passes on the packaged runtime without the dev
    share: `reports/gtk4/repin-qualification-20261022.md`.
- **Conversion tracker:** every gate is closed, including two-guest share
  and join.
- **Retirement gate:** blocked only on `full-parity`. No Activity is
  FULL PORT yet.
- **Host suite:** `make test`.

## Building the ISO
1. Export the runtime from the dev guest with `scripts/sugar-gtk4-export.sh`.
2. Copy the export over `aspartame-build/artifacts/gtk4-preview-standalone.tar.gz`.
   Copying is required: `sudo` drops `GTK4_PREVIEW_ARCHIVE`, and the
   chroot cannot see host paths.
3. Run `make iso`, which asks for sudo once. The build refuses a stale
   archive.
4. The upstream Activities are copied in from `packages/upstream-activities`
   at build time.

## Next
1. **Owner decision:** the FULL PORT standard for Portfolio, Markdown,
   Finance, Write, Pippy, Jukebox, Color My World and Abacus. This is the
   only retirement blocker.
2. **Open proposals:** see `docs/OPEN-PROPOSALS.md`.
   - Unknown-key preservation for JSON payloads.
   - Snakepit GUI workflow observability.
   - Activity Manager semantics.
   - Chirality handoff and resume validation.
3. **Collaboration:** test joining from the Neighborhood view and
   exchanging content between peers.
4. **Upstream:** report the bugs listed on issue #1 to Sugar Labs.

## Guest workflow notes
- Boot a test VM with `QEMU_HEADLESS=1 QEMU_SNAPSHOT=1` and add
  `QEMU_DEV_SHARE_MOUNT=0` for packaged runs. SSH is on port 2222; QMP is
  `/tmp/aspartame-qemu-qmp`.
- `./scripts/ssh-asp` needs `SSH_ASKPASS=/tmp/aspartame-askpass
  SSH_ASKPASS_REQUIRE=force`; do not use BatchMode.
- On the ISO, the packaged runtime is `/usr/lib/aspartame/gtk4-preview`,
  and its probes are in `scripts/` there. Copy
  `sugar-gtk4-settings-probe.py` to `/tmp` first.
