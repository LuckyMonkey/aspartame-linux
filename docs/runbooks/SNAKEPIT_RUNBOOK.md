# Snakepit qualification runbook

**Status: planned; implementation has not begun.**

This runbook records the intended boundary before code exists so future autonomous work does not turn `reverse package manager` into six projects wearing a trench coat.

## Purpose

Snakepit answers a stronger question than `did dependency resolution succeed?`:

> **Can this software actually run in an Aspartame environment, why or why not, and what did we learn when we tried?**

Snakepit may delegate ordinary dependency solving, environment construction, and package installation to existing tools. Its distinctive responsibility is qualification feedback and preserved compatibility knowledge.

## Core loop

```text
request software
      |
existing compatibility evidence?
      |
choose smallest plausible environment
      |
resolve/install
      |
exercise real workflow
      |
    worked?
    /    \
  yes     no
   |       |
record    classify failure
recipe       |
   |      smallest remediation
   |          |
   +------> retest
```

Installation success never implies operational success.

## Runtime minimization

Aspartame intentionally minimizes language runtimes and Python interpreter proliferation. Snakepit must not default to `one application, one arbitrary Python forever` merely because isolation makes that easy.

Prefer the newest already-qualified common runtime that satisfies the corpus. Introduce an older/alternate interpreter only when demonstrated compatibility requires it. Track why it exists and which qualified software still depends on it. A future qualification pass may collapse applications upward and retire a compatibility runtime.

The system Python is protected substrate, not a dumping ground for arbitrary application dependencies.

## Wong-Baker compatibility

Wong-Baker is a human-readable compatibility/pain projection backed by structured evidence. It is not a review score and must not replace the underlying facts.

A qualification record should be able to explain at least:

```text
software + version
Aspartame target
Python interpreter
Python dependencies and pins
native dependencies / ABI requirements
runtime/display/network/storage requirements
patches or shims
launch method
qualification workflow
observed result
failure cause when known
remediation attempts
Wong-Baker projection
evidence/provenance
```

Do not invent a precise Wong-Baker level when evidence is incomplete. Unknown is a valid state.

## Failure taxonomy

Initial investigation may classify failures such as interpreter incompatibility, Python dependency conflict, inaccurate metadata, missing native library, native ABI mismatch, GUI/display/backend requirement, permission/policy failure, packaging defect, upstream application defect, or unknown.

The taxonomy exists to guide investigation, not to force every failure into a premature category.

## Agents

Agents may inspect tracebacks, compare successful and failing environments, propose pins, select alternate interpreters, build patches, search upstream history, and generate candidate remediation.

Agents do **not** declare software qualified. A deterministic harness or explicitly documented human workflow demonstrates the claimed operation.

> **AI investigates. Reality judges.**

Do not repeatedly spend inference rediscovering a solved compatibility problem. Preserve a verified recipe and reuse it until a relevant environmental change invalidates its evidence.

## First implementation slice

Do not begin with a universal resolver, capability marketplace, compatibility cloud, distributed worker fleet, or AI remediation service.

Start with one real Python application and one bounded principal workflow:

1. define the requested software/version;
2. inspect declared requirements;
3. choose a candidate interpreter/environment;
4. install without contaminating system Python;
5. run a meaningful probe/workflow;
6. record success or exact failure;
7. if failure is bounded, make one remediation and retest;
8. emit an explainable qualification record;
9. repeat with a second application that creates an interpreter/dependency tension.

The first milestone is not `many packages`. It is **one complete explainable loop**.

## Minimal / server / desktop targets

Qualification must name the target rather than treating Aspartame as one undifferentiated environment.

- `aspartame-minimal-x86`: no Sugar or GTK requirement; ideal baseline/container specimen for CLI and service-capable Python software.
- `aspartame-server`: headless server profile including Django/API/admin capability where defined.
- desktop Aspartame: Sugar/GTK graphical capabilities and Activity integration.

A package may qualify for one target and be irrelevant or unsupported on another.

## Research corpus

Long term, Snakepit may maintain reproducible evidence across software version x Python version x dependency/native environment x Aspartame target. New Python and package releases create new qualification work. The valuable output is the compatibility corpus, diagnosed failures, remediation recipes, and upstreamable fixes—not endless Snakepit feature growth.

Useful research questions include which applications survive a new interpreter release, which dependencies cause the largest compatibility cliffs, where declared metadata differs from observed behavior, and which remediations can be safely automated.

## Non-goals

Snakepit is not required to make every Python program work, replace pacman, replace pip/uv/conda/mamba merely for ownership, hide native Linux dependencies, or call arbitrary software supported after a successful install.

The owner may always leave the qualified path and use the underlying Arch system. `Unqualified` means Aspartame does not currently make a compatibility promise; it does not mean forbidden.

## Documentation rule

Every compatibility intervention that becomes part of a qualified recipe must leave receipts: what changed, why, evidence, rejected attempts where useful, remaining constraints, and how to reproduce the qualification.
