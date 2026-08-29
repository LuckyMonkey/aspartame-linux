Aspartame Universal Help — Feature Runbook

Working name: What Is This? / Universal Help
Primary UI: persistent ? button in the upper-right of the Sugar interface.

Purpose: At any time, a user can ask Aspartame what something on the screen is by clicking ? and then clicking the unfamiliar thing.

The system explains the selected element immediately in plain language, with optional progressively deeper documentation.

Core Concept

The computer should be able to answer:

“What is this thing, and why would I use it?”

without requiring the user to:

know its name
know what application it belongs to
search a manual
search the web
understand technical terminology
navigate a Help application

Canonical interaction:

                         [?]

User clicks ?

                          ↓

                    HELP MODE

                          ↓

User clicks something unfamiliar

                          ↓

┌─────────────────────────────────────────┐
│ Journal                                 │
│                                         │
│ This is where things you've worked on   │
│ are remembered. You can come back here  │
│ later and continue working on them.     │
│                                         │
│                         [ See more… ]    │
└─────────────────────────────────────────┘
Fundamental Interaction

The ? button should occupy a predictable location in the upper-right.

Clicking it enters Help Mode.

While in Help Mode:

The interface remains visible.
The pointer/state clearly indicates that the user is selecting something to explain.
Meaningful UI elements become valid help targets.
Clicking a target does not activate that target.
Instead, its explanation appears.
The user can choose See more… for detailed documentation.
Help Mode then exits unless intentionally kept active.

The interaction should be:

?
↓
point
↓
click
↓
explanation

Nothing more should be required.

Example: Sugar Home

User clicks ?, then the XO:

You

This represents you and this computer.

The things arranged around it are Activities
you are using or can return to.

[ See more… ]

User clicks ?, then Journal:

Journal

This is where things you've worked on are
remembered.

Use it when you want to find something you
worked on before or continue where you left off.

[ See more… ]

User clicks ?, then an Activity:

Terminal

Terminal lets you give the computer commands
by typing them.

You normally don't need it, but it gives you
direct access to many advanced parts of the
computer.

[ See more… ]
Example: Count
?
↓
Duplicate Layer

Result:

Duplicate Layer

Makes another layer exactly like the one
you're looking at.

This is useful when you're counting a stack
where several layers contain the same
arrangement of objects.

[ See more… ]
Example: Scale
?
↓
Make Maximum

Result:

Make Maximum

Finds the largest complete amount you can
make with the supplies you currently have.

For example, if you're making a recipe and
you run out of flour first, Scale can use the
amount of flour you have to adjust everything
else.

[ See more… ]

No discussion of ratios, scalar values, dimensional analysis, or limiting constraints is necessary at this level.

Those concepts can appear deeper in the documentation.

Explanation Structure

Every help target should provide at least:

TITLE

SHORT EXPLANATION

[ See more… ]

The short explanation should normally answer, in this order:

What is it?

Why would I use it?

What happens if I use it?

Avoid implementation details.

Progressive Documentation

See more… opens documentation directly related to the selected element.

Documentation should progressively increase in complexity.

Recommended structure:

1. What is this?

2. When would I use it?

3. Simple example

4. How to use it

5. Common questions/problems

6. Related features

7. Advanced details

8. Technical details

A user should never have to read sections 7–8 to understand sections 1–4.

Plain-Language Requirement

First-level help is explicitly written for someone with no assumed computer knowledge.

Bad:

The Journal provides access to datastore-backed
persistent Activity objects.

Good:

The Journal remembers things you've worked on
so you can find them and continue later.

Bad:

This control modifies the global scalar applied
to typed quantities.

Good:

This changes how much of everything in the list
you want to make.

Technical terminology is allowed in deeper documentation when it becomes useful.

It should be introduced and explained rather than assumed.

No Patronizing Language

Plain language does not mean childish language.

Never use language such as:

Don't worry!
It's easy!
For beginners...
Even Grandma can do it!
Simply...
Obviously...

Help should be factual, calm and respectful.

The user is asking the computer for information, not admitting incompetence.

Global Availability

Universal Help should be provided by the Sugar shell whenever practical.

It should work across:

Home
Frame
Journal
Neighborhood
Group
Activities
system interfaces
Aspartame-specific components

Individual Activities provide information about their own controls.

The shell provides the common interaction.

Activity Help Interface

Aspartame Activities should eventually have a standard mechanism for registering help targets.

Conceptually:

help:
    scale-slider:
        title: "Scale"

        short:
            "Changes how much of everything in
             your list you want to make."

        document:
            "help/scale.md#changing-the-scale"

Exact implementation format is not prescribed by this runbook.

It could ultimately use Python APIs, metadata, GTK widget properties, external structured files, or another mechanism.

The important architectural relationship is:

GTK/UI element
      ↓
stable help identifier
      ↓
short explanation
      ↓
documentation target
Help IDs

Help targets should use stable semantic identifiers rather than fragile screen coordinates.

Example:

org.aspartame.scale.scale-factor
org.aspartame.scale.make-maximum
org.aspartame.count.duplicate-layer

org.sugarlabs.shell.home
org.sugarlabs.shell.journal

Do not identify controls as:

button_7
widget_42
x=177,y=62

The documentation should survive reasonable UI/layout changes.

Offline First

Core help must work without an Internet connection.

At minimum, local Aspartame and Sugar functionality must have:

short explanation
+
local detailed documentation

External links may supplement local documentation but must not replace it.

A computer that has lost networking is often precisely when help is needed.

Help Mode Visual Behavior

Entering Help Mode should be visually obvious without obscuring the interface.

