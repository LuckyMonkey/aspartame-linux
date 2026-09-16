# Aspartame Human Interface Guidelines

Aspartame preserves Sugar's human-centered vocabulary while extending it with a capability-first, first-computer doctrine.

> **Capability is demonstrated, not presumed.**

## 1. Do not assume literacy

A first-use path must be operable before the user can read. Spoken instruction, symbolic imagery, animation, direct manipulation, and cause/effect demonstration may establish the interaction vocabulary.

Never require a user to understand the word `click` before teaching clicking, or to read a button that enables spoken text.

The first interface may speak before it asks the user to read. If reading is available and the user does not want teaching narration, narration may recede. Do not confuse teaching narration with persistent spoken-text or screen-reader capability.

## 2. Teach the computer, not the demographic

Do not create child mode, senior mode, blind mode, or expert mode as separate computers. Provide capabilities through one semantic interface.

Ask what is useful, not what kind of person is present. Prefer questions such as `Would you like me to read the words on the screen aloud?` or `Would you like me to show you how to use the mouse?`

Tone must remain respectful at every capability level. Spoken instruction for a pre-literate child must not require infantilizing language that would demean an adult using the same capability. A child deserves respect; an adult using spoken interaction does not become a child.

## 3. Selection and activation are semantic

Important actions must exist independently of one physical input device.

```text
SELECT
  pointer target
  keyboard navigation
  touch
  controller navigation
  spoken/screen-reader navigation

ACTIVATE
  primary mouse button
  Enter/Space where appropriate
  touch
  controller action
  assistive activation
```

The UI owns `selected`, `activate`, `secondary_action`, `back`, `next`, and `previous` semantics. Input methods map onto those semantics.

A visual icon reacting to pointer presence, a screen reader announcing an object, and controller focus landing on the same object are presentations of the same semantic selection state.

Keyboard minimum: Tab moves to the next interactive object, Shift+Tab moves backward, Enter activates, Space activates/toggles where appropriate, and Escape dismisses or goes back. Focus must be visible, deterministic, and free of traps. Important objects require meaningful accessible names and roles, plus state and description where needed.

## 4. First-use learning is demonstrated

A foundational curriculum may introduce capabilities only as needed:

`point -> select -> activate -> back -> type -> erase -> Enter -> scroll -> drag`

Prefer experience -> concept -> word. Example: show a physical mouse moving alongside a pointer, ask the user to move the mouse, visibly respond, then identify the pointer. Ask the user to move onto a large target; visibly react to selection. Highlight the physical left button; after successful activation, name the action `click`.

Typing instruction begins with finding and pressing a key, not formal touch-typing technique. Efficient technique can be taught after the user understands the keyboard's basic causal relationship to text.

Do not front-load the entire curriculum. If dragging is not yet required, do not make mastery of dragging a setup gate. Teach a capability when it becomes useful.

The first-use Activity should teach computing concepts, not merely memorize Aspartame controls. The intended lesson is `physical action -> computer response -> concept`, so knowledge transfers when the person later encounters another operating system.

## 5. Instruction recedes; capability remains

First-use narration and persistent spoken interface are different capabilities. A user who can read may still require or prefer spoken text. Completing or declining a tutorial must not disable a screen reader or other capability globally.

The system may remember demonstrated interaction capabilities so it does not repeatedly teach known skills. Such state describes interaction evidence, not a diagnosis, age, intelligence, or identity.

A user may skip instruction. Experienced use must not be burdened by permanent training wheels.

## 6. Capability, not Accessibility as a product category

Aspartame's product vocabulary prefers **Capability** to `Accessibility` where Aspartame controls the terminology. This is not permission to hide established platform accessibility APIs, standards, AT-SPI roles, or upstream terminology in technical documentation where precise names are required.

A capability describes what the computer provides or what an interaction requires. Examples include spoken text, visual text, selection, activation, text entry, deterministic focus, magnification, captions, and alternate input.

The same interface semantics must remain available through assistive technology. Names, roles, state, descriptions where needed, deterministic focus, visible focus, and escape paths are implementation requirements, not optional polish.

Do not ask `what kind of user is this?` when the useful question is `what capability must the computer provide?`

## 7. Machine grammar and personal identity

Machine state and personal identity are separate visual concepts. XOColor identifies the person. Machine grammar may use a stable two-sided treatment where a product interaction needs two nonhierarchical sides, but hue must never be the only carrier of meaning.

Preserve semantics with position, shape/glyph, labels, spoken names, focus, and bindings. A color pair may make a relationship quickly recognizable; it must not become a prerequisite for understanding it.

