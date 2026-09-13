# GTK4 Journal refresh frontier — 2026-09-13

- Added preview patch `0075-journal-visible-loading-state.patch` to invoke the
  existing Sugar Journal state renderer while an asynchronous datastore query
  is pending.
- Guest preview build passes all patches through `0075`, Casilda, sugar-ext,
  Jarabe, and datastore.
- Runtime `ShowJournal` succeeds and the GTK4 Journal toolbar/search renders.
- A fresh profile still shows a blank canvas after refresh; no `ready` callback
  is logged and the loading state is replaced/hidden when the Journal canvas is
  installed. This is now isolated to the Journal result-set/datastore
  readiness path, not shell startup or GTK4 process failure.
- Next fix: trace `jarabe.journal.model.find()` and `ResultSet.ready` on an empty
  datastore, then make the ListView stack expose an explicit empty state after
  readiness (or a timeout) without relying on GTK3 TreeView behavior.

Follow-up patch `0076-journal-result-readiness-diagnostics.patch` adds traceback
logging around `find_ids()`. The live repro still produces no readiness error,
which narrows the issue to callback/GTK presentation sequencing rather than a
datastore D-Bus exception.

Validation: `timeout 300 /mnt/aspartame-dev/scripts/sugar-gtk4-build.sh` → PASS.
