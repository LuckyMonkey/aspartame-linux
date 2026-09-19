# GTK4 Activity lifecycle: stale-state repair — 2026-09-19

## User-visible gap

The native GTK4 Calculate Activity could launch and stop cleanly at the process
and D-Bus layers while Home still displayed its row as `Running`. This was not
a rendering-only defect: the shell model retained a launched Activity after the
Activity process and `org.laptop.Activity<id>` service had both disappeared.

## Evidence before the fix

- `calculate-roundtrip.py 1` reported `resume=PASS service-release=PASS
  shell-cleanup=PASS`.
- `pgrep -af calculateactivity4` returned no Activity process.
- D-Bus owner monitoring observed `org.laptop.Activity<id>` transition to no
  owner.
- The subsequent Home List screenshot still showed Calculate as `Running`.

This isolated the gap to authoritative ShellModel cleanup, rather than
Casilda surface visibility or Activity input.

## Root cause and repair

Casilda Activities do not create a GTK shell window. Their normal cleanup path
therefore depends on D-Bus `NameOwnerChanged`. A fast launch/stop can cross the
subscription boundary and leave a `LAUNCHED` model object behind. Patch 0160
adds `Activity.service_name_owned()` and a 250-ms ShellModel reconciliation
timer. Only launched Activities whose service name is no longer owned are
removed; launch transitions and Activity-specific UI are untouched.

## Verification after the fix

The rebuilt guest applied patch 0160 and started a fresh GTK4 shell. The direct
Calculate probe completed:

```text
cycle=1 pid=65488 resumed_pid=65508 object=bbc68b71-30f6-436f-8c7a-8618790756c2 resume=PASS service-release=PASS shell-cleanup=PASS
calculate-roundtrip=PASS input-method=AT-SPI datastore-payload=seeded
```

After returning to Home, a new 1920×1080 screenshot showed the Calculate row
with status `Stopped`; no stale lit/running state remained. The screenshot is
saved as `reports/screenshots/sugar-20260919-132250-v0.0.31.png`.

## Scope

This closes the stale model-state gap. It does not claim every Activity is a
FULL PORT; per-Activity launch and functionality tasks remain tracked in
`docs/sugar-modernization/ACTIVITY_LAUNCH_TASKS.md`.
