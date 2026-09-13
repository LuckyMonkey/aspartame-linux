"""GTK-independent activity presentation rules.

Journal history is deliberately not a running-state input.  Only Jarabe's
observed lifecycle may illuminate an installed Activity icon.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Instance:
    activity_id: str
    bundle_id: str
    status: str


def select_instance(bundle_id, instances, active_id=None):
    """Return (state, id), preferring active, then running, then launching.

    Instances are in launch order. Failed launches do not count as running;
    removing a crashed instance therefore resets its icon immediately.
    """
    matches = [item for item in instances if item.bundle_id == bundle_id]
    running = [item for item in matches if item.status == 'running']
    for item in running:
        if item.activity_id == active_id:
            return 'active', item.activity_id
    if running:
        return 'running', running[-1].activity_id
    launching = [item for item in matches if item.status == 'launching']
    if launching:
        return 'launching', launching[-1].activity_id
    return 'stopped', None


def search_terms_match(query, fields):
    """Every normalized query word may match any of the metadata fields."""
    text = ' '.join(fields)
    return all(word in text for word in query.split())
