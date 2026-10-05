from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_qemu_forwards_keyboard_by_default_while_remaining_floating():
    script = (ROOT / "scripts/run-qemu.sh").read_text()
    assert 'QEMU_GRAB_ON_HOVER=${QEMU_GRAB_ON_HOVER:-on}' in script
    assert 'grab-on-hover=$QEMU_GRAB_ON_HOVER' in script
    assert 'zoom-to-fit=on' in script
    assert '-device virtio-vga,id=video0' in script
    assert '-device usb-kbd,id=usb_keyboard,display=video0' in script
    assert '-device virtio-keyboard-pci,id=virtio_keyboard,display=video0' in script


def test_qemu_runner_can_add_a_private_peer_network_without_changing_ssh():
    script = (ROOT / "scripts/run-qemu.sh").read_text()
    assert 'QEMU_EXTRA_NIC=${QEMU_EXTRA_NIC:-}' in script
    assert 'QEMU_EXTRA_NIC_MAC=${QEMU_EXTRA_NIC_MAC:-}' in script
    assert 'mac=$QEMU_EXTRA_NIC_MAC' in script
    assert 'EXTRA_NIC_ARGS=(-nic "$QEMU_EXTRA_NIC")' in script
    assert '"${EXTRA_NIC_ARGS[@]}"' in script
    assert 'hostfwd=tcp:127.0.0.1:${SSH_FORWARD_PORT}-:22' in script
    assert 'QEMU_WINDOW_WIDTH=${QEMU_WINDOW_WIDTH:-1600}' in script
    assert 'QEMU_WINDOW_HEIGHT=${QEMU_WINDOW_HEIGHT:-900}' in script
    assert 'xdotool windowsize' in script


def test_qemu_can_run_without_a_host_window_or_pointer_grab():
    script = (ROOT / "scripts/run-qemu.sh").read_text()
    assert 'QEMU_HEADLESS=${QEMU_HEADLESS:-0}' in script
    assert 'QEMU_DISPLAY=${QEMU_DISPLAY:-none}' in script
    assert 'test "$QEMU_HEADLESS" != 1' in script
    assert 'QEMU_SNAPSHOT=${QEMU_SNAPSHOT:-0}' in script
    assert 'SNAPSHOT_ARGS=(-snapshot)' in script


def test_gtk4_dev_sync_copies_only_runtime_inputs():
    script = (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert 'patches/gtk4-preview' in script
    assert 'packages/gtk4-help-activity' in script
    assert 'gtk4-overlay' in script
    assert 'cp -a' in script
    assert 'Generated guest build trees and runtime state remain untouched' in script


def test_gtk4_dev_sync_removes_retired_share_experiments():
    script = (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert '0186-toolkit-accept-public-join-requests.patch' in script
    assert '0187-toolkit-invite-public-contacts.patch' in script


def test_peer_fixture_isolated_from_the_normal_sugar_profile():
    runner = (ROOT / "scripts/sugar-gtk4-run.sh").read_text()
    fixture = (ROOT / "scripts/sugar-gtk4-peer-prepare.sh").read_text()

    assert 'sugar_home=${ASPARTAME_SUGAR_HOME:-$state_root/home}' in runner
    assert 'SUGAR_HOME="$sugar_home"' in runner
    assert 'SUGAR_PROFILE="$sugar_profile"' in runner
    assert 'SUGAR_PROFILE_NAME="$sugar_profile_name"' in runner
    assert 'ip -4 addr flush dev "$interface"' in fixture
    assert 'SetStaticHostname' in fixture
    assert 'ASPARTAME_SUGAR_HOME' in fixture
    assert 'systemctl restart avahi-daemon' in fixture


def test_qemu_key_sender_supports_reverse_focus_chord():
    script = (ROOT / "scripts/qemu-send-key.py").read_text()
    assert '"SHIFT+TAB": ("shift", "tab")' in script
    assert 'reversed(qcodes)' in script
    assert 'ASPARTAME_QEMU_INPUT_DEVICE' in script
    assert '"video0"' in script
