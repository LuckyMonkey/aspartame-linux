# Aspartame doctrine

> **A sweeter computer.**

Aspartame is an opinionated Python computing platform. Sugar is its graphical expression, not its definition. The project deliberately asks how much of a complete useful computer can share one approachable high-level language while keeping the unavoidable native Linux substrate underneath.

## The proof boots

Aspartame prefers Python wherever a high-level implementation is appropriate: shell logic, Activities, services, orchestration, tooling, tests, automation, package intelligence, web services, and user programming. GTK, GLib, libc, the kernel, drivers, firmware, codecs, compositors, and other hard native layers remain native when Python would be the wrong abstraction.

> **Python all the way down until continuing to use Python would become stupid.**

Runtime minimization is a design constraint. Do not add another language runtime merely because an upstream application happens to ship one. Prefer software that can inhabit the existing Python/native substrate when choices are otherwise reasonable. Additional runtimes must earn their place through capability that cannot reasonably be supplied by the existing platform.

This is not Python advocacy and it is not a claim that Python is good merely because it is Python. Aspartame is, in part, an adversarial proof of concept: Python's version fragmentation, packaging archaeology, native bindings, abandoned metadata, dependency conflicts, and environment conventions are real defects in the experience of using its ecosystem. The project treats those failures as engineering problems to observe, contain, document, and where practical repair.

The proof is not a manifesto. **The proof boots.** A Python-heavy desktop, service stack, Activities, tooling, automation, and future package-qualification system are deliberately visible demonstrations of how far one high-level language can carry a complete computing environment.

Sugar is chosen because it is unusually compatible with that experiment: its shell, toolkit-facing logic, and Activity culture are deeply Python-oriented. Sugar is not sacred. The Python-first, inspectable-computer idea is the larger project.

```text
🐧 Linux / native substrate
        ↓
🐍 Python common language
        ├── 🍬 Sugar / Jarabe desktop
        ├── 🧩 Activities
        ├── 🌐 Django / server services
        ├── 🛠️ system tooling and automation
        └── 🧪 Snakepit qualification
```

The native substrate is not denied; it is kept at the layer where native code is appropriate. The experiment is to avoid multiplying high-level runtimes above it without a demonstrated reason.

## Capability is demonstrated, not presumed

**Capability** is the common vocabulary for people, software, and environments.

Aspartame avoids treating accessibility as a separate kind of computer for a separate kind of person. It also avoids treating successful package installation as proof that software works. In both cases the question is the same:

> **Can this participant use the capabilities required by this environment?**

For a person, the requirement might be selection, activation, reading, writing, hearing information, navigation, or pointer control. For software, it might be an interpreter version, ABI, module, native library, display backend, network service, storage interface, or patch.

When a capability is missing, determine whether the environment can provide, teach, translate, substitute, or otherwise satisfy the missing capability. Then demonstrate the result.

```text
                    ASPARTAME CAPABILITY MODEL

          PERSON                              SOFTWARE
            │                                    │
            ▼                                    ▼
     required interaction                 required runtime
        capabilities                        capabilities
            │                                    │
            ├─ select                            ├─ Python version
            ├─ activate                          ├─ ABI / module
            ├─ read / hear                       ├─ native library
            ├─ type                              ├─ display backend
            └─ navigate                          └─ patch / service
            │                                    │
            └──────────────┬─────────────────────┘
                           ▼
                 DOES THE ENVIRONMENT
                 PROVIDE WHAT IS NEEDED?
                         /     \
                       yes      no
                        │        │
                    demonstrate  identify gap
                        │        │
                    preserve     remediate
                    evidence        │
                                   retry
```

A checkbox is not demonstration. A dependency solver returning success is not demonstration. A window appearing is not demonstration. Qualification should exercise the real interaction or principal workflow at the boundary being claimed.

> **Capability is demonstrated, not presumed.**

## One computer, different depth

Aspartame should be usable by a person who cannot yet read, a blind adult, an experienced everyday user, and an expert or scientist without creating demographic editions of the interface.

The system adapts to requested or demonstrated capabilities, not identity categories. A beginner should not receive a toy computer. An expert should not need to replace the simple interface to reach the real machine. Complexity is revealed progressively through the same system.

> **Make the surface understandable enough for someone who knows nothing, while making the substrate inspectable enough for someone who knows everything.**

> **There should be no obvious skill level at which a user has to outgrow Aspartame.**

```text
👶 first contact      icons → selection → Activities
        ↓
📚 growing fluency    Journal → objects → creation
        ↓
⌨️ curious user       terminal → scripting
        ↓
🐍 programmer         Python APIs → services → internals
        ↓
🔬 expert             scientific/development workloads
        ↓
🛠️ hacker             edit the fucking desktop

                 SAME COMPUTER
```

A useful long arc is icons and Activities -> Journal and objects -> terminal and scripting -> Python APIs and internals -> editing the desktop itself. This is progressive disclosure of the same computer, not an unrelated advanced mode.

## The first computer

