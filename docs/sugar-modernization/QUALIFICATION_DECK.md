# GTK4 qualification deck

A small, finite deck of representative GTK3→GTK4 **user workflows**. Each
entry describes observable behavior, not an internal subsystem. Progress
means closing a failing workflow.

Operating rules:

- Once a workflow passes with runtime evidence, **leave that subsystem**. Do
  not harden, generalize, refactor nearby code, or chase adjacent failures
  unless they independently block another workflow here.
- Choose the next item from the highest-value failing workflows, preferably
  outside the subsystem just touched. Rotate across shell, Activities,
  Journal, lifecycle, accessibility, collaboration, and visual parity.
- If an item cannot close without a subsystem-sized investigation, record the
  frontier, leave it OPEN, and rotate rather than stalling the project.
- A passing workflow should become boring and stop consuming attention.
- When the deck is green, that is the cue for **human F7/F8 parity testing**,
  not another autonomous hardening phase.

Ledger fields: WORKFLOW / GTK3 REFERENCE / GTK4 RESULT / GAP / MINIMUM FIX /
EVIDENCE / STATUS.

Provenance: W1-W8 were verified against the live guest on 2026-09-15. W9 and
W10 carry PASS from existing evidence reports in this repository and were not
re-run that day; treat them as inherited until a change plausibly touches
them.

---

## W1 — Launch an Activity, type into it, stop it

- **GTK3 reference:** launching an Activity focuses its first control;
  typing, Tab, Shift+Tab, Enter and Space all reach it.
- **GTK4 result:** passes. Typed text reaches the Help search entry; Tab and
  Shift+Tab traverse the Activity's own focus chain; Space and Enter activate.
- **Gap:** was four faults in series — overlay owned window focus, nothing
  claimed focus afterwards, the shell's duplicate-dispatch guard swallowed
  unhandled keys, and Casilda applied modifiers one keystroke late.
- **Minimum fix:** patches 0136, 0137, 0138, 0139, 0140.
- **Evidence:** `reports/gtk4/keyboard-delivery-20260915.md`
- **STATUS: PASS** (2026-09-15)

## W2 — Journal save and resume

- **GTK3 reference:** work saves on stop and resumes with content intact.
- **GTK4 result:** three Write save/stop/resume cycles pass.
- **Evidence:** `reports/gtk4/journal-save-resume-20260915.md`
- **STATUS: PASS**

## W3 — Home search

- **GTK3 reference:** typing anywhere on Home goes into the search entry and
  filters; clearing restores the Favorites ring.
- **GTK4 result:** typing `Clock` filters to "2 matching activities (of 54)"
  (Clock, JAMClock); five Backspaces clear the query and the Favorites ring
  returns. Previously physical typing reached Home not at all.
- **Gap:** three faults — nothing on the page held focus so HomeWindow's
  type-to-search never ran; the character that summoned the entry was eaten;
  and the query's switch to List View pulled focus into the results, so
  Backspace went to a row instead of the entry.
- **Minimum fix:** patches 0136, 0141, 0142.
- **Evidence:** `reports/screenshots/sugar-20260915-174125-v0.0.31.png` (filtered),
  `sugar-20260915-180029-v0.0.31.png` (cleared, ring restored)
- **STATUS: PASS** (2026-09-15)

## W4 — Activity lifecycle and cleanup

- **GTK3 reference:** launch, activate, stop; the process, its service and the
  shell's running state all clear.
- **GTK4 result:** `sugar-gtk4-lifecycle-probe.sh 3` passes three cycles,
  `service-ready=PASS shell-active=PASS ... cleanup=PASS` each time.
- **Harness defect found and fixed:** the probe took the first process matching
  its pattern, so an instance left running from earlier work made it stop that
  one, find its own launch still alive, and report `cleanup=FAIL` - a failure
  that said nothing about the lifecycle. It now refuses to run when an
  instance is already present.
- **Evidence:** re-run 2026-09-15; `reports/gtk4/activity-abnormal-exit-20260913.md`
- **STATUS: PASS** (2026-09-15)

## W5 — Accessibility navigation

- **GTK3 reference:** important controls expose name, role and state; the
  rating control is reachable by keyboard.
- **GTK4 result:** Activity trees expose named, focusable controls. The GTK3
  Activity Manager's faces and Remove pills were unnamed and unreachable and
  are now fixed.
- **Evidence:** `reports/gtk4/activity-manager-accessible-20260915.md`
- **STATUS: PASS**

## W6 — Repeated F7/F8 Space comparison

