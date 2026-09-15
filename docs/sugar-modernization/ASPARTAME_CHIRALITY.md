Aspartame Chirality

Status: Design doctrine / post-GTK4 implementation runbook
Scope: Sugar shell, Activity lifecycle, object handoff, Journal, input, accessibility
Current implementation dependency: GTK3/GTK4 Spaces migration must complete first

Two hands. One focus. No third hand.

1. Purpose

Sugar's single-Activity model is one of its strongest ideas.

A task occupies the screen. The user works on that task. The desktop does not ask the user to manage an arbitrary collection of overlapping windows.

However, real work frequently requires two Activities to accomplish one task.

Examples:

Read      ↔ Write
Browser   ↔ Annotate
Journal   ↔ Edit
Camera    ↔ Paint
Terminal  ↔ Documentation
Dataset   ↔ Analysis
Mail      ↔ Document

Conventional desktops solve this by allowing unlimited windows.

Aspartame will not.

Instead, Aspartame extends Sugar with Chirality:

A task may involve up to two Activities.

These Activities are the Left Hand and Right Hand.

Only one hand is visible and active at any moment.

The other hand holds its state.

The user switches hands as the task requires.

Chirality is not split screen.

Chirality is not tiling.

Chirality is not conventional workspace management.

It is bounded working context.

2. Core Doctrine

The fundamental model is:

                   ONE TASK
                       │
                    OBJECT
                       │
             ┌─────────┴─────────┐
             │                   │
        LEFT HAND           RIGHT HAND
             │                   │
         Activity              Activity
             │                   │
          HELD ◄──────────────► ACTIVE

                 F7       F8

At any moment:

hands <= 2
visible_activities == 1
active_hands == 1

There is no third hand.

There is no mode in which both Activities compete for visual attention.

The operating system may have many processes running and many Activities preserved. Chirality constrains the immediate task context, not the machine.

3. The Ratchet Principle

The physical metaphor is intentional:

One hand holds steady while the other ratchets.

A person using a ratchet does not simultaneously perform two independent tasks with both hands.

One hand establishes context.

The other acts.

Then the roles may reverse.

Aspartame should behave similarly:

LEFT                         RIGHT

Read                         Write
paper.pdf                    notes.odt

HELD ──────────────────────► ACTIVE

The user switches:

LEFT                         RIGHT

Read                         Write
paper.pdf                    notes.odt

ACTIVE ◄──────────────────── HELD

The formerly active Activity does not disappear, terminate, or lose its task state merely because attention moved elsewhere.

It is held.

This distinction is central to Chirality.

4. Chirality Is Not Split Screen

There is deliberately no normal presentation such as:

┌───────────────────┬───────────────────┐
│                   │                   │
│       READ        │       WRITE       │
│                   │                   │
└───────────────────┴───────────────────┘

Do not implement:

50/50 mode
30/70 mode
draggable dividers
tiling
quadrants
floating secondary Activities
picture-in-picture Activities
"just one more pane"
arbitrary Activity layouts

The screen continues to contain one Activity.

┌─────────────────────────────────────────┐
│                                         │
│                                         │
│                  WRITE                  │
│                                         │
│                notes.odt                │
│                                         │
│                                         │
└─────────────────────────────────────────┘

           Left Hand ← F7   F8 → Right Hand

Pressing the opposite hand key replaces the entire Activity surface.

This preserves Sugar's focus-first model.

Chirality adds another context, not another rectangle.

5. Canonical Vocabulary

Use these terms consistently in code, documentation, accessibility metadata, tests, and UI design.

Concept	Canonical term
Overall principle	Chirality
First context	Left Hand
Second context	Right Hand
Currently focused context	Active Hand
Preserved counterpart	Held Hand
Thing being worked with	Object
Change active context	Switch Hands
Replace one context	Let Go / Replace Hand
Move/use an object with counterpart	Other Hand / Give to Other Hand

Avoid making these canonical:

App A / App B
App 1 / App 2
Primary / Secondary
Master / Auxiliary
Source / Destination
Pane 1 / Pane 2
Window 1 / Window 2

The relationship is deliberately non-hierarchical.

Either hand may act.

Either hand may hold.

Either hand may supply or receive an object.

6. Hand Identity and XOColor

Aspartame MUST NOT define universal colors for Left and Right.

The hands inherit the user's existing XOColor pair.

Conceptually:

                  USER / XO
                 color A + B
                    /   \
                   /     \
                  /       \
          LEFT HAND       RIGHT HAND
           color A         color B

The exact mapping should be stable for the user.

For example:

XOColor.stroke → Left Hand
XOColor.fill   → Right Hand

