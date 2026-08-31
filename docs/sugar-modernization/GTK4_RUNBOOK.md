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
GTK4_ROOT="$MODERNIZATION_ROOT/sugar-toolkit-gtk4" make sugar-gtk4-smoke
```

The probe returns nonzero when GTK4/PyGObject or the upstream toolkit is not
available. That is a useful result; it does not convert the test into a fake
pass. A complete shell boot requires upstream GTK4 shell work as well and is
not claimed by this repository yet.

## Record a test

```sh
mkdir -p reports/sugar-modernization
git -C "$MODERNIZATION_ROOT/sugar-toolkit-gtk4" rev-parse HEAD \
  > reports/sugar-modernization/gtk4-toolkit-revision.txt
GTK4_ROOT="$MODERNIZATION_ROOT/sugar-toolkit-gtk4" \
  make sugar-gtk4-smoke 2>&1 | tee reports/sugar-modernization/gtk4-smoke.log
```

For a real shell test, use a separate VM disk/profile and an upstream launch
method documented by the branch under test. Never point `make run` at the
GTK4 checkout or overwrite the stable runtime.
