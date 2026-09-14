"""GTK4 Activity Manager model backed by Jarabe's registry."""

from jarabe.model import bundleregistry


def list_activities():
    registry = bundleregistry.get_registry()
    activities = []
    for bundle in registry:
        try:
            bundle_id = bundle.get_bundle_id()
            name = bundle.get_name()
            version = bundle.get_activity_version()
            path = bundle.get_path()
        except Exception:
            continue
        activities.append({
            'id': str(bundle_id),
            'name': str(name or bundle_id),
            'version': str(version),
            'path': str(path),
            'managed': str(path).startswith(('/usr/share/', '/usr/lib/')),
        })
    return sorted(activities, key=lambda item: item['name'].casefold())
