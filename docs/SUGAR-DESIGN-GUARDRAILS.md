# Sugar design guardrails

This document is the design constitution for Aspartame shell work. Aspartame
modernizes Sugar; it does not redesign Sugar into a conventional desktop.

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
6. Does color retain semantic meaning?
7. Does this preserve the meaning of the current Sugar zoom level?
8. Can this be done with less chrome?

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

The primary path should remain understandable without Linux expertise. Deeper
capability should remain available through palettes, inspection, Activities,
terminal tools, and conventional filesystem/network interfaces. Simplifying the
first action must not remove the underlying capability.

## Upstream reference

Use the Sugar Labs upstream design/HIG material and current shell/toolkit source
as references. The repository’s [Sugar development map](SUGAR-DEVELOPMENT.md)
and [styling map](SUGAR-STYLING.md) identify which behavior is actually present
in this Aspartame runtime. When upstream documentation and runtime behavior
differ, record the difference and investigate before changing it.
