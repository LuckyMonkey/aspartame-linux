#!/usr/bin/env python3
"""Host driver for a FULL PORT receipt on a headless Aspartame guest.

Keyboard input is real: every keystroke goes through QEMU's virtual keyboard,
Xorg, the GTK4 shell and Casilda before it reaches the Activity. Focus is
moved with Tab/Ctrl+Tab, as a keyboard user would. The guest half
(sugar-gtk4-fullport-probe.py, copied to /tmp) only observes over AT-SPI,
and seeds test objects into the Journal.

Each receipt checks, for one candidate:
  input     its core workflow, performed with real keystrokes;
  persist   Journal save on stop, then resume of the same object;
  guard     a corrupt payload is refused and its bytes are left unchanged;
  a11y      every visible interactive control has an accessible name.

A candidate is a list of steps:
  ("focus", NAME[, KEY])   press Tab (or KEY) until NAME has focus
  ("key", KEYS)            press a key combination, e.g. "CTRL+A"
  ("type", TEXT)           type text
  ("see", NAME, TEXT)      wait until the node NAME (None: any node) shows TEXT.
                           A GTK4 label's accessible name is its text, so
                           labels are matched with None and distinctive TEXT.
  ("match", REGEX)         wait until some node's text matches REGEX
  ("journal", TITLE)       wait until a Journal object has this title

Usage: sugar-gtk4-fullport-receipt.py {%s}
Environment: ASPARTAME_QEMU_QMP (default /tmp/aspartame-qemu-qmp).
"""
import hashlib, importlib.util, json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("macro", ROOT / "scripts/qemu-headless-macro.py")
macro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(macro)

