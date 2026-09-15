#!/usr/bin/env python3
"""Guest regression: edit Write via AT-SPI, stop, inspect datastore, resume.

This exercises real Activity processes and Journal payloads. AT-SPI editing
does not establish physical keyboard delivery. Test objects are retained in
the preview Journal for inspection. Run as root inside the development VM.
"""

import os
from pathlib import Path
import subprocess
import sys
import time


def wait_for(description, callback):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        result = callback()
        if result:
            return result
        time.sleep(0.1)
    raise RuntimeError(f"Timed out: {description}")


def main():
    if 'IMAGE_ID=aspartame' not in Path('/etc/os-release').read_text():
        raise SystemExit('Run this probe inside the Aspartame guest.')
    if os.getuid() == 0:
        pids = subprocess.check_output(
            ['pgrep', '-u', 'aspartame', '-f', '/sources/sugar/src/jarabe/main.py'],
            text=True).splitlines()
        if len(pids) != 1:
            raise SystemExit('Expected exactly one modern shell.')
        env = dict(item.split('=', 1) for item in
                   Path(f'/proc/{pids[0]}/environ').read_bytes().decode().split('\0')
                   if '=' in item)
        interpreter = '/home/aspartame/Development/gtk4-preview/venv/bin/python'
        os.setgroups([])
        os.setgid(1000)
        os.setuid(1000)
        os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)

    import dbus
    import gi
    gi.require_version('Atspi', '2.0')
    from gi.repository import Atspi

    bus = dbus.SessionBus()
    journal = dbus.Interface(bus.get_object('org.laptop.Journal', '/org/laptop/Journal'),
                             'org.laptop.Journal')
    shell = dbus.Interface(bus.get_object('org.laptop.Shell', '/org/laptop/Shell'),
                           'org.laptop.Shell')
    store = dbus.Interface(bus.get_object('org.laptop.sugar.DataStore',
                                         '/org/laptop/sugar/DataStore'),
                           'org.laptop.sugar.DataStore')

    def processes():
        result = []
        for path in Path('/proc').glob('[0-9]*/cmdline'):
            try:
                args = path.read_bytes().decode().split('\0')
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            if 'writeactivity4.WriteActivity' in args:
                result.append((int(path.parent.name), args[args.index('--activity-id') + 1]))
        return result

    def find_document(node, pid, depth=0):
        if depth > 12:
            return None
        if node.get_name() == 'Document text' and node.get_process_id() == pid:
            return node
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            if child is not None:
                found = find_document(child, pid, depth + 1)
                if found is not None:
                    return found
        return None

    def launch(object_id=''):
        assert journal.LaunchBundle('org.sugarlabs.Write', object_id)
        pid, activity_id = wait_for('Write process', lambda: next(iter(processes()), None))
        wait_for('Activity service', lambda: bus.name_has_owner('org.laptop.Activity' + activity_id))
        wait_for('shell launch completion', lambda: shell.ActivateActivity(activity_id))
        document = wait_for('accessible document', lambda: find_document(Atspi.get_desktop(0), pid))
        return pid, activity_id, document

    def stop(pid, activity_id):
        assert shell.StopActivity(activity_id)
        wait_for('process exit', lambda: not Path(f'/proc/{pid}').exists())
        assert not bus.name_has_owner('org.laptop.Activity' + activity_id)
        assert not shell.ActivateActivity(activity_id), 'stale shell activity'

    if processes():
        raise SystemExit('Write is already running; stop it before this probe.')
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    if cycles < 1:
        raise SystemExit('cycles must be positive')
    for cycle in range(1, cycles + 1):
        content = f'Aspartame Journal round trip {cycle}: café — saved work\nSecond line.'
        pid, activity_id, document = launch()
        assert Atspi.EditableText.set_text_contents(document, content)
        assert Atspi.Text.get_text(document, 0, -1) == content
        stop(pid, activity_id)
        rows, _ = store.find(dbus.Dictionary({'activity_id': activity_id}, signature='sv'),
                             dbus.Array(['uid'], signature='s'))
        assert len(rows) == 1, 'expected one saved Journal object'
        uid = str(rows[0]['uid'])
        filename = str(store.get_filename(uid))
        assert filename and Path(filename).read_text(encoding='utf-8') == content, 'saved payload differs'
        resumed_pid, resumed_id, resumed = launch(uid)
        assert resumed_pid != pid
        wait_for('restored text', lambda: Atspi.Text.get_text(resumed, 0, -1) == content)
        if len(sys.argv) > 2 and cycle == cycles:
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error',
                            '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':0',
                            '-frames:v', '1', '-y', sys.argv[2]], check=True)
        stop(resumed_pid, resumed_id)
        assert Path(str(store.get_filename(uid))).read_text(encoding='utf-8') == content
        print(f'cycle={cycle} pid={pid} resumed_pid={resumed_pid} object={uid} '
              'payload=PASS resume=PASS service-release=PASS shell-cleanup=PASS', flush=True)
    print('journal-roundtrip=PASS input-method=AT-SPI', flush=True)


if __name__ == '__main__':
    main()
