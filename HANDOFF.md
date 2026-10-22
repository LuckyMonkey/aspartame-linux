# Aspartame handoff — 2026-10-22

## Completed
- Fixed malformed hunk length in GTK4 patch 0058: it silently omitted Settings window retention and the success return.
- Added scripts/repair-gtk4-controlpanel-action.py to repair older exported runtimes during preview builds and ISO staging. Handles upstream UTF-8 BOM; rejects unfamiliar method endings.
- Added guest scripts/sugar-gtk4-settings-probe.py, including --lifecycle-only.
- Documented Settings ownership in docs/SETTINGS-ARCHITECTURE.md and runtime evidence in reports/gtk4/settings-lifecycle-20261022.md.
- Temporary October 17 ISO guest reproduced the original failure. After repair and GTK4 restart, three Settings open/close/reopen cycles and duplicate-modal refusal passed.
- Host full run: 581 passed, two staging fixture failures. Fixed those fixtures; focused rerun: 15 passed. No further checks requested by user.

## Remaining / next phase
1. Build a new ISO with `make iso`; the current October 17 image does NOT contain this repair.
2. Copy scripts/sugar-gtk4-settings-probe.py to /tmp in the guest, then run `python3 /tmp/sugar-gtk4-settings-probe.py --lifecycle-only`.
3. Diagnose About Computer tile activation: AT-SPI finds the tile but it exposes no action; GrabFocus is unsupported. AT-SPI GenerateMouseEvent at reported bounds did not reveal inventory. Full probe times out at local inventory; refresh/visual acceptance is NOT qualified.
4. Complete Settings geometry, Escape, and broader lifecycle coverage separately. No new ISO or accepted About screenshot was produced.

## Workspace
- Existing modification in scripts/sugar-gtk4-build.sh adds scoped Git safe.directory arguments. It predates this task and is intentionally excluded from this task's commit.
- Existing untracked reports/gtk4/qemu-go-home.png and October 4 visual-sweep files predate this task; leave intact.
- Test VM used QEMU_HEADLESS=1 QEMU_SNAPSHOT=1 QEMU_DEV_SHARE_MOUNT=0, SSH port 2222, QMP /tmp/aspartame-qemu-qmp. Its changes are temporary and will disappear at shutdown. Existing persistent disks were not intentionally modified.
- /tmp/aspartame-askpass was recreated from the development image's configured login for local testing.

User requested stopping checks, committing and syncing, and leaving this handoff so another agent can continue.

## Continued code-research checkpoint
User resumed work, then explicitly requested **no checks**: research code and
make proposals instead. Do not restart tests, ISO builds, or runtime probing
without a later change of instruction. See `docs/SETTINGS-FIX-PROPOSALS.md`
for prioritized fixes and code evidence: capture-phase Settings focus theft,
inconsistent navigation cleanup, synchronous/repeated About inventory,
archive/overlay drift, tile accessibility, and incomplete GTK4 manager parity.
These are proposals, not implementation or new runtime acceptance claims.
A snapshot guest was started before the no-checks instruction; shutdown was
requested immediately afterward. No new runtime probe was run.
