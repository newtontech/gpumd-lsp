"""Agent-facing JSON API for GPUMD LSP capabilities.

Provides structured JSON responses for:
- Issue #11: Agent JSON check/fix/suggest operations
- Issue #13: Enhanced diagnostics with lint codes
- Issue #21: Code actions (quick fixes)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .analyzer import analyze_text, format_text
from .diagnostics import Diagnostic
from .lint import (
    COMMAND_SIGNATURES,
    KNOWN_THERMOSTATS,
    NEP_SIGNATURES,
    lint_run_in_line,
    lint_nep_in_line,
    parse_runtime_log,
)

SOFTWARE = "gpumd"


def _path_to_uri(path: Path) -> str:
    """Convert a Path to a URI string, handling both absolute and relative paths."""
    try:
        return path.resolve().as_uri()
    except ValueError:
        return f"file:///{path}"


def agent_check(path: Path, content: str) -> dict[str, Any]:
    """Issue #11: Full agent JSON check endpoint.

    Returns a structured JSON payload with all diagnostics for the given content.
    """
    diagnostics = analyze_text(path, content)
    return _build_check_payload(path, diagnostics)


def agent_check_file(path: Path) -> dict[str, Any]:
    """Agent JSON check for a file on disk."""
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        return _build_error_payload(path, str(exc))
    return agent_check(path, content)


def agent_suggest(path: Path, content: str, line: int) -> dict[str, Any]:
    """Issue #11: Agent JSON suggest endpoint.

    Returns suggested completions or fixes for a given line.
    """
    lines = content.splitlines()
    lower_name = path.name.lower()

    if line < 1 or line > len(lines):
        return _build_payload(path, "suggest", {"line": line, "suggestions": []})

    current_line = lines[line - 1].strip()
    tokens = current_line.split()

    suggestions: list[dict[str, Any]] = []

    if not tokens or tokens[0].startswith(("#", "!", ";")):
        # Suggest all commands for the file type
        sigs = COMMAND_SIGNATURES if lower_name == "run.in" else NEP_SIGNATURES
        for cmd, (min_a, max_a, _) in sigs.items():
            suggestions.append({
                "type": "command",
                "label": cmd,
                "detail": f"{cmd} ({min_a}-{max_a} args)" if max_a > 0 else cmd,
            })
    elif tokens[0].lower() in COMMAND_SIGNATURES or tokens[0].lower() in NEP_SIGNATURES:
        # Suggest fixes based on lint diagnostics
        command = tokens[0].lower()
        args = tokens[1:]
        if lower_name == "run.in":
            lint_diags = lint_run_in_line(path, line, current_line)
        else:
            lint_diags = lint_nep_in_line(path, line, current_line)

        for d in lint_diags:
            suggestions.append({
                "type": "fix",
                "code": d.code,
                "message": d.message,
                "fix": d.suggested_fix,
            })

        # If command is ensemble, suggest valid thermostats
        if command == "ensemble" and not args:
            for t in sorted(KNOWN_THERMOSTATS):
                suggestions.append({
                    "type": "completion",
                    "label": t,
                    "detail": f"thermostat: {t}",
                })

    return _build_payload(path, "suggest", {"line": line, "suggestions": suggestions})


# ---------------------------------------------------------------------------
# Code actions (issue #21)
# ---------------------------------------------------------------------------

def get_code_actions(
    path: Path, content: str, line: int, character: int = 0,
) -> list[dict[str, Any]]:
    """Issue #21: Get code actions (quick fixes) for diagnostics at a position.

    Returns a list of code actions that can be applied to fix diagnostics.
    """
    actions: list[dict[str, Any]] = []
    diagnostics = analyze_text(path, content)

    # Find diagnostics on the requested line
    line_diags = [d for d in diagnostics if d.line == line]

    for diag in line_diags:
        fix = diag.suggested_fix
        if not fix:
            continue

        kind = fix.get("kind", "")

        if kind == "check_keyword_spelling":
            keyword = fix.get("keyword", "")
            # Suggest similar known keywords
            similar = _find_similar(keyword)
            for suggestion in similar:
                actions.append({
                    "title": f"Replace '{keyword}' with '{suggestion}'",
                    "kind": "quickfix",
                    "diagnostics": [diag.code],
                    "edit": {
                        "type": "text",
                        "line": line,
                        "old_text": keyword,
                        "new_text": suggestion,
                    },
                })

        elif kind == "fix_argument_count":
            command = fix.get("command", "")
            expected = fix.get("expected", "")
            actions.append({
                "title": f"Fix argument count for '{command}' (expected {expected})",
                "kind": "quickfix",
                "diagnostics": [diag.code],
                "edit": None,
                "message": f"Adjust arguments for '{command}' to match expected: {expected}",
            })

        elif kind == "fix_argument_type":
            command = fix.get("command", "")
            arg_type = fix.get("expected_type", "")
            actions.append({
                "title": f"Fix argument type for '{command}' (expected {arg_type})",
                "kind": "quickfix",
                "diagnostics": [diag.code],
                "edit": None,
                "message": f"Change argument to {arg_type}",
            })

        elif kind == "fix_thermostat":
            thermostat = fix.get("thermostat", "")
            actions.append({
                "title": f"Replace '{thermostat}' with a valid thermostat",
                "kind": "quickfix",
                "diagnostics": [diag.code],
                "edit": None,
                "message": f"Valid thermostats: {', '.join(sorted(KNOWN_THERMOSTATS))}",
            })

        elif kind == "check_file_path":
            file_ref = fix.get("file", "")
            actions.append({
                "title": f"Create or locate file '{file_ref}'",
                "kind": "quickfix",
                "diagnostics": [diag.code],
                "edit": None,
                "message": f"Ensure the file '{file_ref}' exists in the working directory",
            })

        elif kind == "move_command":
            command = fix.get("command", "")
            position = fix.get("position", "")
            actions.append({
                "title": f"Move '{command}' to {position} position",
                "kind": "quickfix",
                "diagnostics": [diag.code],
                "edit": None,
                "message": f"Reorder commands so '{command}' is {position}",
            })

        elif kind == "add_command":
            command = fix.get("command", "")
            actions.append({
                "title": f"Add '{command}' command",
                "kind": "quickfix",
                "diagnostics": [diag.code],
                "edit": None,
                "message": f"Add a '{command}' command to the input file",
            })

        elif kind == "review_runtime_error":
            log_line = fix.get("log_line", "")
            actions.append({
                "title": f"Review runtime error: {log_line[:60]}",
                "kind": "quickfix",
                "diagnostics": [diag.code],
                "edit": None,
                "message": "Review the runtime log for error details",
            })

    return actions


def _find_similar(keyword: str, max_results: int = 3) -> list[str]:
    """Find similar known keywords using simple edit distance."""
    all_keywords = list(COMMAND_SIGNATURES.keys()) + list(NEP_SIGNATURES.keys())
    scored: list[tuple[int, str]] = []
    kw_lower = keyword.lower()
    for candidate in all_keywords:
        if candidate == kw_lower:
            continue
        dist = _levenshtein(kw_lower, candidate)
        if dist <= 4:
            scored.append((dist, candidate))
    scored.sort()
    return [c for _, c in scored[:max_results]]


def _levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(
                prev[j + 1] + 1,
                curr[j] + 1,
                prev[j] + (0 if ca == cb else 1),
            ))
        prev = curr
    return prev[-1]


# ---------------------------------------------------------------------------
# Payload builders
# ---------------------------------------------------------------------------

def _build_check_payload(path: Path, diagnostics: list[Diagnostic]) -> dict[str, Any]:
    errors = sum(1 for d in diagnostics if d.severity == "error")
    warnings = sum(1 for d in diagnostics if d.severity == "warning")
    return {
        "uri": _path_to_uri(path),
        "operation": "check",
        "ok": errors == 0,
        "software": SOFTWARE,
        "diagnostics": [d.to_json() for d in diagnostics],
        "summary": {
            "count": len(diagnostics),
            "errors": errors,
            "warnings": warnings,
        },
    }


def _build_error_payload(path: Path, error_msg: str) -> dict[str, Any]:
    return {
        "uri": _path_to_uri(path),
        "operation": "check",
        "ok": False,
        "software": SOFTWARE,
        "diagnostics": [],
        "summary": {"count": 0, "errors": 1, "warnings": 0},
        "error": error_msg,
    }


def _build_payload(path: Path, operation: str, data: dict[str, Any]) -> dict[str, Any]:
    result = {
        "uri": _path_to_uri(path),
        "operation": operation,
        "software": SOFTWARE,
    }
    result.update(data)
    return result
