"""Small, read-only system inventory for the GTK4 About panel.

The provider intentionally returns data rather than formatted terminal output.
Optional probes fail closed so a missing command or virtual-machine device
never prevents Settings from opening.
"""

import os
import platform
import shutil
import socket
import subprocess


NOT_AVAILABLE = 'Not available'


def read_os_release(path='/etc/os-release'):
    values = {}
    try:
        with open(path, encoding='utf-8') as stream:
            for raw_line in stream:
                line = raw_line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] == '"':
                    value = value[1:-1]
                values[key] = value
    except OSError:
        pass
    return values


def command_output(command):
    try:
        return subprocess.check_output(
            command, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return ''


def memory_size(path='/proc/meminfo'):
    try:
        with open(path, encoding='utf-8') as stream:
            for line in stream:
                if line.startswith('MemTotal:'):
                    kib = int(line.split()[1])
                    return '%.1f GiB' % (kib / 1024 / 1024)
    except (OSError, ValueError, IndexError):
        pass
    return NOT_AVAILABLE


def uptime(path='/proc/uptime'):
    try:
        with open(path, encoding='utf-8') as stream:
            seconds = int(float(stream.read().split()[0]))
        return '%dh %dm' % (seconds // 3600, (seconds % 3600) // 60)
    except (OSError, ValueError, IndexError):
        return NOT_AVAILABLE


def graphics_adapter(output=None):
    output = command_output(['lspci', '-nn']) if output is None else output
    for line in output.splitlines():
        if ('VGA compatible controller' in line or
                '3D controller' in line or 'Display controller' in line):
            return line.split(': ', 1)[-1]
    return NOT_AVAILABLE


def _distribution(os_release):
    if os_release.get('IMAGE_ID') == 'aspartame':
        return 'Aspartame Linux (Arch Linux)'
    return (os_release.get('PRETTY_NAME') or os_release.get('NAME') or
            NOT_AVAILABLE)


def _build(os_release):
    image = os_release.get('IMAGE_VERSION') or os_release.get('BUILD_ID')
    identity = os_release.get('PRETTY_NAME') or os_release.get('NAME')
    if os_release.get('IMAGE_ID') == 'aspartame':
        identity = 'Aspartame Linux (Arch Linux)'
    if identity and image:
        return '%s %s' % (identity, image)
    return identity or NOT_AVAILABLE


def collect_inventory(os_release_path='/etc/os-release',
                      meminfo_path='/proc/meminfo',
                      uptime_path='/proc/uptime', root_path='/',
                      command_runner=None, disk_usage=None,
                      environment=None, kernel=None, machine=None,
                      processor=None, cpu_count=None, hostname=None,
                      python_version=None):
    """Collect stable local fields with injectable readers for tests."""
    os_release = read_os_release(os_release_path)
    command_runner = command_output if command_runner is None else command_runner
    disk_usage = shutil.disk_usage if disk_usage is None else disk_usage
    environment = os.environ if environment is None else environment

    cpu = command_runner(['lscpu', '-p=MODELNAME'])
    cpu = next((line for line in cpu.splitlines()
                if line and not line.startswith('#')), '')
    if not cpu:
        cpu = processor if processor is not None else platform.processor()

    try:
        usage = disk_usage(root_path)
        storage = '%.1f GiB free of %.1f GiB' % (
            usage.free / 1024**3, usage.total / 1024**3)
    except OSError:
        storage = NOT_AVAILABLE

    backend = ('Wayland' if environment.get('WAYLAND_DISPLAY') else
               'X11' if environment.get('DISPLAY') else NOT_AVAILABLE)
    desktop = (environment.get('XDG_CURRENT_DESKTOP') or
               environment.get('XDG_SESSION_DESKTOP') or
               environment.get('DESKTOP_SESSION') or 'Sugar')
    release = kernel if kernel is not None else platform.release()
    architecture = machine if machine is not None else platform.machine()
    python_release = (python_version if python_version is not None else
                      platform.python_version())
    host = hostname if hostname is not None else socket.gethostname()
    cores = cpu_count if cpu_count is not None else os.cpu_count()

    return {
        'distribution': _distribution(os_release),
        'image': os_release.get('IMAGE_VERSION', NOT_AVAILABLE),
        'build': _build(os_release),
        'kernel': release or NOT_AVAILABLE,
        'architecture': architecture or NOT_AVAILABLE,
        'cpu': cpu or NOT_AVAILABLE,
        'cpu_cores': str(cores or NOT_AVAILABLE),
        'memory': memory_size(meminfo_path),
        'storage': storage,
        'graphics': graphics_adapter(command_runner(['lspci', '-nn'])),
        'desktop': desktop,
        'session': backend,
        'python': python_release or NOT_AVAILABLE,
        'hostname': host or NOT_AVAILABLE,
        'uptime': uptime(uptime_path),
    }
