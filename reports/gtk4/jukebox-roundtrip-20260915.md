# Jukebox GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-jukebox-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514701 resumed_pid=514723 object=3b53151b-c3fa-4864-9f96-bedada7f7814 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514743 resumed_pid=514763 object=5cc8cccf-f68e-4767-bdb3-da84b7d66be6 resume=PASS service-release=PASS shell-cleanup=PASS
jukebox-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores a seeded `Field Recording` playlist entry through Journal,
verifies it, and performs canonical Shell stop on both cycles. Known nonfatal
AT-SPI cache warnings occurred during cache restart.
