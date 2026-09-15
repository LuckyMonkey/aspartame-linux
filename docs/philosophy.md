# 🧠 Aspartame philosophy:

Aspartame is **Sugar on Arch**: a general-purpose Linux system that preserves
Sugar's Activities, Home, Journal, fullscreen/task-oriented workflow, and
inspectability. It is not an OLPC restoration and must not become Arch with a
conventional panel and application menu.

Simple means reducing conceptual burden, not removing capability. Ordinary
users get understandable Activities; advanced users retain a terminal,
pacman, systemctl, conda, Flatpak, and normal Linux paths.

Python is preferred for user-layer orchestration and Activities. Native
upstream components remain responsible for kernels, drivers, graphics,
PipeWire, CUPS, browsers, codecs, and other low-level infrastructure.

## Four boundaries:

### Human Interface Guidelines (HIG):

The HIG governs **relationships**—orientation, focus, ownership, feedback, and
exit paths—rather than prescribing a fashionable visual kit. A Sugar control
is successful when a learner can predict what it affects and return safely.

### Activities:

An Activity is a context with an identity, process, surface, and Journal
relationship. Its lifecycle is observable from launch through stop. This
prevents “a window appeared” from being mistaken for a complete integration.

### Objects:

An Object is resumable work with metadata and an Activity association. The
Journal is the user's memory of work, not a thin file picker. Search, resume,
and safe retention follow from that model.

### Neighborhood:

Neighborhood is a contextual collaboration view. It can be empty without
being broken, and it must never synthesize people or shared work to make a
screenshot look busy. Local work and peer presence remain distinct.

## Chirality as an engineering tool:

Chirality makes parallel implementations explicit. GTK3 and GTK4 can be
compared like left and right hands, but neither hand is allowed to reach into
the other's toolkit process. Shared semantics cross a narrow service boundary;
rendering, focus, and lifecycle ownership stay local. The result is a novel
combination of **continuity for the user** and **separation for the engineer**:
the shell feels like Sugar while the migration remains testable.
