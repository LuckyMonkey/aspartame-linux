# Game Of Life GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-gameoflife-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=515600 resumed_pid=515622 object=b0840e12-12a5-41fe-b011-1b1ac286edd7 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=515644 resumed_pid=515664 object=b9a8e2b1-a03e-4088-8c9d-2d41d2e5715f resume=PASS service-release=PASS shell-cleanup=PASS
gameoflife-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores seeded live-cell/generation state through Journal, verifies
the visible summary, and performs canonical Shell stop on both cycles. Known
nonfatal AT-SPI cache warnings occurred during cache restart.
