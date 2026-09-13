# Copyright (C) 2026 Aspartame contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Journal metadata and selection rules, independent of GTK and D-Bus."""

from copy import deepcopy
import json

PROJECT_BUNDLE_ID = 'org.sugarlabs.Project'


def normalized_query(query):
    """Keep the caller's search intact; the datastore adds its own wildcards."""
    result = deepcopy(query)
    result.setdefault('mountpoints', ['/'])
    result.setdefault('order_by', ['-timestamp'])
    text = str(result.get('query', '')).strip()
    if text:
        result['query'] = text
    else:
        result.pop('query', None)
    return result


def is_filtered(query):
    return any(query.get(name) for name in
               ('query', 'mime_type', 'keep', 'timestamp', 'activity'))


def keep_value(value):
    return str(value).lower() in ('1', 'true')


def progress_value(value):
    try:
        return min(100, max(0, int(float(value))))
    except (TypeError, ValueError, OverflowError):
        return 100


def buddies_from_metadata(metadata):
    raw = metadata.get('buddies', '')
    if not raw:
        return []
    try:
        value = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return []
    if isinstance(value, dict):
        value = value.values()
    if not isinstance(value, (list, tuple, type({}.values()))):
        return []
    return [(str(item[0]), str(item[1])) for item in value
            if isinstance(item, (list, tuple)) and len(item) == 2]


def editable_changes(metadata, changes):
    """Whitelist writable fields and preserve the identity of the object."""
    result = dict(metadata)
    for key, value in changes.items():
        if key not in ('title', 'description', 'tags', 'keep', 'comments',
                       'project_id'):
            raise ValueError('Not an editable Journal field: %s' % key)
        if key == 'title':
            value = str(value).strip()
            if not value:
                raise ValueError('Please give your work a title.')
            result['title_set_by_user'] = '1'
        elif key == 'keep':
            value = '1' if keep_value(value) else '0'
        else:
            value = str(value)
        result[key] = value
    return result


class EntrySelection:
    """Checked objects survive refreshes, but never outlive their results."""

    def __init__(self):
        self._selected = set()

    def set(self, uid, selected):
        if selected:
            self._selected.add(str(uid))
        else:
            self._selected.discard(str(uid))

    def contains(self, uid):
        return str(uid) in self._selected

    def restore(self, selected, available):
        self._selected = set(map(str, selected)).intersection(map(str, available))

    def in_order(self, available):
        return [uid for uid in available if self.contains(uid)]

    def clear(self):
        self._selected.clear()
