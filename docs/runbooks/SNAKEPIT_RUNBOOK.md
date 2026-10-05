# 🐍 Snakepit qualification runbook

**Status: v0 qualification loop implemented; interpreter capability preflight is
live and the qualification corpus is still small.**

This runbook records the intended boundary before code exists so future autonomous work does not turn `reverse package manager` into six projects wearing a trench coat.

## 🎯 Purpose

`Reverse package manager` is deliberately a loaded description. A conventional package manager begins with a chosen package and asks:

> What does this package require?

Snakepit begins from the opposite direction:

> **I want this Python software or capability. Where can it safely and correctly exist on this machine, and can Aspartame prove that environment works?**

Snakepit therefore answers a stronger question than `did dependency resolution succeed?`:

> **Can this software actually run in an Aspartame environment, why or why not, and what did we learn when we tried?**

Snakepit still performs package-manager work: select software, inspect requirements, choose an environment, resolve/install dependencies, and manage the resulting installation. It may delegate dependency solving and installation to existing machinery. Its distinguishing behavior is that the transaction does not conceptually end at `installed successfully`. It checks back against reality.

Package managers resolve dependencies. Snakepit also resolves **where software can exist**, investigates **why it failed**, and preserves what was learned.

## 🔄 Direction of resolution

```text
desired Python application/capability
          │
          ▼
   inspect constraints
          │
          ▼
Python versions / ABI / GUI / native libs / conflicts
          │
          ▼
choose or construct viable isolated environment
          │
          ▼
resolve/install using appropriate existing tools
          │
          ▼
 exercise a real workflow
          │
          ▼
 explain success or failure
```

A later discovery layer may map a human capability request such as `edit EXIF` to candidate Python software, but that is not required for Snakepit v0. Do not build app discovery, a capability marketplace, or an AI recommendation system before the environment-resolution loop exists.

## 🧪 Core loop

```text
request software
      │
existing compatibility evidence?
      │
choose smallest plausible environment
      │
resolve/install
      │
exercise real workflow
      │
    worked?
    /    \
  yes     no
   │       │
record    why?
recipe     │
   │    classify observed failure
   │       │
   │    smallest remediation
   │       │
   └────> retest
            │
        preserve result
```

Installation success never implies operational success. Failure is useful state when it is reproducible and recorded.

## 🧱 V0 contract

> **Snakepit does not install arbitrary packages into system Python. Snakepit finds or constructs a Python environment in which the requested software can correctly exist—and explains every decision it made.**

The system Python is a protected substrate and a constraint, not the destination.

The core question is:

> **Where can this safely exist?**

An explainable result should identify why an interpreter was selected, why isolation was necessary, what dependencies/native capabilities were required, what was changed, what was observed, and how to repeat the qualification.

## 🧩 Capability model

Snakepit uses the same capability question as Aspartame's human interface:

> **Can this participant use the capabilities required by this environment?**

For software, capabilities may include a Python interpreter range, package/API version, ABI, native library, GUI/display backend, network/storage service, permission, launch contract, or known source patch.

A failure should become a capability gap when evidence supports that conclusion. Do not label software simply `bad` or `incompatible` when the useful fact is `requires Python 3.12`, `fails against ABI X`, or `needs patch Y`.

After remediation, retest. Capability is demonstrated, not presumed.

```text
package requires capability
          │
          ▼
environment provides it? ── yes ──> exercise workflow
          │ no
          ▼
 identify exact gap
          │
          ▼
provide / translate / patch / choose another runtime
          │
          └────────────────────────> RETEST
```

## 🐍 Runtime minimization

Aspartame intentionally minimizes language runtimes and Python interpreter proliferation. Snakepit must not default to `one application, one arbitrary Python forever` merely because isolation makes that easy.

Prefer the newest already-qualified common runtime that satisfies the corpus. Introduce an older/alternate interpreter only when demonstrated compatibility requires it. Track why it exists and which qualified software still depends on it. A future qualification pass may collapse applications upward and retire a compatibility runtime.

