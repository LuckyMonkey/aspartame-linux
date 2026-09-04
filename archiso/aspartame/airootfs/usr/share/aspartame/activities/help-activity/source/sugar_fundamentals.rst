=================
Sugar Fundamentals
=================

Sugar is a learning environment, not a traditional desktop. It is designed
around curiosity, making things, sharing ideas, and reflecting on what you
have done. The central idea is simple: **Activities are things you do; the
Journal remembers what you did.**

The learning cycle
------------------

1. **Choose** an Activity from Home.
2. **Make** something, alone or with other people.
3. **Share** the Activity when collaboration is useful.
4. **Reflect** in the Journal, then continue or begin something new.

There are no required folders, double-clicks, or save dialogs. Sugar still
uses ordinary files underneath, but presents them as meaningful objects and
records the Activity that created them.

The four main views
-------------------

Sugar uses a zooming interface. Each view fills the screen and has one job:

* **Home** is your personal starting point. The ring or list contains
  Activities, search finds an Activity by name, and the user icon opens your
  personal menu.
* **Neighborhood** shows nearby wireless networks and people. A network icon
  represents a connection; a person icon represents a learner who may invite
  you to collaborate.
* **Group** shows the people in your current group and shared work.
* **Activity** is where you create, explore, read, write, draw, calculate, or
  program.

Use the Home, Neighborhood, and Group keys, or reveal the Frame, to move
between views. Returning Home normally leaves an Activity ready to resume.

The Frame and top bar
---------------------

Move the pointer to an edge of the screen, or press the Frame key, to reveal
the Frame. It contains status indicators, notifications, the clipboard, open
Activities, friends, and collaborators. Activity controls belong in the
Activity toolbar; global controls belong in the Frame. The **Stop** control in
the upper-right closes the current Activity instance. Sugar usually saves
continuously before stopping.

Activities, bundles, and instances
----------------------------------

An Activity is more than a program window. Its bundle contains an identity
(`activity.info`, name, icon, and version), code and resources, Journal
integration, and optional collaboration support. Launching an Activity creates
an **instance**. Two instances of one Activity can have different Journal
entries and collaborators, so opening Write again can start a new document.

The Journal: Sugar's memory
---------------------------

The Journal is both a history and a workspace. It records objects created by
Activities and events such as downloads, recordings, and shared work. Entries
may include a title, description, tags, preview, timestamp, and creator.

Use the Journal to search by title, text, tag, or Activity; sort by date or
type; resume an entry in its original Activity; and copy important work to
removable media. **Erase** is different from stopping an Activity and may
remove the saved object. Saving is normally automatic; an Activity's export
button creates an additional copy for another computer.

Sharing and collaboration
--------------------------

An Activity may be private, shared with a group, or joined by invitation.
Sharing exposes the Activity session and the objects that Activity chooses to
share, not every file on the computer. Check the Activity toolbar and Group
view before sharing. If the network disappears, continue privately and save to
the Journal; local work should remain available.

Learning through source and reuse
---------------------------------

Many Activities offer **View Source**, which opens the code or document that
produced what you see. **Duplicate** makes a personal copy for experiments.
Try this learning loop: run an Activity, inspect its source, duplicate it,
change one small thing, compare the result, and keep the experiment in the
Journal. Sugar is designed so learners can eventually modify their tools.

Controls and keyboard habits
----------------------------

Large icons, color, and shape make controls recognizable without reading every
label. Hover for a tooltip. Common habits are: reveal the Frame; use Home to
return to Home; use arrows and Enter in lists; use Escape to dismiss a palette
or dialog; and use Stop to finish an Activity instead of killing its process.
Exact keys vary by hardware and Activity; the current toolbar is authoritative.

Privacy, permissions, and maintenance
-------------------------------------

Activities run with the permissions needed for their purpose, not as a general
administrator. Installing or removing an Activity may require an approval
prompt. Read the request, type its confirmation word exactly, or choose
**Cancel**. Do not erase Journal entries, system Activities, or profile data
just to fix a visual problem. Preserve important work before maintenance.

When something goes wrong
-------------------------

1. Wait briefly; an Activity may be loading or saving.
2. Open the Frame and check whether it is still running.
3. Stop and resume it from its Journal entry.
4. Check the network icon before diagnosing collaboration.
5. Use Log Activity and record the Activity name, action, time, and error.

Do not repeatedly delete Journal data to cure a crash. Record the error first
so a teacher, maintainer, or administrator can repair the bundle while keeping
evidence.

For parents, teachers, and mentors
----------------------------------

The most useful help is a question, not a takeover: “What were you trying to
make?” and “What do you notice?” Encourage learners to share, explain, and
iterate. A Journal entry records a learning process, not only a final answer.

Further reading
---------------

* :doc:`/sugar_ui` — the zooming interface and design principles.
* :doc:`/home_view` — finding and organizing Activities.
* :doc:`/journal` — searching, resuming, and protecting your work.
* :doc:`/collaborating` — sharing with friends and groups.
* :doc:`/exiting_activities` — stopping an Activity safely.
* :doc:`/glossary` — definitions of Sugar terms.

Where to go next
----------------

* :doc:`/sugar_architecture` explains the shell, toolkit, datastore, and
  Activity lifecycle.
* :doc:`/sugar_accessibility` explains readable screens, focus, speech, and
  inclusive collaboration.
* :doc:`/what_is_an_activity` introduces Activity bundles in more detail.
* :doc:`/launching_activities` covers practical launch and resume steps.
