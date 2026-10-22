"""GTK4 About my Computer model backed by local read-only probes."""

import os
from gettext import gettext as _

from jarabe import config

from cpsection.aboutcomputer.inventory import (NOT_AVAILABLE, build_identity,
                                               collect_inventory)


def get_aboutcomputer():
    return _('Build: %s') % get_build_number()


def print_aboutcomputer():
    print(get_aboutcomputer())


def _read_file(path):
    try:
        with open(path, encoding='utf-8') as stream:
            value = stream.read().strip()
    except OSError:
        return None
    return value or None


def get_serial_number():
    return (_read_file('/sys/class/dmi/id/product_serial') or
            NOT_AVAILABLE)


def print_serial_number():
    print(get_serial_number())


def get_build_number():
    return build_identity()


def print_build_number():
    print(get_build_number())


def get_firmware_number():
    return (_read_file('/sys/class/dmi/id/bios_version') or
            NOT_AVAILABLE)


def print_firmware_number():
    print(get_firmware_number())


def get_hardware_model():
    return (_read_file('/sys/class/dmi/id/product_name') or
            NOT_AVAILABLE)


def get_system_information():
    values = collect_inventory()
    labels = (
        ('Distribution:', 'distribution'),
        ('Image:', 'image'),
        ('Kernel:', 'kernel'),
        ('Architecture:', 'architecture'),
        ('CPU:', 'cpu'),
        ('CPU cores:', 'cpu_cores'),
        ('Memory:', 'memory'),
        ('Storage:', 'storage'),
        ('Graphics:', 'graphics'),
        ('Desktop:', 'desktop'),
        ('Session:', 'session'),
        ('Python:', 'python'),
        ('Hostname:', 'hostname'),
        ('Uptime:', 'uptime'),
    )
    return tuple((_(label), values[key]) for label, key in labels)


def get_wireless_firmware():
    return NOT_AVAILABLE


def get_secondary_licenses():
    licenses = []
    licenses_path = getattr(config, 'licenses_path', '')
    if not os.path.isdir(licenses_path):
        return licenses
    for name in sorted(os.listdir(licenses_path)):
        path = os.path.join(licenses_path, name)
        try:
            with open(path, encoding='utf-8') as stream:
                licenses.append(stream.read())
        except OSError:
            continue
    return licenses


def get_license():
    path = os.path.join(getattr(config, 'data_path', ''), 'GPLv3')
    return _read_file(path) or _('License text is not available.')


def days_from_last_update():
    return -1
