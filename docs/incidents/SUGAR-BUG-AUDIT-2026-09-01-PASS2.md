# Sugar/Jarabe adversarial bug audit — pass 2 — 2026-09-01

This report records five new, independently rooted defects. The prior audit
(docs/incidents/SUGAR-BUG-AUDIT-2026-09-01.md) was read first; none of its
five findings are repeated.

Runtime: Aspartame VM, Sugar 0.121-7, Python 3.14.7, GTK 3.24.52, X11 :0,
1920x1080, live source overlay /mnt/aspartame-dev/sugar/src.

## BUG 1 — Clearing a rating did not persist the unanswered state

Component: Settings → Activity Manager  
Severity: Medium  
Category: state persistence

USER-VISIBLE SYMPTOM

After selecting a Wong–Baker rating and clicking that selected face again, the
face became visually unselected but the old rating returned after reopening.

REPRODUCTION PROCEDURE

Open Settings → Activities, select a face, click it again to clear it, then
reopen the manager.

EXPECTED BEHAVIOR

An explicitly cleared answer remains unanswered.

ACTUAL BEHAVIOR

The control emitted rating 0, but the callback ignored zero, retaining the
old JSON value.

PRE-FIX EVIDENCE

The pre-fix callback only called save_rating when rating was truthy; the
focused fixture demonstrated that the stored value remained.

ROOT CAUSE

ActivityManager._face_rating_changed treated zero as “nothing to save”.

RESPONSIBLE FILES / FUNCTIONS

cpsection/activities/view.py::_face_rating_changed
cpsection/activities/model.py::save_rating

FIX

Added model.clear_rating with atomic JSON replacement and call it for zero.

WHY THIS FIX IS CORRECT

The control has a valid unanswered state; the persisted model now matches it.

REGRESSION COVERAGE

test_clearing_rating_removes_the_answer.

RUNTIME VERIFICATION

Live VM probe: rating clear persistence: PASS.

POST-FIX EVIDENCE

artifacts/sugar-bug-audit-2026-09-01-pass2/post-fix-home.png

COMMIT

8c023df, with callback correction in 59cd67c.

UPSTREAM RELEVANCE

Downstream Activity Manager behavior; applicable to any Sugar rating control.

INDEPENDENCE JUSTIFICATION

This is a JSON state-transition defect, independent of inventory parsing,
bundle precedence, keyboard navigation, and Home geometry.

## BUG 2 — A malformed Activity bundle crashed the entire inventory

Component: Settings → Activity Manager  
Severity: High  
Category: fault isolation / package inventory

USER-VISIBLE SYMPTOM

One damaged or partially installed Activity could make Activity Manager fail
instead of showing the remaining installed Activities.

REPRODUCTION PROCEDURE

Place a valid bundle and a bundle with malformed activity/activity.info in an
Activity root, then open/list the inventory.

EXPECTED BEHAVIOR

The valid Activity remains visible and the malformed one is skipped.

ACTUAL BEHAVIOR

MissingSectionHeaderError escaped _read_info and aborted list_activities.

PRE-FIX EVIDENCE

The live-source probe produced the ConfigParser traceback.

ROOT CAUSE

No per-bundle exception boundary surrounded metadata parsing.

RESPONSIBLE FILES / FUNCTIONS

cpsection/activities/model.py::_read_info and ::list_activities

FIX

Catch OSError, UnicodeError, and configparser.Error per bundle, log a warning,
and continue.

WHY THIS FIX IS CORRECT

One corrupt entry must not destroy unrelated inventory visibility.

REGRESSION COVERAGE

test_malformed_activity_does_not_hide_valid_activities.

RUNTIME VERIFICATION

Live VM: activity metadata isolation: PASS.

POST-FIX EVIDENCE

The probe output and healthy post-fix capture are retained with this audit.

COMMIT

ada06b1.

UPSTREAM RELEVANCE

Suitable for upstream inventory fault isolation.

INDEPENDENCE JUSTIFICATION

This is exception isolation during parsing, unrelated to duplicate selection,
ratings, input direction, or geometry.

## BUG 3 — A user Activity could be hidden by a system copy

Component: Settings → Activity Manager  
Severity: High  
Category: installed-bundle resolution

USER-VISIBLE SYMPTOM

If user and system bundles shared a bundle ID, the manager displayed the
system copy and hid the user’s override.

REPRODUCTION PROCEDURE

Place valid bundles with one bundle ID in system and user roots, then list them.

EXPECTED BEHAVIOR

The user-scoped copy wins.

ACTUAL BEHAVIOR

First-ID-wins scanning inspected system roots before the user root.

PRE-FIX EVIDENCE

The pre-fix fixture returned System Copy when given system then user roots.

ROOT CAUSE

Duplicate suppression had no root precedence policy.

RESPONSIBLE FILES / FUNCTIONS

cpsection/activities/model.py::list_activities

FIX

Added explicit precedence: user root, /usr/local, then system roots.
Noncanonical test roots retain supplied order.

WHY THIS FIX IS CORRECT

Local/user customization gets predictable precedence without changing IDs.

REGRESSION COVERAGE

test_user_copy_wins_over_system_copy.

RUNTIME VERIFICATION

The deployed model and final Sugar health probe passed.

