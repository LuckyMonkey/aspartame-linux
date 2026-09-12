# GTK4 Activity conversion and port runbook

Status: active migration work (2026-09-06)

This runbook covers one GTK4 Activity from source checkout through launch,
D-Bus registration, interaction, stop, and evidence. It is intentionally
separate from the stable GTK3 runtime and from the GTK4 Home/Frame work.

The current preview has verified Home rendering, GTK3/GTK4 Spaces switching,
and Sugar-styled GTK4 palettes. Activity launch/stop is still pending: the
migrated Log Activity currently exits before registering its Activity D-Bus
service. Do not mark an Activity usable because its source imports or because
Home can display its icon.

## 1. Boundary and ownership

The lifecycle under test is:

```text
Home icon
  -> Jarabe ActivityFactory
  -> sugar-activity4
  -> ActivityService on the private D-Bus session
  -> Casilda Wayland socket
  -> GTK4 Activity window

Stop
  -> ActivityService.Close or Sugar Stop action
  -> Activity.close()
  -> release Activity D-Bus name
  -> remove window and quit application when last window closes
```

The preview owns the launcher, private D-Bus session, private runtime
directory, and Casilda socket. The Activity owns its GTK4 window, toolbar,
storage behavior, and clean shutdown. The host X11 display is only the
development desktop containing the preview shell; it is not the Activity's
rendering backend.

The expected identity is:

| Boundary | Expected value |
|---|---|
| Preview root | `/home/aspartame/Development/gtk4-preview` |
| Activity launcher | `$GTK4_ROOT/venv/bin/sugar-activity4` |
| Activity toolkit namespace | `sugar4` |
| Activity display backend | Wayland through Casilda |
| Activity bus name | `org.laptop.Activity<SUGAR_ACTIVITY_ID>` |
| Activity object path | `/org/laptop/Activity/<SUGAR_ACTIVITY_ID>` |
| Activity root | `$SUGAR_HOME/$SUGAR_PROFILE/<bundle_id>/<activity_id>` |

Do not point the launcher at the stable `sugar3` installation and do not
reuse the stable GTK3 profile.

## 2. Preflight

Run the build and launch steps inside the Aspartame development VM as the
desktop user unless a command explicitly says otherwise:

```bash
export GTK4_ROOT=/home/aspartame/Development/gtk4-preview
export PREVIEW=/mnt/aspartame-dev

test -x "$GTK4_ROOT/venv/bin/python"
test -x "$GTK4_ROOT/venv/bin/sugar-activity4"
test -f "$GTK4_ROOT/PINS.tsv"
test -f "$GTK4_ROOT/prefix/share/sugar/activities/Log.activity/activity/activity.info"

"$PREVIEW/scripts/sugar-gtk4-check.sh"
"$PREVIEW/scripts/sugar-gtk4-runtime-check.sh" gtk3
```

If the preview has not been initialized:

```bash
"$PREVIEW/scripts/sugar-gtk4-init.sh"
"$PREVIEW/scripts/sugar-gtk4-build.sh"
```

A failed preflight is a stop condition. Fix the environment or record the
missing dependency; do not add Activity workarounds to make a broken preview
look healthy.

## 3. Classify the Activity before porting

Record these facts in the Activity matrix before changing code:

- bundle ID, activity version, license, and exact source SHA;
- the `exec` line in `activity/activity.info`;
- whether the source imports `sugar3`, GTK3, WebKitGTK 4, Telepathy, or
  other unavailable APIs;
- the Activity class and window construction path;
- Journal/datastore reads and writes;
- toolbar buttons, palettes, drag-and-drop, clipboard, and collaboration;
- the intended stop/resume behavior.

Use a separate port branch or an ordered preview patch. Keep the upstream
Activity checkout reproducible; do not edit a package-owned system copy.

A source-only result is not a runtime result. The matrix should keep
`Import/build`, `D-Bus launch`, `toolbar/palette`, `Journal/storage`,
and `stop/resume` as separate fields.

## 4. Port the smallest executable surface

Port in this order:

1. **Entrypoint** — use GTK4 and `sugar4`; remove GTK3-only imports from the
   executed path.
2. **Application/window** — create the Activity through the GTK4 Activity
   base/application boundary, not a second top-level window.
3. **First paint** — show a minimal valid Activity surface with its bundle
   identity visible in logs.
4. **Toolbar and Stop** — use GTK4 buttons/controllers and the canonical Sugar
   Stop action.
