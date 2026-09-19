import os
from pathlib import Path
import subprocess
import tarfile


ROOT = Path(__file__).resolve().parents[1]


def test_iso_builder_requires_and_stages_standalone_preview():
    script = (ROOT / "scripts" / "build-iso.sh").read_text()
    assert "GTK4_PREVIEW_ARCHIVE" in script
    assert "gtk4-preview-standalone.tar.gz" in script
    assert "STANDALONE-MANIFEST" in script
    assert "/usr/lib/aspartame" in script
    assert "gtk4-overlay" in script


def test_live_session_prefers_packaged_preview_without_dev_share():
    script = (
        ROOT
        / "archiso"
        / "aspartame"
        / "airootfs"
        / "usr"
        / "local"
        / "bin"
        / "aspartame-x-session"
    ).read_text()
    assert "ASPARTAME_GTK4_ROOT:-/usr/lib/aspartame/gtk4-preview" in script
    assert "sugar-gtk4-space.sh" in script
    assert "mountpoint -q /mnt/aspartame-dev" in script


def test_staged_activities_keep_gtk4_log_and_refresh_legacy_count(tmp_path):
    """Exercise ISO staging with the two broken layouts from the guest archive."""
    project = tmp_path / "project"
    profile = project / "archiso/aspartame"
    profile.mkdir(parents=True)
    for directory in ("packages", "scripts", "gtk4-overlay"):
        (project / directory).symlink_to(ROOT / directory, target_is_directory=True)
    preview = tmp_path / "archive/gtk4-preview"
    (preview / "venv/bin").mkdir(parents=True)
    (preview / "venv/bin/python").symlink_to("/usr/bin/python3")
    activities = preview / "prefix/share/sugar/activities"
    activities.mkdir(parents=True)
    for name, package, entrypoint in (
        ("Log", "log-activity", "logviewer.LogActivity"),
        ("ImageViewer", "imageviewer-activity", "imageviewer.ImageViewerActivity"),
    ):
        source = preview / "sources" / package
        (source / "activity").mkdir(parents=True)
        (source / "activity/activity.info").write_text(
            f"[Activity]\nname = {name}\nexec = sugar-activity4 {entrypoint}\n"
        )
        (source / "entrypoint.py").write_text("from sugar4.activity import activity\n")
        (activities / f"{name}.activity").symlink_to(
            f"/home/aspartame/Development/gtk4-preview/sources/{package}"
        )
    count = activities / "Count.activity"
    count.mkdir()
    (count / "countactivity4.py").write_text("# stale archived Activity\n")
    (count / "gtk4-count-activity").symlink_to(
        "/mnt/aspartame-dev/packages/gtk4-count-activity"
    )
    (activities / "Calculate.activity").symlink_to(
        "/mnt/aspartame-dev/packages/gtk4-calculate-activity"
    )
    archive = tmp_path / "preview.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        output.add(preview, arcname="gtk4-preview")
    tools = tmp_path / "bin"
    tools.mkdir()
    mkarchiso = tools / "mkarchiso"
    mkarchiso.write_text("#!/bin/sh\nexit 0\n")
    mkarchiso.chmod(0o755)
    work = tmp_path / "work"
    subprocess.run(
        ["bash", str(ROOT / "scripts/build-iso.sh")],
        env={
            **os.environ,
            "PATH": f"{tools}:{os.environ['PATH']}",
            "PROFILE": str(profile),
            "OUT_DIR": str(tmp_path / "out"),
            "WORK_DIR": str(work),
            "GTK4_PREVIEW_ARCHIVE": str(archive),
        },
        check=True,
        capture_output=True,
        text=True,
    )
    staged = (
        work / "profile/airootfs/usr/lib/aspartame/gtk4-preview"
        / "prefix/share/sugar/activities"
    )
    log = staged / "Log.activity"
    assert "exec = sugar-activity4" in (log / "activity/activity.info").read_text()
    assert "from sugar4" in (log / "entrypoint.py").read_text()
    assert (staged / "Count.activity/countactivity4.py").read_bytes() == (
        ROOT / "packages/gtk4-count-activity/countactivity4.py"
    ).read_bytes()
    assert not (staged / "Count.activity/gtk4-count-activity").exists()
    assert (staged / "Calculate.activity/calculateactivity4.py").is_file()
    assert not any(path.is_symlink() for path in staged.rglob("*"))


def test_export_contains_built_runtime_without_user_state(tmp_path):
    root = tmp_path / "custom-preview-root"
    for directory in (
        "sources/sugar/src", "prefix/lib", "venv/bin", "runtime/schemas",
        "runtime/home", "runtime/config", "runtime/activities", "logs", "build",
    ):
        (root / directory).mkdir(parents=True)
    for required in (
        "PINS.tsv", "sources/sugar/src/main.py", "prefix/lib/libcasilda.so",
        "runtime/schemas/gschemas.compiled", "runtime/group-labels.json",
    ):
        (root / required).write_text("built input\n")
    for private in (
        "runtime/home/journal", "runtime/config/settings", "runtime/wayland-sugar.lock",
        "runtime/activities/stale", "logs/shell.log", "build/compiler-output",
    ):
        (root / private).write_text("must not ship\n")
    (root / "venv/bin/python").symlink_to("./python3")
    archive = tmp_path / "artifacts/preview.tar.gz"
    subprocess.run(
        ["bash", str(ROOT / "scripts/sugar-gtk4-export.sh"), str(archive)],
        env={**os.environ, "GTK4_ROOT": str(root)},
        check=True,
        capture_output=True,
        text=True,
    )
    with tarfile.open(archive) as exported:
        names = set(exported.getnames())
        assert "gtk4-preview/sources/sugar/src/main.py" in names
        assert "gtk4-preview/prefix/lib/libcasilda.so" in names
        assert "gtk4-preview/PINS.tsv" in names
        assert exported.getmember("gtk4-preview/venv/bin/python").linkname == "./python3"
        assert {name for name in names if name.startswith("gtk4-preview/runtime/")} == {
            "gtk4-preview/runtime/schemas",
            "gtk4-preview/runtime/schemas/gschemas.compiled",
            "gtk4-preview/runtime/group-labels.json",
        }
        assert not any(name.startswith(("gtk4-preview/logs/", "gtk4-preview/build/"))
                       for name in names)
