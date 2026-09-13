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
