# Standalone image runtime evidence — 2026-09-19

Image under test:

```text
/media/freezer/SteamLibrary/vms/aspartame-build/artifacts/out/aspartame-2026.09.19-x86_64.iso
```

The VM was booted without a `-virtfs` development share and queried over the
image's SSH service.

## Observed

```text
dev-share-not-mounted
python3 -m jarabe.main                 # GTK3 reference Space
metacity --no-force-fullscreen
/usr/lib/aspartame/gtk4-preview/venv/bin/python .../jarabe/main.py
.../sugar-datastore/bin/datastore-service
fusermount3 .../runtime/doc            # portal/Casilda document surface
Sugar Spaces ready: F7 = GTK3, F8 = GTK4
```

The packaged GTK4 root, helper scripts, Activity launcher, generated prefix
paths, and Activity trees were all resolved inside `/usr/lib/aspartame/gtk4-preview`.

Calculate was launched from its packaged Activity directory with the GTK4
environment and `ASPARTAME_GTK4_PREVIEW=1`. Two independent launch/stop cycles
completed; the Activity process was absent after each stop. This proves the
packaged launcher can start a real GTK4 Activity without importing GTK3 into its
process. The launcher emitted one known GTK overlay assertion during teardown;
it did not leave a process or prevent the next cycle.

## Not yet proven

The VM was booted without a writable data disk because the host VM volume had
previously remounted read-only. Journal persistence across a guest reboot and
the complete Home/Frame/Journal/Settings manual interaction matrix therefore
remain separate acceptance work. The stable GTK3 Space was preserved and both
Space processes started in this shareless boot.
