"""One Snakepit launch-contract policy for the CLI and the Activity Manager.

Pure standard library: imported by the GTK4 Activity Manager and, installed
beside it, by ``snakepit.py``. Record-shape validation is cheap and safe to
run while listing rows; source freshness hashes the tree and belongs right
before a launch, off the GTK main loop.

The source fingerprint is a receipt for the qualified source tree. It does
not attest the interpreter environment, and none of this is a sandbox.
"""

import hashlib
from pathlib import Path

SCHEMA = "aspartame.snakepit.qualification/v0"
FINGERPRINT_IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".cache",
    "build",
    "dist",
    "out",
    "reports",
    "work",
}


class ContractError(ValueError):
    """A record that must not be launched; the message says why."""


def source_fingerprint(source):
    """Return a compact receipt for the source used by a qualification.

    It ignores generated caches and nested virtual environments so that only
    a real change to the source tree invalidates the launch contract.
    """
    source = Path(source)
    digest = hashlib.sha256()
    files = 0
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if (
            path.is_symlink()
            or not path.is_file()
            or any(part in FINGERPRINT_IGNORED_DIRECTORIES for part in relative.parts[:-1])
        ):
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        files += 1
    return {"algorithm": "sha256", "files": files, "digest": digest.hexdigest()}


def _path_field(contract, key):
    value = contract.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"launch contract has no {key} path")
    return Path(value).expanduser().resolve()


def launch_contract(record):
    """Validate a record's shape and return ``(command, cwd, environment)``.

    Raises ContractError with a user-facing reason. Does not hash sources.
    """
    if not isinstance(record, dict):
        raise ContractError("qualification record is not a JSON object")
    if record.get("schema") != SCHEMA:
        raise ContractError(f"unsupported qualification record schema: {record.get('schema')!r}")
    if record.get("status") != "PASS":
        raise ContractError("only a passing qualification record can be launched")
    contract = record.get("launch")
    if not isinstance(contract, dict):
        raise ContractError("qualification record has no explicit launch contract")
    command = contract.get("command")
    if not isinstance(command, list) or not command or not all(
            isinstance(item, str) and item for item in command):
        raise ContractError("qualification record has an invalid launch command")
    cwd = _path_field(contract, "cwd")
    environment = _path_field(contract, "environment")
    if not cwd.is_dir():
        raise ContractError(f"launch source directory not found: {cwd}")
    if not (environment / "bin" / "python").is_file():
        raise ContractError(
            f"launch environment interpreter not found: {environment / 'bin' / 'python'}")
    return list(command), cwd, environment


def freshness_problem(record, cwd):
    """Return why the source no longer matches its qualification, or None."""
    expected = record.get("source_fingerprint")
    if not isinstance(expected, dict) or not expected.get("digest"):
        return "qualification record has no source fingerprint; qualify it again"
    if source_fingerprint(cwd)["digest"] != expected["digest"]:
        return "launch source changed since qualification; qualify it again"
    return None


def verified_launch_contract(record):
    """launch_contract() plus the source freshness check; for launch time."""
    command, cwd, environment = launch_contract(record)
    problem = freshness_problem(record, cwd)
    if problem:
        raise ContractError(problem)
    return command, cwd, environment


def describe(record):
    """Display metadata for a row, never raising on malformed fields."""
    record = record if isinstance(record, dict) else {}
    software = record.get("software") if isinstance(record.get("software"), dict) else {}
    interpreter = record.get("interpreter") if isinstance(record.get("interpreter"), dict) else {}
    try:
        launch_contract(record)
        problem = None
    except ContractError as error:
        problem = str(error)
    return {
        "name": str(software.get("name") or ""),
        "icon": str(software.get("icon") or ""),
        "version": str(interpreter.get("version") or "record"),
        "problem": problem,
    }