5. **Activity behavior** — add the real controls and storage one behavior at a
   time.
6. **Resume/close** — test Journal identity, saved state, D-Bus release, and
   process exit.

Mechanical GTK3-to-GTK4 changes are acceptable when isolated:

| GTK3 pattern | GTK4 direction |
|---|---|
| `pack_start` / `add` | `append`, `set_child`, or `insert_child_after` |
| event masks and button events | `Gtk.GestureClick`, `Gtk.EventControllerKey`, motion controllers |
| `Gdk.Screen` | `Gdk.Display` and monitor APIs |
| `Gtk.Menu` | `Gtk.Popover` or menu models |
| `Gtk.TreeView` renderers | `Gtk.ListView`/`Gtk.ColumnView` row widgets |
| `Gtk.Clipboard` | `Gdk.Clipboard` |
| `show_all()` | explicit visibility and widget hierarchy |

Do not permanently recreate GTK3 renderers or add broad compatibility aliases
when a GTK4-native row/widget boundary is the actual target. Keep Journal,
collaboration, window ownership, and persistence changes in separate commits.

## 5. Activity D-Bus lifecycle contract

The Activity must acquire its private D-Bus service before it is considered
launched. A visible window without a registered service is a failed Activity
launch.

The proof must include bus-name release and process exit, not only a visible
surface.

The service must provide:

- `SetActive(bool)`, forwarding focus/active state to the Activity;
- `Close()`, forwarding to the Activity close path;
- deterministic cleanup of the object and well-known bus name;
- no second close crash if the window, Stop button, and shell all request
  shutdown;
- a clean application quit after the Activity's last window is removed.

The launcher must provide:

- a unique `SUGAR_ACTIVITY_ID`;
- `SUGAR_ACTIVITY_ROOT` with `instance`, `data`, `tmp`, and `logs`;
- the bundle path and metadata environment;
- a private Wayland socket inherited by the child;
- captured stdout/stderr under the Activity root;
- a child-watch path that reports abnormal exit to the shell.

When registration fails, preserve the first traceback and the Activity log. Do
not convert the failure into a generic Home icon or a successful-looking
timeout.

## 6. Build and launch ladder

Build the preview after each meaningful patch boundary:

```bash
"$PREVIEW/scripts/sugar-gtk4-build.sh"
```

Use the two-Space controller so the stable desktop and preview remain
separately observable:

```bash
"$PREVIEW/scripts/sugar-gtk4-space.sh" setup
"$PREVIEW/scripts/sugar-gtk4-space.sh" gtk4
"$PREVIEW/scripts/sugar-gtk4-runtime-check.sh" gtk4
```

Then launch the Activity from the GTK4 Home icon. For a first-paint probe,
use the smallest Activity surface available; do not begin with Journal,
collaboration, or a large data migration.

After the icon activation:

```bash
gtk4_pid=$(pgrep -u "$(id -u)" -f   "^$GTK4_ROOT/venv/bin/python $GTK4_ROOT/sources/sugar/src/jarabe/main.py$" |
  head -n1)
test -n "$gtk4_pid"

activity_pid=$(pgrep -u "$(id -u)" -f   'sugar4\.activity\.activityinstance' | head -n1 || true)
test -n "$activity_pid"
```

If `activity_pid` is empty, the Activity did not launch. Inspect the preview
log and the Activity's `logs/activity.log` before changing UI code.

## 7. Verify the private D-Bus service

Read the bus address from the running GTK4 shell or Activity; do not use the
stable session bus accidentally:

```bash
bus_address=$(tr '\0' '\n' < "/proc/$activity_pid/environ" |
  sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p')
activity_id=$(tr '\0' '\n' < "/proc/$activity_pid/environ" |
  sed -n 's/^SUGAR_ACTIVITY_ID=//p')
test -n "$bus_address"
test -n "$activity_id"

DBUS_SESSION_BUS_ADDRESS="$bus_address"   dbus-send --print-reply   --dest=org.freedesktop.DBus   /org/freedesktop/DBus org.freedesktop.DBus.ListNames |
  grep "org.laptop.Activity$activity_id"

DBUS_SESSION_BUS_ADDRESS="$bus_address"   dbus-send --print-reply   --dest="org.laptop.Activity$activity_id"   "/org/laptop/Activity/$activity_id"   org.freedesktop.DBus.Introspectable.Introspect >/tmp/activity-introspection.xml
```

