# Sugar design guardrails

This document is the design constitution for Aspartame shell work. Aspartame
modernizes Sugar; it does not redesign Sugar into a conventional desktop. Read
[ASPARTAME-DOCTRINE.md](ASPARTAME-DOCTRINE.md) and
[ASPARTAME-HIG.md](ASPARTAME-HIG.md) alongside this file.

## Constitution

- Preserve intentional Sugar interaction models unless strong evidence shows
  that they are obsolete.
- Distinguish intentional UX decisions from limitations caused by old XO
  hardware or obsolete implementation details.
- Home means “me.”
- Neighborhood means “what is around me.”
- Group means “my deliberately associated group or community.”
- Activity means “what I am doing.”
- Journal means “what I have done.”
- **Capability means what the computer can provide and what an interaction
  requires. Capability is demonstrated, not presumed.**
- The Frame is contextual peripheral UI, not a taskbar.
- Activities are not conventional application windows.
- Journal is not merely a file manager.
- Activity and XO colors communicate identity and state. Do not normalize them
  away for aesthetic consistency.
- Prefer capabilities and actions over exposing implementation or application
  names.
- Preserve Sugar’s spatial hierarchy and direct-manipulation concepts.
- Preserve “low floor, no ceiling”: simple primary interaction with deeper
  capability available progressively.
- Do not assume literacy, pointer knowledge, keyboard knowledge, sight, hearing,
  or prior computer experience merely because a setup screen can be displayed.
- Do not create demographic interfaces such as child mode, blind mode, senior
  mode, or expert mode where one semantic interface with different capabilities
  can serve the interaction.
- Avoid permanent chrome unless the information genuinely needs to be globally
  available.
- Conventional Linux functionality may exist underneath without becoming the
  primary UI metaphor.

> **DO NOT “FIX” SOMETHING UNTIL YOU UNDERSTAND WHY SUGAR DOES IT.**

Do not introduce taskbars, docks, Start menus, desktop icon grids, conventional
system trays, or GNOME/KDE/XFCE metaphors merely because they are familiar. Do
not replace Sugar icon semantics with a generic icon library. External SVG or
icon libraries may provide source geometry, but Sugar remains responsible for
presentation, color, identity, and state semantics.

## Required questions before shell UI changes

Before changing a shell surface, answer all of these in the design note or
commit message:

1. What Sugar concept owns this?
2. Is the existing behavior intentional design or obsolete implementation?
3. Does this introduce a conventional desktop metaphor Sugar deliberately
   avoided?
4. Does it preserve low-floor/no-ceiling?
5. Is new permanent information actually necessary?
6. Does color retain semantic meaning without becoming the sole carrier of it?
7. Does this preserve the meaning of the current Sugar zoom level?
8. Can this be done with less chrome?
9. Which human capability does the interaction require: selection, activation,
   reading, writing, navigation, pointer control, or something else?
10. Does the interaction accidentally require knowledge Aspartame has not given
    a first-time user an opportunity to discover?

If the answers are unclear, perform archaeology and runtime observation first.
A source diff is not evidence that a design problem exists.

## Reference modernization: the Frame clock

The Frame clock is the reference example for an Aspartame-compatible
modernization:

- Old Sugar lacked a clock in this surface.
- Modern users reasonably expect time to be globally available.
- The clock was added inside the existing Sugar Frame/navigation toolbar.
- It is centered, small, passive, and useful across Activities.
- It does not create a panel, taskbar, status bar, indicator area, or new
  permanent chrome.

The clock must remain a clock, not grow weather, battery, network, CPU, date,
notifications, or other status-bar responsibilities.

## Spatial meanings

Sugar’s zoom levels are semantic places, not merely alternate application
layouts. Home, Activity, Group, Neighborhood, and Journal should retain their
meaning. A new control belongs in the place whose concept it serves; it should
not be duplicated globally because global placement is convenient.

Likewise, an Activity’s running state, color, resume behavior, and Journal
identity are part of the Activity model. Conventional applications can be
integrated underneath that model, but their ordinary window-management
assumptions must not silently replace it.

## Progressive capability

The primary path should remain understandable without Linux expertise or even
prior GUI expertise. Deeper capability should remain available through palettes,
inspection, Activities, terminal tools, Python, and conventional
filesystem/network interfaces. Simplifying the first action must not remove the
underlying capability.

Aspartame should be able to introduce the computer itself. First-use teaching
may use spoken instruction, symbolic imagery, animation, and direct cause/effect
to introduce pointer movement, selection, activation, typing, scrolling, and
other interaction concepts without requiring literacy first. Teaching narration
must be separable from persistent spoken-text/screen-reader capability.

A pre-literate child and a blind adult may require the same spoken-text or
semantic-navigation capability for different reasons. The system should not need
to classify either person to provide it, and it must not speak to either in a
patronizing special-mode voice.

## Color grammar

Aspartame's default machine duotone is orange/blue, especially for two-sided
relationships such as future Chirality. Orange and blue are peers, not good/bad
or primary/secondary. Hue is supplemental: position, glyph, labels, spoken
semantics, focus, and bindings must carry the same meaning when color cannot.
XOColor continues to identify the person; orange/blue is machine grammar.

## Upstream reference

Use the Sugar Labs upstream design/HIG material and current shell/toolkit source
as references. The repository’s [Sugar development map](SUGAR-DEVELOPMENT.md)
and [styling map](SUGAR-STYLING.md) identify which behavior is actually present
in this Aspartame runtime. When upstream documentation and runtime behavior
differ, record the difference and investigate before changing it.
