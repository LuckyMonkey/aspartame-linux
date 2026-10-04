# GTK4 Activity UX qualification — 2026-10-03

This pass targets the three Activity surfaces that were visibly collapsing
into sparse, calculator-like layouts. Testing used the headless Aspartame ISO
in QEMU at 1920×1080 with snapshot disks and no host pointer or keyboard grab.

## Changes verified

- Portfolio now gives the project description a labeled, bordered,
  expanding editor surface.
- Markdown now gives both source and preview labeled, bordered,
  independently scrollable surfaces.
- Finance now fills the available Activity width, keeps description and amount
  columns aligned, and explains the empty transaction state.
- Portfolio, Markdown, and Finance retain their existing Journal payload
  formats and lifecycle behavior.

## Evidence

- Focused source tests: 7 passed.
- Full host suite: 434 passed.
- Rebuilt standalone ISO: `e4be73387b1f44f097b9bdd9634e1bc114335a22e57e5825462bbc3d92db4b17`.
- Headless visual sweep: 3/3 passed.
- Journal roundtrip: 2 cycles each for Portfolio, Markdown, and Finance;
  launch, visible restore, stop, service release, and datastore payload all
  passed.
- The roundtrip helpers now select the packaged `/usr/lib/aspartame` Python
  runtime when present, while retaining the development-tree fallback.

Screenshots:

- [Portfolio](visual-sweep-ux-20261003/org.sugarlabs.PortfolioActivity.png)
- [Markdown](visual-sweep-ux-20261003/org.sugarlabs.Markdown.png)
- [Finance](visual-sweep-ux-20261003/org.laptop.community.Finance.png)

## Retirement boundary

These three are now valid **modern-space retirement candidates**: the GTK4
launcher path is visible, usable at the target resolution, and covered by
input/lifecycle/Journal evidence. The GTK4 Home registry already suppresses a
classic duplicate when a supported GTK4 replacement has the same display
name.

This is not a claim of full upstream feature parity and does not remove the
GTK3 bundles from the image. GTK3 remains available as the reference/fallback
until the richer workflow, collaboration, and physical-input gates are
qualified. The next safe retirement step is therefore catalog-level removal
from the modern Space, followed by package removal only after a separate
parity decision.