A missing name means the launch contract is not complete, even if a process or
window exists. A missing object path means the service object was not exported
correctly.

## 8. Test interaction and Stop separately

Run these as separate checks:

1. focus the Activity and verify its toolbar;
2. open one Sugar palette and verify it is anchored to the owning widget;
3. perform one Activity-specific action;
4. save or mutate one piece of state;
5. invoke the Activity's visible Stop action;
6. verify the Activity process exits and its bus name disappears;
7. relaunch and verify the expected state/resume behavior.

For a diagnostic stop when the visible control is not yet usable:

```bash
DBUS_SESSION_BUS_ADDRESS="$bus_address"   dbus-send --print-reply   --dest="org.laptop.Activity$activity_id"   "/org/laptop/Activity/$activity_id"   org.laptop.Activity.Close
```

Then verify:

```bash
for attempt in $(seq 1 50); do
    kill -0 "$activity_pid" 2>/dev/null || break
    sleep 0.1
done
! kill -0 "$activity_pid" 2>/dev/null
! DBUS_SESSION_BUS_ADDRESS="$bus_address"   dbus-send --print-reply   --dest="org.freedesktop.DBus"   /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null |
  grep -q "org.laptop.Activity$activity_id"
```

A process that disappears but leaves the bus name, or a bus name that
disappears while the process remains, is a lifecycle failure.

## 9. Evidence package

For every Activity milestone, retain:

```bash
mkdir -p reports/gtk4/activities/<bundle-id>
cp "$GTK4_ROOT/logs/"* reports/gtk4/activities/<bundle-id>/ 2>/dev/null || true
find "$GTK4_ROOT/runtime/home" -path '*/logs/activity.log' -type f   -exec cp --parents {} reports/gtk4/activities/<bundle-id>/ \; 2>/dev/null || true
sha256sum reports/gtk4/activities/<bundle-id>/*   > reports/gtk4/activities/<bundle-id>/SHA256SUMS 2>/dev/null || true
"$PREVIEW/scripts/sugar-gtk4-runtime-check.sh" gtk4   > reports/gtk4/activities/<bundle-id>/runtime-check.txt
```

Also record:

- shell, toolkit, datastore, Casilda, and Activity SHAs from `PINS.tsv`;
- exact build and launch commands;
- whether the Activity was launched from Home or by a diagnostic command;
- screenshot of the Activity surface and Stop/palette state where visual behavior
  matters;
- first failure traceback, if the test failed;
- explicit tested/not-tested rows in `GTK4_ACTIVITY_MATRIX.md`.

Do not overwrite a previous evidence package. Use a timestamp or a new
milestone directory.

## 10. Acceptance gate

An Activity can be marked **usable** only when all applicable checks pass:

- [ ] exact source SHA is recorded;
- [ ] import/build succeeds in the isolated venv;
- [ ] Home activation starts one Activity process;
- [ ] Activity D-Bus name and object path are present;
- [ ] private Wayland client surface appears;
- [ ] toolbar and canonical Stop action work;
- [ ] one real Activity behavior works;
- [ ] Journal/datastore behavior works if the Activity uses it;
- [ ] palette/menu behavior is Sugar-consistent;
- [ ] close releases the bus name and exits the process;
- [ ] relaunch/resume behavior is verified;
- [ ] no new fatal traceback appears in the retained logs;
- [ ] screenshot/runtime evidence is retained;
- [ ] stable GTK3 and isolation checks still pass.

If a check is not applicable, write why. Do not silently mark it passed.

## 11. Failure routing

| Symptom | First place to look | Do not do first |
|---|---|---|
| Home icon does nothing | Jarabe launch log and bundle command | change toolbar CSS |
| Activity process exits immediately | Activity `logs/activity.log` and first traceback | add a fake window |
| No `org.laptop.Activity...` name | `ActivityService` construction and private bus address | inspect the stable bus |
| Window exists but no Wayland surface | Casilda socket and inherited environment | install host Wayland |
| Stop hides UI but process remains | `_complete_close`, application window list, child PID | kill it manually and call pass |
| Journal row is empty/stale | datastore D-Bus/query path | hard-code sample rows |
| palette appears detached | Popover parent/pointing widget | add another top-level window |
| GTK3 namespace error | process environment and import order | weaken stable `sitecustomize` |

The next valid milestone is a single migrated Activity that passes the launch,
D-Bus, first-paint, Stop, and relaunch checks. Porting multiple Activities
before that boundary is reached multiplies ambiguous failures.
