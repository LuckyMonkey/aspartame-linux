"""Exercise the actual patched registry methods without a GI process."""
import ast
import logging
import os
from pathlib import Path
import shlex
import subprocess
from threading import Lock
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def registry(tmp_path):
    target = tmp_path / "src/jarabe/model/bundleregistry.py"
    target.parent.mkdir(parents=True)
    target.write_text((ROOT / "tests/fixtures/registry-before-0124.py").read_text())
    subprocess.run(
        ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(ROOT / "patches/"
         "gtk4-preview/0124-registry-authoritative-runtime-selection.patch")],
        cwd=tmp_path, check=True, capture_output=True)
    tree = ast.parse(target.read_text())
    klass = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    namespace = dict(os=os, shlex=shlex, logging=logging,
                     NormalizedVersion=int, MalformedBundleException=ValueError)
    bundles = {}
    namespace["bundle_from_dir"] = bundles.__getitem__
    exec(compile(ast.Module(body=[klass], type_ignores=[]), str(target), "exec"),
         namespace)
    instance = namespace["BundleRegistry"]()
    instance._lock = Lock()
    instance._bundles = []
    instance.emit = lambda *args: None
    return instance, bundles


def bundle(path, command, version, identity="tv.alterna.Clock"):
    return SimpleNamespace(get_path=lambda: path, get_command=lambda: command,
                           get_activity_version=lambda: str(version),
                           get_bundle_id=lambda: identity)


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("legacy_command", ["sugar-activity3 clock.ClockActivity",
                                          "sugar-activity clock.ClockActivity"])
def test_modern_wins_both_scan_orders_and_directory_names(
        registry, monkeypatch, reverse, legacy_command):
    monkeypatch.setenv("ASPARTAME_GTK4_PREVIEW", "1")
    reg, bundles = registry
    legacy = bundle("/usr/share/sugar/activities/clock.activity", legacy_command, 22)
    modern = bundle("/isolated/Clock.activity",
                    "/prefix/bin/sugar-activity4 clockactivity4.ClockActivity", 1)
    ordered = [legacy, modern]
    if reverse:
        ordered.reverse()
    for item in ordered:
        bundles[item.get_path()] = item
        reg.add_bundle(item.get_path())
    assert reg.get_bundle("tv.alterna.Clock") is modern
    assert list(reg) == [modern]
    # Lookup returns the authoritative registered object without filesystem reads.
    bundles.clear()
    assert reg.get_bundle("tv.alterna.Clock") is modern


@pytest.mark.parametrize("modern_space", [False, True])
def test_same_runtime_still_uses_versions(registry, monkeypatch, modern_space):
    monkeypatch.setenv("ASPARTAME_GTK4_PREVIEW", "1" if modern_space else "0")
    reg, bundles = registry
    old = bundle("/system/Clock", "sugar-activity4 clock.ClockActivity", 1)
    new = bundle("/user/Clock", "sugar-activity4 clock.ClockActivity", 2)
    for item in [old, new, old]:
        bundles[item.get_path()] = item
        reg.add_bundle(item.get_path())
    assert list(reg) == [new]


def test_classic_keeps_existing_version_policy(registry, monkeypatch):
    monkeypatch.delenv("ASPARTAME_GTK4_PREVIEW", raising=False)
    reg, bundles = registry
    legacy = bundle("/classic/clock.activity", "sugar-activity3 clock.ClockActivity", 22)
    modern = bundle("/modern/Clock.activity", "sugar-activity4 clock.ClockActivity", 1)
    for item in [legacy, modern]:
        bundles[item.get_path()] = item
        reg.add_bundle(item.get_path())
    assert list(reg) == [legacy]
