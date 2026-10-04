# GTK4 Chirality object continuity - 2026-10-04

Scope: qualify the first real object handoff milestone without creating a
split-screen surface or a presentation history.

Probe:

```sh
SSH_PORT=2230 ./scripts/ssh-asp \
  /usr/lib/aspartame/gtk4-preview/venv/bin/python \
  /mnt/aspartame-dev/scripts/sugar-gtk4-chirality-object-roundtrip.py
```

Result:

```text
chirality-object-roundtrip=PASS object=b60e97d4-6390-4b90-98cb-ee57a4e07bc9 active-sequence=left,right,left hands=write,read payload=utf8 cleanup=PASS mode=single-surface
```

The probe creates a UTF-8 payload through native GTK4 Write, stops and finds
the resulting Journal UID, then resumes that UID in Write and Read. Both live
Activities are assigned to Left and Right; the adapter activates Left, Right,
and Left again. The same UID is present in both semantic hand records, the
Read surface exposes the expected text, both Activity services release cleanly,
and the final datastore payload remains unchanged.

AT-SPI emitted transient cache warnings while traversing the guest tree. They
did not prevent visible text discovery or cleanup.

This qualifies bounded UTF-8 object continuity only. Unsupported format or
Activity/object refusal, crash isolation, and shell/session resume while a
hand is held remain explicit follow-up gates before user-facing object actions
or GTK3 package retirement.
