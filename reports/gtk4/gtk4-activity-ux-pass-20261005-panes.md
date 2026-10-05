# GTK4 activity pane allocation pass — 2026-10-05

The packaged visual sweep showed Markdown and Jukebox rendering only the left
side of their intended two-surface workspaces. Their source used homogeneous
`Gtk.Grid` columns, but the capture did not provide a visible editor/preview or
playlist/player split at the guest boundary.

Both activities now use an explicit horizontal `Gtk.Paned` with non-shrinking
start and end children, resize participation on both sides, and a wide
divider handle. This makes the two work surfaces part of the actual GTK4
allocation contract instead of relying on the grid's preferred-size result.

This is a source-level correction. A new packaged screenshot is still required
before marking the visual receipt `PASS`; the older capture is retained as the
reason for the change, not reused as proof of the fix.
