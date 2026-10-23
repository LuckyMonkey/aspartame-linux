#!/usr/bin/env python3
"""Guest half of the FULL PORT receipt: observe a GTK4 Activity over AT-SPI.

The host driver (sugar-gtk4-fullport-receipt.py) delivers real keyboard
input through QEMU and calls these subcommands between keystrokes:

  launch BUNDLE_ID MARKER [UID]  start (or resume) an Activity; JSON pid/aid
  focused PID                    accessible name and role of the focused node
  text PID NAME                  text of the node with that accessible name
  stop PID AID [UID]             stop it; JSON Journal uid and payload path
                                 (pass UID when resuming: the object keeps its
                                 original activity_id)
  a11y PID                       interactive nodes that have no accessible name
  names PID                      every node: role, name and text (for writing specs)
  payload UID                    payload path of a Journal object
  seed KIND                      put test objects in the Journal: tone (audio),
                                 clip (video, when GStreamer can encode one),
                                 starred (two starred entries)
  find TITLE                     how many Journal objects have this title
"""
import json, math, os, struct, subprocess, sys, tempfile, time, wave, zlib
from pathlib import Path

INTERACTIVE = {"button", "push button", "toggle button", "check box", "radio button",
               "combo box", "entry", "text", "spin button", "slider", "link"}


def reexec_as_session_user():
    shells = subprocess.check_output(
        ["pgrep", "-u", "aspartame", "-f", "/sources/sugar/src/jarabe/main.py"],
        text=True).split()
    if len(shells) != 1:
        raise SystemExit("expected one modern shell, found %d" % len(shells))
    env = dict(item.split("=", 1) for item in
               Path("/proc/%s/environ" % shells[0]).read_bytes().decode().split("\0")
               if "=" in item)
    py = next(c for c in ("/usr/lib/aspartame/gtk4-preview/venv/bin/python",
                          "/home/aspartame/Development/gtk4-preview/venv/bin/python")
              if Path(c).exists())
    os.setgroups([]); os.setgid(1000); os.setuid(1000)
    os.execve(py, [py, __file__, *sys.argv[1:]], env)


def tone_wav(path, seconds=10, rate=8000):
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(rate)
        out.writeframes(b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / rate)))
                                 for i in range(seconds * rate)))


def png(width=64, height=48, rgb=(30, 120, 200)):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rows = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def wait_for(desc, fn, timeout=20):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(0.1)
    raise SystemExit("timed out: %s" % desc)


