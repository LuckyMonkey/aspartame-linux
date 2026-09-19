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
  are now fixed. Home's Favorites ring is reachable by Tab and launchable with
  Enter (patches 0146/0147), and Sugar tool buttons carry accessible names
  (0148).
- **Evidence:** `reports/gtk4/activity-manager-accessible-20260915.md`,
  `reports/gtk4/five-fix-pass-20260915.md`
- **STATUS: PASS**

## W6 — Repeated F7/F8 Space comparison

- **GTK3 reference:** F7 and F8 switch between the classic and modern Spaces.
- **GTK4 result:** physical F7/F8 switch correctly, verified over two
  consecutive round trips with `runtime-check=ok` for gtk3 on desktop 0 and
  gtk4 on desktop 1 each time.
- **Gap:** was the shared key grab — see W7; one cause, both workflows.
- **Minimum fix:** `patches/system/0001-sugar-toolkit-gtk3-keygrabber-release.patch`,
  shipped by `packages/sugar-toolkit-gtk3/PKGBUILD`
- **Evidence:** `reports/gtk4/fkey-grab-resolved-20260915.md`
- **STATUS: PASS** (2026-09-16, re-verified after patch 0153). The F7 half
  regressed and was root-caused: Sugar disables every window manager
  keybinding at startup, so the Metacity `switch-to-workspace-1 = ['F7']`
  binding never fired; F7/F8 were bolted onto the modern shell's main window
  only; and the Settings control panel is a plain `Gtk.Window` that never
  joins the application, so no shell key reached the keyboard while it was
  open. Patch 0153 makes the Space keys shell actions and registers the
  control panel with the key handler. See
  `reports/gtk4/f7-space-key-rootcause-20260916.md`.

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
  shipped by `packages/sugar-toolkit-gtk3/PKGBUILD`.
- **Evidence:** `reports/gtk4/fkey-grab-resolved-20260915.md`
- **STATUS: PASS** (2026-09-15), with the F7 half regressed on 2026-09-16 —
  see W6.

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
- **GTK4 result:** navigation, Activity Manager policy and approval prompt
  verified. About my Computer reports the real build rather than
  "Not available" (patch 0145).
- **Evidence:** `reports/gtk4/settings-runtime-20260915.md`,
  `reports/gtk4/five-fix-pass-20260915.md`
- **STATUS: PASS**

## W11 — Neighborhood / Group collaboration with a peer

- **GTK3 reference:** peers appear; shared Activities can be joined.
- **GTK4 result:** honest empty state only.
- **Gap:** requires a second live participant.
- **Evidence:** `reports/gtk4/neighborhood-runtime-20260915.md`
- **STATUS: OPEN — blocked on a second participant, not on code**

## W12 — A refused session action must not destroy the session

- **GTK3 reference:** shutdown and logout live behind the XO owner palette,
  are confirmed, and do nothing to the desktop if the system refuses.
- **GTK4 result:** choosing Shutdown raises the existing confirmation alert;
  Cancel returns safely; a refused `PowerOff` now leaves the session running
  and logs one plain warning instead of a fatal traceback.
- **Gap:** `shutdown_completed()` quit the shell whether or not the privileged
  call succeeded - `# Always quit the shell model to ensure we exit` - so a
  polkit refusal destroyed the desktop and shut nothing down.
- **Minimum fix:** patch 0143.
- **Evidence:** `reports/gtk4/w12-session-control-20260915.md`
- **STATUS: PASS** (2026-09-15), with one limitation recorded: teardown of
  Activities still begins before authorization is known.

---

## Open findings from the second five-fix pass (2026-09-16)

Reproduced and left open. Full evidence in
`reports/gtk4/five-fix-pass-2-20260916.md`.

- **Settings → Language crashes on construction.** The image ships three
  locales, so `read_all_languages()` returns nothing, `_add_row()` falls
  back to `'English'`, and `_build_country_list` raises `KeyError:
  'English'`. Closed by 0161 with an English/USA `C.UTF-8` fallback row;
  `scripts/sugar-gtk4-language-settings.py` now constructs the real section
  and passes on the rebuilt guest.
- **Settings semantic close left the modal counter set.** `ShowHome()` could
  make the window disappear while the next `ShowControlPanel()` was refused.
  Closed by 0162, which releases `_has_modal` ownership in the shared shell
  close path.
- **The Settings control panel cannot be dismissed from the keyboard.**
  Escape, F3 and F4 leave it up and every keystroke reaches its search
  entry. Related to the 2026-09-15 finding that it does not cover the
  screen.
- **The shell logs every keystroke at WARNING**, so typed text lands in the
  shell log and real warnings are buried.
- **Alt+Tab selects the next Activity but its surface is not raised.** The
  shell has one compositor page for all Activities and Casilda exposes no
  way to raise a chosen toplevel. Compositor work, not a bounded fix.

## Open findings from the five-fix pass (2026-09-15)

Reproduced and left open rather than pursued, each recorded because it exceeds
a bounded fix. See `reports/gtk4/five-fix-pass-20260915.md`.

- **F5 does not open the Journal.** `show_journal()` calls `reveal()`, which
  uses top-level window semantics, and never moves the shell's view state to
  the Journal page. Poking the stack directly was tried and rejected: it left
  F3 unable to return Home. The coherent fix drives the shell's zoom and
  active-activity state. The Journal is reachable from the Frame meanwhile.
- **Journal list rows render their palette inline.** Every entry shows three
  full-width action bars, so ~4 of 697 entries fit on screen. The row actions
  belong in the palette that `listview.py` already builds; the fault is in the
  GTK4 list-row/palette-invoker port.
- **The Settings window does not cover the screen.** Home's toolbar and search
  entry stay visible above a modal control panel, leaving two stacked search
  entries. Calling `fullscreen()` on the window had no effect, so this is
  window management between the shell and a transient modal under Metacity.

---

## Next

W11 remains open and is blocked on a second live participant rather than on
code. W6 regressed on 2026-09-16: F8 still reaches the modern Space, F7 no
longer returns from it. Every other workflow in the deck passes with runtime
evidence.

**Re-verify F7 from a clean boot first.** It is the one thing standing
between here and the point the deck was built for: **human F7/F8 parity
testing**, not another autonomous hardening phase.

The key grabber fix now ships as a rebuilt package
(`packages/sugar-toolkit-gtk3/PKGBUILD`, installed from the profile's
`[aspartame]` repository) rather than a hand-installed library. Running
`mkarchiso` against that repository is the one step not yet executed.
