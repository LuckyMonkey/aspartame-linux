"""Pure Activity Manager presentation helpers.

Keep bundle metadata and filesystem probing outside the GTK widget so the
Activity Manager's row contract can be tested without a display or GI.
"""

import os


DEFAULT_ACTIVITY_ICON = 'activity-start'


def activity_icon_file(activity):
    """Return the first valid bundle icon path, or ``None`` for fallback."""
    value = str(activity.get('icon') or '').strip()
    if not value:
        return None
    root = str(activity.get('path') or '')
    candidates = [value]
    if not os.path.isabs(value) and root:
        candidates.extend((
            os.path.join(root, value),
            os.path.join(root, value + '.svg'),
            os.path.join(root, 'activity', value),
            os.path.join(root, 'activity', value + '.svg'),
        ))
    for candidate in dict.fromkeys(candidates):
        if os.path.isfile(candidate):
            return candidate
    return None


def activity_row_data(activity):
    """Normalize one inventory record for the GTK row boundary."""
    name = str(activity.get('name') or activity.get('id') or 'Activity')
    summary = str(activity.get('summary') or '').strip()
    runtime = str(activity.get('runtime') or 'experimental')
    version = str(activity.get('version') or '?')
    managed = bool(activity.get('managed', False))
    removable = bool(activity.get('removable', False))
    launchable = bool(activity.get('launchable', False))
    return {
        'name': name,
        'summary': summary,
        'runtime': runtime,
        'version': version,
        'managed': managed,
        'removable': removable,
        'launchable': launchable,
        'action_enabled': removable or launchable,
    }
