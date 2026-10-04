# Chirality Milestone 1 qualification

Date: 2026-10-04

## Result

The GTK4-only hand adapter now has a real headless guest qualification. The
probe launches two independent GTK4 Activities, assigns Calculate to Left
Hand and Clock to Right Hand, activates each hand in sequence, and verifies
that both Activity services are released cleanly afterward.

```text
chirality-activity-roundtrip=PASS active-sequence=left,right,left mode=single-surface
```

The sequence proves that only one selected Activity is activated at each
step, while the other Activity remains assigned and resumable. No split-screen
surface, workspace geometry, GTK3 target, or presentation history is involved.

## Implementation boundary

- `scripts/sugar-chirality-activity.py` is the GTK4 Shell D-Bus adapter.
- `scripts/aspartame_chirality.py` remains the presentation-independent
  semantic model.
- `scripts/sugar-chirality-space.sh` remains the migration bridge for the
  separate Classic/Modern Spaces comparison.
- Object continuity and user-facing object handoff remain Milestone 2.

The function-key mapping is intentionally still migration-gated; developer
comparison tooling remains available while GTK3 retirement evidence is built.
