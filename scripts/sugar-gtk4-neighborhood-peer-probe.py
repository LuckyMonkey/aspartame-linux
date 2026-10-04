#!/usr/bin/env python3
"""Report the live GTK4 Neighborhood accessibility tree and peer names."""

import os
from pathlib import Path
import subprocess
import sys


def walk(node, depth=0):
    if node is None or depth > 16:
        return
    yield node, depth
    try:
        count = node.get_child_count()
    except Exception:
        return
    for index in range(count):
        try:
            child = node.get_child_at_index(index)
        except Exception:
            child = None
        yield from walk(child, depth + 1)


if 'IMAGE_ID=aspartame' not in Path('/etc/os-release').read_text():
    raise SystemExit('guest-only')

if os.getuid() == 0:
    pids = subprocess.check_output(
        ['pgrep', '-u', 'aspartame', '-f', '/sources/sugar/src/jarabe/main.py'],
        text=True).splitlines()
    if len(pids) != 1:
        raise SystemExit(f'expected one modern shell, found {pids!r}')
    env = dict(item.split('=', 1) for item in
               Path(f'/proc/{pids[0]}/environ').read_bytes().decode().split('\0')
               if '=' in item)
    env['ASPARTAME_ATSPI_BUS'] = (
        f"unix:path={env['XDG_RUNTIME_DIR']}/at-spi/bus_0")
    interpreter = os.environ.get(
        'GTK4_PYTHON', '/usr/lib/aspartame/gtk4-preview/venv/bin/python')
    os.setgroups([])
    os.setgid(1000)
    os.setuid(1000)
    os.execve(interpreter, [interpreter, __file__], env)

import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi


root = Atspi.get_desktop(0)
matches = []
for node, depth in walk(root):
    try:
        name = node.get_name() or ''
        role = node.get_role_name() or ''
        pid = node.get_process_id()
    except Exception:
        continue
    if name or role in ('frame', 'panel', 'image'):
        if ('Aspartame' in name or 'Neighborhood' in name or
                'nearby' in name or role in ('frame', 'panel')):
            matches.append((depth, role, name, pid))

print(f'atspi-matches={len(matches)}')
for depth, role, name, pid in matches:
    print(f'depth={depth} role={role!r} name={name!r} pid={pid}')
print('neighborhood-peer-probe=PASS')