def main():
    if "IMAGE_ID=aspartame" not in Path("/etc/os-release").read_text():
        raise SystemExit("run inside the Aspartame guest")
    if os.getuid() == 0:
        reexec_as_session_user()
    import dbus, gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    bus = dbus.SessionBus()
    journal = dbus.Interface(bus.get_object("org.laptop.Journal", "/org/laptop/Journal"),
                             "org.laptop.Journal")
    shell = dbus.Interface(bus.get_object("org.laptop.Shell", "/org/laptop/Shell"),
                           "org.laptop.Shell")
    store = dbus.Interface(bus.get_object("org.laptop.sugar.DataStore",
                                          "/org/laptop/sugar/DataStore"),
                           "org.laptop.sugar.DataStore")

    def processes(marker):
        found = []
        for cmdline in Path("/proc").glob("[0-9]*/cmdline"):
            try:
                args = cmdline.read_bytes().decode().split("\0")
            except OSError:
                continue
            if marker in args and "--activity-id" in args:
                found.append((int(cmdline.parent.name), args[args.index("--activity-id") + 1]))
        return found

    def nodes(pid):
        stack = [Atspi.get_desktop(0)]
        while stack:
            node = stack.pop()
            try:
                if node.get_process_id() == pid:
                    yield node
                count = node.get_child_count()
            except Exception:
                continue
            if node.get_role_name() == "desktop frame" or node.get_process_id() == pid:
                stack.extend(c for c in (node.get_child_at_index(i) for i in range(count)) if c)

    def titled(title):
        # The datastore ignores a title filter, so match titles here.
        rows, _count = store.find(dbus.Dictionary({}, signature="sv"),
                                  dbus.Array(["uid", "title"], signature="s"))
        return [str(r["uid"]) for r in rows if str(r.get("title", "")) == title]

    def text_of(node):
        try:
            return Atspi.Text.get_text(node, 0, -1)
        except Exception:
            return ""

    command, args = sys.argv[1], sys.argv[2:]
    if command == "launch":
        bundle, marker = args[0], args[1]
        uid = args[2] if len(args) > 2 else ""
        if processes(marker):
            raise SystemExit("%s is already running" % marker)
        assert journal.LaunchBundle(bundle, uid)
        pid, aid = wait_for("process", lambda: next(iter(processes(marker)), None))
        wait_for("service", lambda: bus.name_has_owner("org.laptop.Activity" + aid))
        wait_for("activation", lambda: shell.ActivateActivity(aid))
        wait_for("accessible tree", lambda: any(True for _ in nodes(pid)))
        time.sleep(1.5)
        print(json.dumps({"pid": pid, "aid": str(aid)}))
    elif command == "focused":
        pid = int(args[0])
        for node in nodes(pid):
            if node.get_state_set().contains(Atspi.StateType.FOCUSED):
                print(json.dumps({"name": node.get_name(), "role": node.get_role_name()}))
                return
        print(json.dumps({"name": None, "role": None}))
    elif command == "text":
        pid, name = int(args[0]), args[1]
        node = next((n for n in nodes(pid) if n.get_name() == name), None)
        if node is None:
            raise SystemExit("no node named %r" % name)
        print(json.dumps({"text": text_of(node)}))
    elif command == "stop":
        pid, aid = int(args[0]), args[1]
        assert shell.StopActivity(aid)
        wait_for("exit", lambda: not Path("/proc/%d" % pid).exists())
        assert not bus.name_has_owner("org.laptop.Activity" + aid)
        if len(args) > 2:
            uid = args[2]
        else:
            rows = wait_for("Journal entry", lambda: store.find(
                dbus.Dictionary({"activity_id": aid}, signature="sv"),
                dbus.Array(["uid"], signature="s"))[0])
            assert len(rows) == 1, rows
            uid = str(rows[0]["uid"])
        print(json.dumps({"uid": uid, "path": str(store.get_filename(uid))}))
    elif command == "names":
        print(json.dumps([[n.get_role_name(), n.get_name(), text_of(n)[:200]]
                          for n in nodes(int(args[0]))]))
    elif command == "seed":
        made = {}

        def create(title, mime, data_path, **extra):
            # One object per test title, so earlier runs never get picked.
            for uid in titled(title):
                store.delete(uid)
            props = dbus.Dictionary({"title": title, "mime_type": mime, "keep": "0",
                                     "activity": "", **extra}, signature="sv")
            made[title] = str(store.create(props, str(data_path), True))

        tmp = Path(tempfile.mkdtemp())
        if args[0] == "tone":
            tone_wav(tmp / "tone.wav")
            create("Tone", "audio/x-wav", tmp / "tone.wav")
        elif args[0] == "clip":
            out = tmp / "clip.webm"
            subprocess.run(["gst-launch-1.0", "-q", "videotestsrc", "num-buffers=240", "!",
                            "video/x-raw,width=320,height=240,framerate=30/1", "!", "vp8enc", "!",
                            "webmmux", "!", "filesink", "location=%s" % out],
                           check=True, capture_output=True, timeout=60)
            create("Clip", "video/webm", out)
        elif args[0] == "starred":
            (tmp / "kite.png").write_bytes(png(rgb=(30, 120, 200)))
            create("Kite", "image/png", tmp / "kite.png", keep="1", description="We built a kite")
            (tmp / "volcano.txt").write_text("Baking soda and vinegar.\n")
            create("Volcano", "text/plain", tmp / "volcano.txt", keep="1",
                   preview=dbus.ByteArray(png(rgb=(200, 80, 40))))
        else:
            raise SystemExit("unknown seed %r" % args[0])
        print(json.dumps(made))
    elif command == "find":
        print(json.dumps({"count": len(titled(args[0]))}))
    elif command == "payload":
        print(json.dumps({"path": str(store.get_filename(args[0]))}))
    elif command == "a11y":
        pid = int(args[0])
        unnamed, checked = [], 0
        for node in nodes(pid):
            role = node.get_role_name()
            if role not in INTERACTIVE:
                continue
            states = node.get_state_set()
            if not states.contains(Atspi.StateType.SHOWING):
                continue
            checked += 1
            if not (node.get_name() or "").strip():
                children = [node.get_child_at_index(i) for i in range(node.get_child_count())]
                unnamed.append({"role": role, "description": node.get_description(),
                                "children": [[ch.get_role_name(), ch.get_name()]
                                             for ch in children if ch]})
        print(json.dumps({"checked": checked, "unnamed": unnamed}))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
