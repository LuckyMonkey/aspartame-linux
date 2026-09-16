# Aspartame doctrine

> **A sweeter computer.**

Aspartame is an opinionated Python computing platform. Sugar is its graphical expression, not its definition. The project deliberately asks how much of a complete useful computer can share one approachable high-level language while keeping the unavoidable native Linux substrate underneath.

## The proof boots

Aspartame prefers Python wherever a high-level implementation is appropriate: shell logic, Activities, services, orchestration, tooling, tests, automation, package intelligence, web services, and user programming. GTK, GLib, libc, the kernel, drivers, firmware, codecs, compositors, and other hard native layers remain native when Python would be the wrong abstraction.

> **Python all the way down until continuing to use Python would become stupid.**

Runtime minimization is a design constraint. Do not add another language runtime merely because an upstream application happens to ship one. Prefer software that can inhabit the existing Python/native substrate when choices are otherwise reasonable. Additional runtimes must earn their place through capability that cannot reasonably be supplied by the existing platform.

This is not a claim that Python is perfect. Aspartame exists partly because Python's version fragmentation, packaging archaeology, native bindings, abandoned metadata, dependency conflicts, and environment conventions too often become the user's problem. The project treats those failures as engineering problems to observe, contain, document, and where practical repair.

## Capability is demonstrated, not presumed

**Capability** is the common vocabulary for people, software, and environments.

Aspartame avoids treating accessibility as a separate kind of computer for a separate kind of person. It also avoids treating successful package installation as proof that software works. In both cases the question is the same:

> **Can this participant use the capabilities required by this environment?**

For a person, the requirement might be selection, activation, reading, writing, hearing information, navigation, or pointer control. For software, it might be an interpreter version, ABI, module, native library, display backend, network service, storage interface, or patch.

When a capability is missing, do not classify the participant as defective. Determine whether the environment can provide, teach, translate, substitute, or otherwise satisfy the missing capability. Then demonstrate the result.

This produces one operating-system-wide loop:

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

A checkbox is not demonstration. A dependency solver returning success is not demonstration. A window appearing is not demonstration. Qualification should exercise the real interaction or principal workflow at the boundary being claimed.

## One computer, different depth

Aspartame should be usable by a person who cannot yet read, a blind adult, an experienced everyday user, and an expert without creating demographic editions of the interface.

The system adapts to requested or demonstrated capabilities, not identity categories. Do not ask whether someone is a child, disabled, elderly, or an expert in order to choose what computer they receive. Ask what the computer needs to provide: spoken text, visual text, deterministic selection, pointer instruction, keyboard navigation, dictation, magnification, or deeper inspection.

A beginner should not receive a toy computer. An expert should not need to replace the simple interface to reach the real machine. Complexity is revealed progressively through the same system.

> **Make the surface understandable enough for someone who knows nothing, while making the substrate inspectable enough for someone who knows everything.**

A user should not have to outgrow Aspartame.

## The first computer

Aspartame aims to be a computer a parent can show a child before Windows or another conventional desktop. It should teach computing concepts rather than merely teach Aspartame conventions.

First-use interaction must not assume literacy or prior GUI knowledge. The computer may speak before it asks the user to read. It should be able to demonstrate pointer movement, targeting, selection, activation, keyboard input, erasing, Enter, scrolling, and dragging through cause and effect.

Teach experience before terminology where practical: move the physical mouse and observe the pointer; point at a target and observe selection; press the highlighted button and observe activation; then name the action as a click.

Instruction must remain respectful and capability-based. A pre-literate child and a blind forty-year-old may use the same spoken-text capability for entirely different reasons. Neither should be placed in a patronizing special mode. Teaching narration may recede when no longer wanted while screen-reader or spoken-text capability remains independently available.

> **No prerequisite interaction may require knowledge that Aspartame has not yet given the user an opportunity to discover.**

## Activity, capability, object

Aspartame inherits Sugar's useful refusal to let implementation nouns define the human experience.

