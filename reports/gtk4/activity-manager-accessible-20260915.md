# Activity Manager accessibility — 2026-09-15

Closes two open Activity Manager backlog items: compact Remove pills being
discoverable and accessible, and focused UI tests for face selection.

## Defects

1. `rating_faces.py` called `button.set_can_focus(False)` on all five faces.
   A face carries an image and no label, so ATK had no name to read either.
   The rating control — a real answer the user is asked to give — was
   unreachable by keyboard and silent to a screen reader.
2. The Remove/Uninstall pill in `view.py` had a tooltip but no accessible
   name. The pill repeats once per row and its own label does not say which
   Activity it acts on, so 34 identical unnamed buttons were exposed.
3. `view.py` called `LOG.warning()` in `_remove_clicked` without importing
   `logging` or defining `LOG`. Any failed **or declined** uninstall raised
   `NameError` inside the signal handler instead of reporting the error —
   and declining the approval prompt is the ordinary path.

## Live evidence

Probed through AT-SPI against the running GTK3 control panel (pid 30191),
Activity Manager section open, 34 Activities listed.

Before, on the same live panel:

    roles seen: {'toggle button': 170, 'button': 36, ...}
    face buttons: 0
    remove pill: 0

170 face toggles (34 Activities x 5) and 36 buttons existed, and not one
carried an accessible name.

After:

    face buttons: 5
      name='Broken'     role=toggle button focusable=True
         description='Broken: Across and Down'
      name='Bad'        role=toggle button focusable=True
         description='Bad: Across and Down'
      name='Needs work' role=toggle button focusable=True
         description='Needs work: Across and Down'
      name='Good'       role=toggle button focusable=True
         description='Good: Across and Down'
      name='Perfect'    role=toggle button focusable=True
         description='Perfect: Across and Down'
    remove pill: 1
      name='Request approval: Across and Down'
         description='Request Sugar approval to uninstall this Activity.'

Screenshot: `reports/gtk4/activity-manager-accessible-20260915.png`
(SHA-256 `ecd1d8c51f949ac7c3d75ba880150331e35806633f6d4057f1c5b120e8c2452f`),
showing rows, icons with fallbacks, preserved ratings, and the compact pills.

## Deployment note

The repo keeps one source of truth at
`archiso/.../usr/share/aspartame/cpsection/activities/`. At runtime the
control panel resolves `cpsection` from `/usr/share/sugar/extensions`, which
comes first on `PYTHONPATH`; `customize_airootfs.sh` populates it by copying
the aspartame tree at image build time. Editing the repo copy is therefore
correct, but a live guest needs both paths refreshed to see the change
before an ISO rebuild. Guest originals are backed up under
`/root/aspartame-cpsection-backup-20260915/`.

## Tests

`tests/test_activity_manager_faces.py` builds the real GTK3 `FaceRating`
widget and covers one-or-none selection, the valid unanswered state, the
`rating-changed` value, out-of-range clamping, the selection style class,
keyboard reachability, accessible names and descriptions, and missing face
artwork. The keyboard and naming assertions were confirmed load-bearing by
reproducing the pre-fix state on a live widget and watching them flip.

Activity-icon fallback and row layout remain untested: both live in
`view.py`, which cannot be imported headless because it needs `sugar3` and
`jarabe.controlpanel`.