or another mapping established by Sugar's actual color semantics.

Once chosen, it must remain deterministic.

Why

Sugar already gives the user a two-color visual identity.

Chirality makes that identity functional.

The user does not need to learn an unrelated color system for multitasking.

Their existing pair becomes their pair of hands.

7. Color Is Reinforcement, Not Semantics

Color must never be the sole means of identifying a hand.

This is required for accessibility and for XOColor combinations with weak visual differentiation.

Hand identity must also be communicated through:

left/right position where appropriate
F7/F8
accessible names
focus state
optional hand iconography
shell transition direction
spoken feedback
controller mappings

The system should remain fully usable without perceiving color.

Therefore:

Handedness is semantic. XOColor is wayfinding.

8. Portal as Cultural Precedent, Not Dependency

Blue/orange paired endpoints are already familiar to many users through Portal.

That existing cultural vocabulary demonstrates that two strongly differentiated colors can communicate:

these two things belong together

without lengthy explanation.

Aspartame should benefit from that learned intuition where it happens naturally.

However:

Aspartame does not require Portal knowledge.
Aspartame does not hardcode Portal's colors.
Portal terminology does not enter the user model.
XOColor remains authoritative.

A user unfamiliar with Portal loses nothing.

A user familiar with the visual grammar may recognize the relationship immediately.

9. Singular Activity Mode

Chirality does not mean every task requires two hands to be occupied.

Normal Sugar behavior remains valid:

                   ONE TASK
                       │
                    OBJECT
                       │
                  LEFT HAND
                       │
                    Write

One hand may be empty.

The user can simply work.

No empty secondary Activity should occupy screen space.

No permanent reminder of "missing multitasking" is necessary.

Chirality should remain invisible until useful.

10. Establishing a Pair

Suppose the user is reading:

LEFT HAND
Read
paper.pdf

They choose to work with the object using Write.

Aspartame establishes:

LEFT HAND                  RIGHT HAND

Read                       Write
paper.pdf                  notes.odt

HELD                       ACTIVE

The screen contains only Write.

Read remains immediately available.

Press:

F7

and the screen becomes Read.

Write becomes held.

Press:

F8

and Write returns exactly where it was.

This operation must be fast enough that switching hands feels cheaper than managing windows.

11. F7 and F8

The canonical post-migration controls are:

F7 → Left Hand
F8 → Right Hand

These keys select hands directly.

They are not toggles.

Therefore:

F7 F7 F7 → Left
F8 F8 F8 → Right

rather than relying upon hidden toggle state.

Direct selection is more predictable for:

keyboard use
accessibility
automation
testing
controller mapping
muscle memory
12. Current GTK3/GTK4 Spaces

During the GTK4 migration, F7 and F8 retain their current development purpose:

F7 → GTK3 Space
F8 → GTK4 Space

This provides an immediate behavioral oracle:

F7
 ↓
known-good GTK3 behavior

F8
 ↓
GTK4 implementation

The current mechanism already exercises several concepts Chirality will eventually require:

two persistent contexts
only one context visible
explicit switching
focus handoff
preserved state
Activity ownership
shell state transition

This is useful implementation experience.

It does not mean the existing Spaces implementation automatically becomes final Chirality architecture.

13. GTK4 Migration Gate

Do not repurpose F7/F8 while GTK3 remains necessary for parity work.

The migration must first reach an explicit completion gate covering at minimum:

Home
Frame
Journal
Neighborhood
Group
Control Panel
Activity launch
Activity stop
abnormal Activity exit
resume
palettes/context actions
keyboard navigation
accessibility fundamentals
focus behavior
object opening
repeated lifecycle
normal Activity inventory
acceptable visual parity

Only after GTK4 becomes the authoritative normal Sugar implementation may the normal user-facing meaning of F7/F8 change.

GTK3 comparison tooling may remain available through developer/test mechanisms.

Do not destroy the behavioral oracle merely to reclaim two keys.

14. Spaces → Hands Transition

The intended evolution is:

MIGRATION

F7                    F8
│                     │
GTK3 Space             GTK4 Space
│                     │
known-good             candidate
implementation         implementation

After migration:

CHIRALITY

F7                    F8
│                     │
Left Hand              Right Hand
│                     │
Activity               Activity
│                     │
XOColor A              XOColor B

The conceptual behavior remains:

Select one of two preserved contexts.

What changes is what those contexts represent.

During development they represent implementations of Sugar.

After development they represent two Activities participating in one task.

15. Reuse, Do Not Inherit Blindly

After GTK4 migration, audit the Spaces implementation.

Classify every component:

KEEP

Behavior genuinely required by Chirality:

