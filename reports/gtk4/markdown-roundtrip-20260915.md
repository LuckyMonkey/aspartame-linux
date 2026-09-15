# Markdown GTK4 Journal round-trip — 2026-09-15

Guest command:

```text
scripts/ssh-asp '/tmp/sugar-gtk4-markdown-roundtrip.py 2'
```

Result:

```text
cycle=1 pid=514168 resumed_pid=514190 object=a8ed4ceb-fcee-41b6-8840-f9cbcf44adb6 resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 pid=514212 resumed_pid=514232 object=46436dac-1153-446b-be2f-8eb466a54e8c4 resume=PASS service-release=PASS shell-cleanup=PASS
markdown-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

The probe restores `# GTK4` UTF-8 source through the Journal launcher and
verifies it before canonical Shell stop. Nonfatal AT-SPI cache warnings were
observed during cache restart.
