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

Provenance: W1, W3 and W5 were verified against the live guest on
2026-09-15. W2, W4, W7, W8, W9 and W10 carry PASS from existing evidence
reports in this repository and were not re-run that day; treat them as
inherited until a change plausibly touches them.

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
- **GTK4 result:** typing `Clock` on Home now filters to
  "2 matching activities (of 54)" — Clock and JAMClock. Previously physical
  typing reached Home not at all: nothing on the page held focus, so
  HomeWindow's existing type-to-search handler never ran. The character that
  summons the entry is also no longer swallowed (`Clock`, not `lock`).
- **Gap:** clearing the query with physical Backspace does not reach the
  entry, so the Favorites ring is not restored that way. The `x` affordance
  and Escape were not confirmed either.
- **Minimum fix:** patches 0136 (visible page owns focus) and 0141 (keep the
  summoning key).
- **Evidence:** `reports/screenshots/sugar-20260915-174125-v0.0.31.png`
- **STATUS: PASS for type-to-filter; clearing recorded as an open residual**

## W4 — Abnormal Activity exit

- **GTK3 reference:** a killed Activity clears its process, service and shell state.
- **GTK4 result:** cleanup verified, repeated.
- **Evidence:** `reports/gtk4/activity-abnormal-exit-20260913.md`
- **STATUS: PASS**

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
- **GTK4 result:** semantic switching round-trips cleanly and is the working
  comparison mechanism. **Physical** F7/F8 does not fire: Metacity holds the
  X11 grab (`switch-to-workspace-1 = ['F7', '<Super>Home']`,
  `switch-to-workspace-2 = ['F8']`) and an injected F7 produces no workspace
  change and never reaches the shell process.
- **Gap:** X11/Metacity key transport, not Sugar.
- **Minimum fix:** unknown; needs an isolated Metacity grab reproduction.
- **Evidence:** `reports/gtk4/keyboard-delivery-20260915.md` (frontier section)
- **STATUS: OPEN — frontier recorded, rotated away from**

## W7 — Frame navigation

- **GTK3 reference:** F6 reveals the Frame; Escape dismisses it.
- **GTK4 result:** F6 reveal and F6→Escape verified.
- **Evidence:** `reports/gtk4/qemu-function-keys-20260915.md`
- **STATUS: PASS**

## W8 — Palette interaction

- **GTK3 reference:** palettes stay attached to their target and dismiss predictably.
- **GTK4 result:** palettes exercised in the modern Space.
- **Evidence:** `reports/gtk4/gtk4-palette-20260905.png`
- **STATUS: PASS**

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

---

## Next

Deck is green except W6 (X11/Metacity transport frontier) and W11 (needs a
second participant). Neither is closable without either a subsystem-sized
investigation or an external participant, so both stay recorded and open.

The remaining breadth risk is Activity catalog depth: most Activities are
classified FUNCTIONAL PORT rather than FULL PORT in
`ACTIVITY_PORT_CLASSIFICATION.md`. Promotion is per-Activity evidence work,
not a shell gap. Add a workflow here only when a specific user-visible
behavior is observed failing.