Multiple Python versions are intentional compatibility tools, not an excuse for unmanaged proliferation: newest/common preferred; older compatibility runtime justified by evidence; truly legacy state quarantined.

The system Python is protected substrate, not a dumping ground for arbitrary application dependencies. Isolation may use venv/uv/pipx-like prefixes or other appropriate mechanisms; the exact tool is subordinate to the explainable environment contract.

This is how Snakepit can make Python version fragmentation less visible to the user without pretending incompatible interpreter versions are magically compatible. The user asks for software; Snakepit owns the ugly question of which known environment actually makes it work.

## 🙂 Wong-Baker compatibility

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

The face or rating is the projection; the evidence is authoritative. Do not invent a precise Wong-Baker level when evidence is incomplete. **Unknown is a valid state.**

## 🔬 Failure taxonomy

Initial investigation may classify failures such as interpreter incompatibility, Python dependency conflict, inaccurate metadata, missing native library, native ABI mismatch, GUI/display/backend requirement, permission/policy failure, packaging defect, upstream application defect, or unknown.

The taxonomy exists to guide investigation, not to force every failure into a premature category.

Declared metadata and observed compatibility are separate facts. An upstream package may claim a broad interpreter range while qualification demonstrates a narrower one. Preserve both rather than silently rewriting history.

## 🤖 Agents and the enrichment center

A future Snakepit laboratory may use a small controller/VPS to schedule disposable workers across a version/environment matrix. Workers should be replaceable and isolated; do not assume one long-lived VPS must directly execute every specimen. This is later infrastructure, not v0.

```text
             🧠 controller / scheduler
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      worker A      worker B      worker C
      Py 3.x        Py 3.y        Py 3.z
          │            │            │
          └────── qualification ─────┘
                       │
                       ▼
             evidence / recipes
```

Agents may inspect tracebacks, compare successful and failing environments, propose pins, select alternate interpreters, build patches, search upstream history, and generate candidate remediation.

Agents do **not** declare software qualified. A deterministic harness or explicitly documented human workflow demonstrates the claimed operation.

> **AI investigates. Reality judges.**
>
> **The model does not declare compatibility. The test chamber does.**

Do not repeatedly spend inference rediscovering a solved compatibility problem. A successful investigation should become durable compatibility knowledge: preserve a verified recipe and reuse it until a relevant environmental change invalidates its evidence.

The economic value, if this ever becomes a hosted or funded service, is not “AI ran a command.” It is that one expensive investigation can become reusable compatibility knowledge for many later installations: **reason when needed, verify mechanically, preserve the recipe, reinvestigate only when relevant conditions change.**

## 🥇 First implementation slice

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

The second specimen now exercises a bounded dependency-tension failure. The
fixture declares `aspartame-tension-core>=1,<2` in `pyproject.toml` while its
requirements file asks for `aspartame-tension-core>=2,<3`. Snakepit detects the
empty intersection before creating a venv or contacting a package index and
preserves both declarations in the qualification record. This is evidence of
safe failure and explainability, not yet a claim that Snakepit can solve every
dependency graph.

### Aspartame v0 command

The v0 implementation is `scripts/snakepit.py`. It qualifies the existing
standard-library management service without touching system Python and can
select among repeated `--python` candidates:

```sh
make snakepit-qualify
```

For a real interpreter matrix, repeat the option. Snakepit records every
candidate and selects the newest one whose declared `requires-python` is
compatible:

```sh
python3 scripts/snakepit.py qualify \
  --software example \
  --source ./example \
  --environment /tmp/example-snakepit \
  --launchable \
  --python /usr/bin/python3.14 \
  --python /usr/bin/python3.12 \
  --command python -m example_probe
```

