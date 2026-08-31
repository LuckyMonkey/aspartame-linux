# Aspartame Activity review pipeline

This is the red-pen review record for Activities shipped or considered by Aspartame.
It is separate from Sugar's per-user runtime ratings in ~/.config/aspartame/activity-ratings.json.
Runtime ratings remain the user's durable assessment; this table records engineering evidence.

Review states: unreviewed, queued, testing, pass, needs-work, blocked, remove-candidate.
Ratings use the existing five-point scale: 1 Broken, 2 Bad, 3 Needs work, 4 Good, 5 Perfect.
A rating is evidence, not a deletion command.

Repeatable loop:

    make run
    ./scripts/ssh-asp true
    make activity-review-inventory
    make activity-review-check

In Sugar, launch one Activity from Home, then capture the guest display through SSH:

    make activity-review-capture ACTIVITY=Help.activity

This writes a screenshot and runtime record under reports/activity-review/Help.activity/.
The capture helper does not launch, stop, or modify the Activity.

Checklist for every Activity:

- [ ] appears in Home with expected icon and name
- [ ] launches without a traceback
- [ ] main surface is visible and understandable
- [ ] toolbar, palettes, keyboard, and pointer work
- [ ] stops and resumes cleanly where supported
- [ ] screenshot and runtime record are captured
- [ ] network requirements are identified
- [ ] status and rating are recorded

Existing installed Activities are never removed by this pipeline.
Sugarizer activities are reviewed separately as web applications, not native sugar-activity3 bundles.
