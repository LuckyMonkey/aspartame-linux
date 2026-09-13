# GTK4 function-key verification — 2026-09-12

The running 1920×1080 QEMU guest accepted synthetic HMP key events through
`scripts/qemu-send-key.py` after the monitor greeting was drained to its
prompt. The modern shell remained alive while switching views:

| Key | Result |
| --- | --- |
| F1 | Neighborhood view (`Scan network`) |
| F2 | Group view (empty peer state) |
| F3 | Home favorites ring |
| F4 | Activity/Journal view |
| F5 | Journal view |
| F6 | Sugar Frame reveal |

Screenshots were captured after each transition under
`reports/screenshots/sugar-20260912-2044*.png`. This proves the key actions
are dispatched; an empty collaboration view is not a shell crash. Real peer
data and physical-key delivery remain separate runtime coverage items.

## Spaces round-trip (2026-09-13)

With both shells running under the guest Metacity session, QEMU HMP events
proved the semantic workspace bindings:

| Event | Controller status |
| --- | --- |
| F8 | `current=1`, GTK4 PID present |
| F7 | `current=0`, GTK3 PID present |

The GTK3 overlay now explicitly includes F7/F8 in its `SugarExt.KeyGrabber`
passive-grab set, so these keys are handled by the semantic Space controller
rather than falling through to the upstream action table.
