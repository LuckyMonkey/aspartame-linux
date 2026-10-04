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