Possible treatments include:

changed pointer
subtle highlighting of selectable elements
small ? indicator near pointer
restrained overlay treatment

Do not dramatically recolor the entire interface.

The user needs to clearly see the thing they are asking about.

Hover may preview which element will be selected, but hover must not be required.

Activation Safety

While Help Mode is active, clicking a help target should explain it rather than perform its normal action.

For example:

NORMAL MODE

[ Delete Layer ]
      ↓
deletes layer

versus:

HELP MODE

[ Delete Layer ]
      ↓
explains Delete Layer

This makes it safe to ask about destructive controls.

Exiting Help Mode

Support predictable exits:

Esc

click ? again

select an item and receive its explanation

Do not trap the user in Help Mode.

Missing Help

Not every third-party application will initially provide Aspartame help metadata.

Missing documentation must fail gracefully.

Example:

No explanation yet

Aspartame doesn't have an explanation for
this control yet.

If basic accessible GTK information is available, it may be used to provide useful context.

Do not invent explanations based solely on a widget's appearance.

Nested Targets

UI elements may contain other explainable elements.

Example:

Activity toolbar
    ↓
Scale control
    ↓
percentage field

Help selection should prefer the most specific meaningful target under the pointer.

But explanations can link upward:

Percentage

Enter the exact amount you want the whole
list scaled to.

Part of: Scale control

[ See more… ]
Keyboard Accessibility

Universal Help must not depend exclusively on pointing devices.

A keyboard workflow should eventually permit:

activate Help Mode
        ↓
move between help targets
        ↓
select
        ↓
read explanation

Normal GTK focus/navigation should be reused where practical.

Screen readers should be able to read help content.

Documentation Architecture

Help content should live alongside, or be versioned with, the component it documents.

Conceptually:

Activity
├── code
├── UI
├── help metadata
└── help/
    ├── overview.md
    ├── controls.md
    └── advanced.md

This avoids having documentation silently drift away from the software version actually installed.

Development Rule

New Aspartame controls should normally require Universal Help metadata.

A useful review question is:

Can we explain this control clearly to someone who doesn't already know what it does?

If the explanation requires extensive jargon just to describe the basic action, reconsider the UI itself.

Universal Help therefore doubles as a design-quality test.

Relationship to Tooltips

Universal Help does not eliminate conventional tooltips or Sugar palettes.

They serve different purposes.

Tooltip/palette:
"What is this called?"

Universal Help:
"What is this, why would I want it,
and what will it do?"

A normal tooltip might say:

Duplicate Layer

Universal Help says:

Duplicate Layer

Makes another layer exactly like this one.

Use this when several layers of what you're
counting have the same arrangement.
Relationship to Full Documentation

Universal Help is also not the manual.

It is the bridge between the interface and the manual:

thing on screen
      ↓
?
      ↓
plain-language explanation
      ↓
See more…
      ↓
specific documentation
      ↓
advanced/technical information

Never make See more… dump the user at the front page of a giant generic manual when a specific documentation section exists.

Sugar Design Compatibility

This feature should extend Sugar rather than introduce a conventional Help Center metaphor.

Sugar already emphasizes direct manipulation, discoverability, palettes, progressive complexity and contextual interaction.

Universal Help applies those ideas to learning the interface itself:

Point at the thing you don't understand.

This is preferable to simplifying unusual Sugar concepts until they resemble conventional desktops.

For example, Journal does not need to become a conventional file manager merely because new users understand folders.

Instead:

?
↓
Journal
↓
"This is what Journal means."

The unusual concept remains learnable.

MVP

Version 1 should implement:

Global ? control in the upper-right.
Enter/exit Help Mode.
Clear Help Mode pointer/state.
Select a UI element without activating it.
Display title and plain-language explanation.
See more… action.
Local detailed documentation.
Stable help identifiers.
Help targets for core Sugar Home/Frame elements.
Graceful handling of undocumented targets.
Escape/cancel behavior.
Keyboard-accessible path where practical.

Then instrument one Activity completely before attempting to document everything.

Count or Scale would be ideal reference Activities.

Non-Goals for MVP

Do not initially add:

AI-generated explanations
Internet search
chatbot interface
tutorial popups everywhere
forced onboarding
animated walkthroughs
video tutorials
telemetry
user skill levels
“beginner/expert mode”
automatic interface simplification

Universal Help should remain useful even if none of those ever exist.

Critical Design Laws

Help is available where the confusion happens.

The user does not need to know the name of something before asking about it.

Explain purpose before implementation.

Assume no technical vocabulary at the first level.

Plain language must not become patronizing language.

Help Mode must never accidentally activate the selected control.

Detailed help opens directly to the relevant subject.

Core help works offline.

Activities own explanations for their own concepts.

The shell owns the universal interaction.

Missing documentation fails gracefully.

The ? should remain visually restrained and predictable.

Do not simplify away useful unconventional Sugar concepts merely because they require explanation.

One-Sentence Specification

Universal Help is an always-available Sugar interaction where the user clicks ?, selects anything on the screen, and immediately receives a plain-language explanation of what it is and why they might use it, with direct access to progressively deeper offline documentation.

MVP Success Test

Give Aspartame to someone who has never used Sugar.

Do not explain Journal.

Ask them to determine what Journal does.

They should be able to:

click ?
   ↓
click Journal
   ↓
read:
"This is where things you've worked on
are remembered..."
   ↓
understand enough to decide whether
they want to open it

If they have to search the web, open a manual, know the word “Journal” beforehand, or ask another person what the icon means, Universal Help has failed its primary purpose.