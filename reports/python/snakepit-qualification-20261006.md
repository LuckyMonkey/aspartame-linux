# Snakepit Python runtime qualification — 2026-10-06

The host development runtime was re-qualified from the current tree.

```text
qualification=PASS software=aspartame-management target=host-development
workflow-exit=0
launch=PASS software=aspartame-management
launch-workflow-exit=0

qualification=PASS software=dependency-pair-left target=host-development
workflow-exit=0
qualification=PASS software=dependency-pair-right target=host-development
workflow-exit=0

qualification=FAIL software=dependency-tension-specimen target=host-development
reason=dependency conflict before environment creation: aspartame-tension-core: numeric version intervals do not intersect
```

The passing pair used separate temporary environments and proved that the
same named dependency can be qualified at 1.0.0 and 2.0.0 without
contaminating system Python. The management record also passed the explicit
launch-contract path and its real unittest workflow.

The tension failure is expected and useful: Snakepit rejected incompatible
constraints before creating an environment or installing anything. Current
JSON receipts include source fingerprints, interpreter selection, isolation,
workflow output, and failure reasons.

This advances the Python runtime milestone and the GTK4 Activity Manager
bridge; it is not a claim of a security sandbox, arbitrary package-graph
resolution, or full Pippy parity.
