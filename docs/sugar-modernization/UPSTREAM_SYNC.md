# Upstream sync

The shell pin uses the official Sugar Labs pull-request ref (Sugar PR #1106,
`beaae56`). sugar-toolkit-gtk4 PR #35 merged, so the toolkit now follows
`main` (`9d86a31`). The resolved SHAs are still recorded so a preview is
reproducible even if a branch advances.

## Rebased series (re-pinned 2026-10-22)

Sugar and the toolkit each carry one rebased downstream delta:
`0300-sugar-downstream-on-beaae56.patch` and
`0301-toolkit-downstream-on-9d86a31.patch`. They were generated from the
qualified guest checkout (October 5 build plus 0058, 0112z and 0203), then
rebased with `git rebase --onto`. Conflict decisions are recorded in each
patch header. The 132 individual patches they replace stay under
`patches/gtk4-preview/folded/` for provenance.
`tests/test_gtk4_rebased_series.py` fails if a rebase drops a folded
patch's work wholesale.

To move to a newer upstream head:

1. In a scratch clone, rebase the delta onto the new head
   (`git rebase --onto NEW OLD`) and resolve conflicts. Record the decisions
   in the patch header.
2. Update the pins in `scripts/sugar-gtk4-init.sh`.
3. In the guest, run `make sugar-gtk4-init`, which saves a dirty checkout
   to `build/pre-repin-*.diff`. Then run `make sugar-gtk4-build`.
4. Run `scripts/sugar-gtk4-rebase.sh` to regenerate 0300/0301 from the
   checkout.
5. `make sugar-gtk4-series-check` must report exact application, with no
   fuzz.

Upstream note: Sugar commits `9103057`/`beaae56` converted
`src/jarabe/main.py` and `src/jarabe/frame/framewindow.py` to CRLF. 0300
converts them back to LF.
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

## Sending fixes upstream

Aspartame-specific behavior can stay downstream. A fix that would help any
Sugar user should go to Sugar Labs:

1. Reproduce it against the current upstream pin.
2. Reduce it to one conceptual change with a test or an exact manual
   reproduction.
3. Record the Arch, Python and GTK versions and the logs.
4. Link the Sugar Labs issue or pull request, and submit it from a branch
   following their contributor workflow.

Bugs found here but not yet reported are listed on issue #1.
