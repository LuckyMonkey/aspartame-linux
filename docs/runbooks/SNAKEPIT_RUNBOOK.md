# Snakepit qualification runbook

**Status: planned; implementation has not begun.**

This runbook records the intended boundary before code exists so future autonomous work does not turn `reverse package manager` into six projects wearing a trench coat.

## Purpose

`Reverse package manager` is deliberately a loaded description. A conventional package manager begins with a chosen package and asks:

> What does this package require?

Snakepit begins from the opposite direction:

> **I want this Python software or capability. Where can it safely and correctly exist on this machine, and can Aspartame prove that environment works?**

Snakepit therefore answers a stronger question than `did dependency resolution succeed?`:

> **Can this software actually run in an Aspartame environment, why or why not, and what did we learn when we tried?**

It may delegate dependency solving and installation to existing machinery. Its distinctive responsibility is environment selection, empirical qualification, failure diagnosis, bounded remediation, and preservation of the recipe/evidence.

Package managers resolve dependencies. Snakepit also resolves **where software can exist** and investigates **why it failed**.

## Direction of resolution

The basic direction is:

```text
desired Python application/capability
          |
inspect constraints
          |
Python versions / ABI / GUI / native libs / conflicts
          |
choose or construct viable isolated environment
          |
resolve/install using appropriate existing tools
          |
exercise a real workflow
          |
explain success or failure
```

A later discovery layer may map a human capability request such as `edit EXIF` to candidate Python software, but that is not required for Snakepit v0. Do not build app discovery, a capability marketplace, or an AI recommendation system before the environment-resolution loop exists.

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

## V0 contract

> **Snakepit does not install arbitrary packages into system Python. Snakepit finds or constructs a Python environment in which the requested software can correctly exist—and explains every decision it made.**

The system Python is a protected substrate and a constraint, not the destination.

The core question is:

> **Where can this safely exist?**

An explainable result should identify why an interpreter was selected, why isolation was necessary, what dependencies/native capabilities were required, what was changed, what was observed, and how to repeat the qualification.

## Capability model

Snakepit uses the same capability question as Aspartame's human interface:

> **Can this participant use the capabilities required by this environment?**

For software, capabilities may include a Python interpreter range, package/API version, ABI, native library, GUI/display backend, network/storage service, permission, launch contract, or known source patch.

A failure should become a capability gap when evidence supports that conclusion. Do not label software simply `bad` or `incompatible` when the useful fact is `requires Python 3.12`, `fails against ABI X`, or `needs patch Y`.

After remediation, retest. Capability is demonstrated, not presumed.

## Runtime minimization

Aspartame intentionally minimizes language runtimes and Python interpreter proliferation. Snakepit must not default to `one application, one arbitrary Python forever` merely because isolation makes that easy.

Prefer the newest already-qualified common runtime that satisfies the corpus. Introduce an older/alternate interpreter only when demonstrated compatibility requires it. Track why it exists and which qualified software still depends on it. A future qualification pass may collapse applications upward and retire a compatibility runtime.

Multiple Python versions are intentional compatibility tools, not an excuse for unmanaged proliferation: newest/common preferred; older compatibility runtime justified by evidence; truly legacy state quarantined.

The system Python is protected substrate, not a dumping ground for arbitrary application dependencies. Isolation may use venv/uv/pipx-like prefixes or other appropriate mechanisms; the exact tool is subordinate to the explainable environment contract.

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

The taxonomy exists to guide investigation, not to force every failure into a premature category. Declared metadata and observed compatibility are separate facts.

## Agents and the enrichment center

A future Snakepit laboratory may use disposable workers across a version/environment matrix, but that is later infrastructure, not v0.

Agents may inspect tracebacks, compare successful and failing environments, propose pins, select alternate interpreters, build patches, search upstream history, and generate candidate remediation.

Agents do **not** declare software qualified. A deterministic harness or explicitly documented human workflow demonstrates the claimed operation.

> **AI investigates. Reality judges.**
>
> **The model does not declare compatibility. The test chamber does.**

Do not repeatedly spend inference rediscovering a solved compatibility problem. A successful investigation should become durable compatibility knowledge: preserve a verified recipe and reuse it until a relevant environmental change invalidates its evidence.

## First implementation slice

Do not begin with a universal resolver, capability marketplace, compatibility cloud, distributed worker fleet, AI remediation service, generalized Activity integration, or a new package ecosystem.

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

The second specimen exists to prove the first design did not merely hard-code one happy path.

## Minimal / server / desktop targets

Qualification must name the target rather than treating Aspartame as one undifferentiated environment.

- `aspartame-minimal-x86`: container-oriented Python substrate with no Sugar or GTK requirement; ideal baseline/test-chamber specimen for CLI and service-capable Python software.
- `aspartame-server`: headless server profile including Django/API/admin capability where defined.
- desktop Aspartame: Sugar/GTK graphical capabilities and Activity integration.

A package may qualify for one target and be irrelevant or unsupported on another.

## Research corpus

Long term, Snakepit may maintain reproducible evidence across:

`software x software version x Python version x dependency/native environment x Aspartame target`

Every axis moves. New Python releases, dependency changes, native ABI transitions, and new Python software naturally create new qualification work.

The durable output is not perpetual Snakepit feature growth. It is the compatibility corpus, diagnosed failures, remediation recipes, reproducible environments, upstreamable fixes, and longitudinal measurements.

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

It is also not initially an app-discovery engine, capability recommendation service, universal native dependency bridge, distributed compatibility cloud, Activity marketplace, or AI shell. Those may be separately justified later; none are prerequisites for the first explainable environment-resolution loop.

Unknown software may enter investigation because `anything is possible`; qualification is earned by evidence.

The owner may always leave the qualified path and use the underlying Arch system. `Unqualified` means Aspartame does not currently make a compatibility promise; it does not mean forbidden.

## Documentation rule

Every compatibility intervention that becomes part of a qualified recipe must leave receipts: what changed, why, evidence, rejected attempts where useful, remaining constraints, and how to reproduce the qualification.

If you swing a hammer, document it.
