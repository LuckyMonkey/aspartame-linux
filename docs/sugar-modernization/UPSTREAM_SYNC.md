# Upstream sync

The stable pin is recorded in `sugar-overlay/UPSTREAM`; current values are
`sugar 0.121-7` and its SHA-256. Update it only after testing a matching
package and regenerating the overlay patch with `make sugar-patch-check`.

For source reconnaissance:

```sh
export MODERNIZATION_ROOT=/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization
scripts/sugar-upstream-sync.sh "$MODERNIZATION_ROOT/sugar-toolkit-gtk4" \
  "$MODERNIZATION_ROOT/sugar"
git -C "$MODERNIZATION_ROOT/sugar-toolkit-gtk4" log -1 --format='%H %cs %s'
git -C "$MODERNIZATION_ROOT/sugar" log -1 --format='%H %cs %s'
```

Review upstream pull requests in the GitHub repositories, record selected
commit IDs in `GTK4_STATUS.md`, then run the isolated probe. Do not copy
unrelated files from `main` into stable. A downstream patch needs a source,
reason, reproduction, upstream issue/PR link, and removal condition.