POST-FIX EVIDENCE

artifacts/sugar-bug-audit-2026-09-01-pass2/post-fix-home.png

COMMIT

dbade75.

UPSTREAM RELEVANCE

Potential upstream policy if Sugar formalizes user-over-system precedence.

INDEPENDENCE JUSTIFICATION

This is duplicate-resolution policy and remains when all metadata parses.

## BUG 4 — The first Previous Activity action moved forward

Component: Sugar keyboard activity switching  
Severity: High  
Category: keyboard navigation

USER-VISIBLE SYMPTOM

When activity tabbing was not already active, the first Previous Activity
shortcut moved to the next Activity.

REPRODUCTION PROCEDURE

Open at least two Activities, ensure tabbing is inactive, and invoke the
previous-activity shortcut once.

EXPECTED BEHAVIOR

The first invocation moves backward.

ACTUAL BEHAVIOR

previous_activity fell through to _activate_next_activity when the input grab
was not established.

PRE-FIX EVIDENCE

The live source showed the fallback called the next-direction helper.

ROOT CAUSE

The fallback branch used the wrong directional helper.

RESPONSIBLE FILES / FUNCTIONS

jarabe/view/tabbinghandler.py::previous_activity

FIX

Added _activate_previous_activity and used it in the fallback.

WHY THIS FIX IS CORRECT

Input-grab failure must not reverse the meaning of the user’s command.

REGRESSION COVERAGE

Live dispatch probe verified previous receives activation and next does not.

RUNTIME VERIFICATION

Live VM: first previous-activity dispatch: PASS; Sugar health: PASS.

POST-FIX EVIDENCE

artifacts/sugar-bug-audit-2026-09-01-pass2/post-fix-home.png

COMMIT

59cd67c.

UPSTREAM RELEVANCE

Strong upstream candidate; no Aspartame-specific dependency.

INDEPENDENCE JUSTIFICATION

A keyboard fallback-direction defect, independent of Activity Manager and
Home layout state.

## BUG 5 — Home collision detection treated separated icons as overlapping

Component: Sugar Home freeform/Spread layout  
Severity: Medium  
Category: rendering/layout geometry

USER-VISIBLE SYMPTOM

Rectangles with horizontal overlap but no vertical overlap were treated as
collisions, triggering unnecessary displacement and possible Home jitter.

REPRODUCTION PROCEDURE

Give two Home child rectangles the same horizontal span with one entirely
below the other, then run Grid collision detection.

EXPECTED BEHAVIOR

Only overlap in both dimensions is a collision.

ACTUAL BEHAVIOR

The predicate checked only intersection.width > 0.

PRE-FIX EVIDENCE

The pre-fix condition classified vertically separated rectangles as a
collision and scheduled solving.

ROOT CAUSE

A two-dimensional rectangle problem used a one-dimensional predicate.

RESPONSIBLE FILES / FUNCTIONS

jarabe/desktop/grid.py::_detect_collisions

FIX

Require positive intersection width and height.

WHY THIS FIX IS CORRECT

It matches rectangle intersection semantics and prevents unrelated icons moving.

REGRESSION COVERAGE

Live VM probe: grid non-overlap collision: PASS.

RUNTIME VERIFICATION

Deployed through make sugar-reload; Sugar process, Metacity, D-Bus, Home,
and fatal-log checks passed.

POST-FIX EVIDENCE

artifacts/sugar-bug-audit-2026-09-01-pass2/post-fix-home.png

COMMIT

f07eae9.

UPSTREAM RELEVANCE

Strong upstream candidate.

INDEPENDENCE JUSTIFICATION

A geometric predicate defect, independent of inventory, ratings, and keyboard.

## Adversarial review

All five survive:

| Finding | Observable | Reproduced | Root caused | Fixed | Verified | Independent | Prior duplicate |
|---|---|---|---|---|---|---|---|
| 1 rating clear | YES | YES | YES | YES | YES | YES | NO |
| 2 malformed inventory | YES | YES | YES | YES | YES | YES | NO |
| 3 user/system precedence | YES | YES | YES | YES | YES | YES | NO |
| 4 previous direction | YES | YES | YES | YES | YES | YES | NO |
| 5 collision geometry | YES | YES | YES | YES | YES | YES | NO |

Excluded but fixed: SnowflakeLayout.remove was corrected in 700981a because
its recursive self.remove call failed to unparent removed children. It is not
counted: this session lacked sufficiently independent user-visible evidence
of the leak/stale rendering. The reload deployment-path correction in e22d37d
is also not counted because it is development workflow infrastructure.

## Test and status summary

Tests before: focused pre-fix probes demonstrated each listed failure.
Tests after: python3 -m pytest -q — 13 passed.
Patch sync: PASS.
make sugar-reload: PASS.
Live probes: Activity metadata, rating clear, Snowflake unparent, Grid
geometry, and previous dispatch — PASS.
GTK3: stable path healthy; package-owned Sugar untouched.
GTK4: unchanged/experimental; not exercised.
Stable Aspartame: healthy X11 Sugar Home at 1920x1080.

Evidence: artifacts/sugar-bug-audit-2026-09-01-pass2/post-fix-home.png
Audit: docs/incidents/SUGAR-BUG-AUDIT-2026-09-01-PASS2.md
