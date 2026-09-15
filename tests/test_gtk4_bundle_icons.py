"""Activity metadata must resolve a shipped, valid icon before deployment."""
import configparser
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUNDLES = sorted((ROOT / "packages").glob("gtk4-*-activity/activity/activity.info"))


@pytest.mark.parametrize("info", BUNDLES, ids=lambda p: p.parents[1].name)
def test_bundle_icon_resolves(info):
    config = configparser.ConfigParser()
    config.read(info)
    icon = info.parent / (config["Activity"]["icon"] + ".svg")
    assert icon.is_file(), f"{config['Activity']['name']}: missing {icon}"
    assert ET.parse(icon).getroot().tag == "{http://www.w3.org/2000/svg}svg"
