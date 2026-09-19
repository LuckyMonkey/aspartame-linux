#!/usr/bin/env python3
"""Guest smoke probe for GTK4 Settings → Language construction.

The probe instantiates the real section with an empty locale provider and
confirms that it renders an English/USA row instead of raising KeyError. Run
as root inside the development guest; it re-execs as the desktop user with
the modern shell environment.
"""

import os
from pathlib import Path
import subprocess
import sys


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

    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk
    from gi.repository import Gdk
    sys.path.insert(0, '/home/aspartame/Development/gtk4-preview/sources/sugar/extensions')
    from cpsection.language.view import Language

    class EmptyLocaleModel:
        def read_all_languages(self):
            return []

        def get_languages(self):
            return ['C.UTF-8']

    Gtk.init()
    assert Gdk.Display.get_default() is not None, 'GTK display is unavailable'
    view = Language(EmptyLocaleModel(), [])
    assert view._selected_lang_count == 1
    assert view._language_buttons[0] is not None
    assert view._country_dict['English'] == [['C.UTF-8', 'USA']]
    print('language-settings=PASS fallback-row=English country=USA', flush=True)


if __name__ == '__main__':
    main()
