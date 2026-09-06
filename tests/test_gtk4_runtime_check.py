import os
from pathlib import Path
import socket
import subprocess


ROOT = Path(__file__).parents[1]
CHECK = ROOT / "scripts/sugar-gtk4-runtime-check.sh"


def _write_executable(path, text):
    path.write_text(text)
    path.chmod(0o755)


def _runtime(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    os_release = tmp_path / "os-release"
    os_release.write_text("IMAGE_ID=aspartame\n")
    workspace = tmp_path / "workspace"
    _write_executable(workspace, "#!/bin/sh\nprintf 'current=1\\ncount=2\\n'\n")
    _write_executable(
        fake_bin / "pgrep",
        "#!/bin/sh\ncase \"$*\" in *jarabe\\\\.main*) echo 101;; *) echo 202;; esac\n",
    )
    _write_executable(
        fake_bin / "xprop",
        """#!/bin/sh
case "$*" in
  "-root _NET_ACTIVE_WINDOW") echo '_NET_ACTIVE_WINDOW(WINDOW): window id # 0xabc';;
  "-id 0xabc _NET_WM_PID") echo '_NET_WM_PID(CARDINAL) = 202';;
  "-id 0xabc _NET_WM_DESKTOP") echo '_NET_WM_DESKTOP(CARDINAL) = 1';;
  *) exit 2;;
esac
""",
    )
    gtk4_root = tmp_path / "gtk4"
    runtime = gtk4_root / "runtime"
    runtime.mkdir(parents=True, mode=0o700)
    runtime.chmod(0o700)
    listener = socket.socket(socket.AF_UNIX)
    listener.bind(str(runtime / "wayland-sugar"))
    proc_root = tmp_path / "proc"
    (proc_root / "202").mkdir(parents=True)
    (proc_root / "202" / "environ").write_bytes(
        f"XDG_RUNTIME_DIR={runtime}\0".encode()
    )
    log = tmp_path / "gtk4.log"
    log.write_text("Gtk-WARNING: optional portal unavailable\n")
    env = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "ASPARTAME_OS_RELEASE": str(os_release),
        "ASPARTAME_WORKSPACE_TOOL": str(workspace),
        "ASPARTAME_PROC_ROOT": str(proc_root),
        "ASPARTAME_GTK4_LOG": str(log),
        "GTK4_ROOT": str(gtk4_root),
    }
    return env, log, listener


def test_gtk4_runtime_check_accepts_warnings_and_rejects_fatal_markers(tmp_path):
    env, log, listener = _runtime(tmp_path)
    try:
        clean = subprocess.run(
            [CHECK, "gtk4"], env=env, text=True, capture_output=True
        )
        assert clean.returncode == 0, clean.stderr
        assert "runtime-check=ok target=gtk4 pid=202 desktop=1" in clean.stdout

        log.write_text("Gtk-WARNING: harmless\nTraceback (most recent call last):\n")
        fatal = subprocess.run(
            [CHECK, "gtk4"], env=env, text=True, capture_output=True
        )
        assert fatal.returncode == 1
        assert "fatal marker found" in fatal.stderr
    finally:
        listener.close()


def test_runtime_check_is_read_only_and_shell_valid():
    source = CHECK.read_text()
    assert '"$workspace_tool" status' in source
    assert "$workspace_tool switch" not in source
    assert "$workspace_tool activate" not in source
    assert "$workspace_tool place" not in source
    subprocess.run(["bash", "-n", CHECK], check=True)
