from pathlib import Path


ROOT = Path(__file__).parents[1]
MODEL = ROOT / "archiso/aspartame/airootfs/usr/share/aspartame/cpsection/aboutcomputer/model.py"
VIEW = ROOT / "archiso/aspartame/airootfs/usr/share/aspartame/cpsection/aboutcomputer/view.py"


def test_about_computer_uses_os_release_not_lsb_release():
    model = MODEL.read_text()
    assert "def _read_os_release" in model
    assert "Aspartame Linux (Arch Linux)" in model
    assert "lsb_release" not in model


def test_about_computer_exposes_system_inventory():
    model = MODEL.read_text()
    view = VIEW.read_text()
    for label in ("Distribution:", "Kernel:", "Architecture:", "CPU:",
                  "Memory:", "Storage:", "Graphics:", "Session:",
                  "Python:", "Uptime:"):
        assert label in model
    assert "def get_system_information" in model
    assert "self._setup_system()" in view
    assert "for label, value in self._model.get_system_information()" in view
