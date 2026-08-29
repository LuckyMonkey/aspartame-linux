# Aspartame Activity Help Catalog

This catalog describes the Activities currently bundled in the Aspartame image.
Exact capabilities come from each Activity's activity.info file and may differ
between releases. The catalog describes the intended purpose without replacing
the Activity itself.

## How to choose an Activity

Use Home when you want to begin something new. Use Journal when you want to
resume work. Activities are workspaces, not disposable windows. If an Activity
supports saving, its saved state may be represented by a Journal entry or an
exported file; check the Activity before assuming both exist.

## Word, language, and writing Activities

### Across and Down

A crossword-style word puzzle. Build words from letters already provided on
the board. It is useful for vocabulary, spelling, and reasoning from clues.

Try this: choose a puzzle, look for a short word you know, and use the
crossing letters to help with harder words.

### Jumble

A rearrangement puzzle. Put the available pieces into the intended word or
pattern. Start by looking for a recognizable beginning or ending, then use
the remaining pieces to check the whole result.

### Typing Turtle

Typing practice. It teaches hand position and builds speed through repeated
exercises. Progress is practice information, not a judgment.

Use it regularly for short sessions. If a lesson appears to start over, check
whether you launched a new copy or resumed a saved Journal entry.

### FotoToon

A comic and storytelling workspace. Bring pictures into the Activity, arrange
them, and use them to make a visual story.

Use Journal to resume the story. Export or copy important pictures if another
person needs the result outside Sugar.

## Mathematics, science, and programming

### Appel Haken

A mathematical and visual exploration connected with the Appel-Haken
four-color theorem. Explore the supplied construction and inspect how the
visual result changes when you interact with it.

This is an exploration Activity, not a general-purpose proof system.

### IQ

A collection of reasoning and puzzle challenges. Use it for focused problem
solving and pattern recognition. The score or result of one challenge should
not be treated as a measure of a person's worth.

### NumberRush

A quick number-focused game. Use it for short practice with number challenges.
The exact modes depend on the installed Activity version.

### TurtleBlocks

A Logo-inspired programming and drawing Activity. Snap blocks together to
direct a turtle, draw pictures, and explore mathematics and programming.

TurtleBlocks has a low floor and a high ceiling: a first drawing can be small,
while the same blocks can grow into a substantial program.

## Games and puzzles

### BallAndBrick

An arcade game about keeping a ball in play and clearing bricks. It rewards
timing and attention.

### BlockParty

A block-arrangement puzzle. Arrange blocks to solve the presented pattern.
Plan the next move before changing a crowded arrangement.

### Implode

Remove groups of same-colored blocks while the board collapses. A move can
change what groups remain, so look ahead before choosing a group.

### Mancala

A counter-moving board game based on pits. Learn the move rules shown by the
Activity and plan how counters will move around the board.

### Mastermind

A deduction game. Make guesses and use the feedback to narrow down the hidden
arrangement. Treat each guess as information for the next one.

### PlayGo

A Go board-game Activity. Place stones according to the rules and observe
territory, capture, and space. The board is the focus; the surrounding Sugar
shell remains available for navigation.

### Reversi

A board game in which surrounded pieces are turned. Look for moves that change
several pieces and consider the opponent's reply.

### Memorize

A memory-game Activity. Play an existing matching game or create a game for
someone else. Creating the cards is part of the Activity, not an advanced
administration task.

### Maze

Find a route through increasingly difficult paths. Some versions support
playing with another person. Work from the visible path and plan before
committing to a turn.

### JAMClock

A JAM collection Activity for exploring time-related visuals. It is separate
from the passive clock in the Sugar Frame and from the Clock Activity.

### Clock

A configurable clock Activity for exploring ways of displaying time. It is
useful when learning to read different clock faces or experimenting with
presentation. It does not replace the passive time display in the Frame.

## Organization and sharing

### Log

A troubleshooting Activity. Use it when a complicated program or Activity is
not behaving as expected and you need recorded information for a report.

Log output can contain technical details and personal paths. Read it before
sharing it.

### Poll

Create a question and collect responses in a shared Activity context. Make the
question clear and tell participants how their responses will be used.

### Portfolio

Create a slideshow from Journal entries marked as starred. First mark the
work you want to present, then open Portfolio and arrange the presentation.

Portfolio uses deliberate Journal selection; it does not automatically expose
everything in the Journal.

## Help and recovery

If an Activity does not appear:

1. Return to Home and check whether its icon is present.
2. Open Settings and inspect the Activity list when that manager is available.
3. Check the Activity's bundle metadata and launch log.
4. Try a fresh launch separately from resuming a Journal entry.
5. Use Log when a technical report is needed.

If an Activity opens but appears empty, it may be waiting for a new document,
puzzle, board, or Journal object. Do not delete saved work until you have
checked whether the Activity was launched as a new copy.

If the screen stops responding, allow the Activity a moment to finish loading,
then use the Sugar Frame to return Home. A forced process termination should
be a last resort because it can lose unsaved state.

## Relationship to What's This?

The contextual help registry currently has detailed controls for the shell and
Count. Activity-level descriptions are documented here first so future
Activities can register stable IDs without inventing a second vocabulary.

A future target can follow this pattern:

    org.aspartame.clock
    org.aspartame.clock.face
    org.aspartame.clock.format

The first explanation should say what the person can do. Technical
implementation details belong in the deeper documentation.

## Maintainer checklist

When adding an Activity:

- keep its upstream name and bundle identity;
- read activity.info rather than guessing its capabilities;
- add a short plain-language description;
- document save/resume behavior if known;
- document common failure and recovery paths;
- add stable help IDs only for meaningful controls;
- add local anchors before linking them from the registry;
- do not expose GTK class names in primary help;
- do not promise collaboration, printing, or persistence unless tested.
