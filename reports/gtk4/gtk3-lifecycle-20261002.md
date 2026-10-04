# GTK3 lifecycle probe — 2026-10-02

## Result

The existing Aspartame ISO booted both shells in QEMU:

- GTK3 shell: `python3 -m jarabe.main`
- GTK4 shell: `/usr/lib/aspartame/gtk4-preview/sources/sugar/src/jarabe/main.py`

The classic GTK3 probe then completed three Journal launch/stop cycles:

```text
cycle=1 pid=5156 service-ready=PASS shell-active=UNTESTED
cycle=1 launch=(true,) pid=5156 activity_id=0b5d589170e78eb5524bc39e652c06fe3c9a928a stop=signal=TERM cleanup=PASS
cycle=2 pid=5256 service-ready=PASS shell-active=UNTESTED
cycle=2 launch=(true,) pid=5256 activity_id=d9106d3b62c544fff7a6936dea6a812f553e3d70 stop=signal=TERM cleanup=PASS
cycle=3 pid=5341 service-ready=PASS shell-active=UNTESTED
cycle=3 launch=(true,) pid=5341 activity_id=64af88d84025a68cd4cfdee1e463051250041789 stop=signal=TERM cleanup=PASS
lifecycle-probe=PASS target=GTK3
```

GTK3 carries its activity ID as `-a`; classic Shell does not expose the
GTK4-only `StopActivity` method, so the reusable probe uses the activity D-Bus
service as the readiness check and SIGTERM for cleanup. `shell-active` remains
explicitly untested in this classic probe.

## Qualification boundary

This is fresh guest evidence, but it is not yet the full GTK3 retirement gate.
The test used the existing ISO and temporarily corrected two packaged-runtime
defects in the running guest:

1. `Help.activity/bin/sugar-activity4` had lost its executable bit.
2. The bundle-local Help launcher hard-coded the development path instead of
   honoring the packaged GTK4 interpreter.

The source fixes are now in the repository and require a rebuilt ISO. GTK3
physical input, F7/F8 transport, and regression invariants remain unqualified.

## Rebuilt-image rerun

After rebuilding `aspartame-2026.10.03-x86_64.iso` (SHA-256
`8859bc89fca6e7b2190db6cf283a5a7228fcc26e76aff861bec5662d28312ae0`), the
packaged GTK3 probe completed three fresh Journal launch/stop cycles without
the temporary guest fixes used by the earlier run:

```text
cycle=1 pid=2128 service-ready=PASS shell-active=UNTESTED
cycle=1 launch=(true,) pid=2128 activity_id=32ffdc9abd0dc43ed4679225f304d20af50dbbb8 stop=signal=TERM cleanup=PASS
cycle=2 pid=2210 service-ready=PASS shell-active=UNTESTED
cycle=2 launch=(true,) pid=2210 activity_id=0097de35701a2c4a5345186ef45bf611b94c660d stop=signal=TERM cleanup=PASS
cycle=3 pid=2297 service-ready=PASS shell-active=UNTESTED
cycle=3 launch=(true,) pid=2297 activity_id=209ce5c62f9c184fa1242bf968e8feb46315a12c stop=signal=TERM cleanup=PASS
lifecycle-probe=PASS target=GTK3
```

The GTK4 probe also passed three cycles with `shell-active=PASS`. This closes
the packaged-launcher portion of the earlier qualification note; physical
GTK3 input, F7/F8 transport, and regression invariants remain open.

## Current-image rerun

The final datastore-regression image (`aspartame-2026.10.03-x86_64.iso`,
SHA-256 `0f76f2d7b0882039cf8c5eb6fa90db561c9ee929d3d836f43a240b2dbf7e7726`)
passed the packaged GTK3 and GTK4 probes for three cycles each. The host
regression suite also passed `420` tests; physical GTK3 input and F7/F8
transport remain separate open gates.
