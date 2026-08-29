# Sugar styling on Aspartame

Sugar's appearance is produced by several independent layers. There is no
single stylesheet that controls the shell. Choose the layer that actually
renders the object before editing it.

The inspected reference is Sugar 0.121 on GTK 3 at `SUGAR_SCALING=72`.

## Active styling stack

### 1. Process-local GTK and icon themes

`jarabe.main.setup_theme()` sets these on the Sugar shell's `Gtk.Settings`:

```text
gtk-theme-name      sugar-72
gtk-icon-theme-name sugar
```

`/usr/bin/sugar` sets `SUGAR_SCALING=72` when no override exists. This selects:

```text
/usr/share/themes/sugar-72/gtk-3.0/gtk.css
/usr/share/themes/sugar-72/gtk-3.0/gtk-widgets.css
/usr/share/icons/sugar/
```

The files are owned by the official `sugar-artwork` package. A standalone
`gsettings get org.gnome.desktop.interface gtk-theme` returned `Adwaita` in the
same VM. That is not proof of the shell's active theme because Sugar overrides
its own `Gtk.Settings` after startup.

Activities using `sugar3.activity.activity` perform a similar process-local
Sugar theme setup. A shell restart does not restyle an already running Activity
process.

### 2. Sugar toolkit widgets and CSS names

`sugar3` supplies widgets and attaches names/classes used by the artwork CSS.
Examples include:

```text
canvasicon
palette
controlpanel
toolbarbox
htray / VTray
toolitem
palette-down
toolbar-down
sugar-icon-cell
```

The implementation lives under the pacman-owned
`/usr/lib/pythonX.Y/site-packages/sugar3`. Aspartame does not currently overlay
`sugar3`. Toolkit changes need a separate reproducible package/patch; never use
`sudo pip` or edit the installed file in place.

### 3. Sugar symbolic SVG rendering

Sugar artwork SVGs contain replaceable fill/stroke entities. The toolkit's
`sugar3.graphics.icon` loads the SVG, substitutes colors, renders through
Rsvg/Cairo, and caches the result. `XoColor` carries the paired stroke/fill
semantics.

This layer controls XO colors, Buddy icons, Activity state colors, and many
symbolic icons. Generic GTK CSS cannot reliably recolor these objects because
the color is part of the SVG render operation, not a CSS foreground property.

Important locations:

```text
/usr/share/icons/sugar/scalable/
/usr/lib/pythonX.Y/site-packages/sugar3/graphics/icon.py
/usr/lib/pythonX.Y/site-packages/sugar3/graphics/xocolor.py
jarabe/desktop/favoritesview.py
jarabe/desktop/buddyicon.py
```

The colored/running state of an Activity icon is intentional Sugar behavior.
Do not flatten it into a generic monochrome application icon.

### 4. Python widget construction and allocation

Several visual properties are explicit Python layout, not theme CSS:

- Home page composition: `jarabe.desktop.homewindow`;
- ring/spiral geometry: `jarabe.desktop.favoriteslayout`;
- Frame panel positions/animation: `jarabe.frame.frame`;
- edge trigger geometry: `jarabe.frame.eventarea`;
- search and Aspartame clock placement: `jarabe.desktop.viewtoolbar`;
- Neighborhood object placement: `jarabe.desktop.meshbox`.

CSS may alter padding or font metrics, but it cannot replace these custom
allocation algorithms safely.

### 5. Cairo/GdkPixbuf custom drawing

`HomeBackgroundBox` reads:

```text
org.sugarlabs.user.background image-path
org.sugarlabs.user.background alpha-level
```

It loads the image with GdkPixbuf, scales it to the widget allocation, and
paints it with Cairo. Wallpaper fit/scaling behavior is therefore Python/Cairo,
not GTK CSS. The GSettings change signal triggers a redraw without restarting
Sugar.

Toolkit icons and some palette/notification widgets also have custom `do_draw`
paths. Inspect those before assuming a CSS selector can express the change.

### 6. Fonts

`jarabe.main.setup_fonts()` reads:

```text
org.sugarlabs.font default-face
org.sugarlabs.font default-size
```

and writes the shell's process-local `gtk-font-name`. The inspected values were
`Sans Serif`, size `10.0`. Font changes made through that path apply at shell
startup; restart Sugar to verify them consistently.

The v0.0.14 clock intentionally inherits Sugar's active font and follows the active `LC_TIME` hour convention (12- or 24-hour) while always omitting seconds. It reads the optional `org.aspartame.clock` `format` key; blank means locale-derived hours and minutes, while a custom strftime format is rendered after markup escaping. The widget continues to use Pango markup only for `xx-large` and bold weight, preserving the family selected by Sugar.

### 7. Scoped runtime CSS providers

Aspartame currently uses small widget-scoped `Gtk.CssProvider` instances for
features whose style is local to one new shell widget:

- `.aspartame-clock-button` in `jarabe.desktop.viewtoolbar` removes
  button-like hover/active decoration while keeping a native toolbar widget;
- `.aspartame-scan-button` in `jarabe.desktop.meshbox` gives the explicit
  Neighborhood scan action Sugar-compatible pill geometry.