context switching
focus handoff
active-context state
Activity visibility
Activity lifecycle awareness
direct F7/F8 selection
ADAPT

Useful machinery with migration assumptions:

Space ownership
window activation
shell integration
state transitions
keyboard routing
REMOVE

Migration-specific machinery:

GTK3 runtime assumptions
GTK-major comparison logic
preview-only behavior
temporary patch deployment
QEMU-specific workarounds
migration instrumentation

Do not preserve complexity merely because it already exists.

Reuse proven behavior, not accidental architecture.

16. The Third Activity Rule

A chiral task has a hard maximum of two immediate Activities.

If both hands are occupied and another Activity is requested, Aspartame does not create another slot.

It asks which hand to free.

Example:

LEFT HAND                  RIGHT HAND

Read                       Write
paper.pdf                  notes.odt

User requests Browser.

Conceptually:

Browser needs a hand.

[ Let Go of Read  ]
[ Let Go of Write ]
[ Cancel           ]

If Read is released:

LEFT HAND                  RIGHT HAND

Browser                    Write
research                    notes.odt

ACTIVE                     HELD

Read may remain resumable through Sugar/Journal/session state.

It simply no longer occupies one of the two immediate working contexts.

17. "Let Go" Does Not Mean "Destroy"

The distinction between these operations must remain explicit:

LET GO
    remove Activity from immediate hand

STOP
    terminate Activity according to lifecycle

DELETE
    remove persistent object/data where applicable

These are not synonyms.

Replacing a hand should not unexpectedly destroy work.

Sugar's lifecycle and Journal semantics remain authoritative.

18. The Object

The conceptual center of Chirality is not the pair of applications.

It is the work connecting them.

Prefer thinking:

                   report.pdf
                       │
              ┌────────┴────────┐
              │                 │
             Read            Annotate
              │                 │
          Left Hand        Right Hand

rather than:

Read + Annotate

The Activities are capabilities applied to work.

This allows a task to evolve naturally.

19. Linear Workflow

Many ordinary computer workflows are pipelines.

For example:

download
   ↓
inspect
   ↓
move
   ↓
edit
   ↓
convert
   ↓
upload
   ↓
send

Conventional desktop environments frequently represent this as accumulating windows.

Chirality instead represents only the currently meaningful relationship.

Example:

Browser ↔ Read

becomes:

Read ↔ Annotate

becomes:

Annotate ↔ Convert

becomes:

Convert ↔ Mail

The task progresses.

The desktop does not accumulate.

20. Object Handoff

A later Chirality milestone should support explicit semantic transfer between hands.

Candidate language:

Give to Other Hand
Use with…
Open in Other Hand

Example:

LEFT HAND

Browser
report.pdf

     │
     │ Give to Other Hand
     ▼

RIGHT HAND

Read
report.pdf

This should eventually use real object and Activity capabilities.

Do not implement handoff as synthetic drag-and-drop if a meaningful semantic operation is available.

21. Do Not Build the Capability Universe First

Chirality v1 does not require a generalized ontology describing every possible transformation of every object.

Initial implementation may use existing Sugar mechanisms:

Activity metadata
MIME support
Journal objects
open/resume
datastore references
existing launch APIs

A richer capability model may emerge from demonstrated need.

Do not block basic Chirality waiting for it.

22. Journal Relationship

Journal remains the persistent record of work.

Chirality represents immediate working context.

These concepts complement one another:

JOURNAL
"What have I done?"

CHIRALITY
"What am I doing with right now?"

A future Journal may understand relationships created through handoffs:

paper.pdf
   │
   ├── downloaded with Browse
   ├── opened with Read
   ├── referenced while writing notes.odt
   └── shared with Mail

This is desirable.

It is not required for Chirality v1.

Do not accidentally create a workflow database while implementing hand switching.

23. Shell Presentation

Only the Active Hand receives the full Activity surface.

The shell may subtly communicate hand identity through the corresponding XOColor.

Example:

┌─────────────────────────────────────────┐
│ RIGHT HAND • XOColor B                  │
│                                         │
│                                         │
│                 WRITE                   │
│                                         │
│                                         │
└─────────────────────────────────────────┘

Switch:

F7

then:

┌─────────────────────────────────────────┐
│ LEFT HAND • XOColor A                   │
│                                         │
│                                         │
│                  READ                   │
│                                         │
│                                         │
└─────────────────────────────────────────┘

The indication should be recognizable but unobtrusive.

The Activity remains the center of attention.

24. Transition Design

Switching hands should feel immediate.

Possible transition:

F7
 ↓
brief XOColor A edge pulse
 ↓
Left Activity

and:

