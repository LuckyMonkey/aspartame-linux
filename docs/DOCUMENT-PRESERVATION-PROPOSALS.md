# Document preservation proposals — code review, 2026-10-22

**Status (later 2026-10-22): implemented.** The toolkit load-failure guard
(0301), refusing loads in all audited Activities, Read byte preservation,
Write/Calculate unknown-format refusal, TurtleArt/Poll validate-then-assign,
the Jukebox `int()` fix and Record's transactional restore have all landed
in source. Host tests: `tests/test_gtk4_document_preservation.py` and the
updated Activity harness. Still open: Journal row edit persistence
(Priority 2), unknown-key preservation for JSON payloads, and a guest-side
datastore byte comparison on a rebuilt image.

Source observations only; no new checks were run. Prioritize these before
expanding cross-Activity object handoff. Actual datastore replacement on close
must be confirmed later against the toolkit save contract.

## Priority 1: Read must preserve the source object

`packages/gtk4-read-activity/readactivity4.py:read_file()` unwraps
`aspartame-write-v1` JSON into plain text and discards formatting spans.
`write_file()` always serializes the displayed pages as plain UTF-8 text.
If Read saves back to the same Journal UID, viewing a formatted Write object
can strip formatting. The reader has no editing UI, so rewriting the document
is unnecessary for ordinary viewing.

The same loader retains the built-in sample when the input is empty,
whitespace-only, unreadable, or invalid UTF-8. Its save method then serializes
that sample. This creates a potential original-content replacement path when
an existing entry cannot be loaded. Empty input and a new sample document
must be distinct states.

Proposal: preserve original bytes/format for read-only viewing, store reading
position separately as metadata, and prevent source replacement after a failed
load. Unsupported formats should produce an explicit refusal, not a sample.
Use a separate new object for any deliberate conversion. Later acceptance
must compare the original payload after closing Read, including formatting,
empty/whitespace input, and invalid input; visible text alone is insufficient.

## Priority 1: Failed Activity loads must not become successful blank saves

`packages/gtk4-paint-activity/paintactivity4.py:read_file()` catches parse/read
errors and assigns a blank drawing. `write_file()` then emits that blank state.
`packages/gtk4-write-activity/writeactivity4.py:read_file()` reports read errors
but returns without establishing a load-failed save guard. Record similarly
reports failed restore while leaving its current store available to save.
These are code-level risks of overwriting the original on normal close;
this pass does not claim a reproduced datastore-loss event.

Proposal: a shared load outcome contract should distinguish new, loaded,
unsupported and failed objects. Failed/unsupported loads must preserve the
original and offer retry, export/recovery, or an explicit new copy. Do not
silently turn parse failure into a valid empty document.

## Priority 2: Record restore should be transactional

`packages/gtk4-record-activity/recordactivity4.py:ClipStore.load()` writes
media into the live clip directory while still validating the archive.
A later read failure returns False but leaves earlier file writes in place;
existing files with the same names may already have been replaced.
The manifest/store commit occurs only afterward, so in-memory metadata and
media files can disagree after failure. Archive members are read fully into
memory, with no explicit size budget visible in this path.

Proposal: validate and extract into a fresh temporary store, apply reasonable
manifest/member size limits, then swap only after the full restore succeeds.
Leave the current store untouched on failure. Keep the existing filename
validation; transactional restore is an additional requirement.

## Priority 2: Journal editing should reflect persistence outcomes

`gtk4-overlay/src/jarabe/journal/listview.py:_finish_title()` updates metadata,
label text, and closes the editor immediately after calling write_metadata;
the asynchronous error callback only changes the status text. `_keep_toggled()`
also updates cached metadata before persistence succeeds. A failed write can
therefore leave the UI displaying unsaved values. Its synchronous failure
handler calls `button.set_active()` inside the toggle callback, which can
re-enter the same save path; it needs a signal guard.

Proposal: update committed row metadata only in the success callback, retain
an editable draft while pending, and restore the prior toggle value with its
handler blocked on failure. Handle rapid successive edits with an operation
revision so old callbacks cannot overwrite newer user intent. The existing
project assignment callback in the same file provides a useful local pattern:
it updates metadata inside its applied callback.

## Priority 1: The failed-load pattern repeats across the Activity set

Second source-only pass, 2026-10-22: 14 more `read_file()`/`write_file()`
pairs checked. No checks run. Each Activity below
turns an unreadable or unparseable Journal payload into a valid default state.
Its unconditional `write_file()` then serializes that default:

| Activity | Failed read becomes | Severity |
| --- | --- | --- |
| Markdown | empty source (`""`), incl. invalid UTF-8 | high: user prose |
| Pippy | `DEFAULT_PROGRAM` replaces the user's program | high: user code |
| Portfolio | empty title and body | high: user prose |
| GTD | empty task list | medium |
| Finance | empty transactions | medium |
| Fototoon, GridPaint, ColorMyWorld | blank canvas/selection | medium |
| Words, Get Books | empty query/selection | low |
| TurtleArt, Poll | early `return` keeps defaults **after partial assignment** | medium |
| Jukebox | early `return` keeps the default playlist | low |
| Calculate | invalid UTF-8 becomes empty; unknown JSON `version` becomes the expression text | low |

Additional defects found in the same code:
- **Partial application.** TurtleArt assigns `x`/`y`/`heading` before parsing
  `lines`. Poll sets the question and choices before `int()` on `votes` can
  fail. A failed parse leaves a mixed old/new state that is later saved.
- **Uncaught exception.** Jukebox calls `int(payload.get("selected", 0))`
  outside its `try`. A non-numeric `selected` raises out of `read_file()`.
- **Silent lossy round-trip.** GTD drops non-dict and blank tasks. Finance
  drops entries with a missing or invalid `value`. GridPaint drops
  out-of-range cells. All three discard unknown top-level keys, so a newer
  payload loses its fields when an older build resaves it.
- **Calculate forward-compat.** A `version` other than 2 is treated as a
  plain expression. A future-format object is shown, and then saved back,
  as raw JSON text in the entry.

Proposal: this is a shared contract problem, not 14 separate bugs. Add one
small helper to the Aspartame activity contract (see
`docs/ASPARTAME-ACTIVITY-CONTRACT.md`):
1. `read_file()` parses into a local value and assigns widget state only
   after the whole payload validates (no partial assignment).
2. Any failure sets `self._load_failed = True`, shows an explicit
   "couldn't open this entry" state and keeps the original bytes.
3. `write_file()` checks the flag first. When the load failed and the user
   has not deliberately started a new copy, it either rewrites the original
   bytes or raises `NotImplementedError` (whichever the toolkit save
   contract treats as "do not replace"). The toolkit source is only in the
   guest build tree, so this still needs confirming there.
4. Preserve unknown top-level keys when resaving JSON payloads; reject (do
   not reinterpret) unknown `version` values.
Suggested order: Markdown, Pippy, Portfolio (user-authored text), then the
JSON state Activities. Later acceptance: for each Activity, feed it an
invalid-UTF-8 payload and a malformed-JSON payload, close it, and compare the
datastore bytes with the originals.
