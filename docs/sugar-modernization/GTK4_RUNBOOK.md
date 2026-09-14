# GTK4 test runbook

This runbook never changes the installed GTK3 image. Use separate checkouts
and a separate Python environment or container only for tooling; do not use
Docker as the Sugar VM/session itself.

## Inspect the stable path

```sh
make sugar-info
make sugar-patch-check
make sugar-visual-check
```

## Prepare upstream checkouts

```sh
export MODERNIZATION_ROOT=/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4
scripts/sugar-gtk4-init.sh "$MODERNIZATION_ROOT"
```

This checks out the selected shell/toolkit integration PR heads, current
artwork/ext/datastore heads, and five active activity-port heads into a
separate tree. It writes `$MODERNIZATION_ROOT/PINS.tsv`. Use
`scripts/sugar-upstream-sync.sh` afterward only to fetch updates; do not
install either checkout into `/usr`.

## Probe GTK4 availability

```sh
GTK4_ROOT="$MODERNIZATION_ROOT" make sugar-gtk4-smoke
```

The probe returns nonzero when GTK4/PyGObject or the upstream toolkit is not
available. That is a useful result; it does not convert the test into a fake
pass. Aspartame also has an isolated GTK4 preview launcher and VM runtime;
`scripts/sugar-gtk4-check.sh` reports its live boot separately from the full
replacement gate. The stable GTK3 Space remains installed and is the reference
for comparison.

## Record a test

```sh
mkdir -p reports/sugar-modernization
git -C "$MODERNIZATION_ROOT/sugar-toolkit-gtk4" rev-parse HEAD \
  > reports/sugar-modernization/gtk4-toolkit-revision.txt
GTK4_ROOT="$MODERNIZATION_ROOT" \
  make sugar-gtk4-smoke 2>&1 | tee reports/sugar-modernization/gtk4-smoke.log
```

For a real shell test, use `scripts/sugar-gtk4-space.sh gtk4` inside the
development guest, then `scripts/sugar-gtk4-runtime-check.sh gtk4`. Never point
the stable launcher at the GTK4 checkout or overwrite the GTK3 runtime. The
remaining physical F-key and peer-collaboration limits are recorded in the
runtime matrix rather than hidden by this check.
