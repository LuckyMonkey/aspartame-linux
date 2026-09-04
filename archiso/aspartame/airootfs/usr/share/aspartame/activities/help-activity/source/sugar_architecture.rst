=================
How Sugar Works
=================

This chapter describes the pieces underneath the Sugar interface. You do not
need to be a programmer to use it, but understanding the pieces makes support,
maintenance, and Activity development much easier.

From power-on to Home
---------------------

When Sugar starts, the operating system logs in the learner and starts the
Sugar shell. The shell owns the screen-wide experience: the top bar, Frame,
Home, Neighborhood, Group, notifications, and the Activity registry. It then
starts the Journal datastore and discovers installed Activity bundles.

Home reads each bundle's ``activity.info`` metadata. That metadata supplies the
Activity name, icon, version, unique bundle ID, launch command, license, and
supported categories. The shell can therefore show an Activity before running
it. The Activity's code starts only when the learner opens it.

What happens when an Activity launches
--------------------------------------

1. Home or the Journal asks the shell to launch a bundle.
2. The shell creates a unique Activity ID and a Journal entry when appropriate.
3. The Activity launcher builds a private environment containing the bundle
   path, Activity ID, profile, and Journal locations.
4. The Activity process connects to Sugar's session services and creates its
   window or canvas.
5. The shell places the Activity in the Activity list and gives it focus.
6. The Activity reads an existing Journal entry, or starts with a new object.

The Activity should not assume that it owns the entire desktop. Sugar provides
its toolbar, collaboration context, lifecycle, and persistence boundary.

The Activity lifecycle
----------------------

An Activity normally moves through these states:

* **Discovered** — its metadata is visible to Home.
* **Starting** — the launcher created the process and assigned an ID.
* **Active** — its window is visible and it can accept input.
* **Inactive** — another Activity has focus, but this Activity may remain alive.
* **Saving** — Sugar requests a Journal snapshot before stopping or shutdown.
* **Stopped** — the process has exited and the Journal entry remains resumable.

A well-behaved Activity treats stop as a normal event. It finishes pending
writes, releases network or camera resources, and exits without deleting the
Journal object. A crash is different from a stop: capture its log before
relaunching so the cause is not lost.

The shell, toolkit, and datastore
---------------------------------

Sugar is easiest to understand as three cooperating layers:

* **Shell (Jarabe)** manages views, presence, the Frame, Activity discovery,
  launch, focus, and stop.
* **Toolkit** provides Activity windows, toolbars, palettes, Journal helpers,
  icons, notifications, and collaboration APIs.
* **Datastore** stores Journal metadata and object content, indexes text, and
  supplies the resume/save contract.

The layers communicate through Python APIs and session services. A GTK3 or
GTK4 Activity should use the toolkit boundary instead of reaching into shell
internals. This keeps Activities portable across Sugar versions.

GTK3, GTK4, and the display boundary
------------------------------------

Older Activities use GTK3 and ``sugar3``. Newer ports use GTK4 and ``sugar4``.
They can coexist when each Activity receives the toolkit it was built for.
GTK4 Activities may render through a Wayland compositor embedded by the shell,
while the shell itself can still appear as a normal desktop window. This
boundary lets a distribution modernize one Activity at a time.

An Activity should not mix GTK3 and GTK4 widgets in one process. If a port
needs a legacy component, isolate it behind a separate process or replace it
with a native widget. Importing a library before selecting its GTK version can
also make introspection choose the wrong API.

Profiles and private data
-------------------------

A Sugar profile identifies the learner and stores preferences, favorites,
keys, and Journal paths. The profile is separate from the installed Activity
bundle. Reinstalling an Activity should not erase the learner's Journal.

For testing, use a private ``SUGAR_HOME`` or profile directory. Never point a
preview build at a learner's production profile unless you have a backup. A
private D-Bus session and runtime directory prevent test services from
colliding with the running desktop.

Services and session communication
----------------------------------

Sugar starts session services on demand. Common services include the datastore,
presence/collaboration, notifications, and desktop portals. They are scoped to
the learner's session and are not system administrators. If a service is
unavailable, an Activity should degrade gracefully and explain what remains
possible offline.

D-Bus names and object paths are contracts. A service that changes its name
without updating the toolkit can look like a missing Journal or a broken
collaboration feature. Logs should include the service name, Activity ID, and
operation being attempted.

Installing and removing Activities
----------------------------------

An installed Activity is normally a directory ending in ``.activity`` under a
system or user Activity path. The directory is a bundle, not a Journal entry.
Removing the bundle makes the Activity unavailable for new launches; it does
not automatically remove existing Journal objects created by that Activity.

System-wide changes may require an approval prompt. Confirm the Activity name
and requested action, then type the explicit confirmation word or choose
Cancel. Never work around a missing authorization by copying files into a
system directory. Use the Activity Manager or a documented administrator
workflow so the registry and package records stay consistent.

Logs and diagnosis
------------------

The Log Activity is the first place to look for a reproducible failure. Record:

* the Activity name and version;
* whether it was launched from Home, the Journal, or a shared invitation;
* the exact action before the failure;
* network state and connected collaborators;
* the time and any visible error message.

A useful report separates symptoms from guesses. “Write stopped after opening
an existing Journal entry” is more useful than “the Journal is broken.”

For Activity authors
--------------------

A portable Activity should declare metadata accurately, use toolkit APIs for
lifecycle and Journal access, avoid blocking the GTK main loop, and clean up
on stop. Save incrementally, tolerate offline mode, expose keyboard focus,
and provide accessible names for important controls. Test a new instance, a
resumed Journal entry, a second instance, collaboration loss, and Stop.

When a port is ready, test it in this order: toolkit import, metadata discovery,
launch, first pixels, text input, Journal save/resume, sharing, stop, and
relaunch. A screenshot proves appearance; a log and a resumed entry prove that
persistence works.
