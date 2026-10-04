# GTK4 Journal roundtrip checkpoint — 2026-10-04

This is a focused runtime checkpoint for the packaged standalone image. It
does not close the full Journal-ready gate; it records the behavior that was
actually exercised.

## Image

- ISO: `/media/freezer/SteamLibrary/vms/aspartame-build/artifacts/out/aspartame-2026.10.04-x86_64.iso`
- SHA-256: `742c849ac5bf55521a9e099a8234b0d1142451987fc5d379813e6807c1965cf7`
- QEMU: headless, SSH forwarded on `127.0.0.1:2223`, no host display

## Command

The source roundtrip probe was copied to the guest without enabling a host
share, then run against the packaged GTK4 runtime:

```sh
SSH_PORT=2223 ./scripts/ssh-asp \
  'python3 /tmp/sugar-gtk4-journal-roundtrip.py 2'
```

## Result

```text
cycle=1 ... payload=PASS resume=PASS service-release=PASS shell-cleanup=PASS
cycle=2 ... payload=PASS resume=PASS service-release=PASS shell-cleanup=PASS
journal-roundtrip=PASS input-method=AT-SPI
```

The probe completed two save/resume cycles, released the Activity service,
and cleaned up the GTK4 shell each time. The AT-SPI dbind cache warnings were
non-fatal and did not produce a traceback or failed cycle.

## Scope

This closes another runtime checkpoint for Journal payload/resume and service
lifecycle. The full acceptance gate remains open for mounted-file handling,
favorite persistence, safe delete/project actions, full ProjectView
navigation, hide/show plus shell restart, and datastore disconnect recovery.