Aspartame aims to be a computer a parent can show a child before Windows or another conventional desktop. It should teach computing concepts rather than merely teach Aspartame conventions.

First-use interaction must not assume literacy or prior GUI knowledge. The computer may speak before it asks the user to read. It should be able to demonstrate pointer movement, targeting, selection, activation, keyboard input, erasing, Enter, scrolling, and dragging through cause and effect.

Teach experience before terminology where practical. Instruction must remain respectful and capability-based. Teaching narration may recede when no longer wanted while screen-reader or spoken-text capability remains independently available.

```text
🖐️ move physical mouse
        ↓
🖱️ pointer moves
        ↓
🎯 pointer reaches target
        ↓
✨ target visibly/spokenly selects
        ↓
👆 press button
        ↓
▶️ target activates
        ↓
💬 only then name the concept: “click”
```

The same semantic lesson can be expressed through keyboard, touch, controller, speech, or screen-reader navigation. The computer teaches the capability; it does not classify the person.

> **No prerequisite interaction may require knowledge that Aspartame has not yet given the user an opportunity to discover.**

## Activity, capability, object

Aspartame inherits Sugar's useful refusal to let implementation nouns define the human experience.

- **Activity**, not application: what I am doing.
- **Object**, not merely file: what I made or worked with.
- **Journal**, not merely file manager: what I have done.
- **Capability**, not accessibility mode: what the computer can provide and what an interaction requires.

Where Aspartame controls product vocabulary, prefer **Capability** over using `Accessibility` as a segregating product category. This does not rename standards such as AT-SPI or erase precise upstream technical terminology.

## Identity and machine grammar

XOColor is personal identity. Machine-state grammar is separate and must never depend on hue alone.

Aspartame's default two-sided machine grammar is **orange + blue**. 🟠🔵 It is intentionally familiar before it is explained: many users, including very young users, have already encountered orange/blue as a paired visual distinction in games, videos, toys, diagrams, and popular culture. That prior exposure is useful cognitive scaffolding, not a dependency and not a reference the user must recognize.

```text
          🟠 LEFT HAND       RIGHT HAND 🔵
                │                │
                └──── one task ──┘
                       one focus
```

Orange does not mean warning and blue does not mean safe. Neither means primary, good, source, or preferred. They mean two related sides. Position, glyph, semantic names, spoken labels, focus, and bindings remain authoritative so color is never the only carrier of meaning.

For Chirality, the concepts are **Left Hand** and **Right Hand**. Do not collapse them into `A/B`, `primary/secondary`, or permanent `source/destination` roles. The hands are peers.

> **XOColor identifies the person. Orange/blue explains the machine.**

## Product family

Aspartame is larger than the Sugar desktop.

- **aspartame-minimal-x86** is the bare Python-oriented substrate, intended to be usable as a container and qualification specimen: no Sugar and no GTK requirement.
- **aspartame-server** omits Sugar but includes the server stack, including Django for API and administration surfaces where that stack is defined.
- **Aspartame desktop** adds Sugar, GTK4/native graphical substrate, Journal, Activities, and the human-facing capability model.

```text
                         ASPARTAME
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       🧪 MINIMAL       🌐 SERVER       🍬 DESKTOP
          Python           Python          Python
          substrate        substrate       substrate
             │              │              │
          Snakepit       Django/API     Sugar/GTK4
          specimen         admin        Journal/Activities
```

Sugar and Django are sibling demonstrations on the Aspartame substrate. Neither is included as a declaration that it is universally superior; each demonstrates serious software inhabiting the same coherent Python-oriented platform.

Django is deliberately useful as a demonstrative load: not “Django is good,” but “this serious Python service stack can run here, and the environment can explain why.” The desktop is the spectacular human-facing proof; Minimal is the control specimen; Server is the service proof.

## Snakepit: reverse package management as a compatibility laboratory

**Snakepit has not been implemented.** The idea is intentionally constrained in documentation before code begins.

Calling it a `reverse package manager` is deliberately loaded. A conventional package manager begins with a chosen package and asks what it requires. Snakepit begins with desired Python software or capability and asks:

> **Where can this safely and correctly exist on this machine, and can we prove that it works there?**

The system Python is protected substrate, not the destination for arbitrary application dependencies. Snakepit should prefer the newest already-qualified common runtime, use isolated environments where needed, introduce older interpreters only when demonstrated compatibility requires them, record why they exist, and collapse applications upward when later qualification makes compatibility state unnecessary.

Its first implementation must be one complete explainable vertical slice, not a universal resolver, app store, compatibility cloud, distributed worker fleet, or six projects wearing a trench coat:

```text
requested Python application
        |
inspect requirements
        |
choose viable interpreter/environment
        |
resolve dependencies without contaminating system Python
        |
exercise one meaningful workflow
        |
record exact success/failure and why
        |
remediate once if bounded
        |
retest and preserve evidence
```

Then repeat with a second application that creates a real interpreter or dependency tension.

The package manager is not authoritative about whether software works. **Reality is.**

