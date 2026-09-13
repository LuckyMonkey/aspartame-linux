# GTK4 native Journal surface — 2026-09-13

The GTK4 runner now prepends `gtk4-overlay/src` to `PYTHONPATH`. Its native
Journal `ListView` uses GTK4 `Gtk.ListBox` rows backed by datastore metadata.

Live VM evidence:

- `ShowJournal` launches successfully.
- Screenshot `sugar-20260913-084023-v0.0.31.png`: populated Journal rows.
- Screenshot `sugar-20260913-084045-v0.0.31.png`: search query `log` filters to
  Log Activity entries.
- Screenshot `sugar-20260913-084057-v0.0.31.png`: activating a row opens the
  Journal detail view.

GTK3 source and runtime paths are unchanged. The overlay preserves the signal
contract needed by JournalActivity and ObjectChooser while replacing only the
GTK4 presentation surface.
