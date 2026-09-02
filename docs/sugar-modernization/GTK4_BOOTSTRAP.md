# GTK4 preview bootstrap

This is intentionally separate from stable GTK3 Sugar.

```bash
make sugar-gtk4-init
GTK4_ROOT=/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4 make sugar-gtk4-check
GTK4_ROOT=/media/freezer/SteamLibrary/vms/aspartame-build/sugar-modernization/gtk4 make sugar-gtk4-build
```

The initializer checks out exact refs listed in `scripts/sugar-gtk4-init.sh` and records resolved SHAs in the external `PINS.tsv`. The preview venv uses system GTK4 introspection but installs toolkit Python code editable under the preview root. `sugar-ext` installs only under the preview prefix when that build completes.

`make sugar-gtk4-run` intentionally exits with a clear not-supported result until a real shell runner exists. This prevents a false success claim and protects the stable X11/GTK3 session.
