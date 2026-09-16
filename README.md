![Aspartame banner](aspartame.jpg)

### as-part-a-me

> **A Python-first computing platform whose desktop is Sugar.**  
> *a sweeter computer*

Aspartame asks a deliberately unreasonable question: **how much of a complete useful computer can share one approachable high-level language?** The answer is not `everything is literally Python`; Linux, GTK, GLib, libc, drivers, codecs, compositors, and firmware remain native where they should. The experiment is to make Python the common inspectable language wherever a high-level implementation is appropriate.

> **Python all the way down until continuing to use Python would become stupid.**

Sugar is the desktop because it is an unusually Python-heavy, human-centered environment—not because Sugar itself is sacred. Aspartame is the larger experiment. The claim is demonstrated rather than advertised: **the proof boots.**

Aspartame is also intended to be a person's first computer without becoming a computer they later outgrow: simple enough for someone who cannot yet read, capable enough for an expert, and built around the same semantic interface rather than demographic modes.

> **There should be no obvious skill level at which a user has to outgrow Aspartame.**

## Capability is demonstrated, not presumed

Aspartame uses **Capability** as a unifying product concept. For a person: can they select, activate, read or hear information, enter text, navigate, and understand what the machine is asking them to do? For software: can this Python program actually run here? If not, which interpreter, dependency, ABI, native library, backend, permission, or patch is missing—and does remediation actually work?

A checkbox is not demonstration. An install transaction is not demonstration. A window appearing is not demonstration.

> **Capability is demonstrated, not presumed.**

See [Aspartame Doctrine](docs/ASPARTAME-DOCTRINE.md) and the [Human Interface Guidelines](docs/ASPARTAME-HIG.md).

## One computer, different depth

Aspartame does not want separate `child`, `blind`, `senior`, and `expert` computers. It wants one semantic computer that can provide different capabilities and reveal different depths.

```text
first encounter: symbols, Activities, obvious actions
later: Journal, objects, files, settings
deeper: terminal, scripting, inspection
further: Python APIs, services, internals
expert: edit the desktop itself
```

A first-time user may interact through symbolic imagery and spoken instruction before they can read. A blind adult may use the same semantic/spoken machinery without being treated as a child. An experienced user can skip teaching. A developer can descend into the real machine without replacing the interface with an unrelated advanced mode.

> **Make the surface understandable enough for someone who knows nothing, while making the substrate inspectable enough for someone who knows everything.**

## Activity, Object, Journal, Capability

Aspartame inherits Sugar's refusal to let implementation nouns define the human experience:

- **Activity** — what I am doing, rather than merely an application process.
- **Object** — the meaningful thing I made or worked with, rather than merely a path.
- **Journal** — what I have done and can resume, rather than merely a file tree.
- **Capability** — what an interaction or environment can provide, rather than a segregated accessibility mode.

## First-computer interaction

First use must not require literacy or prior GUI knowledge. Aspartame should be able to speak before asking someone to read and teach interaction through cause and effect:

```text
physical movement -> pointer movement -> target -> selection
physical button   -> activation
key               -> visible/spoken symbol
```

Teach experience before terminology where practical. Teaching narration should recede when no longer wanted without disabling persistent spoken-text capability.

> **No prerequisite interaction may require knowledge that Aspartame has not yet given the user an opportunity to discover.**

## Product family

Aspartame is larger than the Sugar desktop.

| Target | Purpose |
| --- | --- |
| **aspartame-minimal-x86** | Minimal/container-oriented Python substrate. No Sugar; no GTK requirement. Qualification control specimen. |
| **aspartame-server** | Headless Aspartame with Python service stack, including Django API/admin surfaces where defined. |
| **Aspartame desktop** | Sugar + GTK/native graphical substrate + Journal + Activities + human-facing capability model. |

Sugar and Django are sibling demonstrations on the same Python-oriented substrate, not declarations that either technology is universally superior.

## Snakepit — planned reverse package manager / compatibility laboratory

**Snakepit has not been implemented yet.** Its runbook exists precisely so `reverse package manager` does not turn into six projects wearing a trench coat before the first useful loop works.

Traditional package management begins with a selected package and asks what dependencies it needs. Snakepit's inverse question is:

> **I want this Python software. Where can it safely and correctly exist on this machine, and can we prove it works there?**

The system Python is protected substrate, not a dumping ground. Snakepit should choose or construct the smallest viable isolated environment, prefer the newest already-qualified common interpreter, use older runtimes only when evidence requires them, and remember why compatibility state exists so it can later be retired.

Its first implementation target is intentionally tiny:

```text
one real Python application
  -> inspect requirements
  -> choose interpreter/environment
  -> resolve dependencies
  -> exercise one meaningful workflow
  -> record exact success/failure
  -> bounded remediation if needed
  -> retest
  -> explain why it works
```

Then do a second application that creates a real interpreter/dependency tension. **One complete explainable loop before breadth.**

Existing solvers such as pacman, pip/uv, Conda/Mamba, or other appropriate machinery may do the solving. Snakepit's distinctive job is the feedback loop around them and the durable compatibility knowledge produced by execution.

> **AI investigates. Reality judges.**

