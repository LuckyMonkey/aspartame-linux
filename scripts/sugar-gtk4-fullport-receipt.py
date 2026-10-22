#!/usr/bin/env python3
"""Host driver for a FULL PORT receipt on a headless Aspartame guest.

Keyboard input is real: every keystroke goes through QEMU's virtual keyboard,
Xorg, the GTK4 shell and Casilda before it reaches the Activity. Focus is
moved with Tab/Ctrl+Tab, as a keyboard user would. The guest half
(sugar-gtk4-fullport-probe.py, copied to /tmp) only observes over AT-SPI.

Each receipt checks, for one candidate:
  input     its core workflow, performed with real keystrokes;
  persist   Journal save on stop, then resume of the same object;
  guard     a corrupt payload is refused and its bytes are left unchanged;
  a11y      every visible interactive control has an accessible name.

Usage: sugar-gtk4-fullport-receipt.py {markdown|pippy}
Environment: ASPARTAME_QEMU_QMP (default /tmp/aspartame-qemu-qmp).
"""
import hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("macro", ROOT / "scripts/qemu-headless-macro.py")
macro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(macro)

CANDIDATES = {
    "markdown": {
        "bundle": "org.sugarlabs.Markdown",
        "marker": "markdownactivity4.MarkdownActivity",
        "editor": "Markdown source",
        "typed": "# Field notes\n\nTyped through QEMU.",
        # The preview label is exposed under its rendered text.
        "observe": (None, "Field notes\n\nTyped through QEMU."),
    },
    "pippy": {
        "bundle": "org.laptop.Pippy",
        "marker": "pippyactivity4.PippyActivity",
        "editor": "Python program editor",
        "typed": "print(6*7)",
        # Buttons are exposed under their visible label.
        "press": "Run",
        "observe": ("Program output", "42"),
    },
}
CORRUPT = b"\xff\xfe not a valid payload \xc3\x28\n"


def guest(*args):
    env = dict(os.environ, SSH_ASKPASS=os.environ.get("SSH_ASKPASS", "/tmp/aspartame-askpass"),
               SSH_ASKPASS_REQUIRE="force")
    out = subprocess.run([str(ROOT / "scripts/ssh-asp"),
                          "python3 /tmp/sugar-gtk4-fullport-probe.py " +
                          " ".join("'%s'" % a.replace("'", "'\\''") for a in args)],
                         env=env, capture_output=True, text=True, timeout=120)
    if out.returncode:
        raise SystemExit("guest %s failed: %s" % (args[0], out.stderr.strip() or out.stdout))
    return json.loads(out.stdout.strip().splitlines()[-1])


def guest_shell(command):
    env = dict(os.environ, SSH_ASKPASS="/tmp/aspartame-askpass", SSH_ASKPASS_REQUIRE="force")
    return subprocess.run([str(ROOT / "scripts/ssh-asp"), command], env=env,
                          capture_output=True, text=True, timeout=60, check=True).stdout


def sha(path):
    return guest_shell("sha256sum '%s'" % path).split()[0]


def focus(qmp, pid, name, key="TAB", limit=30):
    for _ in range(limit):
        if guest("focused", str(pid))["name"] == name:
            return True
        qmp.key(key)
        time.sleep(0.3)
    raise SystemExit("could not reach %r with %s" % (name, key))


def wait_text(pid, name, needle, timeout=15):
    """Wait until the named node (or, with name None, any node) shows needle."""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if name is None:
            texts = [row[2] for row in guest("names", str(pid))]
            text = next((t for t in texts if needle in t), "")
        else:
            text = guest("text", str(pid), name)["text"]
        if needle in text:
            return text
        time.sleep(0.5)
    raise SystemExit("%r never showed %r (last: %r)" % (name, needle, text))


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    if name not in CANDIDATES:
        raise SystemExit(__doc__)
    c = CANDIDATES[name]
    qmp = macro.Qmp(os.environ.get("ASPARTAME_QEMU_QMP", "/tmp/aspartame-qemu-qmp"))
    results = {}

    # input: a fresh object, edited only with real keystrokes.
    run = guest("launch", c["bundle"], c["marker"])
    pid, aid = run["pid"], run["aid"]
    focus(qmp, pid, c["editor"])
    qmp.key("CTRL+A")
    qmp.type_text(c["typed"])
    if "press" in c:
        focus(qmp, pid, c["press"], key="CTRL+TAB")
        qmp.key("SPACE")
    wait_text(pid, *c["observe"])
    editor_text = guest("text", str(pid), c["editor"])["text"]
    assert editor_text == c["typed"], (editor_text, c["typed"])
    results["input"] = "PASS keys=qemu focus=%s" % ("tab" if "press" not in c else "tab,ctrl+tab")

    a11y = guest("a11y", str(pid))
    results["a11y"] = ("PASS" if not a11y["unnamed"] else "FAIL unnamed=%s" % a11y["unnamed"]) + \
        " checked=%d" % a11y["checked"]

    # persist: stop saves to the Journal; resume shows the same work.
    saved = guest("stop", str(pid), aid)
    payload = guest_shell("cat '%s'" % saved["path"])
    assert payload == c["typed"], (payload, c["typed"])
    run = guest("launch", c["bundle"], c["marker"], saved["uid"])
    wait_text(run["pid"], c["editor"], c["typed"])
    guest("stop", str(run["pid"]), run["aid"], saved["uid"])
    results["persist"] = "PASS object=%s" % saved["uid"]

    # guard: a corrupt payload is refused and left byte-for-byte unchanged.
    path = guest("payload", saved["uid"])["path"]
    guest_shell("printf '%s' > '%s'" % ("".join("\\%03o" % b for b in CORRUPT), path))
    before = sha(path)
    run = guest("launch", c["bundle"], c["marker"], saved["uid"])
    guest("stop", str(run["pid"]), run["aid"], saved["uid"])
    after = sha(guest("payload", saved["uid"])["path"])
    results["guard"] = ("PASS" if before == after else "FAIL") + " sha256=%s" % before[:12]

    for key in ("input", "persist", "guard", "a11y"):
        print("%s-%s=%s" % (name, key, results[key]))
    ok = all(v.startswith("PASS") for v in results.values())
    print("fullport-receipt=%s candidate=%s" % ("PASS" if ok else "FAIL", name))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
