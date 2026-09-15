# Level GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-level-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514065 resumed_pid=514087 object=95fc97a2-6689-4c60-9af9-fe7a264d1736 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514108 resumed_pid=514128 object=00f86ef0-2a2c-46c9-a740-89c9f482cb84 resume=PASS service-release=PASS shell-cleanup=PASS
level-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores a seeded `-17` degree JSON payload, verifies the readout,
and performs canonical Shell stop/cleanup on both cycles. AT-SPI cache warnings
were nonfatal. This is offline interaction/persistence evidence, not hardware
orientation-sensor parity.
