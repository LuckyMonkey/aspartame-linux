# Autonomous contribution runbook

Aspartame is developed by humans and long-running coding agents. That is useful only if autonomous work remains reviewable, evidence-led, and capable of stopping.

> **If you swing a hammer, document it.**

The purpose of this runbook is not to make agents timid. It is to prevent a reasonable local choice from becoming accidental architecture merely because later tests, documentation, and agents inherited it.

## Prime directive: progress over saturation

The goal is not to maximize commit count, infrastructure, abstraction, hardening, or local completeness.

> **Increase verified user-visible capability while minimizing new architectural surface area.**

During GTK4 modernization, ask before extending a subsystem:

> **Does this close a real GTK3 -> GTK4 behavioral gap, or am I making an existing implementation more elaborate?**

A bug may be fixed later. A subsystem-sized rabbit hole created around one strange edge case is much more expensive to unwind.

## The bounded loop

For parity and qualification work, use this loop:

```text
reproduce a user-visible failure
        |
identify the narrowest root cause
        |
make the minimum coherent fix
        |
prove the previously failing workflow
        |
check the nearest regression boundary
        |
document the receipts
        |
LEAVE THAT SUBSYSTEM
        |
next failing workflow
```

Once the claimed workflow passes, stop improving that subsystem unless a new independently reproduced defect requires returning to it.

A discovered problem is allowed to remain open.

## Qualification deck discipline

Do not treat `finish GTK4` as an infinitely divisible task. Treat the GTK4 shell as a qualification platform and burn down a finite deck of representative user-visible workflows.

During migration:

1. F7 enters stable GTK3 Sugar, the executable behavioral reference.
2. Perform the normal workflow there.
3. F8 enters the GTK4 candidate.
4. Repeat the same workflow.
5. A meaningful difference is a parity gap.
6. Make the smallest fix that closes that gap.
7. Repeat F7 -> F8 and then leave the subsystem.

Behavioral parity, not launch count, is the GTK3 retirement meter. Passing unit tests, starting a process, or displaying a window does not establish parity.

Do not repurpose F7/F8 for Chirality until the migration gate is complete.

## Finding defects without manufacturing work

When asked to find and fix a bounded number of defects, the number is a hard ceiling. Use the product and discover failures through real workflows rather than mining grep output for work-shaped objects.

Before coding each candidate, record:

```text
DEFECT:
USER-VISIBLE REPRODUCTION:
EXPECTED BEHAVIOR:
ACTUAL BEHAVIOR:
ROOT CAUSE:
SMALLEST FIX:
FILES EXPECTED TO CHANGE:
RABBIT-HOLE RISK:
```

A qualifying defect is reproducible, externally observable or behavior-affecting, independent of the other selected defects, and narrow enough for a reviewable repair. Stale comments, formatting, naming, lint, dead code, speculative races, aesthetic preferences, and abstract missing parity do not count.

If investigation expands materially beyond the expected root cause, write:

`DEFERRED — exceeds bounded fix pass`

Then choose another defect. Do not convert discovery into a blood oath.

If the pass says five defects, stop after five. Do not begin a sixth because the fifth exposed something interesting.

## Architecture restraint

Do not create a new framework, daemon, generalized abstraction, compatibility layer, package architecture, compositor redesign, input architecture, lifecycle architecture, or mass conversion merely to close a bounded defect unless the task explicitly requires architectural work and evidence shows the architecture is unavoidable.

Distinguish:

- **actually wrong** — runtime evidence contradicts required behavior;
- **different implementation choice** — another contributor would have written it differently;
- **scaffolding** — temporary machinery supporting migration;
- **doctrine** — an intentional product invariant with documented rationale.

Do not rewrite another contributor's working choice merely to make it look like your preferred implementation.

## Receipts are mandatory

For a meaningful intervention, leave enough information for the next human or agent to answer:

```text
what changed?
why?
what evidence showed the old behavior was wrong?
what was tried?
what was rejected or reverted?
what proves the new behavior?
what remains strange or incomplete?
how can I reproduce the proof?
```

Runtime evidence outranks prose. Documentation does not make a decision sacred; it makes disagreement intelligent.

Tests and documentation must not launder an accidental choice into doctrine. When evidence changes, update the conclusion.

## Native-layer bugs belong at the native layer

Do not paper over a lower-layer defect with increasingly elaborate Python if the root cause is demonstrably below Python. The SugarExt F-key incident is the reference example: stale X11 passive grabs were ultimately a C-level lifecycle defect, not a reason to invent a Python input architecture.

Likewise, do not confuse neighboring failures merely because they share a symptom. Casilda Activity keyboard delivery and stale shell F-key grabs were separate bugs and required separate evidence and fixes.

## Activity claims

Use the established classifications precisely:

- **FULL PORT** — core workflow, persistence/object behavior, and normal interaction demonstrated against the reference.
- **FUNCTIONAL PORT** — principal offline workflow usable; some breadth, collaboration, or persistence intentionally reduced.
- **COVERAGE IMPLEMENTATION** — native GTK4 surface primarily exercises registry/rendering/input/lifecycle.
- **PLACEHOLDER** — launchable stub; never counts toward retirement.

Prefer promotion based on real workflow and Journal roundtrip evidence rather than the number of Activities that launch.

## Handoff rule

Before ending a bounded autonomous run:

1. run focused tests and the nearest representative qualification workflows;
2. verify both migration Spaces remain healthy when relevant;
3. verify physical F7/F8 and Activity keyboard paths when the work touches those boundaries;
4. reconcile documentation only where behavior or status actually changed;
5. leave the worktree/repository state explicit;
6. report exact commits, tests, evidence, remaining debt, and deferred discoveries;
7. stop.

The desired rhythm is:

> **fix -> prove -> document -> get out.**

The enrichment center is allowed to be productive. It is not allowed to become self-justifying.