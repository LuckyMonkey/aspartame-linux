# GTK4 Jukebox UX pass — 2026-10-04

## Result

The packaged GTK4 sweep showed Jukebox's track list and controls spread across
a mostly empty page, with the player surface effectively collapsed. The
activity now puts the Playlist and Player frames directly in the expanding
root as a side-by-side workspace. The selected track and playback hint remain
visible at normal Sugar dimensions, with status and controls aligned beneath
the panes.

The offline demo-track model and Journal payload remain compatible. Local
tracks now retain their URI and use an optional native GStreamer `playbin`
backend when the guest provides one; demo tracks continue to exercise the
deterministic UI without requiring audio files. This is a backend path, not a
claim that every codec or audio device is qualified.

## Verification

Focused host check:

```text
pytest -q tests/test_gtk4_jukebox_activity.py
3 passed
```

The rebuilt writable GTK4 guest preview passed:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Jukebox launched through the real Journal D-Bus path in the headless GTK4
shell. The initial 1920x1080 capture showed the Playlist and Player panes with
`Ready: Morning Bell`; its SHA-256 was
`cf8a76b2be1ba74a3d4614e49ca0b08350848560c916dcb13f5f721fca432a56`.

A headless QEMU click on `Play` changed the player and status to
`Playing: Morning Bell` and enabled `Stop`. The follow-up 1920x1080 capture
checksum was
`35c43c3acf979ccf959d611aa3d71a4553709703791e0d8489ef73884403c2d9`.

## Follow-up layout correction — 2026-10-05

The source audit found the Playlist/Player `Gtk.Paned` was initialized at
`-1`, which can collapse the leading playlist or player surface on GTK4. It
now opens with a 640-pixel split and the layout qualification rejects the
collapsed pattern. This is committed as `18b3055` and pushed to GitHub. A
fresh guest screenshot remains pending; the source and focused tests pass.

## Boundary

Jukebox remains a `FUNCTIONAL PORT`, not a `FULL PORT`. Codec-backed media
playback and full upstream media breadth remain open. No GTK3 package was
removed.
