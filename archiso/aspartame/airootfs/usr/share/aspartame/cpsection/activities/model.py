"""User-facing Activity inventory and ratings for Aspartame Settings."""

import configparser
import json
import os
import shutil
import subprocess
import time

from gettext import gettext as _


RATINGS = (_('Broken'), _('Bad'), _('Needs work'), _('Good'), _('Perfect'))
RATING_FILE = os.path.expanduser('~/.config/aspartame/activity-ratings.json')
ACTIVITY_ROOTS = (
    '/usr/share/sugar/activities',
    # Aspartame's bundled canonical/third-party Activities live separately
    # from Sugar's package-owned Activity directory.
    '/usr/share/aspartame/activities',
    '/usr/local/share/sugar/activities',
    os.path.expanduser('~/.local/share/sugar/activities'),
)
QUARANTINE_ROOT = os.path.expanduser('~/.local/share/aspartame/removed-activities')
SYSTEM_REMOVER = '/usr/local/libexec/aspartame-remove-activity'
MANAGED_SYSTEM_ROOTS = (
    '/usr/share/sugar/activities',
    '/usr/share/aspartame/activities',
    '/usr/local/share/sugar/activities',
)


def _read_info(path):
    info_path = os.path.join(path, 'activity', 'activity.info')
    if not os.path.isfile(info_path):
        return None
    parser = configparser.ConfigParser()
    parser.read(info_path, encoding='utf-8')
    section = parser['Activity'] if parser.has_section('Activity') else parser.defaults()
    bundle_id = section.get('bundle_id', os.path.basename(path))
    return {
        'id': bundle_id,
        'name': section.get('name', bundle_id),
        'icon': section.get('icon', ''),
        'version': section.get('activity_version', section.get('version', '')),
        'summary': section.get('summary', '').strip(),
        'url': section.get('url', ''),
        'path': path,
        'user': path.startswith(os.path.expanduser('~')),
    }


def list_activities(roots=ACTIVITY_ROOTS):
    """Return installed Activity metadata, sorted for a stable UI."""
    found = {}
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if not os.path.isdir(path):
                continue
            info = _read_info(path)
            if info and info['id'] not in found:
                found[info['id']] = info
    return sorted(found.values(), key=lambda item: item['name'].lower())


def load_ratings(filename=RATING_FILE):
    try:
        with open(filename, encoding='utf-8') as stream:
            data = json.load(stream)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_rating(activity_id, rating, filename=RATING_FILE):
    if rating not in range(1, 6):
        raise ValueError(_('Rating must be between 1 and 5.'))
    ratings = load_ratings(filename)
    ratings[activity_id] = rating
    parent = os.path.dirname(filename)
    os.makedirs(parent, mode=0o700, exist_ok=True)
    temporary = filename + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as stream:
        json.dump(ratings, stream, indent=2, sort_keys=True)
        stream.write('\n')
    os.replace(temporary, filename)


def remove_activity(path, quarantine=QUARANTINE_ROOT):
    """Move an Activity bundle aside, never recursively delete it."""
    path = os.path.realpath(path)
    user_root = os.path.realpath(os.path.expanduser('~/.local/share/sugar/activities'))
    if not os.path.isdir(os.path.join(path, 'activity')):
        raise ValueError(_('That Activity bundle is not valid.'))
    if not path.startswith(user_root + os.sep):
        if not any(path.startswith(os.path.realpath(root) + os.sep)
                   for root in MANAGED_SYSTEM_ROOTS):
            raise PermissionError(_('That Activity is outside a managed Activity folder.'))
        result = subprocess.run(
            ['pkexec', SYSTEM_REMOVER, path], capture_output=True, text=True)
        if result.returncode:
            message = result.stderr.strip() or _('Administrator approval was cancelled.')
            raise PermissionError(message)
        return result.stdout.strip() or path
    os.makedirs(quarantine, mode=0o700, exist_ok=True)
    target = os.path.join(quarantine, '%d-%s' % (time.time_ns(), os.path.basename(path)))
    shutil.move(path, target)
    return target
