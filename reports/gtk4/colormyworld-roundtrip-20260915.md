# Color My World GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-colormyworld-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=515373 resumed_pid=515395 object=e39c97a2-6f2c-4f94-8eab-2107b6323592 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=515415 resumed_pid=515435 object=45cf52f7-d2ec-4ffe-9c0b-8611c8e44d3e resume=PASS service-release=PASS shell-cleanup=PASS
colormyworld-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores the seeded `Violet` palette selection through Journal,
verifies the visible selection, and performs canonical Shell stop on both
cycles. Known nonfatal AT-SPI cache warnings occurred during cache restart.
