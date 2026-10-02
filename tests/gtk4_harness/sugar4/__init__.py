"""Minimal host-side stand-in for the guest ``sugar4`` toolkit.

Only the surface the native GTK4 Activity bundles actually use is provided:
``SimpleActivity`` with ``set_canvas``/``get_canvas`` and the Journal
``read_file``/``write_file`` hooks.  It exists so the host suite can exercise
real GTK4 widget trees without a Sugar session, D-Bus, or datastore.  It is
not a substitute for the guest round-trip probes under ``scripts/``.
"""
