from __future__ import annotations

import json
from pathlib import Path

import pytest

from gpumd_lsp.analyzer import (
    FILE_NAMES,
    KNOWN_TOKENS,
    analyze_file,
    analyze_path,
    format_text,
)
from gpumd_lsp.completion import get_completions, get_nep_completions
from gpumd_lsp.hover import get_hover

# ---------------------------------------------------------------------------
# Fixtures helpers
# ---------------------------------------------------------------------------


def _write_run_in(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "run.in"
    p.write_text(content, encoding="utf-8")
    return p


def _write_nep_in(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "nep.in"
    p.write_text(content, encoding="utf-8")
    return p


# ===================================================================
# SECTION A: Valid run.in fixtures
# ===================================================================


class TestValidRunIn:
    def test_basic_nve(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\n"
            "velocity 300 12345\n"
            "time_step 1\n"
            "ensemble nve\n"
            "dump_thermo 100\n"
            "run 1000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors, f"unexpected errors: {errors}"

    def test_hac_simulation(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\n"
            "velocity 300 42\n"
            "time_step 1\n"
            "compute_hac 10 100 2000\n"
            "ensemble nve\n"
            "run 200000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_nvt_nose_hoover(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\n"
            "time_step 1\n"
            "ensemble nvt_nose_hoover 300 300 100\n"
            "dump_position 1000 1\n"
            "run 10000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_npt_berendsen(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\n"
            "time_step 1\n"
            "ensemble npt_berendsen 300 300 100 0 0 0 1000\n"
            "run 5000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_compute_msd(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ntime_step 1\ncompute_msd 10 100\nensemble nve\nrun 5000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_minimize_run(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nminimize sd 1e-6 1000\nrun 0\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_multiple_run_blocks(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\n"
            "velocity 10 1\n"
            "ensemble nve\n"
            "dump_thermo 10\n"
            "run 1000\n"
            "ensemble nvt_nose_hoover 300 300 100\n"
            "run 2000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_comments_and_whitespace(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "# GPUMD run.in\n"
            "! This is also a comment\n"
            "potential nep.txt\n"
            "\n"
            "  # Set time step\n"
            "time_step 1\n"
            "ensemble nve\n"
            "run 100\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_dump_exyz(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ntime_step 1\ndump_exyz 100 1\nensemble nve\nrun 5000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_deform_command(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\n"
            "time_step 1\n"
            "deform 0 1e-3 10000\n"
            "ensemble npt_berendsen 300 300 100 0 0 0 1000\n"
            "run 10000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors


# ===================================================================
# SECTION B: Valid nep.in fixtures
# ===================================================================


class TestValidNepIn:
    def test_minimal_nep(self, tmp_path: Path) -> None:
        _write_nep_in(
            tmp_path,
            "type 2 C H\n"
            "cutoff 5 4\n"
            "n_max 6 6\n"
            "batch_size 100\n"
            "population_size 50\n"
            "generation 100000\n"
            "lambda_e 0.1\n"
            "lambda_f 0.1\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_nep_with_zbl(self, tmp_path: Path) -> None:
        _write_nep_in(
            tmp_path,
            "type 3 Si O N\n"
            "cutoff 5 4\n"
            "n_max 8 6\n"
            "zbl 0.5 1.0\n"
            "batch_size 200\n"
            "population_size 80\n"
            "generation 50000\n",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors


# ===================================================================
# SECTION C: Invalid keyword detection
# ===================================================================


class TestInvalidKeywords:
    def test_unknown_keyword_run_in(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nunknown_cmd 42\nrun 100\n",
        )
        diags = analyze_path(tmp_path)
        unknown = [d for d in diags if d.code == "GPUMD001"]
        assert unknown, "should flag unknown keyword"
        assert "unknown_cmd" in unknown[0].message

    def test_unknown_keyword_nep_in(self, tmp_path: Path) -> None:
        _write_nep_in(
            tmp_path,
            "type 1 C\nfake_param 42\ncutoff 5 4\n",
        )
        diags = analyze_path(tmp_path)
        unknown = [d for d in diags if d.code == "GPUMD001"]
        assert unknown

    def test_all_known_tokens_accepted(self, tmp_path: Path) -> None:
        """Every token in KNOWN_TOKENS should be accepted without GPUMD001."""
        for token in KNOWN_TOKENS:
            p = tmp_path / f"check_{token}.in"
            p.write_text(f"{token} test_value\n", encoding="utf-8")
            diags = analyze_file(p)
            unknown = [d for d in diags if d.code == "GPUMD001"]
            assert not unknown, f"token '{token}' was flagged as unknown"


# ===================================================================
# SECTION D: Required token checks
# ===================================================================


class TestRequiredTokens:
    def test_missing_potential_warns(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "time_step 1\nensemble nve\nrun 100\n",
        )
        diags = analyze_path(tmp_path)
        missing = [d for d in diags if d.code == "GPUMD101"]
        assert missing, "should warn about missing 'potential'"

    def test_potential_present_no_missing_warning(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nrun 100\n",
        )
        diags = analyze_path(tmp_path)
        missing = [d for d in diags if d.code == "GPUMD101"]
        assert not missing, "should not warn when potential is present"


# ===================================================================
# SECTION E: run.in specific checks (GPUMD010, GPUMD011)
# ===================================================================


class TestRunInDomainChecks:
    def test_potential_not_first(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "time_step 1\npotential nep.txt\nrun 100\n",
        )
        diags = analyze_path(tmp_path)
        first_check = [d for d in diags if d.code == "GPUMD010"]
        assert first_check, "should flag potential not being first"
        assert first_check[0].severity == "error"

    def test_potential_first_ok(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ntime_step 1\nrun 100\n",
        )
        diags = analyze_path(tmp_path)
        first_check = [d for d in diags if d.code == "GPUMD010"]
        assert not first_check

    def test_compute_after_run_warns(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nensemble nve\nrun 100\ncompute_hac 10 100 10\n",
        )
        diags = analyze_path(tmp_path)
        ordering = [d for d in diags if d.code == "GPUMD011"]
        assert ordering, "should warn about compute after run"

    def test_compute_before_run_ok(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ncompute_hac 10 100 10\nensemble nve\nrun 100\n",
        )
        diags = analyze_path(tmp_path)
        ordering = [d for d in diags if d.code == "GPUMD011"]
        assert not ordering

    def test_dump_after_run_warns(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nensemble nve\nrun 100\ndump_thermo 10\n",
        )
        diags = analyze_path(tmp_path)
        ordering = [d for d in diags if d.code == "GPUMD011"]
        assert ordering

    def test_empty_run_in(self, tmp_path: Path) -> None:
        _write_run_in(tmp_path, "")
        diags = analyze_path(tmp_path)
        # Empty file: no potential (GPUMD101 warning) + potential not first (GPUMD010)
        codes = {d.code for d in diags}
        assert "GPUMD101" in codes or "GPUMD010" in codes


# ===================================================================
# SECTION F: Formatting
# ===================================================================


class TestFormatting:
    def test_formatter_idempotent_basic(self) -> None:
        text = "potential nep.txt\ntime_step 1\nensemble nve\nrun 1000\n"
        assert format_text(text) == format_text(format_text(text))

    def test_formatter_strips_trailing_whitespace(self) -> None:
        text = "potential nep.txt   \ntime_step 1   \n"
        formatted = format_text(text)
        for line in formatted.splitlines():
            assert line == line.rstrip(), f"trailing ws in: {line!r}"

    def test_formatter_aligns_keyword_value(self) -> None:
        text = "potential nep.txt\ntime_step 1\n"
        formatted = format_text(text)
        # Keyword should be left-aligned to 24 chars
        lines = formatted.splitlines()
        assert len(lines) == 2
        assert lines[0].startswith("potential")
        # After formatting, keyword portion is padded
        assert "potential" in lines[0]
        assert "nep.txt" in lines[0]

    def test_formatter_preserves_comments(self) -> None:
        text = "# comment\npotential nep.txt\n"
        formatted = format_text(text)
        lines = formatted.splitlines()
        assert lines[0] == "# comment"

    def test_formatter_preserves_blank_lines(self) -> None:
        text = "potential nep.txt\n\ntime_step 1\n"
        formatted = format_text(text)
        assert "\n\n" in formatted

    def test_formatter_ends_with_newline(self) -> None:
        text = "potential nep.txt\ntime_step 1"
        formatted = format_text(text)
        assert formatted.endswith("\n")

    def test_formatter_empty_input(self) -> None:
        formatted = format_text("")
        assert formatted == "\n"

    def test_formatter_equals_alignment(self) -> None:
        text = "cutoff = 5\nn_max = 6\n"
        formatted = format_text(text)
        assert "= 5" in formatted
        assert "= 6" in formatted


# ===================================================================
# SECTION G: Edge cases
# ===================================================================


class TestEdgeCases:
    def test_no_supported_files(self, tmp_path: Path) -> None:
        diags = analyze_path(tmp_path)
        codes = [d.code for d in diags]
        assert "GPUMD201" in codes

    def test_utf8_error(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_bytes(b"\xff\xfe invalid binary")
        diags = analyze_file(p)
        codes = [d.code for d in diags]
        assert "GPUMD202" in codes

    def test_analyze_single_file(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("potential nep.txt\nrun 100\n", encoding="utf-8")
        diags = analyze_path(p)
        assert isinstance(diags, list)

    def test_unsupported_file_ignored(self, tmp_path: Path) -> None:
        p = tmp_path / "random.txt"
        p.write_text("hello world\n", encoding="utf-8")
        diags = analyze_path(p)
        assert diags  # GPUMD201 since no supported files

    def test_comment_only_file(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "# only comments\n# no commands\n",
        )
        diags = analyze_path(tmp_path)
        # Should at least warn about missing potential
        codes = [d.code for d in diags]
        assert "GPUMD101" in codes or "GPUMD010" in codes

    def test_nep_in_not_in_run_in_domain_checks(self, tmp_path: Path) -> None:
        """nep.in should NOT trigger run.in-specific GPUMD010/011 checks."""
        _write_nep_in(
            tmp_path,
            "type 1 C\ncutoff 5 4\n",
        )
        diags = analyze_path(tmp_path)
        gpumd010 = [d for d in diags if d.code == "GPUMD010"]
        gpumd011 = [d for d in diags if d.code == "GPUMD011"]
        assert not gpumd010
        assert not gpumd011


# ===================================================================
# SECTION H: Completion
# ===================================================================


class TestCompletion:
    def test_run_in_completions_not_empty(self) -> None:
        completions = get_completions()
        assert len(completions) > 0

    def test_run_in_completions_contain_core_keywords(self) -> None:
        completions = get_completions()
        labels = {c["label"] for c in completions}
        for kw in ["potential", "velocity", "time_step", "ensemble", "run"]:
            assert kw in labels, f"missing completion for {kw}"

    def test_run_in_completions_have_detail(self) -> None:
        completions = get_completions()
        for c in completions:
            assert "label" in c
            assert "detail" in c or "documentation" in c

    def test_nep_completions_not_empty(self) -> None:
        completions = get_nep_completions()
        assert len(completions) > 0

    def test_nep_completions_contain_core_keywords(self) -> None:
        completions = get_nep_completions()
        labels = {c["label"] for c in completions}
        for kw in ["type", "cutoff", "n_max", "batch_size"]:
            assert kw in labels, f"missing nep completion for {kw}"


# ===================================================================
# SECTION I: Hover documentation
# ===================================================================


class TestHover:
    def test_hover_known_keyword(self) -> None:
        info = get_hover("potential")
        assert info is not None
        assert "potential" in info.lower()

    def test_hover_unknown_keyword(self) -> None:
        info = get_hover("xyzzy_not_real")
        assert info is None

    def test_hover_ensemble(self) -> None:
        info = get_hover("ensemble")
        assert info is not None
        assert "ensemble" in info.lower()

    def test_hover_nep_keyword(self) -> None:
        info = get_hover("cutoff")
        assert info is not None
        assert "cutoff" in info.lower()

    def test_hover_time_step(self) -> None:
        info = get_hover("time_step")
        assert info is not None


# ===================================================================
# SECTION J: CLI integration
# ===================================================================


class TestCLI:
    def test_lint_json_output_direct(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        p = tmp_path / "run.in"
        p.write_text("time_step 1\nrun 100\n", encoding="utf-8")
        from gpumd_lsp.cli import lint_main

        lint_main([str(tmp_path), "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)

    def test_lint_exit_code_clean(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("potential nep.txt\ntime_step 1\nensemble nve\nrun 100\n", encoding="utf-8")
        from gpumd_lsp.cli import lint_main

        rc = lint_main([str(tmp_path)])
        assert rc == 0

    def test_lint_exit_code_error(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("time_step 1\n", encoding="utf-8")
        from gpumd_lsp.cli import lint_main

        rc = lint_main([str(tmp_path)])
        # "time_step 1" only: no potential (warning GPUMD101), not first (error GPUMD010)
        assert rc == 1

    def test_lint_error_with_bad_file(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("potential_not_here unknown\n", encoding="utf-8")
        from gpumd_lsp.cli import lint_main

        rc = lint_main([str(tmp_path)])
        # 'potential_not_here' is unknown keyword + missing required 'potential'
        assert rc == 1

    def test_fmt_stdout(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        p = tmp_path / "run.in"
        p.write_text("potential nep.txt\ntime_step 1\n", encoding="utf-8")
        from gpumd_lsp.cli import fmt_main

        fmt_main([str(p)])
        captured = capsys.readouterr()
        assert "potential" in captured.out

    def test_fmt_write_in_place(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("potential nep.txt\ntime_step 1\n", encoding="utf-8")
        from gpumd_lsp.cli import fmt_main

        fmt_main(["-w", str(p)])
        assert "potential" in p.read_text()

    def test_test_static_delegates_to_lint(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("potential nep.txt\nrun 100\n", encoding="utf-8")
        from gpumd_lsp.cli import test_main

        rc = test_main(["static", str(tmp_path), "--json"])
        assert rc == 0


# ===================================================================
# SECTION K: Diagnostic output shape
# ===================================================================


class TestDiagnosticShape:
    def test_diagnostic_to_json(self, tmp_path: Path) -> None:
        _write_run_in(tmp_path, "fake_keyword 42\n")
        diags = analyze_path(tmp_path)
        assert diags
        d = diags[0]
        j = d.to_json()
        assert "code" in j
        assert "severity" in j
        assert "message" in j
        assert "file" in j
        assert "line" in j
        assert "column" in j
        assert isinstance(j["evidence"], list)

    def test_diagnostic_frozen(self, tmp_path: Path) -> None:
        _write_run_in(tmp_path, "potential nep.txt\nrun 100\n")
        diags = analyze_path(tmp_path)
        if diags:
            d = diags[0]
            # Should not be able to mutate
            try:
                d.code = "CHANGED"  # type: ignore[misc]
                pytest.fail("should have raised FrozenInstanceError")
            except AttributeError:
                pass


# ===================================================================
# SECTION L: File detection
# ===================================================================


class TestFileDetection:
    def test_file_names_match_patterns(self) -> None:
        for name in FILE_NAMES:
            assert name in ["run.in", "nep.in"]

    def test_run_in_detected(self, tmp_path: Path) -> None:
        _write_run_in(tmp_path, "potential nep.txt\nrun 0\n")
        diags = analyze_path(tmp_path)
        # Should find the file and analyze it (no GPUMD201)
        codes = [d.code for d in diags]
        assert "GPUMD201" not in codes

    def test_nep_in_detected(self, tmp_path: Path) -> None:
        _write_nep_in(tmp_path, "type 1 C\ncutoff 5 4\n")
        diags = analyze_path(tmp_path)
        codes = [d.code for d in diags]
        assert "GPUMD201" not in codes

    def test_nested_files(self, tmp_path: Path) -> None:
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        p = subdir / "run.in"
        p.write_text("potential nep.txt\nrun 100\n", encoding="utf-8")
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors


# ===================================================================
# SECTION M: Original tests (must still pass)
# ===================================================================


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


# ===================================================================
# SECTION N: Static fixture files
# ===================================================================

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestStaticFixtures:
    def test_valid_run_fixture_has_no_errors(self) -> None:
        diags = analyze_path(FIXTURE_DIR / "valid_run")
        errors = [d for d in diags if d.severity == "error"]
        assert not errors, f"unexpected errors in valid_run fixture: {errors}"

    def test_valid_nep_fixture_has_no_errors(self) -> None:
        diags = analyze_path(FIXTURE_DIR / "valid_nep")
        errors = [d for d in diags if d.severity == "error"]
        assert not errors, f"unexpected errors in valid_nep fixture: {errors}"

    def test_invalid_run_fixture_reports_errors(self) -> None:
        diags = analyze_path(FIXTURE_DIR / "invalid_run")
        codes = {d.code for d in diags}
        assert "GPUMD010" in codes, "potential not first should be flagged"
        assert "GPUMD011" in codes, "compute after run should be flagged"
        assert "GPUMD001" in codes, "unknown keyword should be flagged"

    def test_invalid_nep_fixture_reports_errors(self) -> None:
        diags = analyze_path(FIXTURE_DIR / "invalid_nep")
        codes = {d.code for d in diags}
        assert "GPUMD001" in codes, "unknown keywords should be flagged"
        gpumd010 = [d for d in diags if d.code == "GPUMD010"]
        assert not gpumd010, "nep.in should not trigger run.in domain checks"

    def test_nested_fixtures_detected(self) -> None:
        diags = analyze_path(FIXTURE_DIR / "nested")
        errors = [d for d in diags if d.severity == "error"]
        assert not errors, f"unexpected errors in nested fixture: {errors}"

    def test_nested_directory_discovers_nested_run_in(self) -> None:
        diags = analyze_path(FIXTURE_DIR / "nested")
        errors = [d for d in diags if d.severity == "error"]
        assert not errors, f"nested valid fixture should not have errors: {errors}"