These providers are attached at application priority to the specific widget's
style context. They are not a substitute for a coherent artwork theme. If a
rule should affect all Sugar widgets of a type, package it in Sugar artwork
rather than duplicating providers across modules.

### 8. Metacity

Metacity is started by `jarabe.main`, owns X11 window management, and has its
own GSettings/theme behavior. Sugar disables Metacity keybindings and mouse
button modifiers after detecting the WM. Window placement, fullscreen policy,
and decorations are not controlled by the Sugar GTK stylesheet.

Aspartame deliberately keeps Sugar's Activity/window model. Do not introduce a
generic panel, dock, taskbar, or overlapping-window-first policy through WM
configuration.

## Concrete change recipes

### Change a shell toolbar widget

Edit its repository `jarabe` file, not `/usr/lib` or `/mnt`:

```sh
$EDITOR sugar-overlay/src/jarabe/desktop/viewtoolbar.py
./scripts/sugar-patch.sh update
make sugar-reload
make sugar-screenshot
```

Use the existing GTK widget hierarchy and a narrow CSS class only when the
property is genuinely CSS-driven. Layout/allocation belongs in Python.

### Change the Home ring or spiral

The geometry is in `jarabe.desktop.favoriteslayout`, not CSS. Add the exact
baseline file to `sugar-overlay/src` and `sugar-overlay/files.list`, regenerate
the patch, and reload Sugar. Preserve `RingLayout`/`SunflowerLayout` semantics.

### Change XO or Activity icon colors

Trace `ActivityIcon`/`OwnerIcon` to `CanvasIcon`, `Icon`, and `XoColor`. Change
the SVG entity/color semantics only with a clear state-model reason. CSS
`color:` does not replace Sugar's paired fill/stroke rendering.

### Change an icon glyph

Use a valid symbolic SVG in the Sugar icon theme or the Activity bundle's icon.
Preserve Sugar's fill/stroke entities when recoloring is required. An icon
cache or already running process may require a shell/Activity restart.

### Change wallpaper

For content/opacity only, set the existing GSettings keys; the Home widget
redraws live. To change fill/fit/interpolation, edit
`jarabe.desktop.homebackgroundbox.HomeBackgroundBox`, because it performs the
GdkPixbuf/Cairo scaling.

### Change Frame reveal behavior

Edit `jarabe.frame.eventarea` and the `org.sugarlabs.frame` settings for edge,
corner, delay, or trigger-size behavior. Frame panel construction and animation
are in `jarabe.frame.frame`. F6 dispatch is in `jarabe.view.keyhandler`.

### Change palette appearance

Check both sugar-artwork CSS and `sugar3.graphics.palette`/
`palettewindow`. Headers/separators and icon content may use custom drawing;
popup background/borders and widget spacing may be CSS.

### Change global Sugar GTK colors or controls

The correct long-term location is an Aspartame-owned package derived from
`sugar-artwork`, with an isolated patch. Do not live-edit
`/usr/share/themes/sugar-72`. There is not yet a hot artwork-overlay workflow;
this is a known limitation of this pass.

### Change Metacity decorations or policy

Treat this as a separate WM layer. Inspect Metacity GSettings and package
resources. Use `make sugar-session-restart` when WM startup/environment changes;
a shell reload already replaces the shell-owned Metacity child, but it does not
replace Xorg.

## Inspection commands

```sh
make sugar-info
./scripts/ssh-asp pacman -Qo /usr/share/themes/sugar-72/gtk-3.0/gtk.css
./scripts/ssh-asp grep -RIn CssProvider /mnt/aspartame-dev/sugar/src/jarabe
./scripts/ssh-asp grep -RIn set_css_name /usr/lib/python3.14/site-packages/sugar3
make sugar-screenshot
```

Use the Python minor version printed by `make sugar-info` rather than assuming
`3.14` on future images.

## Reload matrix

| Change | Minimum verified action |
|---|---|
| Repository `jarabe` shell Python | `make sugar-reload` |
| Shell-local `GtkCssProvider` | `make sugar-reload` |
| Wallpaper GSettings path/alpha | live redraw |
| Sugar artwork CSS/SVG package | shell reload; restart affected Activities |
| Toolkit `sugar3` | rebuild/package, then shell and affected Activity restart |
| Font setup/theme selection | shell reload |
| Metacity startup/X environment | `make sugar-session-restart` |
| `.xinitrc`/`aspartame-x-session` | `make sugar-session-restart` |

## Styling traps confirmed in this environment

- Editing `sugar-100` would not change this shell; `SUGAR_SCALING=72` selects
  `sugar-72`.
- GSettings' desktop GTK theme is not Sugar's process-local GTK theme.
- SVG/XO colors are not ordinary CSS text colors.
- Wallpaper is a Cairo paint path, not a desktop CSS background.
- A widget can allocate correctly yet draw nothing if its actual internal GTK
  render widget is not the one being styled. Inspect the hierarchy and confirm
  with a screenshot.
- `Gtk.ToolButton` carries hover/active behavior; the clock removes those states
  through a class on the internal button while remaining part of the toolbar.
