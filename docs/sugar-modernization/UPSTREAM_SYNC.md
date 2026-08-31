# Upstream sync

The shell and toolkit preview pins use the official Sugar Labs pull-request
refs directly: Sugar PR #1106 and sugar-toolkit-gtk4 PR #35. The resolved SHAs
are still recorded so a preview is reproducible even if a PR branch advances.
Activity migration heads remain explicitly provisional until their upstream
ownership is confirmed.

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

Verify every recorded upstream ref without changing the checkout:

    make sugar-gtk4-status

This compares every row in the external PINS.tsv with the exact remote ref
and fails if a ref moved or disappeared. Re-run make sugar-gtk4-init only
after deliberately reviewing such a change.
