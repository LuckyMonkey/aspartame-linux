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

## Runtime state research checkpoint
See `docs/RUNTIME-STATE-FIX-PROPOSALS.md` for code-backed proposals covering:
- CLI/GUI Snakepit source-freshness mismatch and malformed record handling.
- Missing GUI workflow completion/exit reporting.
- Chirality lost-update risks across independent state writers.
- Partial resume/retry and cross-session process matching.
- Model-only handoff versus actual target object delivery.
- Validation occurring after visible activation.
The snapshot guest shutdown completed successfully. Current mode remains
code research and documentation only; no new checks were run.

## 10% checkpoint — document preservation
New source-only findings are in `docs/DOCUMENT-PRESERVATION-PROPOSALS.md`.
Highest priority: Read drops Write formatting on serialization and retains its
sample after empty/failed loads; Paint substitutes blank content after parse
failure. Review the toolkit save contract before exposing cross-Activity
handoff, and preserve original objects on unsupported/failed loads.
Also proposed transactional Record restore and success-driven Journal row
updates. No new tests/builds/runtime checks. User requested immediate commit
and sync at 10%; continue from these documents instead of rediscovering.

## Checkpoint — document preservation, second pass
Extended `docs/DOCUMENT-PRESERVATION-PROPOSALS.md` with a 14-Activity audit.
Markdown, Pippy, Portfolio, GTD, Finance, Fototoon, GridPaint, ColorMyWorld,
Words, Get Books, TurtleArt, Poll, Jukebox and Calculate all turn a failed
load into a default state that is saved on close. TurtleArt and Poll also
partially assign state. Jukebox can raise out of `read_file()`. GTD,
Finance and GridPaint resave lossily. Proposed one shared load-outcome guard
in the activity contract. The toolkit save contract is still unconfirmed:
its source exists only in the guest tree (/home/aspartame/Development/gtk4-preview).
Still source-only, with no checks. Suggested next step, when the user allows
code changes and checks: implement the guard in Markdown/Pippy/Portfolio first.

## 2026-10-22 — upstream re-pin (checks allowed again)
The user lifted no-checks and asked to finish as much GTK4 work as possible.
The plan is in `~/.claude/plans/glittery-napping-peacock.md`.
- Re-pinned sugar to PR #1106 `beaae56` and the toolkit to main `9d86a31`
  (PR #35 merged). The series is now 0300/0301 plus seven other-repo
  patches; 132 patches moved to `patches/gtk4-preview/folded/`. See
  `docs/sugar-modernization/UPSTREAM_SYNC.md`.
- Host replay is exact (GTK4-025 closed). Host suite: 563 passed.
- `build-iso.sh` refuses a stale runtime archive. The October 4 archive
  was stale: it lacked 0058, 0112z and 0180-0205.
- Not yet done: guest `make sugar-gtk4-init sugar-gtk4-build`, re-export,
  `make iso`, then the qualification probes. Palettes, menus and icons
  took upstream's rewrite, so re-check them visually.

## 2026-10-22 — re-pin qualified in the guest, Settings/About/documents fixed
Receipt: `reports/gtk4/repin-qualification-20261022.md`. The guest build
on the new pins passes the runtime check, the GTK3 and GTK4 lifecycle
probes (3/3 each), the full Settings + About probe (HANDOFF item 3 is
closed) and the 50-Activity matrix. Host suite: 575 passed.
Also landed: Journal payload preservation (toolkit guard plus all audited
Activities), the single Settings dismissal contract, bounded and
asynchronous About inventory, Settings tiles as real buttons, and
GTK4 theme lookup on the XDG data dirs.

Next phase (needs the owner):
1. In the guest: `GTK4_ROOT=/home/aspartame/Development/gtk4-preview
   bash /mnt/aspartame-dev/scripts/sugar-gtk4-export.sh
   /mnt/aspartame-dev/artifacts/gtk4-preview-standalone.tar.gz`
   (the VM is in snapshot mode, so export before shutdown).
2. Host, with sudo:
   copy that tarball over
   `/media/freezer/SteamLibrary/vms/aspartame-build/artifacts/gtk4-preview-standalone.tar.gz`,
   then `make iso`. `sudo` drops `GTK4_PREVIEW_ARCHIVE` and the chroot
   cannot see host paths, so that staged copy is what the build reads. The
   ISO build refuses the stale October 4 archive.
3. Boot the new ISO and rerun the receipt checks against the packaged
   runtime.
Still open: the two-guest share/join run (the last tracker gate), Journal
row persistence (P2), and the runtime-state P1 proposals.

## 2026-10-22 (late): share/join qualified; Snakepit, Chirality and Journal landed
- **Two-guest join PASS** on the re-pinned build. This closes the last
  conversion-tracker gate. The retirement gate now blocks only on
  `full-parity`. Fixed on the way:
  - the Share toggle palette was closed within the same click (upstream
    palette rewrite);
  - `peer-prepare` broke the X cookie;
  - the toolkit never emitted `joined` when the peer initially saw only
    itself in the room.
- Snakepit: one shared launch-contract validator, used by the CLI and the
  GUI. Chirality: locked state updates and per-hand recoverable resume
  (guest round-trips PASS). Journal: row edits commit only on datastore
  success.
- Issue #1 has an upstream-sync comment listing the upstream bugs found.
  PR #4 is closed as superseded.
- Host suite: 584 passed. Fresh runtime export (includes every fix):
  `runtime/aspartame-dev/artifacts/gtk4-preview-standalone-20261022.tar.gz`
  (sha256 `eae0e392…`). Its 0300/0301 freshness is verified.

Owner next steps:
1. `make iso` (needs sudo). The 20261022 export (sha256 `eae0e392…`) is
   already staged as `aspartame-build/artifacts/gtk4-preview-standalone.tar.gz`.
2. Boot the new ISO and rerun the receipts in
   `reports/gtk4/repin-qualification-20261022.md` against the packaged
   runtime.
3. Decide the FULL PORT standard for the eight retirement candidates. This
   is the only remaining retirement blocker.
