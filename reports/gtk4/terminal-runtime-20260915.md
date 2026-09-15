# GTK4 Terminal runtime verification — 2026-09-15

The full Activity matrix initially exposed a real GTK4 process failure:
`terminal.py` imported GTK3 Vte after `sugar4` had loaded GTK4, raising
`RepositoryError: Requiring namespace 'Gtk' version '3.0'`.

The modern prefix was staged with the native `gtk4-terminal-activity` bundle
under the unchanged `org.laptop.Terminal` identity. Its two-cycle lifecycle
probe now passes, and the direct runtime probe found the mapped `Terminal`
surface through AT-SPI, entered `printf terminal-ok` in the accessible command
field, observed the output, and stopped cleanly:

```
terminal-visible=PASS command-input=PASS output=PASS cleanup=PASS
```

The bounded replacement intentionally uses GTK4 `Gtk.TextView` output and a
shell-command entry rather than importing GTK3 Vte. Full terminal emulator
features remain outside this claim.
