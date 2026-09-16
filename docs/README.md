# Project documentation:

Welcome to the long-form project notebook. This folder contains the operating
system doctrine, human-interface guidance, architecture, Sugar interaction
guidance, build procedures, runtime evidence, Activity design runbooks, and
future ideas. The README at the repository root is the visual front door; this
index is the map for engineers, testers, and curious learners.

## Start here:

| Need | Read |
| --- | --- |
| Understand Aspartame itself | [Aspartame doctrine](ASPARTAME-DOCTRINE.md), [Aspartame HIG](ASPARTAME-HIG.md) |
| Understand Sugar design language | [Sugar design guardrails](SUGAR-DESIGN-GUARDRAILS.md), [Chirality](sugar-modernization/ASPARTAME_CHIRALITY.md) |
| Understand future Python qualification | [Snakepit runbook](runbooks/SNAKEPIT_RUNBOOK.md) |
| Build or boot the image | [Building](building.md), [Boot](boot.md), [QEMU](qemu.md) |
| Work on the Sugar shell | [Sugar development](SUGAR-DEVELOPMENT.md), [Sugar styling](SUGAR-STYLING.md) |
| Port an Activity | [Activity contract](ASPARTAME-ACTIVITY-CONTRACT.md), [Activity runbook](sugar-modernization/GTK4_ACTIVITY_RUNBOOK.md), [classification](sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md) |
| Verify GTK4 parity | [Qualification deck](sugar-modernization/QUALIFICATION_DECK.md) (current workflow status), [component status](sugar-modernization/GTK4_STATUS.md), [debugging](sugar-modernization/GTK4_DEBUGGING.md) |
| Find a known GTK4 defect | [Blockers](sugar-modernization/BLOCKERS.md), plus the open findings in the [qualification deck](sugar-modernization/QUALIFICATION_DECK.md) |
| Learn the user-facing model | [Universal Help](UNIVERSAL-HELP.md), [Activity Help catalog](ACTIVITY-HELP-CATALOG.md), [Sugar current state](sugar-current-state.md) |

## Core doctrine:

Aspartame is an opinionated Python computing platform whose graphical desktop is
Sugar. It deliberately minimizes high-level runtimes and uses Python wherever
Python remains an appropriate abstraction, while retaining the native Linux
substrate where it belongs.

The project uses **Capability** as a common design vocabulary for people,
software, and environments. A person is not routed to a separate computer based
on age, literacy, disability, or expertise; the computer provides or teaches the
capabilities needed for the interaction. Likewise, an installed Python package
is not presumed operational merely because dependencies resolved. In both
contexts:

> **Capability is demonstrated, not presumed.**

The first-computer goal follows directly: Aspartame should be usable before a
person can read or already understands a mouse, pointer, selection, clicking, or
typing. It should teach those concepts respectfully through the same semantic
interface used by an experienced or blind adult, without demographic modes.

## Visual evidence:

![GTK4 Home at 1920×1080](../reports/screenshots/sugar-20260915-151748-v0.0.31.png)

![GTK4 Help Activity](../reports/screenshots/sugar-20260915-150938-v0.0.31.png)

Screenshots are paired with runtime logs under `reports/gtk4/`. A picture is a
useful orientation aid, never the sole proof that a lifecycle, input path, or
capability contract works.

## Documentation conventions:

- **Current** means the file describes the present repository and names its
  evidence boundary.
- **Runbook** means an executable procedure or a design contract that can be
  revisited as the system changes.
- **Historical** means the file is retained for incident context and says so
  plainly; it is not silently presented as current behavior.
- **Planned** means an idea or future direction, not an implemented feature.

<details>
<summary>🧭 Browse by subject</summary>

### Doctrine and interface:

[Aspartame doctrine](ASPARTAME-DOCTRINE.md) · [Aspartame HIG](ASPARTAME-HIG.md) ·
[Sugar design guardrails](SUGAR-DESIGN-GUARDRAILS.md) ·
[Chirality](sugar-modernization/ASPARTAME_CHIRALITY.md)

### System and image:

[Architecture](architecture.md) · [Boot](boot.md) · [Building](building.md) ·
[Installer plan](installer-plan.md) · [Networking](networking.md) ·
[Printing](printing.md) · [Packages](packages.md) · [Persistence](persistence.md)

### Sugar and Activities:

[Activities](activities.md) · [Activity sources](ACTIVITY-SOURCES.md) ·
[Activity contract](ASPARTAME-ACTIVITY-CONTRACT.md) · [Icons](icons.md) ·
[Universal Help](UNIVERSAL-HELP.md) · [Neighborhood Board](NEIGHBORHOOD-BOARD.md)

### Modernization:

[GTK4 index](sugar-modernization/README.md) · [Status](sugar-modernization/GTK4_STATUS.md) ·
[Component matrix](sugar-modernization/GTK4_COMPONENT_MATRIX.md) ·
[Journal runbook](sugar-modernization/GTK4_JOURNAL_RUNBOOK.md) ·
[Spaces and Chirality](sugar-modernization/ASPARTAME_CHIRALITY.md)

### Design-desk planning:

[Snakepit (planned)](runbooks/SNAKEPIT_RUNBOOK.md) ·
[Count](runbooks/COUNT_ACTIVITY_RUNBOOK.md) · [Universal Help](runbooks/UNIVERSAL_HELP_RUNBOOK.md) ·
[Scale](runbooks/SCALE_ACTIVITY_RUNBOOK.md) · [Pets (future only)](planned/ASPARTAME_PETS_RUNBOOK.md)

</details>

## Keeping the map healthy:

When a feature changes, update the owning runbook, its evidence link, and this
index if the navigation changes. If you swing a hammer, document what changed,
why, evidence, rejected approaches where useful, what remains strange, and how
to reproduce the result. Run regular regression and “find five” review passes
as maintenance tooling; do not turn any single pass into a permanent milestone
chapter.
