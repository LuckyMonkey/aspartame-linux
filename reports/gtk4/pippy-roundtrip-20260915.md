# Pippy GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-pippy-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=515146 resumed_pid=515168 object=53e780c5-0de5-44ff-9f44-eff2d597042f resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=515188 resumed_pid=515208 object=1cd2d14a-9b41-4171-8c66-2ff128ca4233 resume=PASS service-release=PASS shell-cleanup=PASS
pippy-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores `print("Aspartame")` source through Journal and verifies it
before canonical Shell stop. Known nonfatal AT-SPI cache warnings occurred
during cache restart.
