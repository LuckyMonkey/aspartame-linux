# Sugar/Jarabe behavioral bug audit — 2026-09-01

This incident set records five independent defects found in the running
Aspartame Sugar integration. These are behavior and accessibility failures,
not syntax-only findings.

Evidence captures:
- [pre-fix desktop](../../reports/screenshots/sugar-20260901-204949-v0.0.20.png)
- [post-fix desktop](../../reports/screenshots/sugar-20260901-205618-v0.0.20.png)
- [post-accessibility desktop](../../reports/screenshots/sugar-20260901-205239-v0.0.20.png)

## Incident 1 — Home shell crashed on invalid GTK3 CSS

**Facet:** shell startup/rendering

**Reproduction:** reload Sugar with the help-button CSS containing
`max-width` and `max-height` on a GTK3 button.

**Observed:** `jarabe.main` exited while constructing
`jarabe.desktop.viewtoolbar.ViewToolbar`:

```
GLib.GError: gtk-css-provider-error-quark:
<data>:8:25 'max-width' is not a valid property name (3)
```

Metacity, the shell D-Bus name, and Home then disappeared.

**Fix:** retained the 72px size request and removed unsupported GTK3 CSS
properties. The patch is generated from the authoritative overlay source.

**Verification:** Python compile, patch-sync check, live Sugar reload, Home
window detection, and post-fix screenshot.

## Incident 2 — the universal help control had no accessible identity

**Facet:** accessibility metadata

**Reproduction:** inspect the toolbar help button through the widget's
accessible object.

**Observed:** the visible `?` control had a tooltip but no guaranteed
accessible name, description, or focus metadata.

**Fix:** register the button with the shared help registry. Registration now
sets keyboard focus capability and the ATK name/description when available.

**Verification:** fake-accessible regression test plus live import/reload.

## Incident 3 — Frame navigation controls were not contextual-help targets

**Facet:** shell discoverability/accessibility

**Reproduction:** activate What's This? and select Frame navigation controls.

**Observed:** Neighborhood, Group, Home, Activity, and Journal controls were
not consistently registered, so the user could not receive semantic help for
core Sugar navigation.

**Fix:** registered the controls through the existing `guard()` API and
added the missing Activity target.

**Verification:** source import map, registry tests, live reload, and post-fix
desktop capture.

## Incident 4 — List view was documented as Frame

**Facet:** semantic correctness

**Reproduction:** select List view while What's This? mode is active.

**Observed:** `viewtoolbar.py` assigned
`org.aspartame.shell.frame`, producing the wrong explanation.

**Fix:** added `org.aspartame.shell.list` metadata and changed List view to
use it.

**Verification:** patch inspection, registry coverage test, and live reload.

## Incident 5 — keyboard activation bypassed contextual-help interception

**Facet:** keyboard accessibility/input behavior

**Reproduction:** focus a registered button, enable What's This?, and invoke
it with keyboard activation rather than a pointer click.

**Observed:** pointer interception existed, but keyboard activation was not
handled by the reusable guard path.

**Fix:** `guard()` now attaches an `activate` handler when the widget
supports it. Escape handling remains available at the shell window level;
missing metadata fails with a plain-language message rather than a traceback.

**Verification:** Python compile, registry regression tests, and live shell
startup. Full keyboard interaction remains a manual test item because this
agent session cannot inject guest keyboard input.

## Result

The stable GTK3 path remains the active path. No GTK4 or package-owned Sugar
files were modified. The five fixes are currently uncommitted and should be
reviewed together before committing.