CANDIDATES = {
    "markdown": {
        "bundle": "org.sugarlabs.Markdown",
        "marker": "markdownactivity4.MarkdownActivity",
        "steps": [("focus", "Markdown source"), ("key", "CTRL+A"),
                  ("type", "# Field notes\n\nTyped through QEMU."),
                  # The preview label is exposed under its rendered text.
                  ("see", None, "Field notes\n\nTyped through QEMU.")],
        "payload": ["# Field notes\n\nTyped through QEMU."],
        "resume": ("Markdown source", "# Field notes\n\nTyped through QEMU."),
    },
    "pippy": {
        "bundle": "org.laptop.Pippy",
        "marker": "pippyactivity4.PippyActivity",
        "steps": [("focus", "Python program editor"), ("key", "CTRL+A"), ("type", "print(6*7)"),
                  # Buttons are exposed under their visible label.
                  ("focus", "Run", "CTRL+TAB"), ("key", "SPACE"),
                  ("see", "Program output", "42")],
        "payload": ["print(6*7)"],
        "resume": ("Python program editor", "print(6*7)"),
    },
    "abacus": {
        "bundle": "com.homegrownapps.abacus",
        "marker": "abacusactivity4.AbacusActivity",
        # Soroban, chosen from the type list: its units rod sits mid-frame,
        # so 3.25 fits (it does not on the default suanpan). Then one bead
        # up with the arrow key on the last rod (10^-7).
        # A dropdown's focusable button is named by its current choice.
        "steps": [("focus", "Suanpan"), ("key", "SPACE"), ("key", "DOWN"), ("key", "RET"),
                  ("focus", "Number to show"), ("type", "3.25"), ("key", "RET"),
                  ("see", None, "Showing 3.25"),
                  ("focus", "Abacus beads"), ("key", "UP"),
                  ("see", None, "3.2500001")],
        "payload": ['"type": "soroban"'],
        "resume": (None, "3.2500001"),
    },
    "finance": {
        "bundle": "org.laptop.community.Finance",
        "marker": "financeactivity4.FinanceActivity",
        "steps": [("focus", "Description"), ("type", "Bread"),
                  ("focus", "Category"), ("type", "Food"),
                  ("focus", "Amount"), ("type", "4.50"), ("key", "RET"),
                  ("see", None, "Out 4.50"),
                  ("focus", "Budget"), ("key", "SPACE"),
                  ("focus", "Budget category"), ("type", "Food"),
                  ("focus", "Monthly budget"), ("type", "10"), ("key", "RET"),
                  ("see", None, "Budget for Food: 10.00 a month")],
        "payload": ['"budgets": {"Food": {"amount": 10.0}}', '"category": "Food"'],
        "resume": (None, "Out 4.50"),
    },
    "jukebox": {
        "bundle": "org.laptop.sugar.Jukebox",
        "marker": "jukeboxactivity4.JukeboxActivity",
        "seed": ["tone", "clip"],
        "steps": [("focus", "Add from Journal"), ("key", "SPACE"),
                  ("focus", "Add Tone to playlist"), ("key", "SPACE"),
                  ("focus", "Add Clip to playlist"), ("key", "SPACE"),
                  ("see", None, "2. Clip"),
                  ("focus", "Play"), ("key", "SPACE"),
                  ("see", None, "Playing: Tone"),
                  # The 10 s tone is under way...
                  ("match", r"^0:0[1-9] / 0:10$"),
                  # ...Next (or its end) moves on to the 8 s video, whose
                  # first frame reports its size.
                  ("focus", "Next"), ("key", "SPACE"),
                  ("see", None, "Playing: Clip · video 320×240"),
                  ("match", r"^0:0[1-7] / 0:08$")],
        "payload": ["#EXTINF:Tone\njournal://", "#EXTINF:Clip\njournal://"],
        "resume": (None, "2. Clip"),
    },
    "write": {
        "bundle": "org.sugarlabs.Write",
        "marker": "writeactivity4.WriteActivity",
        "steps": [("focus", "Document text"), ("type", "Field notes"), ("key", "SHIFT+HOME"),
                  # In the document Tab types a tab; Ctrl+Tab leaves it.
                  ("focus", "Normal", "CTRL+TAB"), ("key", "SPACE"), ("key", "DOWN"), ("key", "RET"),
                  ("see", None, "Style: Heading 1"),
                  ("focus", "Document text"), ("key", "CTRL+END"),
                  ("type", "\nHello "), ("key", "CTRL+B"), ("type", "bold"), ("key", "CTRL+B"),
                  ("type", " text"),
                  ("see", "Document text", "Field notes\nHello bold text"),
                  ("focus", "Export PDF", "CTRL+TAB"), ("key", "SPACE"),
                  ("see", None, "(PDF) to the Journal")],
        "payload": ["{\\rtf1", "{\\*\\aspstyle h1}", "\\b bold}"],
        "resume": ("Document text", "Field notes\nHello bold text"),
    },
    "portfolio": {
        "bundle": "org.sugarlabs.PortfolioActivity",
        "marker": "portfolioactivity4.PortfolioActivity",
        "seed": ["starred"],
        "steps": [("see", "Slide title", "Kite"),
                  ("focus", "Next"), ("key", "SPACE"),
                  ("see", "Slide title", "Volcano"),
                  ("focus", "Slide title"), ("key", "CTRL+A"), ("type", "Volcano model"),
                  ("focus", "Save as PDF"), ("key", "SPACE"),
                  ("see", None, "pages, to the Journal")],
        "payload": ['"format": "aspartame-portfolio-v2"'],
        "journal": ["Volcano model"],
        "resume": ("Slide title", "Volcano model"),
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


def focus(qmp, pid, name, key="TAB", limit=80):
    for _ in range(limit):
        if guest("focused", str(pid))["name"] == name:
            return True
        qmp.key(key)
        time.sleep(0.3)
    raise SystemExit("could not reach %r with %s" % (name, key))


def wait_text(pid, name, needle, timeout=20):
    """Wait until the named node (or, with name None, any node) shows needle."""
    end, text = time.monotonic() + timeout, None
    while time.monotonic() < end:
        if name is None:
            texts = [row[2] for row in guest("names", str(pid))]
            text = next((t for t in texts if needle in t), "")
        else:
            try:
                text = guest("text", str(pid), name)["text"]
            except SystemExit:
                text = None   # not there yet
        if text is not None and needle in text:
            return text
        time.sleep(0.5)
    raise SystemExit("%r never showed %r (last: %r)" % (name, needle, text))


def wait_match(pattern, pid, timeout=20):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if any(re.search(pattern, row[2]) for row in guest("names", str(pid))):
            return True
        time.sleep(0.3)
    raise SystemExit("no node matched %r" % pattern)


def wait_journal(title, timeout=20):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if guest("find", title)["count"]:
            return True
        time.sleep(0.5)
    raise SystemExit("no Journal object titled %r" % title)


def run_steps(qmp, pid, steps):
    for step in steps:
        kind = step[0]
        if kind == "focus":
            focus(qmp, pid, step[1], *step[2:])
        elif kind == "key":
            qmp.key(step[1])
            time.sleep(0.4)
        elif kind == "type":
            qmp.type_text(step[1])
            time.sleep(0.3)
        elif kind == "see":
            wait_text(pid, step[1], step[2])
        elif kind == "match":
            wait_match(step[1], pid)
        elif kind == "journal":
            wait_journal(step[1])
        else:
            raise ValueError(kind)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    if name not in CANDIDATES:
        raise SystemExit(__doc__ % "|".join(CANDIDATES))
    c = CANDIDATES[name]
    qmp = macro.Qmp(os.environ.get("ASPARTAME_QEMU_QMP", "/tmp/aspartame-qemu-qmp"))
    results = {}

    for kind in c.get("seed", ()):
        guest("seed", kind)

    # input: a fresh object, worked only with real keystrokes.
    run = guest("launch", c["bundle"], c["marker"])
    pid, aid = run["pid"], run["aid"]
    run_steps(qmp, pid, c["steps"])
    results["input"] = "PASS keys=qemu steps=%d" % len(c["steps"])

    a11y = guest("a11y", str(pid))
    results["a11y"] = ("PASS" if not a11y["unnamed"] else "FAIL unnamed=%s" % a11y["unnamed"]) + \
        " checked=%d" % a11y["checked"]

    # persist: stop saves to the Journal; resume shows the same work.
    saved = guest("stop", str(pid), aid)
    payload = guest_shell("cat '%s'" % saved["path"])
    missing = [needle for needle in c["payload"] if needle not in payload]
    assert not missing, ("payload lacks", missing, payload[:600])
    for title in c.get("journal", ()):
        wait_journal(title)
    run = guest("launch", c["bundle"], c["marker"], saved["uid"])
    wait_text(run["pid"], *c["resume"])
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
