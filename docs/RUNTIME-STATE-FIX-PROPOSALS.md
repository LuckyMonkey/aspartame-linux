# Python launch and Chirality proposals — code review, 2026-10-22

Source review only. No new tests, runtime probes, or build results are claimed.

## Priority 1: Use the same qualification policy in CLI and Activity Manager

Evidence:
- `scripts/snakepit.py:launch()` compares `source_fingerprint(cwd)` to the
  recorded digest before running the command.
- `gtk4-overlay/src/cpsection/activities/model.py:_launch_contract()` checks
  schema/status, command shape, directory existence and interpreter existence,
  but does not compare the recorded source digest.
- Its `launch_activity()` calls Popen directly. Thus the GTK4 route can run
  source that the CLI route would reject as changed since qualification.
- `scripts/snakepit.py:register()` also does not check source freshness.
- `explanation_summary()` calls any dictionary-valued launch contract
  launchable, even if its status or fields would fail actual launch.

Proposal: extract a non-GTK contract validator shared by inspect/explain,
register, CLI launch and GUI launch. Separate cheap record-shape validation
from launch-time source freshness. Recheck the latter immediately before
launch; do not put recursive hashing on the GTK main loop. The UI should
say “needs requalification” with the reason when the source changed.
Preserve GUI asynchronous execution and the CLI timeout behavior rather
than blindly blocking the GUI on the CLI command.

The existing fingerprint is a source receipt, not environment attestation.
The environment can change after qualification; interpreter file existence
does not establish that dependencies and interpreter still match the receipt.
Proposal: decide and document whether environment mutation invalidates
qualification, then record the relevant interpreter/package identity and
report stale evidence honestly. Do not describe this mechanism as a sandbox.

## Priority 1: Validate record structure before constructing rows

Evidence: `_snakepit_activity()` guards JSON decoding and the outer software
dictionary, but `record.get('interpreter', {}).get('version')` assumes the
interpreter value is a dictionary. A null or list value raises AttributeError
outside the decoding exception handler, aborting the inventory loop.
`_qualified_launch()` converts missing cwd to `Path('')` (the current directory),
whereas `_launch_contract()` later indexes `contract['cwd']` and
`contract['environment']` directly. A partially populated record can therefore
be classified differently at display and launch time.
CLI `_load_record()`, launch and register also assume the JSON top level is
a dictionary before calling `.get()`.

Proposal: validate required types and nonempty explicit path fields once;
return a structured invalid-record reason. Show an invalid record as Not ready
or skip it with a diagnostic without breaking unrelated Activity rows.
Keep launch disabled until the same validator accepts the record. Catch
expected data errors at the row boundary, rather than broad-catching all
programming errors inside the whole manager.

## Priority 2: Make GUI-launched Python workflows observable

Evidence: `ActivityManager._launch_clicked()` appends the Popen object to
`self._processes` and immediately reports Started. No exit observation or
status update exists in that view. A process that exits with failure almost
immediately receives the same feedback as a running workflow. The window
owns the handle list even though children use `start_new_session=True` and
can outlive it. There is no visible stop or output/result surface.

Proposal: add a small workflow owner outside the transient Settings section.
Track running/completed/failed status and a bounded output log; let reopening
the manager recover current state. Define whether user Stop terminates the
whole process group and whether closing Settings leaves workflows running.
Do not kill existing workflows merely because the view closes.

## Priority 1: Coordinate all Chirality read-modify-write operations

Evidence:
- `scripts/sugar-chirality-activity.py` loads the state at CLI entry and saves
  it after mutation using atomic replace. There is no interprocess lock or
  revision comparison around load + mutation + save.
- `scripts/sugar-gtk4-chirality-session-resume.py` loads once, performs slow
  launch/service waits, then writes after each hand restoration. Other CLI
  commands can change the state during those waits; its next save can replace
  newer changes with the old snapshot.
- Resume uses a fixed `.resume-tmp` path, which also collides if multiple
  resume processes run. The Activity CLI uses unique temporary files.

Atomic replacement prevents partial JSON; it does not prevent lost updates.
Proposal: centralize state mutations in a shell service, or use a shared lock
plus revision/expected-hand checks. Do not hold a global filesystem lock while
waiting for Activity startup. Record intent, launch, then reconcile against
the current state before attaching the result. Use unique temporary files
and remove them on failure. Preserve the no-history model: a revision token
is concurrency control, not a user navigation history.

## Priority 1: Make partial session resume a recoverable result

Evidence: session-resume writes a successful Left restoration before trying
Right. If Right is missing or times out, it raises immediately; restoration
of the originally active hand is below the loop and never runs. Already
launched Activities are not summarized or rolled back. Re-running ignores
all pre-existing processes and launches again, rather than recognizing the
hand that was already restored. `activity_processes()` matches environment
bundle/object IDs without requiring the modern session bus identity, so a
concurrently launched matching Activity from another session could match.

Proposal: report a result for each hand, restore the desired active hand when
available even if the other fails, and make retry recognize valid live IDs on
the intended GTK4 bus. Match a launch token/service owner rather than scanning
only environment strings. Keep failed hands explicitly resumable; do not
silently erase their Journal references or destroy working opposite hands.

## Priority 2: Keep model handoff distinct from live object delivery

Evidence: `ChiralSession.handoff_object()` copies object_ref/title while
preserving the target Activity identity, which is appropriate model behavior.
The CLI `handoff-object` branch only calls that method and saves JSON; it does
not ask the running target Activity to open the object or check its capability.
Thus the target's recorded reference can change while its current visible
content remains unchanged. A later session resume may open that reference,
which differs from immediate handoff semantics.

Proposal: keep this explicitly model-only until an adapter can validate
format support and complete target load/resume. Commit the new target object
reference only after delivery succeeds. Refusals should preserve the old
reference and content. Avoid exposing a user-facing “handoff complete” action
based solely on this model mutation.

## Priority 2: Validate the resume transition before switching visible Activity

Evidence: the Activity CLI `resume` branch calls `_activate_activity()` before
`session.resume_activity()`. The latter can reject an empty hand or an Activity
already occupying the opposite hand, after the visible switch has happened.
Also `_activate_activity()` calls shell.ActivateActivity and then SetActive;
if the second D-Bus call fails, the visible shell may have changed but the
JSON state is not saved.

Proposal: validate the intended model transition on a copy first; perform
activation through one authoritative shell contract, then reconcile/persist
its actual outcome. Distinguish a refused request from a partially completed
activation instead of leaving UI and recorded state silently divergent.