> **AI investigates. Reality judges.**
>
> **The model does not declare compatibility. The test chamber does.**

A future qualification laboratory may use a small controller/VPS and disposable workers across Python/package/native-version matrices. The valuable output is not inference itself; it is durable compatibility knowledge: exact failures, verified fixes, recipes, patches, evidence, and the conditions under which those results remain true.

```text
new Python/package code
        ↓
🧪 disposable test matrix
        ↓
install → exercise → observe
        ↓
      failure?
      /     \
    no       yes
    │         ↓
 preserve   agent investigates
 evidence      ↓
             bounded fix
                ↓
              RETEST
                ↓
        preserve reusable recipe
```

See the Snakepit runbook for the qualification corpus, runtime-minimization rules, Wong-Baker projection, and non-goals.

## GTK4 modernization is a parity program

GTK4 is not permission to redesign Sugar into a conventional desktop. The migration exists to modernize the implementation while preserving and proving the human model.

Stable GTK3 Sugar remains an executable specification while the port is active. F7 selects the known-good GTK3 reference; F8 selects the GTK4 candidate. Perform the same normal workflow on both. A meaningful difference is a parity gap.

> **Behavioral parity, not launch count, is the GTK3 retirement meter.**

A process starting, a window appearing, or an automated matrix passing proves only the boundary actually exercised. Activity classifications must remain honest: FULL PORT, FUNCTIONAL PORT, COVERAGE IMPLEMENTATION, and PLACEHOLDER are different claims.

Port by runtime milestone rather than directory. Prefer pure Python state/model logic where useful and GTK4 presentation at the edge. Use normal widgets for normal UI and Snapshot/GSK for genuinely custom Sugar graphics. Abstract platform seams, not every widget.

GTK CSS is not web CSS. Geometry belongs in GTK layout APIs; styling belongs in supported GTK CSS. Parse CSS with the real provider rather than trusting browser intuition.

Wayland and GTK4 are related but separate milestones. Casilda is the intended embedded Wayland surface for modern Activity integration; do not casually replace it because another compositor architecture looks interesting.

For transitions:

> **Animate pixels, not managed shell windows.**

Prefer a fixed opaque transition surface containing a snapshot/framebuffer representation. Do not make the product depend on arbitrary managed-window geometry or compositor-specific cross-top-level transparency.

## Chirality: bounded attention

After GTK4 parity, Aspartame's advanced multitasking doctrine is Chirality:

> **Two hands. One focus. No third hand.**

A task may have Left Hand and Right Hand Activities, but only one is visible and active at a time. The other holds context. This is not split screen, tiling, arbitrary workspaces, or a claim that only two processes may run.

```text
hands <= 2
active_hands == 1
visible_activities == 1
```

Human work is often cooperative rather than parallel: one hand holds steady while the other ratchets. Chirality bounds the attention surface while allowing the underlying system to remain a full computer.

During GTK4 migration, F7/F8 belong exclusively to the reference/candidate oracle. Reuse proven switching behavior for Chirality only after the migration gate; do not preserve migration scaffolding merely because the keys will later have a product role.

## Progress over saturation

Long-running autonomous work can accidentally turn one reasonable local choice into apparent doctrine:

```text
reasonable choice
  -> tests encode it
  -> docs explain it
  -> next agent assumes intent
  -> another subsystem integrates it
  -> accident now looks architectural
```

Therefore Aspartame optimizes for verified forward motion, not subsystem saturation.

> **Does this close a real user-visible gap, or am I making an existing implementation more elaborate?**

When a bounded workflow passes, leave that subsystem. A discovered problem is allowed to remain open. Do not create a framework-sized answer to a defect-sized question.

Independent contributors are welcome to disagree. Distinguish `actually wrong` from `I would have implemented this differently`. Runtime evidence settles behavioral claims; doctrine settles intentional product invariants; style preference alone does neither.

See the autonomous contribution runbook.

## Ownership and escape hatch

Aspartame is deliberately constrained; the owner is not. Snakepit and the Aspartame product should qualify a coherent environment rather than pretend every possible Arch package belongs in it.

When a user asks for a large alternate stack such as another desktop environment, first determine the capability they actually want. They may be reaching for a file browser, setting, workflow, or familiar tool rather than truly wanting a second operating environment.

If they genuinely want GNOME, KDE, another runtime, or some other unqualified stack, the underlying Arch system and terminal remain theirs. The machine belongs to the owner. Aspartame clearly distinguishes **unsupported/unqualified** from **forbidden**.

## Documentation is memory

> **If you swing a hammer, document it.**

For meaningful changes, preserve enough evidence to answer: what changed, why, what was tried, what was rejected, how it was verified, what remains strange, and how another person can reproduce the result.

Documentation does not make a decision sacred. It lets the next person disagree intelligently.

Do not let agent-generated tests and documentation turn an accidental architectural choice into unquestioned doctrine. Runtime evidence outranks confident prose. A discovered problem is allowed to remain open.

The desired contribution rhythm is:

> **fix -> prove -> document -> get out.**
