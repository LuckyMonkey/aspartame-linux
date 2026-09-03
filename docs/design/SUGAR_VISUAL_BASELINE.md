# Aspartame Sugar visual baseline

Status: GTK3 reference contract, 2026-09-03

This document describes the visual behavior the GTK4 shell must reproduce. It
is a contract for meaning and hierarchy, not a request to redraw Sugar with a
different toolkit or a generic desktop theme.

## Identity and composition

Aspartame remains Sugar: Home is the user's place, Activities are the work in
progress, the Frame is contextual peripheral UI, and the Journal is the record
of work. The Home ring/list, XO identity, palettes, symbolic icons, and
Activity lifecycle retain their Sugar semantics.

There is no permanent taskbar, dock, Start menu, desktop icon grid, or generic
system tray. New shell information belongs inside an existing Sugar surface.
The reference clock is therefore a small passive element inside the existing
Frame/toolbar, not a status bar.

## Color and state

`XoColor` and Sugar artwork remain the source of truth for Sugar symbolic icon
stroke/fill rendering. Aspartame must not flatten Activity/XO colors into a
single theme color, and must not recolor fixed-color or photographic artwork.

Aspartame-owned widgets use a small semantic token set defined in
`aspartame_visual.py`. The tokens are deliberately limited to Aspartame
additions; they do not replace Sugar artwork's XOColor pipeline.

Activity state is semantic: installed/not running uses ordinary artwork;
launching/running may use Sugar's established active treatment; active/current
is distinct; stopped/crashed returns to the ordinary icon without stale UI
state. The source of truth is Jarabe's Activity model, never a click cache.

## Sizing and density

Activity icons occupy a fixed slot so an unusual SVG cannot enlarge a row or
change table geometry. The Activity Manager currently uses a 52px icon slot,
52px rating faces, and a compact 32px outlined Help control target. These are implementation
defaults, not new Sugar concepts; GTK4 should preserve the visual bounds while
using its own measurement/rendering APIs.

Controls have one clear purpose, enough room for keyboard focus, and no
decorative color variation. Focus is visible without relying on color alone.

## Help and emphasis

What's This? is a Sugar shell capability. It selects a semantic target without
activating it, explains the target in plain language, and optionally opens
offline detail. Any dimming/highlight belongs inside a known GTK surface or a
fixed opaque presentation surface; transparent native top-level compositing is not a requirement.

## GTK4 migration contract

The following must remain reusable when rendering moves:

- Sugar `XoColor` meaning and Activity state model: direct semantic equivalent.
- Aspartame visual tokens: direct model/style equivalent, renderer replaced.
- fixed icon slots and hit targets: GTK4 measurement/layout equivalent.
- Help target IDs and explanations: renderer-independent.
- Home ring/list geometry: preserve behavior; replace only obsolete widget APIs.

Before changing shell UI, ask what Sugar concept owns it, whether the behavior
is intentional, whether less chrome works, and whether color/state semantics
remain intact.
