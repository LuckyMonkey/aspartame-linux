# Document preservation proposals — code review, 2026-10-22

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
