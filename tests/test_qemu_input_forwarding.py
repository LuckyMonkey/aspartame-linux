from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_qemu_forwards_keyboard_by_default_while_remaining_floating():
    script = (ROOT / "scripts/run-qemu.sh").read_text()
    assert 'QEMU_GRAB_ON_HOVER=${QEMU_GRAB_ON_HOVER:-on}' in script
    assert 'grab-on-hover=$QEMU_GRAB_ON_HOVER' in script
    assert 'zoom-to-fit=on' in script
    assert '-device usb-kbd' in script
    assert 'QEMU_WINDOW_WIDTH=${QEMU_WINDOW_WIDTH:-1600}' in script
    assert 'QEMU_WINDOW_HEIGHT=${QEMU_WINDOW_HEIGHT:-900}' in script
    assert 'xdotool windowsize' in script
