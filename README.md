![Aspartame banner](aspartame.jpg)

### as-part-a-me

> **A Python-first computing platform whose desktop is Sugar.**  
> *a sweeter computer*

Aspartame asks a deliberately unreasonable question: **how much of a complete useful computer can share one approachable high-level language?** The answer is not `everything is literally Python`; Linux, GTK, GLib, libc, drivers, codecs, compositors, and firmware remain native where they should. The experiment is to minimize additional language runtimes and make Python the common inspectable language wherever a high-level implementation is appropriate.

> **Python all the way down until continuing to use Python would become stupid.**

The project is not Python advocacy. Python's version fragmentation, packaging archaeology, native bindings, dependency conflicts, and environment conventions are part of the problem Aspartame wants to expose and contain. The claim is demonstrated rather than advertised: **the proof boots.**

Aspartame is also intended to be a person's first computer without becoming a computer they later outgrow: simple enough for someone who cannot yet read, capable enough for an expert, and built around the same semantic interface rather than demographic modes.

## Capability is demonstrated, not presumed

Aspartame uses **Capability** as a unifying product concept.

For a person: can they select, activate, read or hear information, enter text, navigate, and understand what the machine is asking them to do? If not, what capability should the computer provide or teach?

For software: can this Python package actually run in this environment? If not, which interpreter, dependency, ABI, native library, backend, permission, or patch is missing—and does remediation actually work?

Those are the same question at different layers.

```text
participant + environment
        |
required capabilities
        |
provided capabilities
        |
      works?
      /   \
    yes    no
     |      |
 preserve  identify gap
 evidence   |
            v
        remediation
            |
           retry
```

A checkbox is not demonstration. An install transaction is not demonstration. A window appearing is not demonstration.

> **Capability is demonstrated, not presumed.**

See [Aspartame Doctrine](docs/ASPARTAME-DOCTRINE.md) and the [Human Interface Guidelines](docs/ASPARTAME-HIG.md).

## One computer, different depth

Aspartame does not want separate `child`, `blind`, `senior`, and `expert` computers. It wants one semantic computer that can provide different capabilities and reveal different depths.

A first-time user may interact through symbolic imagery and spoken instruction before they can read. A blind adult may use the same spoken-text and semantic-selection machinery without being treated as a child. An experienced user can skip teaching entirely. A scientist or developer can descend through Activities, Journal objects, terminal tools, Python, services, and source without replacing the simple interface with an unrelated `advanced mode`.

> **Make the surface understandable enough for someone who knows nothing, while making the substrate inspectable enough for someone who knows everything.**

Aspartame aims to be an operating system a parent can introduce before Windows or another conventional desktop: teach pointer movement, selection, clicking, typing, navigation, creation, and persistence as computing concepts rather than assuming the learner already knows them.

## Activity, Object, Journal, Capability

Aspartame inherits Sugar's refusal to let implementation nouns define the human experience:

- **Activity** — what I am doing, rather than merely an application process.
- **Object** — the meaningful thing I made or worked with, rather than merely a path.
- **Journal** — what I have done and can resume, rather than merely a file tree.
- **Capability** — what an interaction or environment can provide, rather than a segregated accessibility mode.

Established technical names such as AT-SPI remain precise technical names. `Capability` is the Aspartame product model, not an attempt to rename external standards.

## First-computer interaction

First use must not require literacy or prior GUI knowledge. Aspartame should be able to speak before asking someone to read and teach interaction through cause and effect:

```text
physical movement -> pointer movement -> target -> selection
physical button   -> activation
key               -> visible/spoken symbol
```

Teach experience before terminology where practical. Do not require someone to understand `click` before teaching clicking. Do not require a text-only setup button before spoken text can be enabled. Teaching narration should recede when no longer wanted without disabling persistent spoken-text capability.

> **No prerequisite interaction may require knowledge that Aspartame has not yet given the user an opportunity to discover.**

## Orange + blue machine grammar

Aspartame's default machine duotone is **orange and blue**: a familiar two-part visual language for related sides without implying good/bad or primary/secondary. It is especially useful for future Chirality: Left Hand / Right Hand.

Prior cultural exposure can make the pair feel familiar even to a very young user, but no particular media knowledge is required. Aspartame teaches its semantics through interaction. Hue is never the only carrier of meaning: position, glyph, focus, spoken labels, semantic names, and bindings preserve the distinction. XOColor remains personal identity; orange/blue is machine grammar.

## Product family

Aspartame is larger than the Sugar desktop.

| Target | Purpose |
| --- | --- |
| **aspartame-minimal-x86** | Minimal/container-oriented Python substrate. No Sugar; no GTK requirement. Qualification control specimen. |
| **aspartame-server** | Headless Aspartame with Python service stack, including Django API/admin surfaces where defined. |
| **Aspartame desktop** | Sugar + GTK/native graphical substrate + Journal + Activities + human-facing capability model. |

