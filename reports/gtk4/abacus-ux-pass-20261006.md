# Abacus GTK4 UX pass — 2026-10-06

The native Abacus activity already had the correct place-value interaction,
per-bead accessible names, and Journal round-trip. Its remaining visual risk
was proportion: five compact rows could read like a small calculator on a
large Sugar display.

The rods are now the expanding primary workspace. The rod frame and each rod
row claim available vertical space while keeping the bead controls centered;
the value card, instruction hierarchy, and Clear action remain stable. This
keeps the activity legible at 1920×1080 without changing its arithmetic or
Journal contract.

The earlier packaged screenshot was captured before the activity surface had
settled and is not used as current UX evidence. The next targeted headless
visual sweep should use the corrected X11-auth driver and a longer compositor
settle, matching the Color My World qualification path.
