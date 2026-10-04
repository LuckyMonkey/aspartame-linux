from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_journal_reboot_probe_is_uid_based_across_restarts():
    source = (ROOT / "scripts/sugar-gtk4-journal-reboot-probe.py").read_text()
    assert '"prepare", "verify"' in source
    assert 'json.dumps({"uid": uid}' in source
    assert 'store.get_filename(uid)' in source
    assert "journal-reboot-prepare=PASS" in source
    assert "journal-reboot-verify=PASS" in source
    assert "QEMU_SNAPSHOT" not in source