F8
 ↓
brief XOColor B edge pulse
 ↓
Right Activity

Avoid:

elaborate desktop cubes
long sliding animations
fake physical windows
excessive blur
animations that delay interaction

The transition exists to answer:

Which hand am I using?

not to demonstrate GPU capability.

Respect reduced-motion settings.

25. Accessibility Contract

Chirality must be fully operable without color or pointer input.

Minimum semantic state:

Left Hand:
    Activity
    Object
    held/active state

Right Hand:
    Activity
    Object
    held/active state

Active Hand:
    Left | Right

Example screen-reader announcement:

"Left Hand. Read. paper.pdf."

Switching:

"Right Hand. Write. notes.odt."

Required properties:

deterministic focus
visible focus
no focus traps
correct Activity accessible name
hand state exposed semantically
F7/F8 usable without pointer
no information communicated solely by XOColor
26. Pre-Reader Comprehension

The internal doctrine may be called Chirality.

The UI does not require the user to understand that word.

A pre-reader can learn:

my first color  → this hand
my second color → that hand

and:

F7 → this one
F8 → that one

The interface can teach the relationship visually.

The metaphor should permit a simple explanation:

Your computer has two hands. It can hold something in one while you work with the other.

That is sufficient.

27. Input Beyond Keyboard

F7/F8 are the canonical keyboard controls, not the entire abstraction.

Future mappings may include:

Keyboard
    F7 / F8

Gamepad
    left shoulder / right shoulder

Touch
    explicit hand selector

Accessibility switch
    semantic Left Hand / Right Hand actions

All input methods must invoke the same semantic operations:

activate_left_hand()
activate_right_hand()

Do not encode Chirality as keyboard behavior.

28. Proposed Core State Model

Keep the model independent of presentation.

Conceptually:

class ChiralSession:
    left_hand: Hand | None
    right_hand: Hand | None
    active_hand: Side | None
    task: TaskContext | None

Each hand may reference:

class Hand:
    activity_id
    object_ref
    lifecycle_state

Important invariants:

maximum two hands
maximum one active hand
maximum one visible Activity
held Activity retains valid lifecycle state
hand identity survives Activity replacement
XOColor belongs to hand, not Activity

Do not make:

LeftHand == left-side Gtk.Widget

an architectural assumption.

There is no split-screen geometry to encode.

29. Implementation Phases
Phase 0 — Document Only

While GTK4 migration remains active.

Keep:

F7 → GTK3
F8 → GTK4

Add this doctrine/runbook.

Do not begin Chirality implementation merely because current Spaces resemble it.

Exit condition: GTK4 migration gate satisfied.

Phase 1 — Retire GTK-Major Meaning

Remove GTK3/GTK4 meaning from normal F7/F8 operation.

Preserve developer comparison tooling separately if still useful.

Extract generic context-switching behavior from Spaces.

Proof:

GTK4 Sugar remains healthy
F7/F8 no longer depend upon GTK major
no GTK3 runtime required for normal session
Phase 2 — Two Persistent Activities

Allow two GTK4 Activities to occupy two semantic slots while only one is visible.

Do not add object transfer yet.

Test:

launch A
launch B

F7 → A
F8 → B
F7 → A
F8 → B

A retains state
B retains state

Proof: repeated switching does not alter lifecycle or state.

Phase 3 — Left Hand / Right Hand

Introduce canonical semantic state.

F7 → Left Hand
F8 → Right Hand

Assign XOColor identities.

Expose Active/Held state.

Proof: shell, accessibility layer, and tests agree on hand identity.

Phase 4 — Replacement

Enforce:

No third hand.

When two hands are occupied, launching a third immediate Activity requires choosing a hand to release.

Test both replacement directions.

Test cancellation.

Test preservation/resume of released Activity.

Phase 5 — Object Continuity

Use one real Journal object across two Activities.

Initial target should be intentionally boring.

Example:

PDF
 ↓
Read
 ↓
Other Hand
 ↓
compatible second Activity

Prove:

correct object
correct Activity
correct hand
persistence
resume
no accidental duplication/loss
Phase 6 — Semantic Handoff

Introduce user-facing:

Use with…
Give to Other Hand

using existing Sugar capability information wherever possible.

Do not generalize beyond demonstrated requirements.

Phase 7 — Accessibility and Alternate Input

Complete:

screen-reader announcements
semantic hand state
keyboard-only operation
controller mapping
touch affordance
high-contrast behavior
reduced motion
color-independent identification

Accessibility is a release gate, not polish.

Phase 8 — Journal Enrichment

Only after core Chirality is stable, consider recording useful relationships between:

task
object
Activity
handoff
derived object

