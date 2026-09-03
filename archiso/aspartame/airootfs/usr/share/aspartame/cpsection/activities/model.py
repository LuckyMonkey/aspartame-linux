"""User-facing Activity inventory and ratings for Aspartame Settings."""

import configparser
import logging
import json
import os
import shutil
import subprocess
import time

from gettext import gettext as _


LOG = logging.getLogger(__name__)
RATINGS = (_('Broken'), _('Bad'), _('Needs work'), _('Good'), _('Perfect'))
RATING_FILE = os.path.expanduser('~/.config/aspartame/activity-ratings.json')
# Inventory only installed Activity locations. The Aspartame bundle tree is
# an image/source staging area and must not reappear after its installed copy
# has been removed.
ACTIVITY_ROOTS = (
    '/usr/share/sugar/activities',
    '/usr/local/share/sugar/activities',
    os.path.expanduser('~/.local/share/sugar/activities'),
)
QUARANTINE_ROOT = os.path.expanduser('~/.local/share/aspartame/removed-activities')
FAVORITES_FILE = os.path.expanduser('~/.sugar/default/favorite_activities')
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


def _root_priority(root):
    root = os.path.realpath(root)
    if root == os.path.realpath(os.path.expanduser("~/.local/share/sugar/activities")):
        return 0
    if root == os.path.realpath("/usr/local/share/sugar/activities"):
        return 1
    return 2


def list_activities(roots=ACTIVITY_ROOTS, favorites_file=FAVORITES_FILE):
    """Return installed Activity metadata, preferring user overrides."""
    found = {}
    priorities = {}
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if not os.path.isdir(path):
                continue
            try:
                info = _read_info(path)
            except (OSError, UnicodeError, configparser.Error) as error:
                LOG.warning("Skipping malformed Activity metadata %s: %s", path, error)
                continue
            if info:
                priority = _root_priority(root)
                if (info['id'] not in found or
                        priority < priorities[info['id']]):
                    found[info['id']] = info
                    priorities[info['id']] = priority
    for activity in found.values():
        activity['hidden'] = (not activity['user'] and
                              is_activity_hidden(activity['id'],
                                                 activity['version'],
                                                 favorites_file))
    return sorted(found.values(), key=lambda item: item['name'].lower())



def _favorite_key(activity_id, version):
    return '%s %s' % (activity_id, version)


def _load_favorites(filename=FAVORITES_FILE):
    try:
        with open(filename, encoding='utf-8') as stream:
            data = json.load(stream)
    except (OSError, ValueError):
        data = {}
    favorites = data.get('favorites') if isinstance(data, dict) else None
    return {'favorites': favorites if isinstance(favorites, dict) else {}}


def _save_favorites(data, filename=FAVORITES_FILE):
    parent = os.path.dirname(filename)
    os.makedirs(parent, mode=0o700, exist_ok=True)
    temporary = filename + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as stream:
        json.dump(data, stream, indent=1, sort_keys=True)
        stream.write('\n')
    os.replace(temporary, filename)


def is_activity_hidden(activity_id, version, filename=FAVORITES_FILE):
    """Return whether Sugar's persistent favorites state hides this Activity."""
    record = _load_favorites(filename)['favorites'].get(
        _favorite_key(activity_id, version), {})
    return isinstance(record, dict) and record.get('favorite') is False


def set_activity_hidden(activity_id, version, hidden, filename=FAVORITES_FILE):
    """Persist a system Activity Hide/Restore choice in Sugar's own profile."""
    data = _load_favorites(filename)
    key = _favorite_key(activity_id, version)
    record = data['favorites'].setdefault(key, {})
    record['favorite'] = not hidden
    _save_favorites(data, filename)

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




def clear_rating(activity_id, filename=RATING_FILE):
    """Remove an answer from the rating record, if one exists."""
    ratings = load_ratings(filename)
    if activity_id not in ratings:
        return
    del ratings[activity_id]
    parent = os.path.dirname(filename)
    os.makedirs(parent, mode=0o700, exist_ok=True)
    temporary = filename + ".tmp"
    with open(temporary, "w", encoding="utf-8") as stream:
        json.dump(ratings, stream, indent=2, sort_keys=True)
        stream.write("\n")
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
            ['pkexec', '--disable-internal-agent', SYSTEM_REMOVER, path],
            capture_output=True, text=True)
        if result.returncode:
            message = result.stderr.strip() or _('Administrator approval was cancelled.')
            raise PermissionError(message)
        return result.stdout.strip() or path
    os.makedirs(quarantine, mode=0o700, exist_ok=True)
    target = os.path.join(quarantine, '%d-%s' % (time.time_ns(), os.path.basename(path)))
    shutil.move(path, target)
    return target
