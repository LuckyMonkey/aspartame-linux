# Aspartame engineering backlog

This is the durable project backlog. Items are intentionally grouped by
milestone so future sessions can resume without relying on chat history.

## Current milestone: Activity Manager

- [x] Preserve installed Activities and existing five-level ratings.
- [x] Remove SVG filenames from face-rating controls.
- [x] Extract the five-face control into a reusable `FaceRating` widget.
- [x] Keep the selected face visually distinct with a dark circular selection.
- [ ] Verify the revised Activity Manager visually after the next ISO rebuild.
- [ ] Add Activity icons and metadata fallbacks for every installed bundle.
- [ ] Add missing descriptions from Activity metadata or reviewed local help.
- [ ] Confirm compact Remove pills remain discoverable and accessible.
- [ ] Add focused UI tests for face selection, icon fallback, and row layout.

## Next milestone: About This Computer

- [ ] Inspect the current About section and its floating-window/session owner.
- [ ] Replace stale distribution text such as Debian with Aspartame/Arch data.
- [ ] Show kernel, desktop, graphics, memory, storage, and build information.
- [ ] Use fastfetch/neofetch-style data only as an input, not as a raw UI dump.
- [ ] Keep the information readable, Sugar-styled, and offline-capable.

## Next milestone: Settings architecture

- [ ] Determine whether the floating Settings window is intentional Sugar
  control-panel behavior or an Aspartame integration problem.
- [ ] Preserve Sugar control-panel navigation and lifecycle while improving
  sizing, ownership, placement, and visual consistency.
- [ ] Keep Activity Manager ratings/removal state persistent and recoverable.
- [ ] Add a real user-facing Activity management model without deleting bundles.
- [ ] Document which settings require a shell reload, session restart, or reboot.

## Help and discoverability

- [ ] Repair What's This? interception so help clicks do not activate targets.
- [ ] Ensure every registered target has a tooltip and offline “See more…” page.
- [ ] Add missing-help diagnostics without exposing technical IDs to users.
- [ ] Add Activity Manager, About, Settings, and face-rating help metadata.
- [ ] Verify keyboard access and Escape/toggle behavior.

## Activity quality pass

- [ ] Inventory every installed Activity and record version, source, license,
  icon, description, runtime dependencies, and current rating.
- [ ] Review each Activity against Sugar interaction, palette, toolbar, color,
  typography, localization, and lifecycle conventions.
- [ ] Remove unexplained giant instructional text and random visual chrome.
- [ ] Normalize terminology and visual behavior without erasing useful Activity
  identity or intentional color/state semantics.
- [ ] Classify each Activity: keep, repair, replace, quarantine, or remove only
  after an explicit recoverable decision.
- [ ] Add a repeatable Activity smoke test: launch, interact, save, resume,
  stop, and inspect logs.
- [ ] Preserve third-party source and document every Aspartame patch.

## Platform and persistence

- [x] Persistent Archiso system CoW overlay on `ASPARTAME_COW`.
- [x] Persistent user data on `ASPARTAME_DATA`.
- [x] Install and verify modern Unicode emoji font support.
- [ ] Add a clean known-good VM snapshot procedure to the runbook.
- [ ] Verify emoji rendering in Sugar Activities and text-entry widgets.
- [ ] Keep package changes reproducible in the archiso recipe.
- [ ] Avoid host-side mount/remount churn and protect unrelated drives.

## Future product work

- [ ] Make Neighborhood passive network/service discovery first.
- [ ] Design the public Neighborhood Board abstraction before implementing it.
- [ ] Evolve Group toward trusted peer/VPN concepts without hiding protocols.
- [ ] Build Python-first Settings, Software, Print, and Python environment
  Activities over stable system D-Bus/API interfaces.
- [ ] Integrate conda/Miniforge without modifying system Python.
- [ ] Investigate Flatpak as an application substrate, not a replacement for
  pacman or the Sugar Activity model.
- [ ] Evaluate Calamares for the eventual approachable installer.
- [ ] Measure boot-to-Sugar and responsive-Home timings before optimizing.

## Working rules

- Preserve Sugar's Home, Frame, Journal, Neighborhood, Group, Activity, color,
  palette, and lifecycle semantics unless evidence shows an implementation
  constraint is obsolete.
- Use small commits and the established source → deploy → reload → screenshot
  loop for every visible change.
- Back up VM state before destructive operations; never touch the Android-x86
  VM under `/media/freezer/One Touch/vms/android-x86/`.