Do not turn Journal into a workflow engine unless later evidence justifies one.

30. Runtime Test Matrix

Every implementation phase should exercise:

Scenario	Required result
Only Left occupied	Valid
Only Right occupied	Valid
Both occupied	Valid
Switch Left → Right	State preserved
Switch Right → Left	State preserved
Repeated F7	Deterministically Left
Repeated F8	Deterministically Right
Rapid F7/F8	No lifecycle corruption
Held Activity crashes	Active survives
Active Activity crashes	Held survives
Stop Left	Right unaffected
Stop Right	Left unaffected
Replace Left	Right unaffected
Replace Right	Left unaffected
Cancel replacement	Pair unchanged
Object handoff	Correct object received
Unsupported object	Graceful refusal
Resume	Correct task/object restored
XOColor change	Hand identities remain coherent
31. Failure Tests

Specifically attack:

Activity crashes during hand switch

Activity exits while held

Activity opens modal dialog before becoming held

Activity requests attention while held

both Activities request global shortcuts

object changes while held

object is deleted externally

Activity cannot resume object

Activity launches child process

session exits with both hands populated

screen reader active during switch

controller and keyboard switch simultaneously

XOColor pair has poor contrast

F7/F8 consumed by Activity

F7/F8 consumed by compositor

rapid switching causes focus race

These are bugs to solve.

They are not invitations to invent new subsystems unless necessary.

32. Progress-Over-Saturation Rule

For every Chirality implementation task ask:

Does this make the two-hand model visibly work better, or am I elaborating machinery around it?

Prefer:

Activity switching works
object survives
replacement works
focus works
accessibility works

over:

generic workspace abstraction
generalized keybinding framework
arbitrary pane manager
future capability ontology
complex animation engine
new IPC architecture

If one F-key develops bizarre affinity to some compositor/focus/window-manager edge:

solve the minimum behavior required and continue.

Do not let F7 become a three-week architecture project.

33. Explicit Non-Goals

Chirality is not an excuse to build:

a tiling window manager
arbitrary window layouts
multiple visible Activities
three-hand mode
conventional virtual desktops
tabs containing Activities
desktop window chrome
a workflow programming language
a generalized object graph database
a replacement for Journal
a new compositor
an all-purpose application IPC framework
a reason to retain GTK migration scaffolding forever

These require separate justification.

Chirality does not justify them.

34. Minimum Viable Chirality

The first implementation is successful when this works reliably:

1. Launch Activity A.

2. Assign A to Left Hand.

3. Launch Activity B.

4. Assign B to Right Hand.

5. Only B is visible.

6. Press F7.

7. Only A is visible.
   A's previous state remains intact.

8. Press F8.

9. Only B is visible.
   B's previous state remains intact.

10. Attempt Activity C.

11. Aspartame requires releasing
    Left or Right.

12. Pass one real object between
    the two Activities.

13. Repeat without lifecycle,
    focus, persistence, or
    accessibility failure.

No animation is required.

No sophisticated Journal graph is required.

No new capability system is required.

No split screen exists.

That is Chirality.

35. User Experience Test

A user should naturally reach this rhythm:

I'm writing.

I need my source.

F7.

Read.

I know what I need.

F8.

Write.

I need something from the web.

My source hand can go.

Replace Left with Browser.

F7.

Find it.

F8.

Use it.

At no point should the user think:

"I am managing windows."

At no point should the interface suggest they are expected to visually monitor both Activities simultaneously.

The computer remembers the other context so the user does not have to reconstruct it.

36. Design Test

When considering any future Chirality feature, ask three questions:

Does it preserve singular attention?

If it requires two Activities to be simultaneously visually active, probably reject it.

Does it strengthen the relationship between two Activities?

If not, it probably belongs elsewhere.

Does it require a third immediate context?

If yes, the task probably needs to change context rather than expand Chirality.

37. Final Doctrine
Chirality

Sugar is built around focused Activities rather than collections of windows. Aspartame preserves that principle while recognizing that real work often requires two cooperating contexts.

A task may therefore have a Left Hand and a Right Hand.

Each hand may hold an Activity. Only one hand is active and visible at a time. The other holds its state so it can be returned to immediately.

The hands inherit the user's two-part XOColor identity, providing consistent personal wayfinding without making color the sole carrier of meaning.

Objects may pass between the hands. Either hand may act, supply, receive, reference, or hold. Neither is inherently primary.

When another Activity is needed, the user frees one of the existing hands. Aspartame does not create a third.

Chirality is not split-screen multitasking. It is not tiling. It is not window management.

It is a constraint on immediate attention.

Two hands. One focus. No third hand.