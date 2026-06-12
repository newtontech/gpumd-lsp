"""Agent-facing CLI for Diagnostic Engine v1 operations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .agent_operations import operation_path, with_capabilities
from .rich_diagnostics import agent_check_payload

SOFTWARE = "gpumd"


def _file_type(path: Path) -> str:
    name = path.name.upper()
    if name in {"INCAR", "POSCAR", "KPOINTS", "POTCAR", "CONTCAR"}:
        return name
    if "." in path.name:
        return path.suffix.lstrip(".").lower()
    return name.lower()


def _collect_diagnostics(path: Path) -> list[Any]:
    from .analyzer import analyze_path

    return list(analyze_path(path))


def check_path(path: Path) -> dict[str, Any]:
    uri = path.resolve().as_uri()
    diagnostics = _collect_diagnostics(path)
    return agent_check_payload(
        software=SOFTWARE,
        uri=uri,
        operation="check",
        diagnostics=diagnostics,
        path=str(path),
        file_type=_file_type(path),
    )


def _operation_payload(
    path: Path,
    operation: str,
    line: int = 0,
    character: int = 0,
) -> dict[str, Any]:
    return operation_path(
        path,
        operation,
        software=SOFTWARE,
        file_type_func=_file_type,
        collect_diagnostics=_collect_diagnostics,
        line=line,
        character=character,
    )


def _do_check(args: argparse.Namespace) -> int:
    payload = with_capabilities(check_path(args.path), "check")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if getattr(args, "fail_on_blocking", False) and not payload["ok"] else 0


def _do_suggest(args: argparse.Namespace) -> int:
    from .agent_api import agent_suggest

    try:
        content = args.path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    payload = agent_suggest(args.path, content, getattr(args, "line", 1))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _do_code_actions(args: argparse.Namespace) -> int:
    from .agent_api import get_code_actions

    try:
        content = args.path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    line = getattr(args, "line", 1)
    actions = get_code_actions(args.path, content, line)
    print(json.dumps(actions, indent=2, sort_keys=True))
    return 0


def _do_parse_log(args: argparse.Namespace) -> int:
    from .lint import parse_runtime_log_file

    diagnostics = parse_runtime_log_file(args.path)
    print(
        json.dumps(
            [d.to_json() for d in diagnostics],
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if diagnostics else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gpumd-lsp-tool")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    for operation in (
        "check",
        "context",
        "complete",
        "hover",
        "symbols",
        "fix",
        "suggest",
        "code_actions",
        "parse_log",
    ):
        sub = subparsers.add_parser(operation)
        sub.add_argument("path", type=Path)
        sub.add_argument("--format", choices=["json"], default="json")
        if operation in ("check", "context", "complete", "hover", "symbols", "fix"):
            sub.add_argument(
                "--line",
                type=int,
                default=0,
                help="0-based line for position-aware operations.",
            )
            sub.add_argument(
                "--character",
                type=int,
                default=0,
                help="0-based character for position-aware operations.",
            )
        if operation == "check":
            sub.add_argument("--fail-on-blocking", action="store_true")
        if operation in ("suggest", "code_actions"):
            sub.add_argument("--line", type=int, default=1)
    args = parser.parse_args(argv)

    if args.operation == "check":
        return _do_check(args)
    if args.operation == "suggest":
        return _do_suggest(args)
    if args.operation == "code_actions":
        return _do_code_actions(args)
    if args.operation == "parse_log":
        return _do_parse_log(args)

    payload = _operation_payload(args.path, args.operation, args.line, args.character)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
