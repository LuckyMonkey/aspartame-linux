# Open proposals

The 2026-10-22 code reviews produced three proposal documents: Settings and
packaging, runtime state, and document preservation. Their Priority 1 items
are implemented and qualified on the 2026.10.22 ISO
(`reports/gtk4/repin-qualification-20261022.md`). The full proposals are in
git history before this file replaced them. Only what remains open is kept
here.

## Done

- **Settings:**
  - The capture-phase key handler now handles only navigation keys.
  - All shell navigation dismisses Settings through
    `actions.dismiss_settings()`.
  - The About inventory is bounded and asynchronous.
  - Tiles are real buttons, so AT-SPI activation works.
  - A stale runtime archive fails the ISO build.
  - Patch fidelity is a build contract: patches 0300/0301 must replay
    exactly, and `sugar-gtk4-series-check` must show no fuzz.
- **Runtime state:**
  - CLI and GUI launch share one Snakepit validator
    (`snakepit_contract.py`).
  - Malformed records become "Not ready" rows.
  - Chirality read-modify-write goes through `chirality_state.py` (flock
    plus atomic write).
  - Partial session resume reports per-hand PASS/PARTIAL/FAIL.
- **Document preservation:**
  - The toolkit load-failure guard (0301) means a failed load never
    becomes a blank save.
  - Every audited Activity validates before assigning and raises on a bad
    payload.
  - Read keeps the source bytes.
  - Record restore is transactional.
  - Journal title and keep edits commit only on datastore success.
  - Tests: `tests/test_gtk4_document_preservation.py` and
    `tests/test_gtk4_journal_edit_persistence.py`. The contract is in
    `docs/ASPARTAME-ACTIVITY-CONTRACT.md`.

## Open

### Preserve unknown JSON keys on resave

GTD, Finance and GridPaint discard unknown top-level keys. A newer payload
therefore loses fields when an older build resaves it. Proposal: keep
unknown top-level keys when writing JSON payloads back, and keep rejecting
unknown `version` values rather than reinterpreting them.

Acceptance: for each JSON-state Activity, feed it these payloads, close it,
and compare the datastore bytes with the originals:
- an invalid-UTF-8 payload;
- a malformed-JSON payload;
- a payload with an extra key.

### Make GUI-launched Python workflows observable

`ActivityManager._launch_clicked()` keeps the Popen handle and reports
Started immediately. A process that fails right away gets the same
feedback as a running one, and children (`start_new_session=True`) outlive
the view.

Proposal: add a small workflow owner outside the Settings section. It
tracks running/completed/failed status and a bounded output log, and
reopening the manager recovers it. Decide whether Stop ends the whole
process group. Closing Settings must not kill workflows.

### Finish Activity Manager semantics

- The GTK4 view has no face-rating control, and its action buttons share
  one accessible name.
- Remove and approval run synchronously on the UI thread.
- `undo()` only reloads rows, and there is no restore action for
  quarantined bundles.
- `MANAGED_ROOTS` omits the packaged
  `/usr/lib/aspartame/gtk4-preview/prefix/share/sugar/activities`.

Proposal:
- Share the rating data contract and add native GTK4 face controls.
- Give each action button an Activity-specific accessible name.
- Mark bundled Activities read-only, using hide/disable rather than
  deletion.
- Move approval and removal off the UI thread without bypassing approval.

### Keep Chirality model handoff distinct from live delivery

The `handoff-object` CLI only changes the recorded object reference. It
does not ask the running target Activity to open that object, so the
visible content and the record can diverge. Proposal: keep it model-only
until an adapter can validate format support and complete the target load.
Commit the new reference only after delivery succeeds.

### Validate a Chirality resume before switching the visible Activity

The CLI `resume` branch activates the Activity before
`session.resume_activity()` validates the transition. If the second D-Bus
call fails, the shell has switched but the state is not saved. Proposal:
validate the transition on a copy, activate through one shell contract,
then persist the actual outcome. Report a refused request differently
from a partial activation.
