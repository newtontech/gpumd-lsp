"""GPUMD-specific lint rules with GPUMD-prefixed diagnostic codes.

RULE codes:
  GPUMD-E060  unknown command
  GPUMD-E061  invalid argument count
  GPUMD-E062  invalid argument type
  GPUMD-E063  missing model file referenced by potential
  GPUMD-W060  invalid thermostat in ensemble command
  GPUMD-E064  missing training file in nep.in
  GPUMD-E065  runtime error parsed from log
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic

# ---------------------------------------------------------------------------
# Command signature registry
# ---------------------------------------------------------------------------


def _is_int(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _is_path(s: str) -> bool:
    return bool(s and not s.startswith(("#", "!", ";")))


def _is_thermostat(s: str) -> bool:
    return s in (
        "nve",
        "nvt_ber",
        "nvt_berendsen",
        "nvt_nose_hoover",
        "npt_ber",
        "npt_berendsen",
        "npt_mtk",
        "heat_bc",
    )


# command: (min_args, max_args, [(check_fn, label), ...])
# max_args = -1 means unlimited
COMMAND_SIGNATURES: dict[str, tuple[int, int, list[tuple[Any, str]]]] = {
    "potential": (1, 2, [(_is_path, "filepath")]),
    "velocity": (1, 2, [(_is_float, "temperature"), (_is_int, "seed")]),
    "time_step": (1, 1, [(_is_float, "dt")]),
    "ensemble": (1, -1, [(_is_thermostat, "thermostat")]),
    "dump_thermo": (1, 1, [(_is_int, "interval")]),
    "dump_position": (2, 2, [(_is_int, "interval"), (_is_int, "group")]),
    "dump_velocity": (2, 2, [(_is_int, "interval"), (_is_int, "group")]),
    "dump_force": (2, 2, [(_is_int, "interval"), (_is_int, "group")]),
    "dump_exyz": (2, 2, [(_is_int, "interval"), (_is_int, "group")]),
    "compute_hac": (3, 3, [(_is_int, "sample"), (_is_int, "output_interval"), (_is_int, "Nc")]),
    "compute_hnemd": (1, 1, [(_is_float, "Fe")]),
    "compute_msd": (2, 2, [(_is_int, "sample"), (_is_int, "interval")]),
    "compute_shc": (
        3,
        4,
        [
            (_is_int, "sample"),
            (_is_int, "output_interval"),
            (_is_int, "Nc"),
            (_is_int, "sample_interval"),
        ],
    ),
    "compute_dos": (2, 2, [(_is_int, "sample"), (_is_int, "Nc")]),
    "compute_phonon": (0, 0, []),
    "compute_sdc": (2, 2, [(_is_int, "sample"), (_is_int, "interval")]),
    "compute_gkma": (3, 3, [(_is_int, "sample"), (_is_int, "interval"), (_is_int, "Nc")]),
    "compute_heat": (2, 2, [(_is_int, "sample"), (_is_int, "interval")]),
    "fix": (1, 1, [(_is_int, "group")]),
    "deform": (3, 3, [(_is_int, "direction"), (_is_float, "strain_rate"), (_is_int, "steps")]),
    "change_box": (0, -1, []),
    "replicate": (3, 3, [(_is_int, "nx"), (_is_int, "ny"), (_is_int, "nz")]),
    "run": (1, 1, [(_is_int, "N_steps")]),
    "minimize": (3, 3, [(_is_path, "method"), (_is_float, "tolerance"), (_is_int, "max_steps")]),
    "neighbor": (2, 2, [(_is_float, "skin"), (_is_int, "update_freq")]),
    "group": (2, -1, [(_is_int, "id"), (_is_int, "type")]),
    "space": (1, 1, [(_is_int, "group")]),
    "plumed": (1, 1, [(_is_path, "filepath")]),
    "dftd3": (0, -1, []),
}

NEP_SIGNATURES: dict[str, tuple[int, int, list[tuple[Any, str]]]] = {
    "type": (2, -1, [(_is_int, "N"), (_is_path, "type_label")]),
    "version": (1, 1, [(_is_int, "version")]),
    "cutoff": (2, 2, [(_is_float, "rc_radial"), (_is_float, "rc_angular")]),
    "n_max": (2, 2, [(_is_int, "n_radial"), (_is_int, "n_angular")]),
    "l_max": (2, 2, [(_is_int, "l_radial"), (_is_int, "l_angular")]),
    "basis_size": (1, 1, [(_is_int, "size")]),
    "lambda_e": (1, 1, [(_is_float, "value")]),
    "lambda_f": (1, 1, [(_is_float, "value")]),
    "lambda_v": (1, 1, [(_is_float, "value")]),
    "batch_size": (1, 1, [(_is_int, "N")]),
    "population_size": (1, 1, [(_is_int, "N")]),
    "generation": (1, 1, [(_is_int, "N")]),
    "train_file": (1, 1, [(_is_path, "filepath")]),
    "test_file": (1, 1, [(_is_path, "filepath")]),
    "zbl": (2, 2, [(_is_float, "r_inner"), (_is_float, "r_outer")]),
    "weight": (3, 3, [(_is_float, "energy"), (_is_float, "force"), (_is_float, "virial")]),
    "prediction_csv": (0, 0, []),
}

KNOWN_THERMOSTATS = frozenset(
    {
        "nve",
        "nvt_ber",
        "nvt_berendsen",
        "nvt_nose_hoover",
        "npt_ber",
        "npt_berendsen",
        "npt_mtk",
        "heat_bc",
    }
)

THERMOSTAT_ARGS: dict[str, tuple[int, int]] = {
    "nve": (0, 0),
    "nvt_ber": (3, 3),
    "nvt_berendsen": (3, 3),
    "nvt_nose_hoover": (3, 3),
    "npt_ber": (7, 7),
    "npt_berendsen": (7, 7),
    "npt_mtk": (7, 7),
    "heat_bc": (3, 3),
}

# MatMaster execution rules (issue #8)
MATMASTER_GUARDS = {
    "potential_first": "potential must be the first non-comment command in run.in",
    "run_required": "at least one 'run' command is required for simulation",
    "ensemble_before_run": "ensemble must be declared before run",
    "compute_before_run": "compute_*/dump_* commands must appear before run",
    "model_file_exists": "potential model file must exist on disk",
    "nep_train_file_exists": "train_file must exist for NEP training",
}


# ---------------------------------------------------------------------------
# Lint functions
# ---------------------------------------------------------------------------


def lint_unknown_command(path: Path, line_no: int, token: str) -> list[Diagnostic]:
    """GPUMD-E060: unknown command."""
    return [
        Diagnostic(
            code="GPUMD-E060",
            severity="error",
            message=f"unknown command '{token}'",
            file=str(path),
            line=line_no,
            suggested_fix={"kind": "check_keyword_spelling", "keyword": token},
            confidence=0.85,
        )
    ]


def lint_argument_count(
    path: Path,
    line_no: int,
    command: str,
    actual_args: int,
    sig: tuple[int, int, list[tuple[Any, str]]],
) -> list[Diagnostic]:
    """GPUMD-E061: invalid argument count."""
    min_args, max_args, _ = sig
    if max_args == -1:
        if actual_args >= min_args:
            return []
        expected = f"at least {min_args}"
    else:
        if min_args <= actual_args <= max_args:
            return []
        if min_args == max_args:
            expected = f"exactly {min_args}"
        else:
            expected = f"{min_args}-{max_args}"
    return [
        Diagnostic(
            code="GPUMD-E061",
            severity="error",
            message=f"command '{command}' expects {expected} argument(s), got {actual_args}",
            file=str(path),
            line=line_no,
            suggested_fix={"kind": "fix_argument_count", "command": command, "expected": expected},
            confidence=0.92,
        )
    ]


def lint_argument_type(
    path: Path,
    line_no: int,
    command: str,
    arg_index: int,
    arg_value: str,
    expected_type: str,
) -> list[Diagnostic]:
    """GPUMD-E062: invalid argument type."""
    return [
        Diagnostic(
            code="GPUMD-E062",
            severity="error",
            message=(
                f"command '{command}' argument {arg_index + 1} ('{arg_value}') "
                f"should be {expected_type}"
            ),
            file=str(path),
            line=line_no,
            suggested_fix={
                "kind": "fix_argument_type",
                "command": command,
                "arg_index": arg_index,
                "expected_type": expected_type,
            },
            confidence=0.88,
        )
    ]


def lint_missing_model(path: Path, line_no: int, model_file: str) -> list[Diagnostic]:
    """GPUMD-E063: missing model file."""
    return [
        Diagnostic(
            code="GPUMD-E063",
            severity="error",
            message=f"potential model file '{model_file}' not found",
            file=str(path),
            line=line_no,
            suggested_fix={"kind": "check_file_path", "file": model_file},
            confidence=0.75,
        )
    ]


def lint_invalid_thermostat(path: Path, line_no: int, thermostat: str) -> list[Diagnostic]:
    """GPUMD-W060: invalid thermostat in ensemble command."""
    return [
        Diagnostic(
            code="GPUMD-W060",
            severity="warning",
            message=(
                f"unrecognized thermostat '{thermostat}' in ensemble command. "
                f"Known: {', '.join(sorted(KNOWN_THERMOSTATS))}"
            ),
            file=str(path),
            line=line_no,
            suggested_fix={"kind": "fix_thermostat", "thermostat": thermostat},
            confidence=0.82,
        )
    ]


def lint_ensemble_arg_count(
    path: Path,
    line_no: int,
    thermostat: str,
    actual_count: int,
) -> list[Diagnostic]:
    """GPUMD-E061 for ensemble sub-arguments."""
    if thermostat not in THERMOSTAT_ARGS:
        return []
    min_expected, max_expected = THERMOSTAT_ARGS[thermostat]
    if min_expected <= actual_count <= max_expected:
        return []
    expected_str = f"exactly {min_expected}"
    return [
        Diagnostic(
            code="GPUMD-E061",
            severity="error",
            message=(
                f"thermostat '{thermostat}' expects {expected_str} parameter(s), got {actual_count}"
            ),
            file=str(path),
            line=line_no,
            suggested_fix={
                "kind": "fix_ensemble_args",
                "thermostat": thermostat,
                "expected": expected_str,
            },
            confidence=0.90,
        )
    ]


def lint_missing_training_file(path: Path, line_no: int, train_file: str) -> list[Diagnostic]:
    """GPUMD-E064: missing training file in nep.in."""
    return [
        Diagnostic(
            code="GPUMD-E064",
            severity="error",
            message=f"NEP training file '{train_file}' not found",
            file=str(path),
            line=line_no,
            suggested_fix={"kind": "check_file_path", "file": train_file},
            confidence=0.80,
        )
    ]


def lint_runtime_error(path: Path, line_no: int, log_line: str) -> list[Diagnostic]:
    """GPUMD-E065: runtime error parsed from log."""
    return [
        Diagnostic(
            code="GPUMD-E065",
            severity="error",
            message=f"GPUMD runtime error: {log_line.strip()}",
            file=str(path),
            line=line_no,
            suggested_fix={"kind": "review_runtime_error", "log_line": log_line.strip()},
            confidence=0.90,
        )
    ]


# ---------------------------------------------------------------------------
# Batch linting: run all checks on a single line
# ---------------------------------------------------------------------------


def lint_run_in_line(
    path: Path,
    line_no: int,
    line: str,
    base_dir: Path | None = None,
) -> list[Diagnostic]:
    """Run all lint rules on a single run.in line."""
    tokens = line.strip().split()
    if not tokens:
        return []
    command = tokens[0].lower()
    args = tokens[1:]
    diagnostics: list[Diagnostic] = []

    if command not in COMMAND_SIGNATURES:
        return lint_unknown_command(path, line_no, command)

    sig = COMMAND_SIGNATURES[command]
    diagnostics.extend(lint_argument_count(path, line_no, command, len(args), sig))

    type_checks = sig[2]
    for i, arg in enumerate(args):
        if i < len(type_checks):
            check_fn, label = type_checks[i]
            if not check_fn(arg):
                diagnostics.extend(lint_argument_type(path, line_no, command, i, arg, label))

    if command == "ensemble" and args:
        thermostat = args[0]
        if thermostat not in KNOWN_THERMOSTATS:
            diagnostics.extend(lint_invalid_thermostat(path, line_no, thermostat))
        else:
            sub_args = args[1:]
            diagnostics.extend(lint_ensemble_arg_count(path, line_no, thermostat, len(sub_args)))

    if command == "potential" and args and base_dir is not None:
        model_path = base_dir / args[0]
        if not model_path.exists():
            diagnostics.extend(lint_missing_model(path, line_no, args[0]))

    return diagnostics


def lint_nep_in_line(
    path: Path,
    line_no: int,
    line: str,
    base_dir: Path | None = None,
) -> list[Diagnostic]:
    """Run all lint rules on a single nep.in line."""
    tokens = line.strip().split()
    if not tokens:
        return []
    keyword = tokens[0].lower()
    args = tokens[1:]
    diagnostics: list[Diagnostic] = []

    if keyword not in NEP_SIGNATURES:
        return lint_unknown_command(path, line_no, keyword)

    sig = NEP_SIGNATURES[keyword]
    diagnostics.extend(lint_argument_count(path, line_no, keyword, len(args), sig))

    type_checks = sig[2]
    for i, arg in enumerate(args):
        if i < len(type_checks):
            check_fn, label = type_checks[i]
            if not check_fn(arg):
                diagnostics.extend(lint_argument_type(path, line_no, keyword, i, arg, label))

    if keyword in ("train_file", "test_file") and args and base_dir is not None:
        file_path = base_dir / args[0]
        if not file_path.exists():
            if keyword == "train_file":
                diagnostics.extend(lint_missing_training_file(path, line_no, args[0]))
            else:
                diagnostics.append(
                    Diagnostic(
                        code="GPUMD-E064",
                        severity="warning",
                        message=f"NEP test file '{args[0]}' not found",
                        file=str(path),
                        line=line_no,
                        suggested_fix={"kind": "check_file_path", "file": args[0]},
                        confidence=0.70,
                    )
                )

    return diagnostics


# ---------------------------------------------------------------------------
# Runtime log parser (issue #22)
# ---------------------------------------------------------------------------

_RUNTIME_ERROR_PATTERNS = [
    re.compile(r"ERROR[:\s]+(.+)", re.IGNORECASE),
    re.compile(r"FATAL[:\s]+(.+)", re.IGNORECASE),
    re.compile(r"segmentation fault", re.IGNORECASE),
    re.compile(r"MPI_ERR", re.IGNORECASE),
    re.compile(r"GPUMD exited with code (\d+)"),
]


def parse_runtime_log(log_content: str, log_path: Path) -> list[Diagnostic]:
    """Parse a GPUMD runtime log file for errors. Returns GPUMD-E065 diagnostics."""
    diagnostics: list[Diagnostic] = []
    lines = log_content.splitlines()

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        for pattern in _RUNTIME_ERROR_PATTERNS:
            match = pattern.search(stripped)
            if match:
                error_msg = match.group(1) if match.lastindex else stripped
                diagnostics.extend(lint_runtime_error(log_path, line_no, error_msg))
                break

    return diagnostics


def parse_runtime_log_file(log_path: Path) -> list[Diagnostic]:
    """Parse a runtime log file from disk."""
    try:
        content = log_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    return parse_runtime_log(content, log_path)
