# Universal Help: What's This?

## Purpose

What's This? is a Sugar shell capability, not a Help Activity. The user
activates ?, then clicks an unfamiliar control. The click is consumed, the
control does not activate, and a short plain-language explanation opens in a
Sugar palette. See more... opens the matching local documentation anchor.

## Archaeology

The existing Frame navigation is built by
sugar-overlay/src/jarabe/frame/zoomtoolbar.py, class ZoomToolbar. It creates
Home, Group, Neighborhood, Activity, and Journal controls. Sugar palettes use
sugar3.graphics.palette.Palette; Frame controls use
jarabe.frame.frameinvoker.FrameWidgetInvoker.

Sugar starts from /usr/local/bin/aspartame-x-session, normally through the
X11 session and dbus-run-session, and runs python3 -m jarabe.main. The
development image places overlay source at /mnt/aspartame-dev/sugar/src
through PYTHONPATH. The help registry is installed at
/usr/share/aspartame/aspartame_help.py so shell and Activity processes share
the same small metadata source.

Count is a Sugar Activity at
packages/aspartame-count/Count.activity/activity.py. Its controls already
have stable names such as org.aspartame.count.total and
org.aspartame.count.layer.copy.

## Metadata API

The registry is deliberately small. A Target contains:

- id: stable semantic identifier
- title: palette title
- short_description: suitable for a future normal tooltip
- explanation: the first plain-language answer
- documentation: optional anchor in the local HTML document

Example:

    import aspartame_help
    aspartame_help.guard(widget, "org.aspartame.count.layer.copy")

For an Activity-specific target, add or register a Target in the registry with
the same metadata that future Activity Manager and documentation tooling can
consume. Do not derive user-facing text from GTK class names.

## Interaction

The shell ? control stores a short-lived mode marker in
/tmp/aspartame-whats-this. Registered widgets install a button-press guard.
When the marker exists, the guard shows the target palette and returns True,
preventing the ordinary GTK clicked/activate path. A successful lookup clears
the marker. Escape clears it too. Shell startup clears stale state.

This first implementation covers existing Frame navigation controls and Count
controls. The most specific nested widget wins because guards are attached to
the actual control rather than its containing Activity.

Missing metadata is safe: the user sees "There isn't an explanation for this
yet." and developers receive a log entry. GTK containers are not registered
automatically.

## Offline documentation

/usr/share/aspartame/docs/universal-help.html is a static, versioned file with
stable anchors. It requires no network, server, database, or package manager.
Documentation targets are anchors such as count#total; the palette opens the
matching file URL. The current file groups anchors by shell and Count.

Each page should progressively answer what something is, when to use it, an
example, common problems, related concepts, and technical detail where useful.

## Styling and accessibility

The ? control is placed inside the existing Frame toolbar and does not create
a panel or taskbar. Its tooltip explains the mode before activation. The mode
is also represented by changed tooltip text and behavior, not color alone.
Escape is handled at the shell window level. Stable semantic IDs leave room
for keyboard focus and screen-reader integration later.

This pass does not make every arbitrary widget help-aware. It also uses a
temporary marker rather than a new D-Bus service, so the mode is local to the
development session and is cleared when the shell starts.

## Developer loop

After changing source:

    make sugar-patch-check
    DISPLAY=:0 SSH_ASKPASS=/tmp/aspartame-askpass       SSH_ASKPASS_REQUIRE=force make sugar-reload
    make sugar-info
    make sugar-logs
    make sugar-screenshot

A fresh ISO is needed when changing the installed help module or offline HTML.
The reload script stages the module to the running guest before restarting
only the Sugar shell. Verify shell PID, imports, health output, and screenshot;
source diffs alone are not proof.

## Current targets

The registry currently documents ?; Home; Journal; Neighborhood; Group;
Frame/Activity navigation; Count; Total; Previous layer; Next layer; Current
layer; New layer; and Copy layer. Count may add more controls later without
changing the interaction mechanism.
