# Excerpt from Jarabe f84a2d5 with preview patches through 0123.
# Copyright Red Hat, Inc. and Aleksey Lim; GPL-2.0-or-later.

import os
import logging
from threading import Thread, Lock

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gtk
import json


class BundleRegistry:
    def get_bundle(self, bundle_id):
        """Returns an bundle given his service name"""
        with self._lock:
            for bundle in self._bundles:
                if bundle.get_bundle_id() == bundle_id:
                    if (os.environ.get('ASPARTAME_GTK4_PREVIEW') == '1' and
                            'sugar-activity3' in bundle.get_command()):
                        modern_dir = os.environ.get('SUGAR_ACTIVITIES_PATH')
                        if modern_dir:
                            candidate = os.path.join(modern_dir,
                                                     os.path.basename(bundle.get_path()))
                            try:
                                modern = bundle_from_dir(candidate)
                                if (modern is not None and
                                        'sugar-activity4' in modern.get_command()):
                                    return modern
                            except Exception:
                                logging.exception('Modern bundle lookup failed')
                    return bundle
        return None

    def __iter__(self):
        with self._lock:
            copy = list(self._bundles)
        return copy.__iter__()

    def __len__(self):
        with self._lock:
            return len(self._bundles)

    def _scan_directory(self, path):
        if not os.path.isdir(path):
            return

        # Sort by mtime to ensure a stable activity order
        bundles = {}
        for f in os.listdir(path):
            try:
                bundle_dir = os.path.join(path, f)
                if os.path.isdir(bundle_dir):
                    bundles[bundle_dir] = os.stat(bundle_dir).st_mtime
            except OSError as e:
                logging.exception('Error while processing installed activity'
                                  ' bundle %s: %s', bundle_dir, e)

        bundle_dirs = list(bundles.keys())
        bundle_dirs.sort(key=lambda x: bundles[x])
        for folder in bundle_dirs:
            try:
                self.add_bundle(folder, emit_signals=False)
            except Exception as e:
                logging.exception('Error while processing installed activity'
                                  ' bundle %s: %s', folder, e)

    def add_bundle(self, bundle_path, set_favorite=False, emit_signals=True,
                   force_downgrade=False):
        """
        Add a bundle to the registry.
        If the bundle is a duplicate with one already in the registry,
        the existing one from the registry is returned.
        Otherwise, the newly added bundle is returned on success, or None on
        failure.
        """
        try:
            bundle = bundle_from_dir(bundle_path)
        except MalformedBundleException:
            logging.exception('Error loading bundle %r', bundle_path)
            return None

        # None is a valid return value from bundle_from_dir helper.
        if bundle is None:
            logging.error('No bundle in %r', bundle_path)
            return None

        bundle_id = bundle.get_bundle_id()
        logging.debug('STARTUP: Adding bundle %s', bundle_id)
        installed = self.get_bundle(bundle_id)
        if (installed is not None and
                os.environ.get('ASPARTAME_GTK4_PREVIEW') == '1'):
            installed_exec = installed.get_command()
            bundle_exec = bundle.get_command()
            if ('sugar-activity3' in installed_exec and
                    'sugar-activity4' in bundle_exec):
                logging.info('Prefer GTK4 bundle %s over GTK3 duplicate',
                             bundle_id)
                self.remove_bundle(installed.get_path(), emit_signals=False)
                installed = None

        if installed is not None:
            if NormalizedVersion(installed.get_activity_version()) == \
                    NormalizedVersion(bundle.get_activity_version()):
                logging.debug("Bundle already known")
                return installed
            if not force_downgrade and \
                    NormalizedVersion(installed.get_activity_version()) >= \
                    NormalizedVersion(bundle.get_activity_version()):
                logging.debug('Skip old version for %s', bundle_id)
                return None
            logging.debug('Upgrade %s', bundle_id)
            self.remove_bundle(installed.get_path(), emit_signals)

        if set_favorite:
            favorite = not self.is_bundle_hidden(
                bundle.get_bundle_id(), bundle.get_activity_version())
            self._set_bundle_favorite(bundle.get_bundle_id(),
                                      bundle.get_activity_version(),
                                      favorite)

        with self._lock:
            self._bundles.append(bundle)
        if emit_signals:
            self.emit('bundle-added', bundle)
        return bundle

    def remove_bundle(self, bundle_path, emit_signals=True):
        removed = None
        self._lock.acquire()
        for bundle in self._bundles:
            if bundle.get_path() == bundle_path:
                self._bundles.remove(bundle)
                removed = bundle
                break
        self._lock.release()

        if emit_signals and removed is not None:
            self.emit('bundle-removed', removed)
        return removed is not None
