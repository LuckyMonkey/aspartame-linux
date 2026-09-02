# GTK4 Journal Runbook

Status: investigation and compatibility work in progress (2026-09-02)

This runbook defines the scope of the GTK4 Journal migration in Aspartame. It
is deliberately honest about the current state: the preview can initialize
Journal far enough to exercise its construction path, but Journal is **not yet
claimed usable**. A renderer compatibility bridge is not the same thing as a
GTK4-native Journal.

## 1. Runtime boundary

The GTK4 preview is isolated from stable GTK3 Sugar.

| Item | Current value |
|---|---|
| Shell checkout | `/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4/sources/sugar` |
| Toolkit checkout | `/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4/sources/sugar-toolkit-gtk4` |
| Datastore checkout | `/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4/sources/sugar-datastore` |
| Preview prefix | `/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4/prefix` |
| Runtime state | `/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4/runtime-first-pixels` |
| Shell SHA | `f84a2d514dbbcab6e30c810b00088f47870e04a5` (Sugar PR #1106 head) |
| Toolkit SHA | `74f6a05a4921c27d0892bc22845fd4d4a60f4119` (toolkit PR #35 head) |
| Datastore SHA | `7aa97e791432d26007a9f16d4214b2085380edec` |
| Host Python | `/usr/bin/python3` 3.12.3 |
| Display used by wrapper | private Xvfb `:99` when `DISPLAY` is unset |

The preview is launched by:

```sh
env -u DISPLAY make sugar-gtk4-run
```

The wrapper starts a private D-Bus session, a private datastore service, and
Xvfb when needed. It sets `SUGAR_HOME`, `PYTHONPATH`, `GI_TYPELIB_PATH`,
`LD_LIBRARY_PATH`, `XDG_DATA_DIRS`, and the isolated runtime directories. It
must not install or replace package-owned GTK3 Sugar files.

## 2. What Journal is

Sugar Journal is the user's activity history and persistent work space. It is
not merely a file browser. Its contract includes:

- displaying real datastore entries and mounted-file entries;
- filtering entries from the Journal toolbar;
- selecting one or many entries;
- opening or resuming an entry through its activity metadata;
- editing a title when the object is editable;
- marking an entry favorite;
- showing activity, buddy, progress, timestamp, and detail information;
- opening palettes with actions appropriate to the object;
- copying or dragging Journal objects where supported;
- creating and updating datastore entries;
- handling projects and object chooser consumers;
- retaining Sugar's Journal lifecycle and resume semantics.

A screen that merely says `Journal` or a list that renders without real entries
does not satisfy this contract.

## 3. Current architecture discovered

### Journal startup

`jarabe/main.py` schedules Journal startup through `setup_journal_cb()`.
`jarabe/journal/journalactivity.py` owns the Journal Activity and builds the
main view in `JournalActivity._setup_main_view()`.

The main view currently contains:

```text
MainToolbox
AddNewBar
ListView(enable_multi_operations=True)
VolumesToolbar
```

`JournalActivity` also owns the project/secondary views, query changes, entry
open/resume routing, visibility/focus state, and datastore signal handling.

### View and model path

The current list path is:

```text
JournalActivity
  -> jarabe.journal.listview.ListView
  -> BaseListView
  -> jarabe.journal.listview.TreeView(Gtk.TreeView)
  -> Gtk.TreeViewColumn + Gtk.CellRenderer*  [legacy GTK3 design]
  -> jarabe.journal.listmodel.ListModel
  -> jarabe.journal.model.ResultSet
  -> sugar-datastore over org.laptop.sugar.DataStore
```

`ListModel` remains a `GObject.GObject, Gtk.TreeModel` implementation. Its
column constants and row semantics are authoritative for the existing data
contract:

| Column | Meaning |
|---:|---|
| 0 | UID |
| 1 | favorite/keep |
| 2 | icon path |
| 3 | icon color |
| 4 | title/markup |
| 5 | elapsed timestamp |
| 6 | creation time |
| 7 | file size |
| 8 | progress |
| 9-11 | buddies |
| 12 | selection state |

The datastore adapter is in `jarabe/journal/model.py`. It calls the pinned
`sugar-datastore` service through D-Bus. The preview launcher stages the
`carquinyol.metadatareader` extension for Python 3.12 and starts the service
on the private session bus.

### Important Journal classes/functions

- `jarabe.journal.journalactivity.JournalActivity._setup_main_view()` — main
  Journal composition.
- `jarabe.journal.journalactivity.JournalActivity._query_changed_cb()` —
  toolbar filtering entry point.
- `jarabe.journal.journalactivity.JournalActivity.show_object()` — open a
  selected object.
- `jarabe.journal.listview.BaseListView.__init__()` — scroller, view, model
  signal, and drag setup.
- `jarabe.journal.listview.BaseListView._add_columns()` — legacy renderer and
  column construction; the primary GTK4 migration boundary.
- `jarabe.journal.listview.BaseListView._do_refresh()` — creates and starts a
  `ListModel` for a query.
- `jarabe.journal.listview.ListView.__button_release_event_cb()` — row
  activation/palette routing.
- `jarabe.journal.listview.ListView._key_press_event_cb()` — keyboard actions.
- `jarabe.journal.listmodel.ListModel` — row adapter and selection state.
- `jarabe.journal.model.find()` — chooses datastore or mounted-file result
  sets.
- `jarabe.journal.model._call_datastore()` — D-Bus call/retry boundary.
- `jarabe.journal.objectchooser.ChooserListView` — consumer of the shared
  BaseListView path; it must not be broken by a Journal migration.
- `jarabe.journal.projectview.ProjectView` — project-specific Journal view.
- `jarabe.journal.expandedentry` — expanded entry/comments presentation.

## 4. What was fixed, and what that means

The following preview-only changes are committed, but none alone completes
Journal:

- `0013-toolkit-palette-icon-compat.patch` — restores the migration spelling
  `PaletteMenuItem.set_icon_widget()` as a narrow delegate to GTK4 `set_image()`.
- `0014-datastore-use-sugar4-modules.patch` — makes the pinned datastore use
  `sugar4` modules and stages its Python/native pieces.
- `0015-toolkit-cell-renderer-props-compat.patch` — temporary compatibility
  surface for old renderer property callers.
- `0016-toolkit-cell-renderer-gobject.patch` — makes the compatibility renderer
  a real `Gtk.CellRenderer`, declares the properties needed by Journal, and
  adds GTK4 snapshot/preferred-size rendering.
- `0017-toolkit-icon-file-alias.patch` — provides the legacy `Icon.props.file`
  alias used by the shell.

These fixes changed the observed failure sequence from:

```text
PaletteMenuItem API failure
 -> datastore unavailable/import failure
 -> CellRendererFavorite has no props
 -> renderer has no connect
 -> TreeViewColumn rejects plain Python renderer
 -> missing renderer properties
 -> missing Icon.props.file
```

to a Journal construction path that stays alive during the preview timeout.
That is progress through compatibility boundaries, not proof of correct rows,
input, filtering, or persistence.

## 5. Current verified state

As of this runbook's status date:

- Toolkit import and build: PASS.
- Datastore metadata reader and private service startup: PASS.
- Journal renderer construction: advances past the previous crashes.
- GTK4 preview process: remains alive for the timed runtime check.
- Stable GTK3 tests and isolation checks: PASS.
- Journal real-entry display: **not yet visually verified**.
- Journal selection: **not yet verified**.
- Journal search/filter: **not yet verified in Journal**.
- Journal open/resume: **not yet verified**.
- Favorite/detail palettes: **not yet verified**.
- title editing: **not yet verified**.
- object chooser/project views: **not yet verified**.

Known preview warnings that are not currently the Journal blocker:

- UPowerGlib typelib is unavailable, so the battery extension is skipped.
- the GStreamer `espeak` element is unavailable.
- Telepathy is unavailable, so FriendsTray/Neighborhood is reduced.
- private Xvfb causes software Casilda rendering and portal/GVFS noise.

## 6. Scope of the remaining migration

The remaining work is larger than adding renderer aliases. It has four
separate layers and should be handled in this order.

### Layer A — make the current view render real data

Verify that the existing result set reaches the view and that at least one
real row is visible. Capture a screenshot or an equivalent widget/model probe.
If the legacy TreeView compatibility path cannot render rows reliably, do not
keep adding random properties; move to Layer B.

### Layer B — migrate presentation to GTK4-native list widgets

The intended direction is:

```text
Datastore ResultSet
  -> Journal row adapter / Gio.ListModel
  -> Gtk.FilterListModel / Gtk.SortListModel where appropriate
  -> Gtk.ListView or Gtk.ColumnView
  -> GTK4 row widget factory
```

The logical data model must remain separate from the widgets. Do not derive
UIDs, favorites, or object metadata from rendered geometry. Preserve the
existing `ListModel` column meanings while introducing a typed row adapter or
view model incrementally.

A GTK4 row should own explicit widgets for, as applicable:

- selection toggle;
- favorite action;
- Activity/object icon;
- title;
- buddy indicators;
- progress;
- elapsed time;
- detail action.

Use GTK4 event controllers and button signals. Do not attempt to reproduce
`Gtk.CellRenderer` as a permanent Aspartame architecture.

### Layer C — restore behavior

After rows render, verify independently:

1. toolbar query changes the model and updates visible rows;
2. empty state and no-match state are distinct and readable;
3. one-row selection and multi-selection work;
4. Enter/double activation opens or resumes the correct object;
5. favorite changes persist through datastore writes;
6. title edits use the existing validation and write path;
7. detail palettes identify the correct UID;
8. Delete and project actions remain correctly scoped;
9. drag/copy uses a stable UID/content provider;
10. returning from an Activity preserves Journal query/selection as intended.

### Layer D — consumers and lifecycle

The shared BaseListView is also used by ObjectChooser and ProjectView. Test
those separately. A fix that makes the main Journal work but breaks an
Activity's object chooser is not complete.

Also verify Journal creation, hiding, re-showing, and shell restart. Datastore
connection loss must fail visibly and recover according to the existing retry
contract; it must not silently present stale data as current.

## 7. Recommended implementation sequence

Use one commit per meaningful boundary:

1. `gtk4: prove Journal rows reach the preview view`
2. `gtk4: add Journal GTK4 row model`
3. `gtk4: render Journal entries with GTK4 list widgets`
4. `gtk4: restore Journal selection and activation`
5. `gtk4: restore Journal palettes and editing`
6. `test: cover Journal datastore/view lifecycle`

Do not mix the Journal migration with Home, Frame, Neighborhood, artwork, or
activity ports.

## 8. Commands and evidence workflow

From the repository:

```sh
python3 -m pytest -q
./scripts/sugar-patch.sh check
./scripts/sugar-modernization-check.sh
make sugar-gtk4-build
env -u DISPLAY timeout 25 make sugar-gtk4-run
```

Capture the run output when investigating:

```sh
env -u DISPLAY timeout 25 make sugar-gtk4-run \
  > /tmp/aspartame-journal-run.log 2>&1
rg -n 'Traceback|AttributeError|TypeError|ServiceUnknown|NameHasNoOwner' \
  /tmp/aspartame-journal-run.log
```

Use the latest wrapper log under:

```text
/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4/logs/
```

A Journal milestone requires durable evidence under
`reports/gtk4/` or `docs/sugar-modernization/artifacts/`, including:

- exact shell/toolkit/datastore SHAs;
- exact launch command and environment wrapper;
- a screenshot of real Journal rows where visual behavior matters;
- a runtime log with no new fatal traceback;
- a focused test result;
- explicit tested/not-tested behavior.

A timeout exit code `124` means the wrapper was stopped by the test timeout; it
does not mean the shell is complete. Check the output for fatal tracebacks and
check the visible state separately.

## 9. Acceptance gate for “Journal GTK4 ready”

Do not use that phrase until all required checks pass in a running preview:

- [ ] Journal opens from the shell without traceback.
- [ ] Real datastore entry is visible.
- [ ] Mounted-file entry path is handled or explicitly documented as pending.
- [ ] Search/filter visibly changes the list.
- [ ] Empty and no-match states work.
- [ ] Keyboard focus reaches the list and traversal is deterministic.
- [ ] Enter activates the selected entry.
- [ ] Pointer selection works.
- [ ] Favorite toggling writes and survives a refresh.
- [ ] Title edit works for an editable entry.
- [ ] Detail/object palette opens for the correct entry.
- [ ] Open/resume returns to the intended Activity.
- [ ] Delete/project actions are safe and scoped.
- [ ] Drag/copy does not corrupt or misidentify an entry.
- [ ] ObjectChooser still works.
- [ ] ProjectView still works.
- [ ] Journal survives hide/show and shell restart.
- [ ] Datastore disconnect/error behavior is observable and recoverable.
- [ ] Screenshot and runtime log are retained.
- [ ] Stable GTK3 tests and isolation checks still pass.

## 10. Do not paper over these failures

Do not:

- claim Journal works because `journalactivity.start()` returned;
- permanently expand the toolkit with every missing GTK3 property;
- convert every old renderer callback into a no-op;
- silently disable Journal after a construction error;
- replace datastore entries with hard-coded sample rows;
- make the preview depend on stable GTK3 packages;
- change datastore IDs or resume metadata to simplify rendering;
- call a screenshot “proof” without identifying the state it shows.

The compatibility renderer patches are scaffolding for investigation. The
long-term target is a GTK4-native Journal view consuming the unchanged logical
Journal contract.

## 11. Next action

The next implementation pass should create a small Journal row/model probe that
reports the number of datastore rows reaching `ListModel`, then capture a
screenshot of the actual Journal view. If rows are present but invisible,
repair the GTK4 row presentation. If no rows reach the model, investigate the
private datastore query/result-set path before changing widgets.
