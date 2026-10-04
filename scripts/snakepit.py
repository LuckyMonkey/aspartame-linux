#!/usr/bin/env python3
"""Run one explainable Python-environment qualification.

Snakepit deliberately starts small.  It chooses an interpreter, creates an
isolated venv, records declared requirements, optionally installs an explicit
requirements file, runs one real workflow, and writes a machine-readable
qualification record.  It does not modify system Python.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any


SCHEMA = "aspartame.snakepit.qualification/v0"
MAX_OUTPUT = 20_000
DEPENDENCY_NAME = re.compile(
    r"^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(?:\[[^\]]+\])?\s*(.*)$"
)
DEPENDENCY_CLAUSE = re.compile(
    r"^(===|~=|==|!=|>=|<=|>|<)\s*(\d+(?:\.\d+)*(?:\.\*)?)$"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def trim_output(value: str) -> tuple[str, bool]:
    if len(value) <= MAX_OUTPUT:
        return value, False
    return value[:MAX_OUTPUT] + "\n[output truncated]", True


def resolve_executable(value: str) -> str:
    path = Path(value).expanduser()
    if path.parent != Path("."):
        return str(path.resolve())
    resolved = shutil.which(value)
    if not resolved:
        raise ValueError(f"interpreter not found: {value}")
    return resolved


def version_tuple(value: str) -> tuple[int, int, int]:
    match = re.match(r"^\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?", value)
    if not match:
        raise ValueError(f"could not parse Python version: {value}")
    return tuple(int(part or 0) for part in match.groups())


def python_version_tuple(python: Path) -> tuple[int, int, int]:
    result = run_checked(
        [
            str(python),
            "-c",
            "import sys; print('.'.join(map(str, sys.version_info[:3])))",
        ]
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "could not query interpreter")
    return version_tuple(result.stdout.strip())


def _specifier_clause_satisfied(
    clause: str, selected: tuple[int, int, int]
) -> bool | None:
    match = re.match(r"^(===|~=|==|!=|>=|<=|>|<)\s*(\d+(?:\.\d+)*(?:\.\*)?)$", clause)
    if not match:
        return None
    operator, requested = match.groups()
    wildcard = requested.endswith(".*")
    if wildcard:
        requested = requested[:-2]
    parts = tuple(int(part) for part in requested.split("."))
    target = parts + (0,) * (3 - len(parts))
    if wildcard:
        matches = selected[: len(parts)] == parts
        if operator == "==":
            return matches
        if operator == "!=":
            return not matches
        return None
    if operator in {"==", "==="}:
        return selected == target
    if operator == "!=":
        return selected != target
    if operator == ">=":
        return selected >= target
    if operator == "<=":
        return selected <= target
    if operator == ">":
        return selected > target
    if operator == "<":
        return selected < target
    if operator == "~=":
        if len(parts) == 1:
            upper = (parts[0] + 1, 0, 0)
        elif len(parts) == 2:
            upper = (parts[0] + 1, 0, 0)
        else:
            upper = (parts[0], parts[1] + 1, 0)
        return selected >= target and selected < upper
    return None


def requires_python_satisfied(
    specifier: str | None, selected: tuple[int, int, int]
) -> bool | None:
    """Evaluate the common PEP 440 clauses without adding a dependency."""
    if not specifier or specifier.strip() in {"", "*"}:
        return True
    results = [
        _specifier_clause_satisfied(clause.strip(), selected)
        for clause in specifier.split(",")
    ]
    if any(result is False for result in results):
        return False
    if any(result is None for result in results):
        return None
    return True


def _dependency_version(value: str) -> tuple[int, int, int] | None:
    if value.endswith(".*"):
        return None
    parts = value.split(".")
    if not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in (parts + ["0", "0"])[:3])


def _dependency_specification(
    value: str,
) -> tuple[str, list[tuple[str, tuple[int, int, int]]]] | None:
    value = value.split(";", 1)[0].strip()
    if not value or value.startswith(("-", "git+", "http:", "https:", "file:")):
        return None
    match = DEPENDENCY_NAME.match(value)
    if not match:
        return None
    name, specifier = match.groups()
    clauses: list[tuple[str, tuple[int, int, int]]] = []
    for raw_clause in (part.strip() for part in specifier.split(",")):
        if not raw_clause:
            continue
        match = DEPENDENCY_CLAUSE.match(raw_clause)
        if not match:
            return None
        operator, raw_version = match.groups()
        version = _dependency_version(raw_version)
        if version is None:
            return None
        clauses.append((operator, version))
    return name.lower().replace("_", "-").replace(".", "-"), clauses


def dependency_conflicts(requirements: dict[str, Any]) -> list[dict[str, Any]]:
    """Find obvious direct-constraint conflicts without invoking a resolver.

    This is intentionally a preflight, not a complete packaging solver. It
    catches exact-version disagreements and empty numeric intervals before
    creating an environment or contacting an index.
    """
    declarations: dict[str, list[dict[str, Any]]] = {}
    for file_info in requirements["files"]:
        for entry in file_info["entries"]:
            parsed = _dependency_specification(entry)
            if parsed is not None:
                name, _ = parsed
                declarations.setdefault(name, []).append(
                    {"specification": entry, "source": file_info["path"]}
                )
    for entry in requirements["dependencies"]:
        parsed = _dependency_specification(entry)
        if parsed is not None:
            name, _ = parsed
            declarations.setdefault(name, []).append(
                {"specification": entry, "source": "pyproject.toml"}
            )

    conflicts: list[dict[str, Any]] = []
    for name, entries in declarations.items():
        constraints: list[tuple[str, tuple[int, int, int], dict[str, Any]]] = []
        for entry in entries:
            parsed = _dependency_specification(entry["specification"])
            if parsed is None:
                continue
            _, clauses = parsed
            constraints.extend(
                (operator, version, entry) for operator, version in clauses
            )
        exact = {
            version
            for operator, version, _entry in constraints
            if operator in {"==", "==="}
        }
        reason: str | None = None
        if len(exact) > 1:
            reason = "multiple exact versions are required"
        elif exact:
            selected = next(iter(exact))
            if any(
                _specifier_clause_satisfied(
                    f"{operator}{'.'.join(map(str, version))}", selected
                )
                is False
                for operator, version, _entry in constraints
                if not (operator in {"==", "==="} and version == selected)
            ):
                reason = "an exact version violates another constraint"
        else:
            lower: tuple[int, int, int] | None = None
            lower_inclusive = True
            upper: tuple[int, int, int] | None = None
            upper_inclusive = True
            excluded: set[tuple[int, int, int]] = set()
            supported = True
            for operator, version, _entry in constraints:
                if operator in {">", ">="}:
                    if lower is None or version > lower:
                        lower = version
                        lower_inclusive = operator == ">="
                    elif version == lower:
                        lower_inclusive = lower_inclusive and operator == ">="
                elif operator in {"<", "<="}:
                    if upper is None or version < upper:
                        upper = version
                        upper_inclusive = operator == "<="
                    elif version == upper:
                        upper_inclusive = upper_inclusive and operator == "<="
                elif operator == "!=":
                    excluded.add(version)
                elif operator == "~=":
                    supported = False
            if supported and lower is not None and upper is not None:
                if lower > upper or (
                    lower == upper and not (lower_inclusive and upper_inclusive)
                ):
                    reason = "numeric version intervals do not intersect"
                elif (
                    lower == upper
                    and lower in excluded
                    and lower_inclusive
                    and upper_inclusive
                ):
                    reason = "the only remaining version is excluded"
        if reason:
            conflicts.append(
                {
                    "name": name,
                    "reason": reason,
                    "constraints": entries,
                }
            )
    return conflicts


def declared_requirements(source: Path, explicit: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {"files": [], "requires_python": None, "dependencies": []}
    requirements_path = Path(explicit).expanduser().resolve() if explicit else None
    if requirements_path is None:
        candidate = source / "requirements.txt"
        if candidate.is_file():
            requirements_path = candidate
    if requirements_path:
        if not requirements_path.is_file():
            raise ValueError(f"requirements file not found: {requirements_path}")
        lines = [
            line.strip()
            for line in requirements_path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        result["files"].append({"path": str(requirements_path), "entries": lines})

    pyproject = source / "pyproject.toml"
    if pyproject.is_file():
        try:
            import tomllib

            data = tomllib.loads(pyproject.read_text())
            project = data.get("project", {})
            result["requires_python"] = project.get("requires-python")
            result["dependencies"] = list(project.get("dependencies", []))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ValueError(f"could not inspect {pyproject}: {exc}") from exc
    return result


def run_checked(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, text=True, capture_output=True, **kwargs)


def python_version(python: Path) -> str:
    return f"Python {'.'.join(map(str, python_version_tuple(python)))}"


def isolation_probe(python: Path) -> dict[str, Any]:
    result = run_checked(
        [
            str(python),
            "-c",
            "import sys; print(sys.prefix); print(sys.base_prefix)",
        ]
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "could not inspect venv")
    lines = result.stdout.splitlines()
    prefix, base_prefix = (lines + ["", ""])[:2]
    return {
        "prefix": prefix,
        "base_prefix": base_prefix,
        "isolated": bool(prefix and base_prefix and prefix != base_prefix),
    }


def normalized_command(command: list[str], environment_python: Path) -> list[str]:
    command = list(command)
    if command and command[0] == "--":
        command.pop(0)
    if not command:
        raise ValueError("provide a workflow after --command")
    if command[0] in {"python", "python3", "{python}"}:
        command[0] = str(environment_python)
    return command


def child_environment(source: Path, environment: Path) -> dict[str, str]:
    """Build the environment used by both qualification and launch."""
    result = os.environ.copy()
    result.update(
        {
            "PATH": f"{environment / 'bin'}{os.pathsep}{result.get('PATH', '')}",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": str(source),
            "VIRTUAL_ENV": str(environment),
            "ASPARTAME_SNAKEPIT_ENVIRONMENT": str(environment),
        }
    )
    return result


def default_record(root: Path, name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return root / "reports" / "python" / f"{name}-{stamp}.json"


def qualify(args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser().resolve()
    if not source.is_dir():
        raise ValueError(f"source directory not found: {source}")

    environment = Path(args.environment).expanduser().resolve()
    record_path = (
        Path(args.record).expanduser().resolve()
        if args.record
        else default_record(Path.cwd(), args.software)
    )
    started = utc_now()
    started_clock = time.monotonic()
    requirements = declared_requirements(source, args.requirements_file)
    requirements["dependency_conflicts"] = dependency_conflicts(requirements)
    steps: list[dict[str, Any]] = []
    status = "FAIL"
    error: str | None = None
    workflow: dict[str, Any] = {}
    launch: dict[str, Any] | None = None
    requested_python: str | None = None
    requested_version: str | None = None
    requested_version_tuple: tuple[int, int, int] | None = None
    candidate_values = args.python or [sys.executable]
    candidate_records: list[dict[str, Any]] = []
    usable_candidates: list[tuple[str, tuple[int, int, int], bool | None]] = []
    compatibility: dict[str, Any] = {
        "requires_python": requirements["requires_python"],
        "selected_version": None,
        "satisfied": None,
    }
    environment_python = environment / "bin" / "python"

    try:
        for candidate in candidate_values:
            detail: dict[str, Any] = {"requested": candidate}
            try:
                resolved = resolve_executable(candidate)
                version_tuple = python_version_tuple(Path(resolved))
                version = ".".join(map(str, version_tuple))
                satisfied = requires_python_satisfied(
                    requirements["requires_python"], version_tuple
                )
                detail.update(
                    {
                        "resolved": resolved,
                        "version": version,
                        "satisfied": satisfied,
                    }
                )
                usable_candidates.append((resolved, version_tuple, satisfied))
            except (OSError, RuntimeError, ValueError) as exc:
                detail["error"] = str(exc)
            candidate_records.append(detail)

        compatible_candidates = [
            item for item in usable_candidates if item[2] is not False
        ]
        if not compatible_candidates:
            requirement = requirements["requires_python"]
            compatibility["satisfied"] = False
            steps.append(
                {
                    "action": "check-interpreter",
                    "requires_python": requirement,
                    "selected_version": None,
                    "satisfied": False,
                    "candidates": candidate_records,
                }
            )
            raise RuntimeError(
                "no candidate interpreter satisfies requires-python "
                f"{requirement!r}; at least one candidate does not satisfy "
                f"requires-python; candidates={candidate_records}"
            )

        # Prefer the newest compatible interpreter. Candidate order remains a
        # deterministic tie-breaker because max() keeps the first equal item.
        requested_python, requested_version_tuple, satisfied = max(
            compatible_candidates, key=lambda item: item[1]
        )
        requested_version = ".".join(map(str, requested_version_tuple))
        compatibility["selected_version"] = requested_version
        compatibility["satisfied"] = satisfied
        if environment.exists() and not args.reuse:
            raise ValueError(
                f"environment already exists: {environment} (use a new path or --reuse)"
            )
        steps.append(
            {
                "action": "check-interpreter",
                "requires_python": requirements["requires_python"],
                "selected_version": requested_version,
                "satisfied": satisfied,
                "candidates": candidate_records,
            }
        )
        if requirements["dependency_conflicts"]:
            conflicts = requirements["dependency_conflicts"]
            steps.append(
                {
                    "action": "check-dependencies",
                    "status": "conflict",
                    "conflicts": conflicts,
                }
            )
            raise RuntimeError(
                "dependency conflict before environment creation: "
                + "; ".join(
                    f"{item['name']}: {item['reason']}" for item in conflicts
                )
            )
        steps.append(
            {
                "action": "check-dependencies",
                "status": "ok",
                "conflicts": [],
            }
        )
        if not environment.exists():
            result = run_checked([requested_python, "-m", "venv", str(environment)])
            steps.append({"action": "create-venv", "returncode": result.returncode})
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or "venv creation failed")
        if not environment_python.is_file():
            raise RuntimeError(f"venv interpreter missing: {environment_python}")

        install_requested = bool(args.install_requirements)
        install_entries = [
            item for file_info in requirements["files"] for item in file_info["entries"]
        ]
        if install_requested and not install_entries:
            raise ValueError("--install-requirements requires a non-empty requirements file")
        if install_requested:
            requirements_path = requirements["files"][0]["path"]
            result = run_checked(
                [
                    str(environment_python),
                    "-m",
                    "pip",
                    "install",
                    "--requirement",
                    requirements_path,
                ],
                cwd=Path(requirements_path).parent,
                timeout=args.install_timeout,
            )
            steps.append(
                {
                    "action": "install-requirements",
                    "path": requirements_path,
                    "returncode": result.returncode,
                    "stdout": trim_output(result.stdout)[0],
                    "stderr": trim_output(result.stderr)[0],
                }
            )
            if result.returncode:
                raise RuntimeError(result.stderr.strip() or "dependency installation failed")
        else:
            steps.append({"action": "install-requirements", "skipped": True})

        isolation = isolation_probe(environment_python)
        command = normalized_command(args.command, environment_python)
        child_env = child_environment(source, environment)
        result = run_checked(command, cwd=source, env=child_env, timeout=args.timeout)
        stdout, stdout_truncated = trim_output(result.stdout)
        stderr, stderr_truncated = trim_output(result.stderr)
        workflow = {
            "command": command,
            "cwd": str(source),
            "returncode": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "stdout_truncated": stdout_truncated,
            "stderr_truncated": stderr_truncated,
        }
        if result.returncode == 0 and isolation["isolated"]:
            status = "PASS"
            if args.launchable:
                launch = {
                    "command": command,
                    "cwd": str(source),
                    "environment": str(environment),
                }
        elif result.returncode == 0:
            raise RuntimeError("workflow ran, but the selected environment was not isolated")
        else:
            raise RuntimeError(f"workflow exited with status {result.returncode}")
    except subprocess.TimeoutExpired as exc:
        error = f"command timed out after {exc.timeout} seconds"
        workflow = {
            "command": locals().get("command", args.command),
            "cwd": str(source),
            "timeout_seconds": exc.timeout,
        }
    except (OSError, RuntimeError, ValueError) as exc:
        error = str(exc)

    finished = utc_now()
    record = {
        "schema": SCHEMA,
        "status": status,
        "software": {"name": args.software, "source": str(source), "target": args.target},
        "interpreter": {
            "requested": requested_python,
            "version": f"Python {requested_version}" if requested_version else None,
            "candidates": candidate_records,
        },
        "compatibility": compatibility,
        "environment": {
            "path": str(environment),
            "python": str(environment_python),
            "reuse": bool(args.reuse),
        },
        "requirements": requirements,
        "steps": steps,
        "workflow": workflow,
        "launch": launch,
        "error": error,
        "started_at": started,
        "finished_at": finished,
        "duration_seconds": round(time.monotonic() - started_clock, 3),
    }
    if environment_python.is_file():
        record["environment"]["python_version"] = python_version(environment_python)
        record["environment"]["isolation"] = isolation_probe(environment_python)

    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"qualification={status} software={args.software} target={args.target}")
    print(f"environment={environment}")
    if workflow:
        print(f"workflow-exit={workflow.get('returncode', 'not-run')}")
    if error:
        print(f"reason={error}", file=sys.stderr)
    print(f"record={record_path}")
    return 0 if status == "PASS" else 1


def launch(args: argparse.Namespace) -> int:
    record_path = Path(args.record).expanduser().resolve()
    if not record_path.is_file():
        raise ValueError(f"qualification record not found: {record_path}")
    try:
        record = json.loads(record_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid qualification record: {record_path}: {exc}") from exc
    if record.get("schema") != SCHEMA:
        raise ValueError(f"unsupported qualification record schema: {record.get('schema')!r}")
    if record.get("status") != "PASS":
        raise ValueError("only a passing qualification record can be launched")

    contract = record.get("launch")
    if not isinstance(contract, dict):
        raise ValueError("qualification record has no explicit launch contract")
    command = contract.get("command")
    cwd = Path(contract.get("cwd", "")).expanduser().resolve()
    environment = Path(contract.get("environment", "")).expanduser().resolve()
    if not isinstance(command, list) or not command or not all(
        isinstance(item, str) and item for item in command
    ):
        raise ValueError("qualification record has an invalid launch command")
    if not cwd.is_dir():
        raise ValueError(f"launch source directory not found: {cwd}")
    if not (environment / "bin" / "python").is_file():
        raise ValueError(
            "launch environment interpreter not found: "
            f"{environment / 'bin' / 'python'}"
        )

    try:
        result = run_checked(
            command,
            cwd=cwd,
            env=child_environment(cwd, environment),
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired as exc:
        print(f"launch=FAIL software={record['software']['name']}")
        print(f"reason=command timed out after {exc.timeout} seconds", file=sys.stderr)
        return 1
    stdout, stdout_truncated = trim_output(result.stdout)
    stderr, stderr_truncated = trim_output(result.stderr)
    print(
        f"launch={'PASS' if result.returncode == 0 else 'FAIL'} "
        f"software={record['software']['name']}"
    )
    print(f"launch-workflow-exit={result.returncode}")
    if stdout:
        print(stdout, end="" if stdout.endswith("\n") else "\n")
    if stderr:
        print(stderr, end="" if stderr.endswith("\n") else "\n", file=sys.stderr)
    if stdout_truncated or stderr_truncated:
        print("launch-output-truncated=1")
    return 0 if result.returncode == 0 else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="subcommand", required=True)
    qualify_parser = commands.add_parser("qualify", help="run one isolated workflow")
    # GTK consumes the generic --name option during Sugar's sitecustomize
    # import before this parser runs. Keep the runtime CLI unambiguous.
    qualify_parser.add_argument("--software", required=True)
    qualify_parser.add_argument("--source", required=True)
    qualify_parser.add_argument("--environment", required=True)
    qualify_parser.add_argument("--record")
    qualify_parser.add_argument("--target", default="host-development")
    qualify_parser.add_argument(
        "--python",
        action="append",
        help="candidate interpreter; repeat to choose among installed Pythons",
    )
    qualify_parser.add_argument("--requirements-file")
    qualify_parser.add_argument("--install-requirements", action="store_true")
    qualify_parser.add_argument("--install-timeout", type=int, default=300)
    qualify_parser.add_argument("--timeout", type=int, default=120)
    qualify_parser.add_argument("--reuse", action="store_true")
    qualify_parser.add_argument(
        "--launchable",
        action="store_true",
        help="record this passing workflow as an explicit launch contract",
    )
    qualify_parser.add_argument("--command", nargs=argparse.REMAINDER, required=True)
    qualify_parser.set_defaults(handler=qualify)
    launch_parser = commands.add_parser(
        "launch", help="run the explicit launch contract from a passing record"
    )
    launch_parser.add_argument("--record", required=True)
    launch_parser.add_argument("--timeout", type=int, default=120)
    launch_parser.set_defaults(handler=launch)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"snakepit: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
