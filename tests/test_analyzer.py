from __future__ import annotations

from pathlib import Path

from gpumd_lsp.analyzer import analyze_path, format_text


def test_valid_fixture_has_no_errors(tmp_path: Path) -> None:
    fixture = tmp_path / "run.in"
    fixture.write_text(
        "potential nep.txt\ntime_step 1\nensemble nve\ncompute_hac 10 100 10\nrun 1000\n",
        encoding="utf-8",
    )

    diagnostics = analyze_path(tmp_path)

    assert not [item for item in diagnostics if item.severity == "error"]


def test_invalid_fixture_reports_diagnostic(tmp_path: Path) -> None:
    fixture = tmp_path / "run.in"
    fixture.write_text("time_step 1\nrun 1000\ncompute_hac 10 100 10\n", encoding="utf-8")

    diagnostics = analyze_path(tmp_path)

    assert diagnostics


def test_formatter_is_idempotent() -> None:
    first = format_text(
        "potential nep.txt\ntime_step 1\nensemble nve\ncompute_hac 10 100 10\nrun 1000\n"
    )
    second = format_text(first)

    assert second == first
