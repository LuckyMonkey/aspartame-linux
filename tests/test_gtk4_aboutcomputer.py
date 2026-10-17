from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'gtk4-overlay/src/cpsection/aboutcomputer/inventory.py'
VIEW = ROOT / 'gtk4-overlay/src/cpsection/aboutcomputer/view.py'
MODEL = ROOT / 'gtk4-overlay/src/cpsection/aboutcomputer/model.py'
PATCH = ROOT / 'patches/gtk4-preview/0112z-controlpanel-aboutcomputer-section.patch'
BUILD = ROOT / 'scripts/sugar-gtk4-build.sh'


def _load_inventory():
    namespace = {}
    exec(compile(INVENTORY.read_text(), str(INVENTORY), 'exec'), namespace)
    return namespace


def test_inventory_maps_os_release_and_proc_sources_without_shell_dump(tmp_path):
    inventory = _load_inventory()
    os_release = tmp_path / 'os-release'
    meminfo = tmp_path / 'meminfo'
    uptime = tmp_path / 'uptime'
    os_release.write_text(
        'NAME="Aspartame Linux"\nIMAGE_ID=aspartame\n'
        'IMAGE_VERSION=2026.10.17\n')
    meminfo.write_text('MemTotal:       2097152 kB\n')
    uptime.write_text('3661.0 0.0\n')

    def command_runner(command):
        if command[0] == 'lscpu':
            return '# comment\nTest CPU 9000\n'
        return '00:02.0 VGA compatible controller: Virtio GPU [1af4:1050]\n'

    values = inventory['collect_inventory'](
        os_release_path=str(os_release), meminfo_path=str(meminfo),
        uptime_path=str(uptime), command_runner=command_runner,
        disk_usage=lambda _path: SimpleNamespace(
            free=2 * 1024**3, total=8 * 1024**3),
        environment={'XDG_CURRENT_DESKTOP': 'Sugar',
                     'WAYLAND_DISPLAY': 'wayland-0'},
        kernel='6.12-aspartame', machine='x86_64', processor='fallback',
        cpu_count=4, hostname='aspartame-vm', python_version='3.13.0')

    assert values['distribution'] == 'Aspartame Linux (Arch Linux)'
    assert values['build'] == 'Aspartame Linux (Arch Linux) 2026.10.17'
    assert values['kernel'] == '6.12-aspartame'
    assert values['memory'] == '2.0 GiB'
    assert values['storage'] == '2.0 GiB free of 8.0 GiB'
    assert values['graphics'] == 'Virtio GPU [1af4:1050]'
    assert values['desktop'] == 'Sugar'
    assert values['session'] == 'Wayland'
    assert values['uptime'] == '1h 1m'
    assert 'fastfetch' not in repr(values)


def test_inventory_falls_back_when_optional_sources_are_missing():
    inventory = _load_inventory()
    values = inventory['collect_inventory'](
        os_release_path='/does/not/exist', meminfo_path='/does/not/exist',
        uptime_path='/does/not/exist', command_runner=lambda _command: '',
        disk_usage=lambda _path: (_ for _ in ()).throw(OSError()),
        environment={}, kernel='', machine='', processor='', cpu_count=0,
        hostname='', python_version='')

    assert values['distribution'] == 'Not available'
    assert values['build'] == 'Not available'
    assert values['memory'] == 'Not available'
    assert values['storage'] == 'Not available'
    assert values['graphics'] == 'Not available'
    assert values['session'] == 'Not available'


def test_about_computer_is_native_refreshable_and_registered():
    view = VIEW.read_text()
    model = MODEL.read_text()
    patch = PATCH.read_text()
    build = BUILD.read_text()

    assert "class AboutComputer(SectionView)" in view
    assert "self._refresh_system()" in view
    assert "Refresh inventory" in view
    assert "get_system_information()" in view
    assert "Gtk3" not in view
    for field in ('Kernel:', 'Desktop:', 'Graphics:', 'Memory:',
                  'Storage:', 'Build:'):
        assert field in model or field in view
    assert 'collect_inventory' in model
    assert "options['aboutcomputer']" in patch
    assert 'import cpsection.aboutcomputer' in patch
    assert '*0112*) target="$root/sources/sugar" ;;' in build
    assert '0112-controlpanel-activity-manager-section.patch' in build
    assert '*0112z*' in build
