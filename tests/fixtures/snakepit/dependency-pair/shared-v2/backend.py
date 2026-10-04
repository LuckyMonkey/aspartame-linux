"""Tiny dependency-free PEP 517 backend used by the offline fixture."""

from pathlib import Path
import base64
import hashlib
import zipfile

import tomllib


def _metadata():
    data = tomllib.loads((Path(__file__).parent / "pyproject.toml").read_text())
    project = data["project"]
    return project["name"], project["version"]


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    name, version = _metadata()
    normalized = name.replace("-", "_")
    dist_info = f"{normalized}-{version}.dist-info"
    filename = f"{normalized}-{version}-py3-none-any.whl"
    files = {
        "tension_core/__init__.py": (Path(__file__).parent / "tension_core/__init__.py").read_bytes(),
        f"{dist_info}/METADATA": (
            f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n\n".encode()
        ),
        f"{dist_info}/WHEEL": (
            b"Wheel-Version: 1.0\nGenerator: aspartame-snakepit-fixture\n"
            b"Root-Is-Purelib: true\nTag: py3-none-any\n"
        ),
    }
    records = []
    for path, content in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
        records.append(f"{path},sha256={digest},{len(content)}")
    records.append(f"{dist_info}/RECORD,,")
    files[f"{dist_info}/RECORD"] = ("\n".join(records) + "\n").encode()
    output = Path(wheel_directory) / filename
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as wheel:
        for path, content in files.items():
            wheel.writestr(path, content)
    return filename
