"""GTK4 Activity Manager model backed by Jarabe's registry.

Removal deliberately reuses Aspartame's recoverable quarantine policy for user
bundles and the native approval/remover boundary for system bundles.
"""

import os
import shutil
import subprocess
import time

from jarabe.model import bundleregistry


UAC_APPROVER = '/usr/local/libexec/aspartame-sudo-askpass'
SYSTEM_REMOVER = '/usr/local/libexec/aspartame-remove-activity'
USER_ROOT = os.path.realpath(os.path.expanduser(
    '~/.local/share/sugar/activities'))
QUARANTINE_ROOT = os.path.expanduser(
    '~/.local/share/aspartame/removed-activities')
MANAGED_ROOTS = (
    '/usr/share/sugar/activities',
    '/usr/share/aspartame/activities',
    '/usr/local/share/sugar/activities',
    '/usr/lib/sugar/activities',
)


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
            'managed': str(path).startswith(MANAGED_ROOTS),
        })
    return sorted(activities, key=lambda item: item['name'].casefold())


def remove_activity(path, quarantine=QUARANTINE_ROOT):
    """Remove a bundle safely, retaining user bundles for recovery.

    System-managed bundles can only be changed through the fullscreen Sugar
    approval helper and the constrained native remover. No recursive delete is
    performed here.
    """
    path = os.path.realpath(path)
    if not os.path.isdir(os.path.join(path, 'activity')):
        raise ValueError('That Activity bundle is not valid.')
    if path.startswith(USER_ROOT + os.sep):
        os.makedirs(quarantine, mode=0o700, exist_ok=True)
        target = os.path.join(
            quarantine, '%d-%s' % (time.time_ns(), os.path.basename(path)))
        shutil.move(path, target)
        return target
    if not any(path.startswith(os.path.realpath(root) + os.sep)
               for root in MANAGED_ROOTS):
        raise PermissionError('That Activity is outside a managed Activity folder.')
    approval = subprocess.run([UAC_APPROVER], capture_output=True, text=True)
    if approval.returncode:
        raise PermissionError('Approval was cancelled.')
    result = subprocess.run(
        ['sudo', '-n', SYSTEM_REMOVER, path], capture_output=True, text=True)
    if result.returncode:
        raise PermissionError(result.stderr.strip() or 'Approval was cancelled.')
    return result.stdout.strip() or path
