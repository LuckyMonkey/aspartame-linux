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
remaining peer-collaboration limits are recorded in the runtime matrix rather
than hidden by this check.

## Compare the Spaces side by side

When visual parity or interaction behavior needs direct comparison, use the
windowed comparison mode inside the guest:

```sh
GTK4_ROOT=/usr/lib/aspartame/gtk4-preview \
  /usr/lib/aspartame/gtk4-preview/scripts/sugar-gtk4-space.sh side-by-side
```

This restarts the stable GTK3 shell with a half-width layout, starts GTK4
windowed, and tiles both Spaces on the same desktop. Click either pane to
interact with it; no function-key delivery through QEMU is required. On GTK4
Home, the four-square Spaces button beside Help opens the same actions; choose
“Compare Spaces side by side” to run this workflow without a function key.
The guest-side accessibility probe exercises that exact button action:

```sh
/usr/lib/aspartame/gtk4-preview/scripts/sugar-gtk4-spaces-menu-probe.py
```

It must report `spaces-menu=PASS` and create the comparison marker. Running
`gtk3`, `gtk4`, or `setup` removes the comparison marker and returns to the
normal workspace/fullscreen arrangement.

For the non-comparison two-context path, use the packaged Chirality bridge:

```sh
/usr/lib/aspartame/gtk4-preview/scripts/sugar-chirality-space.sh left
/usr/lib/aspartame/gtk4-preview/scripts/sugar-chirality-space.sh right
```

Each command selects one complete Space and activates its full surface. It
does not create a split screen and it does not retain a previous-frame or
recent-context history. In the current GTK migration it maps Left to the
Classic Space and Right to the Modern Space; the later GTK4-only Activity
adapter changes that mapping without changing the Chirality object model.

The GTK4-only Activity adapter is now available for headless qualification:

```sh
python3 /usr/lib/aspartame/gtk4-preview/scripts/sugar-chirality-activity.py \
  --state-file "$XDG_RUNTIME_DIR/aspartame/chirality.json" \
  assign left ACTIVITY_A
python3 /usr/lib/aspartame/gtk4-preview/scripts/sugar-chirality-activity.py \
  --state-file "$XDG_RUNTIME_DIR/aspartame/chirality.json" \
  assign right ACTIVITY_B
python3 /usr/lib/aspartame/gtk4-preview/scripts/sugar-chirality-activity.py \
  --state-file "$XDG_RUNTIME_DIR/aspartame/chirality.json" activate left
```

`activate` calls the modern GTK4 Shell's single-surface Activity activation
contract and then records Active/Held state. It does not switch GTK3/GTK4
Spaces; object continuity remains the separate Milestone 2 boundary.
