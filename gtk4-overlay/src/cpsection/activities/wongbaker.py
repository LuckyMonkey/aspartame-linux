"""Wong-Baker-style six-face scale for rating how an Activity is doing.

The question each face answers is "how much does using this Activity hurt?",
scored 0, 2, 4, 6, 8, 10 like the Wong-Baker FACES pain scale.  The faces are
drawn by Aspartame (see ``faces.py``); Wong-Baker FACES is a trademark of the
Wong-Baker FACES Foundation and its artwork is not reproduced here.

Persistence is additive.  The classic GTK3 Activity Manager stores a five-level
answer (1 Broken .. 5 Perfect) in ``activity-ratings.json``; that file is only
ever read here, never rewritten.  New answers go to their own file, and an
Activity with no new answer shows its classic answer mapped onto this scale.
"""

import json
import os
from gettext import gettext as _


SCORES = (0, 2, 4, 6, 8, 10)
LABELS = {
    0: _('No hurt: works well'),
    2: _('Hurts a little bit'),
    4: _('Hurts a little more'),
    6: _('Hurts even more'),
    8: _('Hurts a whole lot'),
    10: _('Hurts worst: unusable'),
}
# Classic five-level answers (1 Broken .. 5 Perfect) on this scale.
LEGACY_TO_SCORE = {5: 0, 4: 2, 3: 4, 2: 8, 1: 10}

CONFIG_ROOT = os.path.expanduser('~/.config/aspartame')
RATING_FILE = os.path.join(CONFIG_ROOT, 'activity-ratings-wong-baker.json')
LEGACY_RATING_FILE = os.path.join(CONFIG_ROOT, 'activity-ratings.json')
FORMAT_VERSION = 1


def label(score):
    return LABELS.get(score, _('Not rated'))


def _read_json(filename):
    try:
        with open(filename, encoding='utf-8') as stream:
            data = json.load(stream)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load_ratings(filename=RATING_FILE, legacy_filename=LEGACY_RATING_FILE):
    """Return ``{activity_id: score}``; ``None`` means deliberately unrated."""
    ratings = {}
    for activity_id, value in _read_json(legacy_filename).items():
        if isinstance(value, int) and value in LEGACY_TO_SCORE:
            ratings[str(activity_id)] = LEGACY_TO_SCORE[value]
    stored = _read_json(filename).get('ratings', {})
    if isinstance(stored, dict):
        for activity_id, value in stored.items():
            if value is None or (isinstance(value, int) and value in SCORES):
                ratings[str(activity_id)] = value
    return ratings


def save_rating(activity_id, score, filename=RATING_FILE):
    """Record ``score`` (or ``None`` to clear) without touching classic data."""
    if score is not None and score not in SCORES:
        raise ValueError('score must be one of %r or None' % (SCORES,))
    data = _read_json(filename)
    ratings = data.get('ratings')
    if not isinstance(ratings, dict):
        ratings = {}
    ratings[str(activity_id)] = score
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    temporary = filename + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as stream:
        json.dump({'version': FORMAT_VERSION, 'ratings': ratings},
                  stream, indent=2, sort_keys=True)
        stream.write('\n')
    os.replace(temporary, filename)
