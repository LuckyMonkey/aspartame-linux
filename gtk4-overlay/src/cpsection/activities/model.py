"""GTK4 Activity Manager model backed by Jarabe's registry.

Removal deliberately reuses Aspartame's recoverable quarantine policy for user
bundles and the native approval/remover boundary for system bundles.
"""

import json
import os
from pathlib import Path
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
SNAKEPIT_SCHEMA = 'aspartame.snakepit.qualification/v0'


def _snakepit_record_root():
    """Return the user-owned directory containing qualification records."""
    configured = os.environ.get('ASPARTAME_SNAKEPIT_RECORD_DIR')
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(os.path.expanduser(
        '~/.local/share/aspartame/snakepit/records')).resolve()


def _qualified_launch(record):
    """Validate the small launch contract without executing it."""
    if record.get('schema') != SNAKEPIT_SCHEMA or record.get('status') != 'PASS':
        return False
    contract = record.get('launch')
    if not isinstance(contract, dict):
        return False
    command = contract.get('command')
    cwd = Path(str(contract.get('cwd', ''))).expanduser()
    environment = Path(str(contract.get('environment', ''))).expanduser()
    return (isinstance(command, list) and bool(command) and
            all(isinstance(item, str) and item for item in command) and
            cwd.is_dir() and (environment / 'bin' / 'python').is_file())


def _snakepit_activity(record_path):
    """Turn one qualified or failed record into a truthful manager row."""
    try:
        record = json.loads(record_path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        return None
    if not isinstance(record, dict):
        return None
    software = record.get('software')
    if not isinstance(software, dict):
        return None
    name = str(software.get('name') or record_path.stem)
    qualified = _qualified_launch(record)
    return {
        'id': 'org.aspartame.snakepit.' + name.replace('_', '-').replace(' ', '-'),
        'name': name,
        'version': str(record.get('interpreter', {}).get('version') or 'record'),
        'path': str(record_path),
        'record': str(record_path),
        'runtime': 'snakepit-python',
        'installed': qualified,
        'launchable': qualified,
        'removable': False,
        'managed': False,
        'summary': ('Qualified launch contract' if qualified else
                    str(record.get('error') or 'Qualification incomplete')),
    }


def list_snakepit_activities():
    """List records without presenting failed or incomplete records as ready."""
    root = _snakepit_record_root()
    if not root.is_dir():
        return []
    activities = []
    for record_path in sorted(root.glob('*.json')):
        activity = _snakepit_activity(record_path)
        if activity is not None:
            activities.append(activity)
    return activities


def _is_managed(path):
    path = os.path.realpath(path)
    return any(path == os.path.realpath(root) or
               path.startswith(os.path.realpath(root) + os.sep)
               for root in MANAGED_ROOTS)


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
        managed = _is_managed(path)
        user_installed = (os.path.realpath(path) == USER_ROOT or
                          os.path.realpath(path).startswith(USER_ROOT + os.sep))
        activities.append({
            'id': str(bundle_id),
            'name': str(name or bundle_id),
            'version': str(version),
            'path': str(path),
            'runtime': 'native-sugar',
            'installed': True,
            'removable': managed or user_installed,
            'managed': managed,
        })
    activities.extend(list_snakepit_activities())
    return sorted(activities, key=lambda item: item['name'].casefold())


def _launch_contract(activity):
    record_path = Path(activity.get('record', '')).expanduser().resolve()
    root = _snakepit_record_root()
    try:
        record_path.relative_to(root)
    except ValueError as error:
        raise PermissionError(
            'That Python record is outside the managed record folder.') from error
    try:
        record = json.loads(record_path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as error:
        raise ValueError('The Python qualification record is not readable.') from error
    if not _qualified_launch(record):
        raise ValueError('This Python Activity has no qualified launch contract.')
    contract = record['launch']
    cwd = Path(contract['cwd']).expanduser().resolve()
    environment = Path(contract['environment']).expanduser().resolve()
    return list(contract['command']), cwd, environment


def launch_activity(activity):
    """Start a qualified Snakepit workflow without making it removable."""
    if activity.get('runtime') != 'snakepit-python':
        raise ValueError('Only Snakepit Python Activities have a launch contract.')
    command, cwd, environment = _launch_contract(activity)
    child_environment = os.environ.copy()
    child_environment.update({
        'PATH': str(environment / 'bin') + os.pathsep + child_environment.get('PATH', ''),
        'PYTHONNOUSERSITE': '1',
        'PYTHONPATH': str(cwd),
        'VIRTUAL_ENV': str(environment),
        'ASPARTAME_SNAKEPIT_ENVIRONMENT': str(environment),
    })
    return subprocess.Popen(command, cwd=str(cwd), env=child_environment,
                            stdin=subprocess.DEVNULL, start_new_session=True)


def remove_activity(path, quarantine=QUARANTINE_ROOT):
    """Remove a bundle safely, retaining user bundles for recovery.

    System-managed bundles can only be changed through the fullscreen Sugar
    approval helper and the constrained native remover. No recursive delete is
    performed here.
    """
    path = os.path.realpath(path)
    if not os.path.isdir(os.path.join(path, 'activity')):
        raise ValueError('That Activity bundle is not valid.')
    registry = bundleregistry.get_registry()
    if path.startswith(USER_ROOT + os.sep):
        os.makedirs(quarantine, mode=0o700, exist_ok=True)
        target = os.path.join(
            quarantine, '%d-%s' % (time.time_ns(), os.path.basename(path)))
        shutil.move(path, target)
        _forget_registry_bundle(registry, path)
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
    _forget_registry_bundle(registry, path)
    return result.stdout.strip() or path


def _forget_registry_bundle(registry, path):
    """Drop a removed bundle from the live registry, when supported."""
    remover = getattr(registry, 'remove_bundle', None)
    if remover is None:
        return
    try:
        remover(path, emit_signals=True)
    except (OSError, ValueError, RuntimeError):
        # Filesystem/remover success is authoritative; an already-refreshed
        # registry must not turn a completed removal into an error.
        return
