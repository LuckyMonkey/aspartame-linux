# Chirality implementation milestones

This file records implementation boundaries, not aspirations. Chirality is a
semantic two-context primitive: at most two immediate Activities, one active
visible context, and one held context. It is not split-screen, tiling, a
window manager, or a history/recent-frames system.

## Milestone 0 — migration-safe semantic core

Status: **implemented in the repository; not yet the normal shell controller**.

`scripts/aspartame_chirality.py` contains the presentation-independent state
model. `scripts/sugar-chirality.py` provides an inspectable runtime-state CLI.
The model proves:

- direct Left Hand / Right Hand selection;
- at most two immediate Activities;
- explicit replacement when both hands are occupied;
- release without destroying the Activity or its object reference;
- removal of a crashed Activity without destroying the other hand;
- object references as data, without inventing a capability ontology;
- semantic accessibility state independent of XOColor;
- no split-screen geometry and no history/rewind state.

Normal F7/F8 behavior remains the GTK3/GTK4 comparison path until the GTK4
migration gate is complete. The core is ready for a later shell adapter; it
does not silently repurpose those keys.

## Milestone 0.5 — single-surface Spaces bridge

Status: **implemented as a migration bridge; not yet the GTK4 Activity
adapter**.

`scripts/sugar-chirality-space.sh left|right` is the first executable shell
boundary for the primitive. It selects one complete Space through the existing
controller (`left` currently maps to the Classic Space and `right` to the
Modern Space). It deliberately has no split-screen, geometry, compare, or
history operation. The comparison action remains available only through the
GTK migration tooling.

This bridge proves the presentation rule independently from object and
Activity ownership. The mapping is intentionally isolated so the next
milestone can point both hands at two GTK4 Activities without changing the
semantic model or reintroducing panes.

The packaged image now carries `aspartame_chirality.py` and
`sugar-chirality.py` beside the bridge. `inspect`, `assign`, `activate`,
`release`, `activity-exited`, and `handoff-object` therefore remain available
for the separate object/Activity milestone without pretending that a shell
switch is an object handoff.

## Milestone 0.75 — Spaces primitive

Status: **implemented as a single-surface semantic selector**.

`aspartame_chirality.py` now exposes immutable `Space` descriptors and a
bounded `Spaces` selector. It records one active full-surface Space and its
controller token, without storing windows, geometry, panes, Activities,
Objects, or previous-space history. The current migration catalog is
`classic` → GTK3 and `modern` → GTK4; the later GTK4-only adapter can replace
those targets without changing the primitive.

This is intentionally separate from `ChiralSession`: Spaces select a visible
surface, while Chirality hands hold Activities and their object references.
The GTK3/GTK4 Space controller now records its successful `classic` or
`modern` selection through `sugar-chirality.py`; the state contains only the
current Space and controller token, never a previous-space log. Button and
F7/F8 routes therefore converge on the same semantic state boundary.

## Milestone 1 — GTK4-only hand adapter

Next implementation boundary, after the migration gate has enough evidence:

1. keep GTK3/GTK4 comparison actions available through developer tooling;
2. let two GTK4 Activity instances occupy the semantic slots;
3. switch visibility and focus through the model, never by laying out panes;
4. expose the accessible Left Hand / Right Hand state;
5. prove repeated switching, rapid switching, stop, resume, and crash
   isolation in a headless guest.

## Milestone 2 — object continuity

Use one real Journal object across two Activities. The first target should be a
boring, deterministic object such as UTF-8 text. Prove the correct object,
Activity, hand, persistence, resume, and graceful refusal for unsupported
objects before adding user-facing “Use with…” or “Give to Other Hand” actions.

## Evidence rule

Each milestone gets its own focused tests, runtime receipt, and commit. A
passing model test does not claim the GTK4 shell or Activity lifecycle is
complete. A visual comparison does not claim object handoff. Those claims are
kept separate so GTK3 retirement remains evidence-driven.