The command creates an isolated environment, records the source and declared
requirements, runs `management/test_server.py` through that environment, and
writes `reports/python/aspartame-management.json`. The default environment is
under `/tmp`; set `SNAKEPIT_ENVIRONMENT` and `SNAKEPIT_RECORD` to choose other
paths. A non-empty requirements file is installed only when
`--install-requirements` is supplied, making network/package changes explicit.

Use `--launchable` only when the qualified workflow is also the application
entry point you intend to hand to Activity Manager. A passing record then
contains an explicit `launch` contract. Re-run that exact contract without
reinstalling or mutating the environment with:

```sh
python3 scripts/snakepit.py launch \
  --record reports/python/aspartame-management.json
```

Records without `--launchable`, failed records, and records with no surviving
environment are intentionally not launchable. Qualification and launch remain
separate so Activity Manager never turns an installation check into a false
application entry.

To publish a passing record to the GTK4 Activity Manager's user-owned record
directory, use the explicit registration step:

```sh
python3 scripts/snakepit.py register \
  --record reports/python/aspartame-management.json \
  --directory "$ASPARTAME_SNAKEPIT_RECORD_DIR"
```

Registration validates the schema, `PASS` status, launch command, source
directory, and environment interpreter before atomically replacing the
record's name-derived JSON file. It does not install packages or modify
system Python. The manager then presents the record as `Snakepit Python` with
`Launch`; failed or incomplete records are not registered.

The packaged launcher was also exercised on the standalone ISO against its
installed source with an unavailable Python 3.13 candidate followed by the
guest Python 3.14 candidate; the desktop-target record for the final rebuilt
image is `reports/python/packaged-snakepit-20261002-v5.json`.

The negative capability path is preserved in
`reports/python/future-python-capability-gap-20261002.json`: the fixture
requires Python `>=99`, so the current Python 3.12 interpreter is rejected
before an environment is created. This is an intentional qualification
failure, not a broken test.

The dependency-tension specimen is reproduced with:

```sh
make snakepit-dependency-tension
```

It intentionally exits with qualification status `FAIL`, writes
`reports/python/dependency-tension-20261002.json`, and must leave
`/tmp/aspartame-snakepit-dependency-tension` absent. The direct-constraint
preflight is deliberately conservative; unsupported packaging syntax remains
for the package resolver rather than being guessed at.

The passing pair is now also available as an offline qualification fixture:

```sh
make snakepit-dependency-pair
```

The left and right applications install local `snakepit-tension-core` 1.0.0
and 2.0.0 wheels into separate environments, then import and report the
selected provider. Their records are
`reports/python/dependency-pair-left-20261002.json` and
`reports/python/dependency-pair-right-20261002.json`. This proves that
different compatible dependency environments can coexist without contaminating
system Python; it does not yet qualify arbitrary remote package graphs. The
next runtime milestone is Activity Manager consuming these explicit launch
contracts for a real user-facing Python application.

The GTK4 Activity Manager now provides that bounded bridge. It reads JSON
records from the user-owned `ASPARTAME_SNAKEPIT_RECORD_DIR` (the GTK4 session
defaults this to its state directory), labels rows `Snakepit Python`, and
marks only a passing record with a valid environment and launch contract as
qualified and launchable. A qualified row offers `Launch`; failed or
incomplete records remain visible as `Not ready` and are never removable.
Launches inherit the recorded environment boundary (`PATH`, `VIRTUAL_ENV`,
`PYTHONNOUSERSITE`, and `PYTHONPATH`) and start as a separate process. This is
explicit v0 contract integration, not a universal package resolver or a
security sandbox.

The JSON record is the authority: it contains the interpreter, venv isolation
probe, dependency declaration, exact workflow command, output, exit status,
timestamps, and failure reason. A passing record proves this one workflow for
the named target; it does not qualify arbitrary Python software or the Sugar
desktop runtime.

Qualification and launch now own each workflow as a process group. If a
workflow times out, Snakepit sends termination to the group and escalates to a
bounded kill before returning the failure, so helper processes cannot survive
behind the Activity Manager or a qualification shell. This is lifecycle
containment, not a security sandbox; the runtime contract still records that
network access is not automatically isolated.

