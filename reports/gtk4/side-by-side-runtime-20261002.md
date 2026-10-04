# GTK4 side-by-side runtime qualification — 2026-10-02

This record proves the comparison workflow on the rebuilt standalone ISO.
It does not claim that GTK3 can already be removed; it removes the QEMU
function-key transport as a prerequisite for visual and interaction comparison.

## Image

- ISO: `aspartame-2026.10.02-x86_64.iso`
- SHA-256: `c7112675cbe69b9a79eee7343f7956d4cef2c8415ac34fd88d09f8cb47fc64f2`
- Boot: fresh QEMU boot with the normal Aspartame test disks
- Packaged controller: `/usr/lib/aspartame/gtk4-preview/scripts/sugar-gtk4-space.sh`
- Runtime root: `/usr/lib/aspartame/gtk4-preview`

## Procedure and result

As the desktop user, run:

```sh
GTK4_ROOT=/usr/lib/aspartame/gtk4-preview DISPLAY=:0 \
  /usr/lib/aspartame/gtk4-preview/scripts/sugar-gtk4-space.sh status
```

The fresh boot exposed the GTK4 Home Spaces button. The packaged accessibility
probe activated that button and its comparison action:

```text
spaces-menu=PASS button=Spaces compare-action=PASS marker=/run/user/1000/aspartame-side-by-side
```

The comparison controller then reported both shells and four workspaces. The
same result was re-run after the transport probe:

```sh
GTK4_ROOT=/usr/lib/aspartame/gtk4-preview DISPLAY=:0 \
  /usr/lib/aspartame/gtk4-preview/scripts/sugar-gtk4-space.sh side-by-side
```

Result:

```text
Sugar Spaces side by side: GTK3=960x1080 GTK4=960x1080
```

Before restoring comparison mode, the semantic round trip also passed the
runtime invariant checker for GTK4 on desktop 1 and GTK3 on desktop 0. The
workspace helper now supplements the EWMH activation request with an X11
input-focus request; this closes the Metacity race that left the GTK3 desktop
surface active after selecting GTK4:

```text
runtime-check=ok target=gtk4 pid=1170 desktop=1 window=0xe00005 stable_pid=743 gtk4_pid=1170
runtime-check=ok target=gtk3 pid=743 desktop=0 window=0x400004 stable_pid=743 gtk4_pid=1170
```

The captured 1920x1080 screen shows the GTK3 reference Space on the left and
the GTK4 candidate Space on the right. The panes are independently clickable.
Latest evidence image: `reports/screenshots/sugar-20261002-192314-v0.0.31.png`
(`SHA-256: 1935eb2737432a494fcd2a537d5cccfe416cbea06d1a0bc202edcb842e11f41b`).
The accessibility probe was re-run against the running final image and again
returned `spaces-menu=PASS button=Spaces compare-action=PASS`.

The mode is reversible. Running `gtk4` removed the comparison marker and
returned to the single GTK4 Space; running `side-by-side` again restored both
panes successfully. The final comparison state in this rerun was
`GTK3=2120`, `GTK4=2315`.

## Rebuilt-image rerun

The source fixes for the packaged GTK4 activity launchers were rebuilt into
`aspartame-2026.10.03-x86_64.iso`:

- SHA-256: `8859bc89fca6e7b2190db6cf283a5a7228fcc26e76aff861bec5662d28312ae0`
- Image identity: `IMAGE_ID=aspartame`, `IMAGE_VERSION=2026.10.03`
- Packaged Help launcher: executable (`0755`) and uses the packaged GTK4
  runtime root rather than the development checkout
- Spaces accessibility action: `spaces-menu=PASS button=Spaces compare-action=PASS`
- Side-by-side controller: `GTK3=960x1080 GTK4=960x1080`
- Fresh visual evidence: `reports/screenshots/sugar-20261002-204244-v0.0.31.png`
- Screenshot SHA-256: `38e1fdb702a8491c10f1b25e1fd28429452bb14343b8123b68e6a51e597d3676`

The screenshot shows the GTK3 reference Space on the left and GTK4 on the
right in one 1920x1080 capture. Both panes are visible and independently
clickable.

## Final datastore-regression rerun

The standalone archive and ISO were rebuilt after finding a persisted empty
numeric Journal metadata file that crashed GTK4 refresh. The guard now drops
malformed `filesize`, `creation_time`, or `timestamp` values while preserving
the Journal entry.

- ISO SHA-256: `0f76f2d7b0882039cf8c5eb6fa90db561c9ee929d3d836f43a240b2dbf7e7726`
- Standalone archive SHA-256: `670b0c8c8134134da3d6dd3c55f933db72b451e95c0a9874ddac70a09247a242`
- Installed source and prefix copies both contain the guard.
- Fresh GTK4 runtime: `runtime-check=ok`; Journal log: clean (no traceback,
  malformed-integer `ValueError`, or `ERROR:jarabe.journal`).
- GTK4 and GTK3 lifecycle probes: 3/3 cycles each, `PASS`.
- Spaces accessibility action: `spaces-menu=PASS button=Spaces compare-action=PASS`.
- Side-by-side geometry: `GTK3=960x1080 GTK4=960x1080`.
- One-cycle activity matrix: all 50 registered GTK4 bundles, `PASS`.

## Boundary

This is comparison and UX evidence, not full GTK4 retirement evidence.
Neighborhood collaboration still needs a second participant, and physical
F7/F8 delivery remains a transport-specific check. Neither blocks clicking
and comparing the two Spaces.
