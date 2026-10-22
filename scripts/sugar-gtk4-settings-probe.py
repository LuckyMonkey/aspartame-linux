#!/usr/bin/env python3
"""Guest acceptance: Settings close/reopen and visible About Computer inventory.

Run as root in an idle Aspartame test guest. Uses the modern shell's own
environment; opens Settings and returns to Home without changing settings.
An optional output path captures the About Computer surface using ffmpeg.
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time


def wait_for(label, callback):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        result = callback()
        if result:
            return result
        time.sleep(0.1)
    raise RuntimeError(f'timed out: {label}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lifecycle-only', action='store_true')
    parser.add_argument('screenshot', nargs='?')
    args = parser.parse_args()
    if 'IMAGE_ID=aspartame' not in Path('/etc/os-release').read_text():
        raise SystemExit('Run inside an Aspartame test guest')
    if os.getuid() == 0:
        pids = subprocess.check_output(
            ['pgrep', '-u', 'aspartame', '-f', '/sources/sugar/src/jarabe/main.py'],
            text=True).splitlines()
        if len(pids) != 1:
            raise SystemExit('Expected exactly one modern shell')
        env = dict(item.split('=', 1) for item in
                   Path(f'/proc/{pids[0]}/environ').read_bytes().decode().split('\0')
                   if '=' in item)
        interpreter = Path(f'/proc/{pids[0]}/cmdline').read_bytes().decode().split('\0')[0]
        owner = Path(f'/proc/{pids[0]}').stat()
        os.setgroups([])
        os.setgid(owner.st_gid)
        os.setuid(owner.st_uid)
        os.execve(interpreter, [interpreter, __file__, *sys.argv[1:]], env)

    import dbus
    session = dbus.SessionBus()
    shell = dbus.Interface(session.get_object('org.laptop.Shell', '/org/laptop/Shell'),
                           'org.laptop.Shell')
    address = dbus.Interface(session.get_object('org.a11y.Bus', '/org/a11y/bus'),
                             'org.a11y.Bus').GetAddress()
    bus = dbus.bus.BusConnection(str(address))

    def interface(ref, name):
        return dbus.Interface(bus.get_object(str(ref[0]), str(ref[1])), name)

    def find(name, ref=('org.a11y.atspi.Registry', '/org/a11y/atspi/accessible/root'), depth=0):
        if depth > 20:
            return None
        try:
            props = interface(ref, 'org.freedesktop.DBus.Properties')
            if str(props.Get('org.a11y.atspi.Accessible', 'Name')) == name:
                return ref
            children = interface(ref, 'org.a11y.atspi.Accessible').GetChildren()
        except dbus.DBusException:
            return None
        for child in children:
            hit = find(name, child, depth + 1)
            if hit:
                return hit
        return None

    def activate(name):
        ref = wait_for(name, lambda: find(name))
        actions = interface(ref, 'org.a11y.atspi.Action')
        if actions.GetActions():
            assert actions.DoAction(0), name
        else:
            # SectionIcon does not export an AT-SPI action on this GTK build.
            # Locate its actual screen bounds before sending a guest click.
            x, y, width, height = interface(
                ref, 'org.a11y.atspi.Component').GetExtents(0)
            assert width > 0 and height > 0, name
            controller = interface(
                ('org.a11y.atspi.Registry', '/org/a11y/atspi/registry/deviceeventcontroller'),
                'org.a11y.atspi.DeviceEventController')
            controller.GenerateMouseEvent(x + width // 2, y + height // 2, 'b1c')

    assert shell.ShowHome()
    try:
        for cycle in range(3):
            assert shell.ShowControlPanel(), 'Settings action did not report success'
            wait_for('About tile', lambda: find('About my Computer'))
            assert not shell.ShowControlPanel(), 'duplicate modal Settings accepted'
            assert shell.ShowHome()
            wait_for('Settings dismissed', lambda: not find('About my Computer'))
            print(f'settings-cycle={cycle + 1} close-reopen=PASS', flush=True)
        if args.lifecycle_only:
            print('settings-lifecycle=PASS', flush=True)
            return
        assert shell.ShowControlPanel()
        activate('About my Computer')
        wait_for('local inventory', lambda: find('Read-only local inventory'))
        activate('Refresh inventory')
        wait_for('refreshed inventory', lambda: find('Refresh inventory'))
        if args.screenshot:
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error',
                            '-f', 'x11grab', '-video_size', '1920x1080',
                            '-i', os.environ.get('DISPLAY', ':0'), '-frames:v',
                            '1', '-y', args.screenshot], check=True)
        print('settings-aboutcomputer=PASS refresh=PASS', flush=True)
    finally:
        shell.ShowHome()


if __name__ == '__main__':
    main()