Sugar and Django are sibling demonstrations on the same substrate. Django is not present because Django is declared the best web framework; it is useful proof that serious service software can inhabit the same Python-oriented platform. Sugar is the spectacular human-facing proof that Python can coordinate far more than scripts and backend glue.

## Snakepit — planned compatibility laboratory

**Snakepit has not been implemented yet.** The runbook exists to constrain the idea before code begins.

Traditional package management can declare victory after dependency resolution and installation. Snakepit's defining follow-up is:

> **Did it actually work?**

The intended loop is `resolve/install -> exercise -> observe -> rate -> diagnose -> remediate -> retest -> preserve what was learned`.

Wong-Baker compatibility is a human-readable projection of structured qualification evidence, not a popularity score. Snakepit should be able to explain why software works: interpreter, dependencies, pins, native requirements, patches, target environment, workflow, and evidence.

Snakepit may use pacman, pip/uv, Conda/Mamba, or other existing machinery where appropriate. It should not reinvent dependency solving merely to own it. Its distinctive job is the feedback loop around those tools and the compatibility knowledge produced by real execution.

It should also minimize Python runtime proliferation rather than casually creating a permanent interpreter universe per application. If a package only works on an older Python, record why. If later qualification lets it move to the common runtime, collapse it upward and retire unnecessary compatibility state.

Agents may investigate failures and propose remediation. **AI investigates; reality judges.** The model does not mark software compatible because its explanation sounds convincing; qualification does.

See [Snakepit qualification runbook](docs/runbooks/SNAKEPIT_RUNBOOK.md).

## Sugar desktop and GTK4 modernization

The desktop target keeps Sugar's learning-centred model—Home, Activities, Frame, Journal, Neighborhood, Group, palettes, XO identity, and visible context—while retaining practical Linux tools underneath: systemd, pacman, ordinary files, networking, audio, CUPS, SSH, and a real terminal.

This is not a GNOME reskin, and GTK4 is not a redesign of Sugar into a conventional desktop. The goal is to modernize the implementation while preserving the interaction model that makes Sugar distinct.

During migration the development VM uses two separate shell spaces:

| Space | Purpose | Boundary |
| --- | --- | --- |
| Classic (F7) | Stable GTK3 Sugar reference | X11 + Metacity |
| Modern (F8) | GTK4 conversion under test | GTK4 shell + Casilda private Wayland Activity surfaces |

GTK3 and GTK4 remain separate Python processes. F7/F8 are an executable behavioral oracle: perform a workflow in stable GTK3, repeat it in GTK4, and treat the difference as a parity gap. Behavioral parity—not launch count—is the retirement meter.

Activities are classified as **FULL PORT**, **FUNCTIONAL PORT**, **COVERAGE IMPLEMENTATION**, or **PLACEHOLDER** so runtime coverage cannot silently become a claim of behavioral parity. See [ACTIVITY_PORT_CLASSIFICATION.md](docs/sugar-modernization/ACTIVITY_PORT_CLASSIFICATION.md) and [CONVERSION_TRACKER.md](docs/sugar-modernization/CONVERSION_TRACKER.md).

## Chirality

Aspartame's future bounded multitasking model is **Chirality**:

> **Two hands. One focus. No third hand.**

A task may have a Left Hand and a Right Hand, but only one is visible and active at a time. The other holds state. It is not split-screen, tiling, arbitrary workspace management, or unlimited window accumulation.

Orange/blue provides the default visual grammar, but position, semantics, spoken labels, and bindings remain authoritative. During GTK4 migration F7/F8 remain the GTK3/GTK4 comparison mechanism; only after that gate should the proven switching behavior be repurposed for Left/Right Hand.

## Ownership and escape hatch

Aspartame is opinionated; the owner is not imprisoned by the opinion. The qualified environment intentionally avoids unnecessary parallel runtimes and alternate operating environments. If someone asks to install GNOME, the useful first question is often **what capability are you actually trying to obtain?**

If they truly want GNOME, Arch and a real terminal remain underneath. The machine belongs to them. Aspartame distinguishes **unqualified** from **forbidden**.

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

If you swing a hammer, document it.

For meaningful changes, leave enough evidence to answer **what changed, why, what was tried, what was rejected, how it was verified, what remains strange, and how another person can reproduce it.** Runtime evidence outranks confident prose. A discovered problem is allowed to remain open.

## Read next

- [Aspartame Doctrine](docs/ASPARTAME-DOCTRINE.md)
- [Aspartame HIG](docs/ASPARTAME-HIG.md)
- [Snakepit qualification runbook](docs/runbooks/SNAKEPIT_RUNBOOK.md)
- [Sugar design guardrails](docs/SUGAR-DESIGN-GUARDRAILS.md)
- [GTK4 modernization runbook](docs/sugar-modernization/GTK4_RUNBOOK.md)
- [Conversion tracker](docs/sugar-modernization/CONVERSION_TRACKER.md)
