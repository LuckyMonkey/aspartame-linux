# GTK4 Browse runtime evidence — 2026-09-15

The full GTK4 Activity matrix reached Browse after the native Terminal fix and
failed before launch because the pinned WebActivity imported `gi.repository.WebKit`,
but the guest had no matching introspection typelib.  Rather than silently
falling back to GTK3, Browse now uses a small GTK4-native URL/status surface and
keeps the WebKit package available for a future embedded renderer.

Live guest round-trip (modern Space, Casilda session):

```
browse-visible=PASS url-input=PASS load-status=PASS cleanup=PASS
```

The probe launched `org.laptop.WebActivity` through Journal, located the real
Activity by PID via AT-SPI, entered `https://example.org`, activated Go, observed
the asynchronous Loaded/Load failed status, stopped the Activity through Shell,
and verified the process disappeared.

Classification: FUNCTIONAL PORT (native GTK4 URL entry, loading status, bounded
text result; full WebKit browsing and collaboration/download parity remain
deferred).
