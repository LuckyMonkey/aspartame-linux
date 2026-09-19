from pathlib import Path


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
