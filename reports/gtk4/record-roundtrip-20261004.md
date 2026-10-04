# Record GTK4 qualification — 2026-10-04

The GTK4 development prefix was rebuilt from the synchronized development
share in the headless QEMU guest on SSH port 2230. The build completed with:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

The one-cycle guest probe ran without bringing QEMU to the foreground or
using the host pointer:

```text
cycle=1 pid=49886 resumed_pid=49913 object=c05887ad-5897-4d1a-a0ad-79054bd3eb3e clip='Probe photo 1' resume=PASS media-preserved=PASS service-release=PASS shell-cleanup=PASS
record-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

Host evidence from `tests/gtk4_harness/record_capture.py` covers real PNG,
WebM, and Ogg/Opus GStreamer test-source capture, preview switching, clip
removal, byte-stable zip Journal resume, and manifest path-traversal refusal.

This qualifies Record as a bounded `FUNCTIONAL PORT`. It does not claim a
live camera viewfinder, capture timers, per-capture Journal objects, video
sound, or collaboration; those remain explicit follow-up work.
