# Notes for AI agents working on Aspartame

Read this before changing anything. It records how this project expects work
to be done so a fresh session continues the conversion correctly instead of
re-deriving it. Humans are welcome to read it too.

## Where the truth lives

| Need | Read |
| --- | --- |
| Forward plan and milestones | `docs/MILESTONES.md` |
| What works now, as workflows | `docs/sugar-modernization/QUALIFICATION_DECK.md` |
| Per-Activity port class | `docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md` |
| GTK3 ↔ GTK4 side-by-side workflow | `docs/sugar-modernization/parity/README.md` |
| Numbered defects | `docs/sugar-modernization/BLOCKERS.md` |
| How to port one Activity | `docs/sugar-modernization/GTK4_ACTIVITY_RUNBOOK.md` |
| Backlog | `TODO.md`, `docs/sugar-modernization/MIGRATION_TODO.md` |

`CONVERSION_TRACKER.md`, `RACE_STATUS.md` and dated reports are history. Prefer
the deck and the classification ledger when they disagree, and correct the
stale document rather than deleting its history.

## Rules that are easy to break

- **Evidence over claims.** Launch/stop coverage is not parity. Do not move an
  Activity up a class without the evidence the ledger describes. If you could
  not run something (no VM, no camera, no peer), say so in the doc and the
  commit; never write "verified" for a host-only result.
- **Add and correct; do not delete data.** Docs, ledgers, reports, ratings,
  and Journal formats are append-and-correct. Mark a wrong statement as
  corrected with the date instead of silently removing it. Never rewrite the
  classic `activity-ratings.json`.
- **GTK3 stays healthy.** The classic Space is the behavioural reference until
  the retirement gate passes. Do not edit stable GTK3 through the GTK4
  overlay, and never import GTK3 and GTK4 in one process.
- **F7/F8 is test machinery, Chirality is the destination.** Keep the
  side-by-side workflow working until GTK3 is retired; do not repurpose the
  Spaces early (see `ASPARTAME_CHIRALITY.md`).
- **UX survives every change.** Large targets, visible focus, accessible
  names on every control, Escape/Stop exits, honest empty states. After a
  visible change, take a screenshot and look at it. Keep column alignment,
  wording, and Sugar vocabulary (Activity, Journal, Frame, Home).
- **Honest states.** No fake peers, fake devices, or fake success. If a camera,
  peer or codec is missing, the UI says so.

## Checks to run before pushing

```sh
xvfb-run -a python3 -m pytest -q tests   # host suite incl. GTK4 harness
./scripts/smoke-test.sh
make parity-check                         # PAIRS.tsv and port_status.json current
```

`tests/test_gtk4_runtime_check.py` refuses to run as root; in a root
container that one failure is environmental. The GTK4 harness needs GTK4
introspection, PyGObject's cairo bridge (`python3-gi-cairo`) and a display
(Xvfb); without them it skips rather than fails, so confirm it actually ran
(`pytest -rs`).

## Adding or changing a GTK4 Activity

1. Package under `packages/gtk4-<name>-activity/` with `activity/activity.info`
   (keep the original bundle id) and `<name>activity4.py` using
   `sugar4.activity.SimpleActivity`.
2. Implement `read_file`/`write_file` so a resumed object saves byte-identically,
   and so empty, malformed, or non-object Journal data never crashes.
3. Register in `scripts/sugar-gtk4-build.sh`, `scripts/sugar-gtk4-dev-sync.sh`
   (two places), and `scripts/sugar-gtk4-activity-matrix.sh`; add a guest
   probe `scripts/sugar-gtk4-<name>-roundtrip.py`.
4. The harness (`tests/test_gtk4_activity_harness.py`) picks the bundle up
   automatically. Add Activity-specific behaviour tests next to it.
5. `make parity-pairs parity-export`, then record the class (or "awaiting
   guest evidence") in the ledger.

## Ratings vocabulary

The Activity Manager uses a six-face Wong-Baker-style scale: 0 no hurt, 2, 4,
6, 8, 10 unusable. The same scale scores side-by-side parity steps. The faces
are Aspartame's own drawings (`gtk4-overlay/src/cpsection/activities/faces.py`);
do not import the Wong-Baker Foundation's artwork.

## Leaving notes for the next agent

- Put progress in the documents above, not only in commit messages.
- Dated reports go in `reports/gtk4/` and name the command that produced them.
- If you stop mid-task, add a short "Handoff" bullet under the relevant
  milestone in `docs/MILESTONES.md`: what is done, what is next, what blocked.

## Handoff log

- 2026-10-02: Added the headless GTK4 harness (fixed seven defects), the
  GTK4 Record port (host-verified only), the parity workflow, and
  Wong-Baker-style ratings in the GTK4 Activity Manager. Next: run the guest
  matrix, the Record round-trip, and the first side-by-side report (Write
  is the recommended first FULL PORT candidate). The container used for this
  work had no VM, so none of this has guest evidence yet.
- 2026-10-02 (later): Jukebox local tracks now play through `Gtk.MediaFile`
  (host-verified only). Guest to-do list, in order: rebuild preview →
  activity matrix → Record and Jukebox round-trips → re-run round-trips for
  Help, Count, Level, Finance, Mastermind, Stopwatch → first parity report
  (Write) → check the face ratings render in guest Settings.
