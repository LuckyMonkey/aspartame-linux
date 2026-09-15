# Count layer overlay — 2026-09-15

The GTK4 Count Activity now keeps every layer on the same XY origin in one
`Gtk.Overlay`. The selected plane remains the final (editable) child; planes
behind it use a stronger translucent context and planes in front use a lighter
translucent context. Context grids cannot receive input, so painting remains
confined to the selected layer.

Live QEMU capture after filling a cell and creating a second layer:

    reports/screenshots/sugar-20260915-104004-v0.0.31.png
    SHA-256: 9c92184d8e30c5d7563f272819c4d7f0d3789ca07559471b81271517f27e3373

The capture shows `Layer 1 of 2`, the selected filled cell, and the second
plane's translucent context in the same canvas. This is a visual layering
proof, not a claim that Count has complete upstream Activity feature parity.
