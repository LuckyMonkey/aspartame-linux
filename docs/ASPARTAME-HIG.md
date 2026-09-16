# Aspartame Human Interface Guidelines

Aspartame preserves Sugar's human-centered vocabulary while extending it with a capability-first first-computer doctrine.

## 1. Do not assume literacy

A first-use path must be operable before the user can read. Spoken instruction, symbolic imagery, animation, direct manipulation, and cause/effect demonstration may establish the interaction vocabulary.

Never require a user to understand the word `click` before teaching clicking, or to read a button that enables spoken text.

## 2. Teach the computer, not the demographic

Do not create child mode, senior mode, blind mode, or expert mode as separate computers. Provide capabilities through one semantic interface.

Ask what is useful, not what kind of person is present. Prefer questions such as `Would you like me to read the words on the screen aloud?` or `Would you like me to show you how to use the mouse?`

Tone must remain respectful at every capability level. Spoken instruction for a pre-literate child must not require infantilizing language that would demean an adult using the same capability.

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

## 4. First-use learning is demonstrated

A foundational curriculum may introduce capabilities only as needed:

`point -> select -> activate -> back -> type -> erase -> Enter -> scroll -> drag`

Prefer experience -> concept -> word. Example: show a physical mouse moving alongside a pointer, ask the user to move the mouse, visibly respond, then identify the pointer. Ask the user to move onto a large target; visibly react to selection. Highlight the physical left button; after successful activation, name the action `click`.

Typing instruction begins with finding and pressing a key, not formal touch-typing technique. Efficient technique can be taught after the user understands the keyboard's basic causal relationship to text.

Do not front-load the entire curriculum. If dragging is not yet required, do not make mastery of dragging a setup gate. Teach a capability when it becomes useful.

## 5. Instruction recedes; capability remains

First-use narration and persistent spoken interface are different capabilities. A user who can read may still require or prefer spoken text. Completing or declining a tutorial must not disable a screen reader or other capability globally.

The system may remember demonstrated interaction capabilities so it does not repeatedly teach known skills. Such state describes interaction evidence, not a diagnosis or identity.

## 6. Capability, not accessibility

Aspartame's product vocabulary prefers **Capability** to `Accessibility` where Aspartame controls the terminology. This is not permission to hide established platform accessibility APIs, standards, AT-SPI roles, or upstream terminology in technical documentation where precise names are required.

A capability describes what the computer provides or what an interaction requires. Examples include spoken text, visual text, selection, activation, text entry, deterministic focus, magnification, captions, and alternate input.

The same interface semantics must remain available through assistive technology. Names, roles, state, descriptions where needed, deterministic focus, visible focus, and escape paths are implementation requirements, not optional polish.

## 7. Orange/blue machine grammar

The default Aspartame duotone is orange/blue. Use it as a familiar two-part visual language, especially for Left Hand / Right Hand Chirality. Do not assign moral or hierarchical meaning to the pair.

Never rely on hue alone. Preserve semantics with position, shape/glyph, labels, spoken names, focus, and bindings. XOColor identifies the person; orange/blue identifies the machine's two-sided grammar.

## 8. Low floor, no ceiling

The primary interaction can be obvious enough for a first encounter with a computer without reducing the underlying machine. Advanced capability should be progressively discoverable through palettes, inspection, terminal tools, Python, services, and source.

Do not replace the simple interface with an unrelated `advanced mode`. The expert should be descending into the same computer the beginner was already using.

## 9. Activity, Object, Journal

Continue Sugar's human vocabulary:

- Activity: what I am doing.
- Object: the meaningful work or thing.
- Journal: what I have done.
- Capability: what this interaction or environment can provide.

Avoid exposing implementation nouns as the first explanation merely because developers think in those nouns.

## 10. Qualification applies to humans too

Do not presume a tutorial worked because it was displayed. The interaction itself should demonstrate capability. If a user cannot complete an action, change the teaching or available interaction path rather than simply repeating prose.

> **Capability is demonstrated, not presumed.**
