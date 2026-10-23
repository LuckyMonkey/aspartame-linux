# Aspartame handoff — 2026-10-23

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
  - `aspartame-build/artifacts/out/aspartame-2026.10.23-x86_64.iso`
    (sha256 `c0d0a5fc…`) carries the runtime export `ccce1187…`
    (`runtime/aspartame-dev/artifacts/gtk4-preview-standalone-20261022b.tar.gz`)
    and the ported Activities.
  - Receipts and regression on the packaged runtime, no dev share:
    `reports/gtk4/fullport-receipts-20261023.md` (runtime) and
    `reports/gtk4/repin-qualification-20261022.md` (Settings, Chirality).
- **Conversion tracker:** every gate is closed, including two-guest share
  and join.
- **Default Space:** GTK4. GTK3 keeps running as the F7 recovery Space
  (`ASPARTAME_DEFAULT_SPACE=gtk3` restores the old default).
- **Retirement gate:** PASS (`scripts/sugar-gtk4-retirement-gate.sh`).
  - All seven candidates are FULL PORT: Markdown, Pippy, Abacus, Finance,
    Jukebox, Write, Portfolio. Gaps are listed per Activity in
    `docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md`.
  - Color My World left the list (no GTK3 version).
  - Nothing is removed. GTK3 packages stay until a separate decision.
- **Host suite:** `make test` (633 passed).

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
1. **GTK3 removal (owner decision).** The evidence gate passes. Next would
   be a disposable image without the GTK3 packages, qualified with the
   same receipts and regression, before touching the main image. Keep
   the F7 recovery Space until then.
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
- Receipts: copy `scripts/sugar-gtk4-fullport-probe.py` to `/tmp` in the
  guest, then run `scripts/sugar-gtk4-fullport-receipt.py <candidate>`
  on the host. The guest probes in `/usr/lib/aspartame/gtk4-preview/scripts`
  need `GTK4_ROOT=/usr/lib/aspartame/gtk4-preview`; the lifecycle probes
  and the matrix run as root.
- On the ISO, the packaged runtime is `/usr/lib/aspartame/gtk4-preview`,
  and its probes are in `scripts/` there. Copy
  `sugar-gtk4-settings-probe.py` to `/tmp` first.
