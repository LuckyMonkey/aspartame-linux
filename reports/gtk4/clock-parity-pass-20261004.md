# GTK4 Clock parity pass — 2026-10-04

## Result

`tv.alterna.Clock` no longer presents as a two-label placeholder. The native
GTK4 Activity now has a scalable drawing surface and responsive FlowBox
controls that remain usable as the Activity width changes.

Implemented from the GTK3 learning workflow:

- Simple analog face with hour numbers and colour-coded hands.
- Nice analog face without hour numbers.
- Digital face with optional seconds.
- Weekday/date display.
- Time-in-words display, including midnight, noon, and AM/PM.
- Ticking-seconds toggle.
- Optional speech on minute boundaries when `spd-say` or `espeak` is present.
- Adjust-hands mode with GTK4 drag gestures for hour, minute, and second hands;
  Digital mode disables this control.
- JSON Journal save/resume for all display choices.
- Malformed and wrong-shaped Journal objects reset safely to defaults.
- Accessible labels and compact controls that wrap instead of forcing a
  fixed-width calculator-like layout.

## Verification

Focused host qualification:

```text
pytest -q tests/test_gtk4_clock_activity.py tests/test_gtk4_activity_harness.py
51 passed in 22.65s
```

The harness constructed the Activity, clicked every visible button, exercised
save/resume, and passed malformed Journal payloads through `read_file`.

The rebuilt writable GTK4 guest preview also passed a headless QMP input
macro. It selected Digital and enabled both Time in words and Weekday/date;
the resulting guest capture was 1920x1080 and visibly showed the digital time,
`one thirty-two PM`, and `Sunday, October 04, 2026`. The capture checksum was
`ca8695a7d27dbbf29c275b982ad86b550a251a5cc6b3ac00f61b857476206b53`.

The guest build completed with:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

The QEMU input receipt was:

```text
qemu-headless-macro=PASS steps=5 repeats=1 qmp=/tmp/aspartame-qemu-qmp
```

After moving the display-options row above the expandable face, all five
actions remained visible at 1920x1080. The stateful GTK4 buttons then passed a
headless drag qualification: QMP enabled Adjust hands and dragged an analog
hand to the 12 position. The receipt was:

```text
qemu-headless-macro=PASS steps=4 repeats=1 qmp=/tmp/aspartame-qemu-qmp
```

The resulting 1920x1080 capture checksum was
`b000c7ba97ce3fe86898d07ea2908ebf4ce3646856346f05776c6785dac2b0ea`.

## Boundary

This remains a `FUNCTIONAL PORT`, not a `FULL PORT`. The OLPC-specific NTP
plus hardware-clock update path and the original decorative clock artwork are
not yet implemented. They remain explicit follow-up work rather than being
hidden behind the GTK4 label.