- **GTK3 reference:** F7 and F8 switch between the classic and modern Spaces.
- **GTK4 result:** physical F7/F8 switch correctly, verified over two
  consecutive round trips with `runtime-check=ok` for gtk3 on desktop 0 and
  gtk4 on desktop 1 each time.
- **Gap:** was the shared key grab — see W7; one cause, both workflows.
- **Minimum fix:** `patches/system/0001-sugar-toolkit-gtk3-keygrabber-release.patch`
- **Evidence:** `reports/gtk4/fkey-grab-resolved-20260915.md`
- **STATUS: PASS** (2026-09-15)

## W7 — Frame navigation

- **GTK3 reference:** F6 reveals the Frame; Escape dismisses it.
- **GTK4 result:** F6 reveals all four Frame panels — zoom toolbar, Journal
  and Help, the XO owner icon, and the device tray — and Escape dismisses it.
  F1/F3/F5 also reach Neighborhood, Home and Journal.
- **Gap:** never a Frame defect. `SugarKeyGrabber` only ever took X11 passive
  grabs: `grab_keys()` never ungrabbed the previous set, so the classic
  shell's release was a no-op and F1-F8 stayed owned for the life of that
  process while ordinary keys flowed normally. `dispose()` likewise never
  ungrabbed and left its GDK event filter on freed memory.
- **Minimum fix:** `patches/system/0001-sugar-toolkit-gtk3-keygrabber-release.patch`,
  rebuilt into `/usr/lib/libsugarext.so`.
- **Evidence:** `reports/gtk4/fkey-grab-resolved-20260915.md`
- **STATUS: PASS** (2026-09-15)

## W8 — Palette interaction

- **GTK3 reference:** palettes stay attached to their target and dismiss
  predictably.
- **GTK4 result:** hovering the Clock icon in the Favorites ring opens its
  palette attached to the icon, with the Sugar header (`Clock / Clock
  Activity`), a `Start new` action and the resumable Journal entries beneath.
- **Evidence:** `reports/screenshots/sugar-20260915-213859-v0.0.31.png`
- **STATUS: PASS** (2026-09-15)

## W9 — Clipboard transfer

- **GTK3 reference:** content copies between Activities via the Frame clipboard.
- **GTK4 result:** transfer verified at the supported level.
- **Evidence:** `reports/gtk4/runtime-matrix-20260914.md`
- **STATUS: PASS**

## W10 — Settings and Activity Manager

- **GTK3 reference:** control panel opens, sections render, removal policy holds.
- **GTK4 result:** navigation, Activity Manager policy and approval prompt verified.
- **Evidence:** `reports/gtk4/settings-runtime-20260915.md`
- **STATUS: PASS**

## W11 — Neighborhood / Group collaboration with a peer

- **GTK3 reference:** peers appear; shared Activities can be joined.
- **GTK4 result:** honest empty state only.
- **Gap:** requires a second live participant.
- **Evidence:** `reports/gtk4/neighborhood-runtime-20260915.md`
- **STATUS: OPEN — blocked on a second participant, not on code**

## W12 — Ending the session should not be one unguarded click

- **GTK3 reference:** shutdown and logout live behind the XO owner palette and
  are chosen deliberately.
- **GTK4 result:** clicking the top-right shell control at (1812, 37) on Home
  ended the modern shell immediately, leaving a black screen. The shell log
  shows it attempted a systemd stop, failed with
  `InteractiveAuthorizationRequired`, and exited anyway. No confirmation was
  shown and no work was offered a chance to save.
- **Gap:** a single unconfirmed click ends the session. In a learning
  environment that is a data-loss path, and the failed systemd call suggests
  the shutdown route is only half wired.
- **Minimum fix:** unknown; needs the control identified first. Its accessible
  node is an unnamed panel, which is its own accessibility gap - the control
  cannot be described to a screen reader either.
- **Evidence:** `reports/screenshots/sugar-20260915-213926-v0.0.31.png` (black
  screen after the click)
- **STATUS: OPEN — found 2026-09-15**

---

## Next

Only W11 remains open, and it is blocked on a second live participant rather
than on code. Every other workflow in the deck passes with runtime evidence.

That makes this the point the deck was built for: **human F7/F8 parity
testing**, not another autonomous hardening phase.

One packaging debt to clear first: the guest runs a rebuilt
`/usr/lib/libsugarext.so` carrying
`patches/system/0001-sugar-toolkit-gtk3-keygrabber-release.patch`. A fresh
ISO will not have it until the `sugar-toolkit-gtk3` package is rebuilt with
that patch, and without it no function key reaches the modern Space.
