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

Status: **implemented as a headless GTK4 Activity adapter; function-key
ownership remains a later migration decision**.

`scripts/sugar-chirality-activity.py` is the executable adapter boundary. It
assigns live GTK4 Activity IDs to Left Hand and Right Hand, activates exactly
one selected Activity through the modern Sugar Shell D-Bus API, and exposes
the semantic Active/Held state through the same model. It does not create a
pane, workspace, geometry comparison, or history log.

The remaining migration-gated work is:

1. keep GTK3/GTK4 comparison actions available through developer tooling;
2. route a user-facing GTK4 control to the adapter;
3. prove two GTK4 Activity instances occupy the semantic slots;
4. prove repeated switching, rapid switching, stop, resume, and crash
   isolation in a headless guest.

The reproducible guest probe is
`scripts/sugar-gtk4-chirality-activity-roundtrip.py`; it launches Calculate
and Clock, assigns them to the two hands, activates Left/Right/Left through
the modern Shell contract, and checks both Activity services are cleaned up.
It covers the two-Activity and basic switching/stop portion of this milestone;
resume and crash-isolation qualification remain explicit follow-up gates.

## Milestone 2 — object continuity

Status: **qualified for one UTF-8 Journal object across two GTK4 Activities;
broader object capability policy remains gated**.

`scripts/sugar-gtk4-chirality-object-roundtrip.py` creates one real UTF-8
Journal object in Write, resumes that same UID in Write and Read, assigns the
two live Activities to Left and Right, activates Left/Right/Left through the
GTK4-only adapter, and verifies the payload and service cleanup. The probe
uses one visible surface and no history or split-screen state.

The remaining gates are explicit:

1. define and qualify graceful refusal for unsupported object formats or
   Activity/object combinations;
2. qualify crash isolation and shell/session resume while a hand is held;
3. only then add user-facing “Use with…” or “Give to Other Hand” actions.

## Evidence rule

Each milestone gets its own focused tests, runtime receipt, and commit. A
passing model test does not claim the GTK4 shell or Activity lifecycle is
complete. A visual comparison does not claim object handoff. Those claims are
kept separate so GTK3 retirement remains evidence-driven.