The preflight also reads `project.requires-python` when present. A compatible
specifier is recorded as a satisfied interpreter capability; an incompatible
specifier fails before venv creation or dependency installation and preserves
the reason in the JSON record. Unsupported specifier syntax remains an
explicit unknown rather than being silently treated as compatible. The
future-interpreter fixture can therefore be qualified as a real capability gap
instead of being mistaken for a package installation failure. The passing
dependency pair above is the second-specimen isolation proof.

The CLI calls the specimen `--software` rather than `--name` because GTK's
startup argument parser consumes the generic `--name` option while Sugar's
image `sitecustomize` is loading.

## 🧰 Minimal / server / desktop targets

Qualification must name the target rather than treating Aspartame as one undifferentiated environment.

- `aspartame-minimal-x86`: container-oriented Python substrate with no Sugar or GTK requirement; ideal baseline/test-chamber specimen for CLI and service-capable Python software.
- `aspartame-server`: headless server profile including Django/API/admin capability where defined.
- desktop Aspartame: Sugar/GTK graphical capabilities and Activity integration.

A package may qualify for one target and be irrelevant or unsupported on another.

Django is a useful demonstration specimen, not a declaration that Django is universally superior. The server profile should be able to explain exactly why its Django stack works: interpreter, dependencies, native requirements, pins, patches, target, and qualification evidence.

```text
🧪 minimal   → prove the Python substrate
🌐 server    → prove serious Python services / Django
🍬 desktop   → prove the complete human-facing computer
```

## 📚 Research corpus

Long term, Snakepit may maintain reproducible evidence across:

`software x software version x Python version x dependency/native environment x Aspartame target`

Every axis moves. New Python releases, dependency changes, native ABI transitions, and new Python software naturally create new qualification work.

The durable output is not perpetual Snakepit feature growth. It is the compatibility corpus, diagnosed failures, remediation recipes, reproducible environments, upstreamable fixes, and longitudinal measurements.

Useful research questions include which applications survive a new interpreter release, which dependencies cause the largest compatibility cliffs, where declared metadata differs from observed behavior, which remediations can be safely automated, and which compatibility runtimes can be retired after the corpus moves forward.

A failed qualification is not wasted compute when it records exact environment, observed failure, cause when known, and whether alternate configurations succeed.

## 🩹 Qualification and upstream repair

```text
observe incompatibility
      │
determine smallest cause
      │
propose remediation
      │
verify across relevant matrix
      │
preserve Aspartame recipe
      │
upstream fix when appropriate
      │
new upstream release
      │
requalify and remove local repair when possible
```

Local patches are evidence and containment, not trophies. Prefer retiring a local patch when upstream behavior makes it unnecessary.

## 🚧 Non-goals

Snakepit is not required to make every Python program work, replace pacman, replace pip/uv/conda/mamba merely for ownership, hide native Linux dependencies, or call arbitrary software supported after a successful install.

It is also not initially an app-discovery engine, capability recommendation service, universal native dependency bridge, distributed compatibility cloud, Activity marketplace, or AI shell. Those may be separately justified later; none are prerequisites for the first explainable environment-resolution loop.

Unknown software may enter investigation because `anything is possible`; qualification is earned by evidence.

The owner may always leave the qualified path and use the underlying Arch system. `Unqualified` means Aspartame does not currently make a compatibility promise; it does not mean forbidden.

If someone asks Snakepit to install a whole alternate desktop environment such as GNOME, first ask what capability they actually want. Aspartame does not need to qualify a second operating environment merely because Arch can install one. If the owner truly wants it, the underlying machine remains theirs.

## 🧾 Documentation rule

Every compatibility intervention that becomes part of a qualified recipe must leave receipts: what changed, why, evidence, rejected attempts where useful, remaining constraints, and how to reproduce the qualification.

> **If you swing a hammer, document it.**
