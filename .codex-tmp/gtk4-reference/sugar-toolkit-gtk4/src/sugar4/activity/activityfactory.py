"""Compatibility activity-launch surface for the GTK4 shell preview.

The current GTK4 toolkit branch moved activity launching into the GTK4
application model but the shell migration still imports this module for
activity IDs and compositor setup. Keep this small compatibility surface
until the corresponding upstream shell/toolkit launch work lands.
"""

import uuid
import logging
import os
import shlex
import subprocess

from gi.repository import GLib

from sugar4.activity import activityhandle

_compositor_fd_getter = None

_SHELL_SERVICE = "org.laptop.Shell"
_SHELL_PATH = "/org/laptop/Shell"
_SHELL_INTERFACE = "org.laptop.Shell"


def create_activity_id():
    """Return a Sugar-compatible unique activity instance ID."""
    return uuid.uuid4().hex


def set_compositor_fd_getter(getter):
    """Store the shell compositor hook for future GTK4 activity launch."""
    global _compositor_fd_getter
    _compositor_fd_getter = getter


def get_environment(bundle, handle):
    """Build the per-instance environment expected by a Sugar Activity."""
    environment = os.environ.copy()
    bundle_path = bundle.get_path()
    bundle_id = bundle.get_bundle_id()
    profile_home = environment.get("SUGAR_HOME", os.path.expanduser("~/.sugar"))
    profile_id = environment.get("SUGAR_PROFILE", "default")
    activity_root = os.path.join(
        profile_home, profile_id, bundle_id, handle.activity_id
    )
    for name in ("instance", "data", "tmp", "logs"):
        os.makedirs(os.path.join(activity_root, name), exist_ok=True)
    environment.update(
        {
            "SUGAR_BUNDLE_PATH": bundle_path,
            "SUGAR_BUNDLE_ID": bundle_id,
            "SUGAR_BUNDLE_NAME": bundle.get_name(),
            "SUGAR_BUNDLE_VERSION": str(bundle.get_activity_version()),
            "SUGAR_ACTIVITY_ID": handle.activity_id,
            "SUGAR_ACTIVITY_ROOT": activity_root,
        }
    )
    if handle.object_id:
        environment["SUGAR_OBJECT_ID"] = handle.object_id
    if handle.uri:
        environment["SUGAR_URI"] = handle.uri
    return environment


def get_command(bundle):
    """Resolve a bundle command to the isolated GTK4 launcher."""
    command = shlex.split(bundle.get_command())
    if not command:
        raise ValueError("Activity bundle has no launch command")
    launcher_name = os.path.basename(command[0])
    if launcher_name == "sugar-activity3":
        raise RuntimeError(
            "GTK3 bundle cannot run inside the isolated GTK4 Activity compositor"
        )
    if launcher_name in ("sugar-activity", "sugar-activity4"):
        command[0] = os.environ.get("SUGAR_ACTIVITY4", "sugar-activity4")
    return command


def _get_shell_interface():
    import dbus

    bus = dbus.SessionBus()
    shell = bus.get_object(_SHELL_SERVICE, _SHELL_PATH)
    return dbus.Interface(shell, _SHELL_INTERFACE)


def _discard_reply(*args):
    pass


def _notification_failed(action, error):
    logging.error("Shell %s notification failed: %s", action, error)


def _notify_launch(bundle_id, activity_id):
    """Queue the shell model and launcher before starting the child."""
    shell = _get_shell_interface()
    shell.NotifyLaunch(
        bundle_id,
        activity_id,
        reply_handler=_discard_reply,
        error_handler=lambda error: _notification_failed("launch", error),
    )


def _notify_launch_failed(activity_id):
    try:
        shell = _get_shell_interface()
        shell.NotifyLaunchFailure(
            activity_id,
            reply_handler=_discard_reply,
            error_handler=lambda error: _notification_failed(
                "launch-failure", error
            ),
        )
    except Exception:
        logging.exception(
            "Could not notify Sugar shell of failed Activity %s", activity_id
        )


def _child_exited(pid, status, activity_id):
    if status:
        logging.error("GTK4 Activity %s exited with status %s", activity_id, status)
        _notify_launch_failed(activity_id)
    else:
        logging.debug("GTK4 Activity %s exited normally", activity_id)
    return GLib.SOURCE_REMOVE


def create(bundle, handle):
    """Launch one Activity client inside the Casilda compositor."""
    if not isinstance(handle, activityhandle.ActivityHandle):
        raise TypeError("handle must be an ActivityHandle")
    if _compositor_fd_getter is None:
        raise RuntimeError("GTK4 Activity compositor socket is not configured")

    try:
        command = get_command(bundle)
    except (RuntimeError, ValueError) as error:
        logging.error("GTK4 Activity %s cannot launch: %s",
                      handle.activity_id, error)
        _notify_launch_failed(handle.activity_id)
        return None
    command = [
        command[0],
        bundle.get_path(),
        *command[1:],
        "-b",
        bundle.get_bundle_id(),
        "-a",
        handle.activity_id,
    ]
    if handle.object_id is not None:
        command.extend(("-o", handle.object_id))
    if handle.uri is not None:
        command.extend(("-u", handle.uri))
    if handle.invited:
        command.append("-i")

    environment = get_environment(bundle, handle)
    environment.pop("DISPLAY", None)
    environment.pop("WAYLAND_DISPLAY", None)
    environment["GDK_BACKEND"] = "wayland"
    log_path = os.path.join(environment["SUGAR_ACTIVITY_ROOT"], "logs", "activity.log")

    _notify_launch(bundle.get_bundle_id(), handle.activity_id)

    client_fd = None
    log_file = None
    try:
        client_fd = _compositor_fd_getter()
        environment["WAYLAND_SOCKET"] = str(client_fd)
        log_file = open(log_path, "ab", buffering=0)
        process = subprocess.Popen(
            command,
            cwd=bundle.get_path(),
            env=environment,
            pass_fds=(client_fd,),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            close_fds=True,
        )
    except Exception:
        _notify_launch_failed(handle.activity_id)
        raise
    finally:
        if client_fd is not None:
            os.close(client_fd)
        if log_file is not None:
            log_file.close()
    GLib.child_watch_add(
        GLib.PRIORITY_DEFAULT, process.pid, _child_exited, handle.activity_id
    )
    logging.info("launched GTK4 Activity %s as PID %s", handle.activity_id, process.pid)
    return process
