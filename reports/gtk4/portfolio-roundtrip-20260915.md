# Portfolio GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-portfolio-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514477 resumed_pid=514499 object=2c4e952c-4546-4011-bb2a-481a606dbe6b resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514519 resumed_pid=514539 object=31d061ee-7c42-448a-bc4e-f605f49744a1 resume=PASS service-release=PASS shell-cleanup=PASS
portfolio-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores UTF-8 `GTK4 Field Notes` title/body content through Journal,
verifies the title, and performs canonical Shell stop on both cycles. The
guest emitted known nonfatal AT-SPI cache warnings.