- **Activity**, not application: what I am doing.
- **Object**, not merely file: what I made or worked with.
- **Journal**, not merely file manager: what I have done.
- **Capability**, not accessibility mode: what the computer can provide and what an interaction requires.

Implementation details remain inspectable, but they do not have to be the first vocabulary a person learns.

## Orange and blue

Aspartame's default machine duotone is **orange and blue**. The pair is a deliberately familiar two-part visual grammar: two related sides without implying good/bad or primary/secondary. It is particularly suitable for Chirality's Left Hand / Right Hand model.

Color must never be the sole carrier of meaning. Position, glyph, focus, spoken labels, semantic names, and input bindings must preserve the distinction for users who cannot perceive the colors. XOColor remains personal identity; orange/blue is machine grammar.

## Product family

Aspartame is larger than the Sugar desktop.

- **aspartame-minimal-x86** is the bare Python-oriented substrate, intended to be usable as a container and qualification specimen: no Sugar and no GTK requirement.
- **aspartame-server** omits Sugar but includes the server stack, including Django where appropriate for API and administration surfaces. It demonstrates the same substrate in a headless service role.
- **Aspartame desktop** adds Sugar, GTK4/native graphical substrate, Journal, Activities, and the human-facing capability model.

Sugar and Django are sibling demonstrations on the Aspartame substrate. Django is not included because the project declares it universally superior; it is useful evidence that serious Python service software can inhabit the same coherent platform.

## Snakepit: the compatibility enrichment center

Snakepit is planned work; it is not yet an implemented subsystem. Its purpose is not to promise that arbitrary Python software magically works. Its purpose is to make Python compatibility empirical, explainable, and reusable.

A conventional package transaction can end when declared dependencies resolve and files install. Snakepit's important question begins there:

> **Did the software actually work?**

The intended loop is resolve/install, exercise, observe, rate, diagnose failure, remediate, retest, and preserve what was learned. Wong-Baker compatibility ratings are a human-readable projection of structured evidence, not a popularity score. A successful configuration should retain the interpreter, dependencies, native requirements, patches, launch method, qualification procedure, platform context, and evidence explaining why it works.

Unknown software may be investigated because **anything is possible**, but it does not become qualified merely because installation succeeded. Failure is useful data when the environment and cause are recorded.

Snakepit should minimize runtime proliferation rather than casually create one interpreter universe per application. It may use existing solvers and environment tools where useful; it should not reinvent dependency solving merely to own it. Its distinctive responsibility is the feedback loop around those tools and the durable compatibility knowledge produced by real execution.

Agents may investigate failures, compare environments, propose pins or patches, and automate experiments. Deterministic qualification machinery decides whether the claimed workflow passed.

> **The model does not declare compatibility. The test chamber does.**

The long-term research value is a reproducible multi-version Python compatibility corpus: what runs, under which Python/runtime conditions, what fails, why it fails, which remediation works, and whether the fix survives retesting. New Python and package releases naturally create new qualification work without requiring architectural churn in Snakepit itself.

## Ownership and escape hatch

Aspartame is deliberately constrained; the owner is not. Snakepit and the Aspartame product should qualify a coherent environment rather than pretend every possible Arch package belongs in it. Installing an entire alternate desktop such as GNOME is outside that qualified product model because it duplicates or replaces the very environment Aspartame is defining.

But the machine still belongs to the user. Arch and a real terminal remain underneath. A user may leave the qualified path and modify the system. Aspartame should clearly distinguish **unsupported/unqualified** from **forbidden**.

## Documentation is memory

If you swing a hammer, document it. For meaningful changes, preserve enough evidence to answer: what changed, why, what was tried, what was rejected, how it was verified, what remains strange, and how another person can reproduce the result.

Do not let agent-generated tests and documentation turn an accidental architectural choice into unquestioned doctrine. Runtime evidence outranks confident prose. A discovered problem is allowed to remain open.
