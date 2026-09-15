# GTK4 Neighborhood runtime verification — 2026-09-15

The modern Jarabe shell was restarted in the guest after applying
`0127-neighborhood-accessibility-order.patch`. Calling the shell service
method `ShowNeighborhood()` returned `1` and switched the live 1920×1080
surface to the Neighborhood view.

The captured surface shows the Sugar search affordance with the placeholder
“Search in Neighborhood”, the owner icon, and the explicit empty-state text
“No people or shared Activities are nearby yet.” No MeshBox construction
traceback occurred.

Evidence: `reports/screenshots/sugar-20260915-075007-v0.0.31.png` and its OCR
sidecar. The original failure was an overlapping accessibility patch that
placed `set_accessible_role()` inside `update_property()`; the corrective
patch restores two independent GTK4 calls.