For Chirality, the authoritative concepts are **Left Hand** and **Right Hand**, not `A/B`, `primary/secondary`, `source/destination`, or a particular pair of colors. The two hands are peers.

## 8. Low floor, no ceiling

The primary interaction can be obvious enough for a first encounter with a computer without reducing the underlying machine. Advanced capability should be progressively discoverable through palettes, inspection, terminal tools, Python, services, and source.

Do not replace the simple interface with an unrelated `advanced mode`. The expert should be descending into the same computer the beginner was already using.

A useful progression is:

```text
first encounter: symbols, Activities, obvious actions
later: Journal, objects, files, settings
deeper: terminal, scripting, inspection
further: Python APIs, services, internals
expert: edit the desktop itself
```

The target range is intentionally broad: a pre-literate child, a blind adult, an older first-time or casual user, and a scientist or developer should not require four different operating-system personalities. They require different capabilities and different depths of the same system.

> **There should be no obvious skill level at which a user has to outgrow Aspartame.**

## 9. Activity, Object, Journal, Capability

Continue Sugar's human vocabulary:

- Activity: what I am doing.
- Object: the meaningful work or thing.
- Journal: what I have done.
- Capability: what this interaction or environment can provide.

Avoid exposing implementation nouns as the first explanation merely because developers think in those nouns.

## 10. Qualification applies to humans too

Do not presume a tutorial worked because it was displayed. The interaction itself should demonstrate capability. If a user cannot complete an action, change the teaching or available interaction path rather than simply repeating prose.

This is the human-facing instance of the same rule used by software qualification: declared support is weaker than observed operation.

## 11. No prerequisite without discovery

> **No prerequisite interaction may require knowledge that Aspartame has not yet given the user an opportunity to discover.**

A button labelled `Continue` cannot be the only path to learning what clicking means. A text-only prompt cannot be the only path to enabling spoken text. A hidden keyboard convention cannot be required before keyboard navigation has been introduced.

The system should be able to bootstrap the user's interaction vocabulary from cause and effect.

## 12. First computer, not first Aspartame

Aspartame should be credible as the operating system a parent introduces before Windows, macOS, or another conventional desktop. Success means the person learns transferable concepts: pointer, selection, activation, text entry, navigation, creation, persistence, and eventually inspection and programming.

Do not teach conventional desktop metaphors merely because they are conventional. Teach the computer first. Other operating systems can then be understood as alternative organizations of concepts the user already owns.

## 13. Chirality: bounded multitasking

Future Aspartame multitasking is intentionally bounded by attention rather than process count.

> **Two hands. One focus. No third hand.**

A task may have zero, one, or two hands. With two hands, one Activity is visible and active while the other preserves context. The model is not split-screen, tiling, arbitrary workspace management, or a third hidden application slot.

```text
hands <= 2
active_hands == 1
visible_activities == 1
```

The Left Hand and Right Hand are nonhierarchical. One may hold steady while the other changes the object or task, but `left` does not mean source and `right` does not mean destination. Sending and receiving are contextual behaviors, not permanent identities.

Chirality is object/task-centered: the two Activities cooperate around meaningful work. Processes may remain alive elsewhere; the attention model does not pretend the operating system can only execute two processes.

During GTK4 migration, F7/F8 belong to the GTK3-reference/GTK4-candidate behavioral oracle. Do not turn those keys into Chirality until migration is complete. Reuse proven switching behavior later, not migration scaffolding.

## 14. Transitions animate pixels, not managed windows

Cross-window transparency and managed-window geometry are not product requirements. For shell transitions, prefer a fixed opaque transition surface containing a snapshot/framebuffer representation of the source or destination, then animate alpha, clipping, scale, or transform inside that surface.

> **Animate pixels, not managed shell windows.**

Do not make Jarabe transitions depend on arbitrary window movement/resizing or compositor-specific cross-top-level transparency. This keeps the interaction model compatible with the modern Wayland/Casilda direction.

## 15. Sugar remains Sugar

GTK4 modernization is not permission to redesign Sugar into a conventional desktop. Preserve Home, Frame, Journal, Neighborhood, palettes, XO identity, Activities, object continuity, and visible context where they express the human model.

Use ordinary GTK widgets for ordinary forms, text, and lists. Use Snapshot/GSK where Sugar genuinely needs custom visual composition. Platform abstractions should exist at real seams—lifecycle, notifications, clipboard, Journal/file interaction, dialogs, session/window behavior, launching, theme tokens, input, and collaboration—not around every widget merely because a port is underway.