See [Snakepit qualification runbook](docs/runbooks/SNAKEPIT_RUNBOOK.md).

## Sugar desktop and GTK4 modernization

The desktop target keeps Sugar's learning-centered model—Home, Activities, Frame, Journal, Neighborhood, palettes, XO identity, and visible context—while retaining practical Linux tools underneath.

GTK4 is not a redesign of Sugar into a conventional desktop. During migration the development VM deliberately keeps two separate shell spaces:

| Space | Purpose | Boundary |
| --- | --- | --- |
| Classic (F7) | Stable GTK3 Sugar reference | X11 + Metacity |
| Modern (F8) | GTK4 conversion under test | GTK4 shell + Casilda private Wayland Activity surfaces |

GTK3 and GTK4 remain separate Python processes. F7/F8 are an executable behavioral oracle: perform a workflow in stable GTK3, repeat it in GTK4, and treat a meaningful difference as a parity gap.

> **Behavioral parity—not launch count—is the GTK3 retirement meter.**

Activities are classified as **FULL PORT**, **FUNCTIONAL PORT**, **COVERAGE IMPLEMENTATION**, or **PLACEHOLDER** so runtime coverage cannot silently become a claim of behavioral parity.

Port by runtime milestone, not directory. Use ordinary GTK widgets for ordinary UI, Snapshot/GSK for genuinely custom Sugar graphics, and abstractions only at real platform seams. GTK CSS is not web CSS; geometry belongs to GTK layout APIs. GTK4 and Wayland are separate milestones, and Casilda remains the intended embedded Wayland boundary for modern Activities.

For shell transitions:

> **Animate pixels, not managed shell windows.**

## Chirality — future bounded multitasking

After the GTK4 migration gate, Aspartame's bounded multitasking model is **Chirality**:

> **Two hands. One focus. No third hand.**

A task may have a Left Hand and Right Hand Activity, but only one is visible and active at a time. The other holds context. This is not split-screen, tiling, arbitrary workspace management, or a limit on how many processes the machine can execute.

```text
hands <= 2
active_hands == 1
visible_activities == 1
```

The hands are nonhierarchical: not A/B, primary/secondary, or permanent source/destination roles. Personal XOColor and machine-state grammar remain distinct, and color is never the sole semantic carrier.

During GTK4 migration F7/F8 remain the GTK3/GTK4 comparison mechanism. Only afterward should proven switching behavior be repurposed for Left/Right Hand; migration scaffolding itself is not product doctrine.

## Progress over saturation

Aspartame uses autonomous agents aggressively, but commit volume is not progress. A reasonable local choice can become accidental architecture when tests encode it, docs explain it, and later agents assume it was intentional.

The operating rule is:

> **Does this close a real user-visible gap, or am I making an existing implementation more elaborate?**

For bounded work: reproduce -> find the narrow root cause -> make the minimum fix -> prove the previously failing workflow -> check the nearest regression boundary -> document the receipts -> **leave that subsystem**.

A discovered problem is allowed to remain open. Do not manufacture work from stale comments, theoretical races, style preferences, or speculative robustness. Do not turn a defect-sized problem into a new framework unless evidence makes that architecture unavoidable.

See [Autonomous contribution runbook](docs/runbooks/AUTONOMOUS_CONTRIBUTION_RUNBOOK.md).

## Ownership and escape hatch

Aspartame is opinionated; the owner is not imprisoned by the opinion. If someone asks to install a large alternate stack, first ask what capability they actually want. If they truly want the alternate environment, Arch and a real terminal remain underneath. Aspartame distinguishes **unqualified** from **forbidden**.

## Build and verification

```sh
git clone https://github.com/LuckyMonkey/aspartame-linux.git
cd aspartame-linux
make test
make iso
make run
```

The GTK4 migration is evidence-led. Runtime probes, qualification workflows, Journal roundtrips, screenshots, and human GTK3↔GTK4 comparison support claims; passing unit tests alone do not imply complete parity.

Useful guest checks include:

```sh
scripts/sugar-gtk4-runtime-check.sh gtk3
scripts/sugar-gtk4-runtime-check.sh gtk4
scripts/sugar-gtk4-space.sh status
```

## Documentation is memory

> **If you swing a hammer, document it.**

For meaningful changes, leave enough evidence to answer **what changed, why, what was tried, what was rejected, how it was verified, what remains strange, and how another person can reproduce it.** Runtime evidence outranks confident prose. Documentation makes disagreement intelligent; it does not make a decision sacred.

The desired rhythm is:

> **fix -> prove -> document -> get out.**

## Read next

- [Aspartame Doctrine](docs/ASPARTAME-DOCTRINE.md)
- [Aspartame HIG](docs/ASPARTAME-HIG.md)
- [Autonomous contribution runbook](docs/runbooks/AUTONOMOUS_CONTRIBUTION_RUNBOOK.md)
- [Snakepit qualification runbook](docs/runbooks/SNAKEPIT_RUNBOOK.md)
- [Sugar design guardrails](docs/SUGAR-DESIGN-GUARDRAILS.md)
- [GTK4 modernization runbook](docs/sugar-modernization/GTK4_RUNBOOK.md)
- [Conversion tracker](docs/sugar-modernization/CONVERSION_TRACKER.md)
