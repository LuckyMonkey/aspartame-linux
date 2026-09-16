# 📚 Aspartame runbooks:

> Design notes are grouped by implementation status so a future reader can
> tell **current behavior**, **verification procedure**, and **future ideas**.

## Current visual reference

![Sugar Home](../screenshots/home-v0.0.15.png)

![Activity Manager](../screenshots/activity-manager-v0.0.15.png)

![Count Activity](../screenshots/count-v0.0.14.png)

The images are reference snapshots from the QEMU development VM. See the screenshot gallery for capture details.

## Runbooks

- [Snakepit](SNAKEPIT_RUNBOOK.md) — **planned, not implemented**; Python compatibility qualification, Wong-Baker evidence, runtime minimization, and the resolve → run → observe → remediate → retest loop
- [Count Activity](COUNT_ACTIVITY_RUNBOOK.md) — behavior and data model
- [Universal Help](UNIVERSAL_HELP_RUNBOOK.md) — contextual help system
- [Scale Activity](SCALE_ACTIVITY_RUNBOOK.md) — future activity direction
- [Pets](../planned/ASPARTAME_PETS_RUNBOOK.md) — planned/maybe/future idea only
- [GTK4 modernization](../sugar-modernization/README.md) — active conversion runbooks

<details>
<summary>🧭 How to use a runbook</summary>

1. Read the purpose and non-goals first.
2. Follow the primary interaction model before adding controls.
3. Record evidence at the boundary the runbook names.
4. Update the owning status table and screenshot/log links.
5. Do not turn a planned runbook into implied implementation. Runtime evidence decides what exists.

</details>
