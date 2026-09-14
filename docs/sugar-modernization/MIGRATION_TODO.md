# GTK4 migration backlog

## P0 — boot/session startup

- [x] Select and pin Sugar PR #1106 and reach real Jarabe pixels in the
  Aspartame VM with embedded Casilda 1.5. This proves startup, not a complete
  session.
- [x] Align the toolkit/datastore D-Bus service contract (preview patch `0018`).
- [x] Propagate locale and runtime-directory state before private D-Bus starts.
- [x] Hold corrected Home beyond 60 seconds without a fatal traceback; search
  and return were also exercised through AT-SPI.
- [x] Remove any GTK3-only shell import from the selected upstream branch.
  The modern process resolves generic `Gtk` imports to 4.0 and no explicit
  GTK3 namespace import remains in `jarabe`; GTK3 stays in its separate Space.

## P1 — major shell functionality

- [x] Frame, Home, Journal, and Activity launch smoke tests on GTK4 (see
  `reports/gtk4/runtime-matrix-20260913.md`).
- [x] Render and clear a real GTK4 Home search without crashing lazy List View.
- [x] Build/register one pinned GTK4 Activity and prove launch/switch/stop.
- [x] Verify Sugar theme/icon behavior without GTK3-only CSS assumptions.

## P2 — Journal / Neighborhood / Frame / clipboard / palettes

- [x] Port the core GTK4 palette and tooltip path using native Popover and Sugar CSS; runtime palette capture is recorded.
- [x] Port clipboard and remaining palette behavior using upstream GTK4 APIs;
  live text transfer is recorded in the runtime matrix.
- [x] Verify datastore and D-Bus boundaries remain unchanged (native Journal,
  ObjectChooser, and repeated Activity lifecycle evidence in the runtime
  matrix).

## P3 — core activities / Fructose

- [x] Test and register the GTK4 Log, Count, and Calculate Activities; all have
  live launch/stop evidence (Calculate also passed repeated lifecycle probing).
- [x] Register and verify native GTK4 Clock and JAMClock replacements, plus
  pinned Image Viewer, Terminal, and Browse bundles, in the live Casilda
  Activity matrix.
- [x] Port and verify a native GTK4 Mastermind Activity; the modern registry
  now includes a self-contained logic game with live launch/stop evidence.
- [x] Port and verify a native GTK4 Poll Activity with editable choices and
  local vote counts.
- [x] Port and verify a native GTK4 Mancala Activity with playable pit and
  store state.
- [x] Port and verify a native GTK4 Reversi Activity with legal capture and
  disc flipping.
- [x] Port and verify a native GTK4 Jumble Activity with answer checking and
  word navigation.
- [x] Port and verify a native GTK4 Number Rush Activity with arithmetic
  rounds and score tracking.
- [x] Port and verify a native Calculate Activity; the modern registry now
  launches Calculate alongside the other verified GTK4 bundles.
- [x] Inventory the remaining legacy Fructose/Sugarizer activities (84 rows in
  `docs/activity-reviews/REVIEWS.tsv`, refreshed 2026-09-14).
- [ ] Port the remaining legacy Fructose activities. Keep each Activity a
  separate reviewable change.
- [x] Port Across and Down as a native GTK4 Activity and verify three repeated
  Casilda launch/stop cycles (`mulawa.AcrossDown`).
- [x] Port IQ as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`mulawa.IQ`).
- [x] Port Appel Haken as a native GTK4 Activity and verify three repeated
  Casilda launch/stop cycles (`mulawa.AppelHaken`).
- [x] Port BallAndBrick as a native GTK4 Activity and verify three repeated
  Casilda launch/stop cycles (`org.sugarlabs.BallAndBrick`).
- [x] Port Implode as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`com.jotaro.ImplodeActivity`).
- [x] Port PlayGo as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`org.laptop.PlayGo`).
- [x] Port BlockParty as a native GTK4 Activity and verify three repeated
  Casilda launch/stop cycles (`org.laptop.BlockPartyActivity`).
- [x] Port Typing Turtle as a native GTK4 Activity and verify three repeated
  Casilda launch/stop cycles (`org.laptop.community.TypingTurtle`).
- [x] Port Memorize as a native GTK4 Activity and verify three repeated
  Casilda launch/stop cycles (`org.laptop.Memorize`).
- [x] Port Maze as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`vu.lux.olpc.Maze`).
- [x] Port FotoToon as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`org.eq.FotoToon`).
- [x] Port Portfolio as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`org.sugarlabs.PortfolioActivity`).
- [x] Port Markdown as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`org.sugarlabs.Markdown`).
- [x] Port Finance as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`org.laptop.community.Finance`).
- [x] Port Words as a native GTK4 Activity and verify three repeated Casilda
  launch/stop cycles (`org.laptop.Words`).

## P4 — Wayland/backend neutrality

- [x] Build Casilda 1.5 against guest Arch wlroots 0.20 and verify the private
  `wayland-sugar` socket/protocol registry.
- [x] Remove accidental new X11 dependencies from migrated code; the current
  GTK4 overlay contains no `GdkX11`, XID, or GTK3-only window imports.

## P5 — cleanup and packaging

- [ ] Track Python/GTK API deprecations and Arch package drift.
- [x] Add the guest-only GTK4/Casilda build dependencies to the ISO profile.

## P6 — optional modernization

- [ ] AI-assisted mechanical ports with upstream references.
- [ ] Typing, documentation, and accessibility improvements after behavior is
  stable.

- [x] Confirm GTK4 Jarabe remains alive for 60 seconds under isolated Xvfb/DBus. Verified 2026-09-01 with no traceback, crash, SIGILL, or fatal marker. This closes process liveness only; Home/Frame/input still require runtime interaction tests.
