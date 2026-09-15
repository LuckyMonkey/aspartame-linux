# FotoToon GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-fototoon-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514584 resumed_pid=514606 object=c402669f-f988-42e9-8160-f89c0ef86660 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514626 resumed_pid=514646 object=40b0f7ca-b063-4e70-a566-4b4039a5588a resume=PASS service-release=PASS shell-cleanup=PASS
fototoon-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores `Sunset study` caption state through Journal and verifies it
before canonical Shell stop. Known nonfatal AT-SPI cache warnings occurred
during cache restart.
