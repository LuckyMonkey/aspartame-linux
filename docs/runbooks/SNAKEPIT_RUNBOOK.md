# Snakepit qualification runbook

**Status: planned; implementation has not begun.**

This runbook records the intended boundary before code exists so future autonomous work does not turn `reverse package manager` into six projects wearing a trench coat.

## Purpose

Snakepit answers a stronger question than `did dependency resolution succeed?`:

> **Can this software actually run in an Aspartame environment, why or why not, and what did we learn when we tried?**

Snakepit still performs package-manager work: select software, inspect requirements, choose an environment, resolve/install dependencies, and manage the resulting installation. Its distinguishing behavior is that the transaction does not conceptually end at `installed successfully`. It checks back against reality.

Package managers resolve dependencies. Snakepit also resolves **failures**.

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
record    why?
recipe     |
   |    classify observed failure
   |       |
   |    smallest remediation
   |       |
   +----> retest
            |
        preserve result
```

Installation success never implies operational success. Failure is useful state when it is reproducible and recorded.

## Capability model

Snakepit uses the same capability question as Aspartame's human interface:

> **Can this participant use the capabilities required by this environment?**

For software, capabilities may include a Python interpreter range, package/API version, ABI, native library, GUI/display backend, network/storage service, permission, launch contract, or known source patch.

A failure should become a capability gap when evidence supports that conclusion. Do not label software simply `bad` or `incompatible` when the useful fact is `requires Python 3.12`, `fails against ABI X`, or `needs patch Y`.

After remediation, retest. Capability is demonstrated, not presumed.

## Runtime minimization

Aspartame intentionally minimizes language runtimes and Python interpreter proliferation. Snakepit must not default to `one application, one arbitrary Python forever` merely because isolation makes that easy.

Prefer the newest already-qualified common runtime that satisfies the corpus. Introduce an older/alternate interpreter only when demonstrated compatibility requires it. Track why it exists and which qualified software still depends on it. A future qualification pass may collapse applications upward and retire a compatibility runtime.

The system Python is protected substrate, not a dumping ground for arbitrary application dependencies.

This is how Snakepit can make Python version fragmentation less visible to the user without pretending incompatible interpreter versions are magically compatible. The user asks for software; Snakepit owns the ugly question of which known environment actually makes it work.

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

The face or rating is the projection; the evidence is authoritative. Do not invent a precise Wong-Baker level when evidence is incomplete. Unknown is a valid state.

## Failure taxonomy

Initial investigation may classify failures such as interpreter incompatibility, Python dependency conflict, inaccurate metadata, missing native library, native ABI mismatch, GUI/display/backend requirement, permission/policy failure, packaging defect, upstream application defect, or unknown.

The taxonomy exists to guide investigation, not to force every failure into a premature category.

Declared metadata and observed compatibility are separate facts. An upstream package may claim a broad interpreter range while qualification demonstrates a narrower one. Preserve both rather than silently rewriting history.

## Agents and the enrichment center

A future Snakepit laboratory may use a small controller/VPS to schedule disposable workers across a version/environment matrix. Workers should be replaceable and isolated; do not assume one long-lived VPS must directly execute every specimen.

Agents may inspect tracebacks, compare successful and failing environments, propose pins, select alternate interpreters, build patches, search upstream history, and generate candidate remediation.

Agents do **not** declare software qualified. A deterministic harness or explicitly documented human workflow demonstrates the claimed operation.

> **AI investigates. Reality judges.**
>
> **The model does not declare compatibility. The test chamber does.**

Do not repeatedly spend inference rediscovering a solved compatibility problem. A successful investigation should become durable compatibility knowledge: preserve a verified recipe and reuse it until a relevant environmental change invalidates its evidence.

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

- `aspartame-minimal-x86`: container-oriented Python substrate with no Sugar or GTK requirement; ideal baseline/test-chamber specimen for CLI and service-capable Python software.
- `aspartame-server`: headless server profile including Django/API/admin capability where defined.
- desktop Aspartame: Sugar/GTK graphical capabilities and Activity integration.

A package may qualify for one target and be irrelevant or unsupported on another.

Django is a useful demonstration specimen, not a declaration that Django is universally superior. The server profile should be able to explain exactly why its Django stack works: interpreter, dependencies, native requirements, pins, patches, target, and qualification evidence.

## Research corpus

Long term, Snakepit may maintain reproducible evidence across:

`software x software version x Python version x dependency/native environment x Aspartame target`

Every axis moves. New Python releases, dependency changes, native ABI transitions, and new Python software naturally create new qualification work.

The durable output is not perpetual Snakepit feature growth. It is the compatibility corpus, diagnosed failures, remediation recipes, reproducible environments, upstreamable fixes, and longitudinal measurements.

Useful research questions include which applications survive a new interpreter release, which dependencies cause the largest compatibility cliffs, where declared metadata differs from observed behavior, which remediations can be safely automated, and which compatibility runtimes can be retired after the corpus moves forward.

A failed qualification is not wasted compute when it records exact environment, observed failure, cause when known, and whether alternate configurations succeed.

## Qualification and upstream repair

A healthy loop is:

```text
observe incompatibility
      |
determine smallest cause
      |
propose remediation
      |
verify across relevant matrix
      |
preserve Aspartame recipe
      |
upstream fix when appropriate
      |
new upstream release
      |
requalify and remove local repair when possible
```

Local patches are evidence and containment, not trophies. Prefer retiring a local patch when upstream behavior makes it unnecessary.

## Non-goals

Snakepit is not required to make every Python program work, replace pacman, replace pip/uv/conda/mamba merely for ownership, hide native Linux dependencies, or call arbitrary software supported after a successful install.

Unknown software may enter investigation because `anything is possible`; qualification is earned by evidence.

The owner may always leave the qualified path and use the underlying Arch system. `Unqualified` means Aspartame does not currently make a compatibility promise; it does not mean forbidden.

If someone asks Snakepit to install a whole alternate desktop environment, first ask what capability they actually want. Aspartame does not need to qualify a second operating environment merely because Arch can install one.

## Documentation rule

Every compatibility intervention that becomes part of a qualified recipe must leave receipts: what changed, why, evidence, rejected attempts where useful, remaining constraints, and how to reproduce the qualification.

If you swing a hammer, document it.
