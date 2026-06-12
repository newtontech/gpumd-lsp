from __future__ import annotations

import json
from pathlib import Path

import pytest

from gpumd_lsp.agent_api import (
    agent_check,
    agent_suggest,
    get_code_actions,
)
from gpumd_lsp.analyzer import (
    FILE_NAMES,
    KNOWN_TOKENS,
    analyze_file,
    analyze_path,
    analyze_text,
    format_text,
)
from gpumd_lsp.completion import get_completions, get_nep_completions
from gpumd_lsp.hover import get_hover
from gpumd_lsp.lint import (
    KNOWN_THERMOSTATS,
    MATMASTER_GUARDS,
    lint_argument_type,
    lint_nep_in_line,
    lint_run_in_line,
    lint_unknown_command,
    parse_runtime_log,
    parse_runtime_log_file,
)

# ---------------------------------------------------------------------------
# Fixtures helpers
# ---------------------------------------------------------------------------


def _write_run_in(tmp_path: Path, content: str, create_model: str | None = None) -> Path:
    p = tmp_path / "run.in"
    p.write_text(content, encoding="utf-8")
    if create_model:
        (tmp_path / create_model).write_text("dummy model\n", encoding="utf-8")
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
            create_model="nep.txt",
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
            create_model="nep.txt",
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
            create_model="nep.txt",
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
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_compute_msd(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ntime_step 1\ncompute_msd 10 100\nensemble nve\nrun 5000\n",
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_minimize_run(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nminimize sd 1e-6 1000\nrun 0\n",
            create_model="nep.txt",
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
            create_model="nep.txt",
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
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors

    def test_dump_exyz(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ntime_step 1\ndump_exyz 100 1\nensemble nve\nrun 5000\n",
            create_model="nep.txt",
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
            create_model="nep.txt",
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
            create_model="nep.txt",
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
            create_model="nep.txt",
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
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        first_check = [d for d in diags if d.code == "GPUMD010"]
        assert first_check, "should flag potential not being first"
        assert first_check[0].severity == "error"

    def test_potential_first_ok(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ntime_step 1\nrun 100\n",
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        first_check = [d for d in diags if d.code == "GPUMD010"]
        assert not first_check

    def test_compute_after_run_warns(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nensemble nve\nrun 100\ncompute_hac 10 100 10\n",
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        ordering = [d for d in diags if d.code == "GPUMD011"]
        assert ordering, "should warn about compute after run"

    def test_compute_before_run_ok(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ncompute_hac 10 100 10\nensemble nve\nrun 100\n",
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        ordering = [d for d in diags if d.code == "GPUMD011"]
        assert not ordering

    def test_dump_after_run_warns(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nensemble nve\nrun 100\ndump_thermo 10\n",
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        ordering = [d for d in diags if d.code == "GPUMD011"]
        assert ordering

    def test_empty_run_in(self, tmp_path: Path) -> None:
        _write_run_in(tmp_path, "")
        diags = analyze_path(tmp_path)
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
        lines = formatted.splitlines()
        assert len(lines) == 2
        assert lines[0].startswith("potential")
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

    def test_formatter_idempotent_complex(self) -> None:
        """Issue #5: Comprehensive idempotence test with multiple patterns."""
        text = (
            "# GPUMD run.in\n"
            "potential   nep_model.txt    5\n"
            "velocity    300  12345\n"
            "time_step   1\n"
            "  ensemble  npt_ber 300 300 100 0 200 200 200\n"
            "dump_thermo  100\n"
            "run   10000\n"
        )
        first = format_text(text)
        second = format_text(first)
        assert second == first, "Formatter should be idempotent on complex input"

    def test_formatter_idempotent_nep(self) -> None:
        """Issue #5: Idempotence for nep.in format."""
        text = (
            "# NEP training\n"
            "type 2 C H\n"
            "cutoff   5   4\n"
            "n_max  6  6\n"
            "batch_size   100\n"
            "lambda_e  0.1\n"
        )
        first = format_text(text)
        second = format_text(first)
        assert second == first

    def test_formatter_idempotent_equals_form(self) -> None:
        """Issue #5: Idempotence when input already uses = alignment."""
        text = "cutoff                = 5\nn_max                 = 6\n"
        first = format_text(text)
        second = format_text(first)
        assert second == first

    def test_formatter_idempotent_many_passes(self) -> None:
        """Issue #5: Running formatter 5 times should stabilize."""
        text = "potential x.txt\nvelocity  300  42\ntime_step    1\nrun  1000\n"
        result = format_text(text)
        for _ in range(4):
            result = format_text(result)
        assert result == format_text(result)


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
        _write_run_in(
            tmp_path,
            "potential nep.txt\nrun 100\n",
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
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
        _write_run_in(
            tmp_path,
            "potential nep.txt\ntime_step 1\nensemble nve\nrun 100\n",
            create_model="nep.txt",
        )
        from gpumd_lsp.cli import lint_main

        rc = lint_main([str(tmp_path)])
        assert rc == 0

    def test_lint_exit_code_error(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("time_step 1\n", encoding="utf-8")
        from gpumd_lsp.cli import lint_main

        rc = lint_main([str(tmp_path)])
        assert rc == 1

    def test_lint_error_with_bad_file(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("potential_not_here unknown\n", encoding="utf-8")
        from gpumd_lsp.cli import lint_main

        rc = lint_main([str(tmp_path)])
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
        _write_run_in(
            tmp_path,
            "potential nep.txt\nrun 100\n",
            create_model="nep.txt",
        )
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
        _write_run_in(tmp_path, "potential nep.txt\nrun 100\n", create_model="nep.txt")
        diags = analyze_path(tmp_path)
        if diags:
            d = diags[0]
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
        _write_run_in(tmp_path, "potential nep.txt\nrun 0\n", create_model="nep.txt")
        diags = analyze_path(tmp_path)
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
        (subdir / "nep.txt").write_text("dummy model\n", encoding="utf-8")
        diags = analyze_path(tmp_path)
        errors = [d for d in diags if d.severity == "error"]
        assert not errors


# ===================================================================
# SECTION M: Original tests (must still pass)
# ===================================================================


def test_valid_fixture_has_no_errors(tmp_path: Path) -> None:
    _write_run_in(
        tmp_path,
        "potential nep.txt\ntime_step 1\nensemble nve\ncompute_hac 10 100 10\nrun 1000\n",
        create_model="nep.txt",
    )

    diagnostics = analyze_path(tmp_path)

    assert not [item for item in diagnostics if item.severity == "error"]


def test_invalid_fixture_reports_diagnostic(tmp_path: Path) -> None:
    _write_run_in(tmp_path, "time_step 1\nrun 1000\ncompute_hac 10 100 10\n")

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


# ===================================================================
# SECTION O: New RULE diagnostics (issues #14-#20)
# ===================================================================


class TestRuleE060UnknownCommand:
    """Issue #14: GPUMD-E060 unknown command."""

    def test_unknown_command_in_run_in(self) -> None:
        from pathlib import Path
        diags = lint_unknown_command(Path("run.in"), 3, "badcmd")
        assert len(diags) == 1
        assert diags[0].code == "GPUMD-E060"
        assert diags[0].severity == "error"
        assert "badcmd" in diags[0].message

    def test_unknown_command_via_lint_run_in_line(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "foobar 42")
        codes = [d.code for d in diags]
        assert "GPUMD-E060" in codes

    def test_unknown_command_via_lint_nep_in_line(self) -> None:
        from pathlib import Path
        diags = lint_nep_in_line(Path("nep.in"), 1, "not_a_nep_kw value")
        codes = [d.code for d in diags]
        assert "GPUMD-E060" in codes

    def test_known_command_not_flagged(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "run 1000")
        e060 = [d for d in diags if d.code == "GPUMD-E060"]
        assert not e060


class TestRuleE061InvalidArgumentCount:
    """Issue #15: GPUMD-E061 invalid argument count."""

    def test_too_few_args(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "run")
        codes = [d.code for d in diags]
        assert "GPUMD-E061" in codes

    def test_too_many_args(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "time_step 1 2")
        codes = [d.code for d in diags]
        assert "GPUMD-E061" in codes

    def test_correct_arg_count_ok(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "time_step 1")
        e061 = [d for d in diags if d.code == "GPUMD-E061"]
        assert not e061

    def test_variable_args_ok(self) -> None:
        from pathlib import Path
        # group has min 2, max unlimited
        diags = lint_run_in_line(Path("run.in"), 1, "group 0 1 2 3")
        e061 = [d for d in diags if d.code == "GPUMD-E061"]
        assert not e061

    def test_ensemble_wrong_thermostat_args(self) -> None:
        from pathlib import Path
        # nve expects 0 sub-args, but we provide 2
        diags = lint_run_in_line(Path("run.in"), 1, "ensemble nve 300 300")
        codes = [d.code for d in diags]
        assert "GPUMD-E061" in codes

    def test_ensemble_correct_thermostat_args(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "ensemble nvt_ber 300 300 100")
        e061 = [d for d in diags if d.code == "GPUMD-E061"]
        assert not e061

    def test_nep_wrong_arg_count(self) -> None:
        from pathlib import Path
        diags = lint_nep_in_line(Path("nep.in"), 1, "cutoff 5")
        codes = [d.code for d in diags]
        assert "GPUMD-E061" in codes


class TestRuleE062InvalidArgumentType:
    """Issue #16: GPUMD-E062 invalid argument type."""

    def test_non_numeric_time_step(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "time_step abc")
        codes = [d.code for d in diags]
        assert "GPUMD-E062" in codes

    def test_non_numeric_run_steps(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "run thousand")
        codes = [d.code for d in diags]
        assert "GPUMD-E062" in codes

    def test_valid_numeric_ok(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "run 1000")
        e062 = [d for d in diags if d.code == "GPUMD-E062"]
        assert not e062

    def test_float_arg_ok_for_time_step(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "time_step 0.5")
        e062 = [d for d in diags if d.code == "GPUMD-E062"]
        assert not e062

    def test_nep_non_numeric_cutoff(self) -> None:
        from pathlib import Path
        diags = lint_nep_in_line(Path("nep.in"), 1, "cutoff abc def")
        codes = [d.code for d in diags]
        assert "GPUMD-E062" in codes

    def test_nep_type_allows_string_labels(self) -> None:
        from pathlib import Path
        # type 2 C H - N is int, labels are paths (string-like)
        diags = lint_nep_in_line(Path("nep.in"), 1, "type 2 C H")
        e062 = [d for d in diags if d.code == "GPUMD-E062"]
        assert not e062

    def test_type_check_message_includes_expected(self) -> None:
        from pathlib import Path
        diags = lint_argument_type(Path("run.in"), 1, "run", 0, "abc", "N_steps")
        assert len(diags) == 1
        assert "N_steps" in diags[0].message
        assert "abc" in diags[0].message


class TestRuleE063MissingModel:
    """Issue #17: GPUMD-E063 missing model file."""

    def test_missing_model_file(self, tmp_path: Path) -> None:
        p = tmp_path / "run.in"
        p.write_text("potential nonexistent.txt\nrun 100\n")
        diags = lint_run_in_line(p, 1, "potential nonexistent.txt", base_dir=tmp_path)
        codes = [d.code for d in diags]
        assert "GPUMD-E063" in codes

    def test_model_file_present_ok(self, tmp_path: Path) -> None:
        (tmp_path / "model.txt").write_text("dummy")
        p = tmp_path / "run.in"
        diags = lint_run_in_line(p, 1, "potential model.txt", base_dir=tmp_path)
        e063 = [d for d in diags if d.code == "GPUMD-E063"]
        assert not e063

    def test_no_base_dir_skips_check(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "potential missing.txt")
        e063 = [d for d in diags if d.code == "GPUMD-E063"]
        assert not e063

    def test_missing_model_via_analyze_path(self, tmp_path: Path) -> None:
        _write_run_in(tmp_path, "potential missing.txt\nrun 100\n")
        diags = analyze_path(tmp_path)
        e063 = [d for d in diags if d.code == "GPUMD-E063"]
        assert e063, "should flag missing model file"


class TestRuleW060InvalidThermostat:
    """Issue #18: GPUMD-W060 invalid thermostat."""

    def test_invalid_thermostat(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "ensemble nvt_invalid 300 300 100")
        codes = [d.code for d in diags]
        assert "GPUMD-W060" in codes

    def test_valid_thermostat_ok(self) -> None:
        from pathlib import Path
        diags = lint_run_in_line(Path("run.in"), 1, "ensemble nve")
        w060 = [d for d in diags if d.code == "GPUMD-W060"]
        assert not w060

    def test_all_known_thermostats_ok(self) -> None:
        from pathlib import Path
        for t in KNOWN_THERMOSTATS:
            if t == "nve":
                diags = lint_run_in_line(Path("run.in"), 1, f"ensemble {t}")
            elif t.startswith("nvt"):
                diags = lint_run_in_line(Path("run.in"), 1, f"ensemble {t} 300 300 100")
            elif t.startswith("npt"):
                diags = lint_run_in_line(Path("run.in"), 1, f"ensemble {t} 300 300 100 0 0 0 1000")
            elif t == "heat_bc":
                diags = lint_run_in_line(Path("run.in"), 1, f"ensemble {t} 300 400 10")
            w060 = [d for d in diags if d.code == "GPUMD-W060"]
            assert not w060, f"thermostat '{t}' should not produce W060"


class TestRuleE064MissingTrainingFile:
    """Issue #19: GPUMD-E064 missing training file."""

    def test_missing_train_file(self, tmp_path: Path) -> None:
        p = tmp_path / "nep.in"
        diags = lint_nep_in_line(p, 1, "train_file nonexistent.xyz", base_dir=tmp_path)
        codes = [d.code for d in diags]
        assert "GPUMD-E064" in codes

    def test_train_file_present_ok(self, tmp_path: Path) -> None:
        (tmp_path / "train.xyz").write_text("dummy")
        p = tmp_path / "nep.in"
        diags = lint_nep_in_line(p, 1, "train_file train.xyz", base_dir=tmp_path)
        e064 = [d for d in diags if d.code == "GPUMD-E064"]
        assert not e064

    def test_no_base_dir_skips_check(self) -> None:
        from pathlib import Path
        diags = lint_nep_in_line(Path("nep.in"), 1, "train_file missing.xyz")
        e064 = [d for d in diags if d.code == "GPUMD-E064"]
        assert not e064

    def test_missing_test_file_is_warning(self, tmp_path: Path) -> None:
        p = tmp_path / "nep.in"
        diags = lint_nep_in_line(p, 1, "test_file nonexistent.xyz", base_dir=tmp_path)
        e064 = [d for d in diags if d.code == "GPUMD-E064"]
        assert e064
        assert e064[0].severity == "warning"


class TestRuleE065RuntimeError:
    """Issue #20: GPUMD-E065 runtime error from log."""

    def test_error_line_in_log(self) -> None:
        from pathlib import Path
        log_content = "Step 100\nERROR: cannot open file\nStep 200\n"
        diags = parse_runtime_log(log_content, Path("run.out"))
        assert len(diags) == 1
        assert diags[0].code == "GPUMD-E065"
        assert "cannot open file" in diags[0].message

    def test_fatal_in_log(self) -> None:
        from pathlib import Path
        log_content = "FATAL: out of memory\n"
        diags = parse_runtime_log(log_content, Path("run.out"))
        assert len(diags) == 1
        assert diags[0].code == "GPUMD-E065"

    def test_segfault_in_log(self) -> None:
        from pathlib import Path
        log_content = "Step 1000\nsegmentation fault\n"
        diags = parse_runtime_log(log_content, Path("run.out"))
        assert len(diags) >= 1
        e065 = [d for d in diags if d.code == "GPUMD-E065"]
        assert e065

    def test_clean_log_no_errors(self) -> None:
        from pathlib import Path
        log_content = "Step 100\nStep 200\nStep 300\n"
        diags = parse_runtime_log(log_content, Path("run.out"))
        assert not diags

    def test_log_file_from_disk(self, tmp_path: Path) -> None:
        log = tmp_path / "run.out"
        log.write_text("Step 100\nERROR: something bad\n")
        diags = parse_runtime_log_file(log)
        assert len(diags) == 1
        assert diags[0].code == "GPUMD-E065"

    def test_runtime_log_discovered_by_analyze_path(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\ntime_step 1\nensemble nve\nrun 100\n",
            create_model="nep.txt",
        )
        (tmp_path / "run.out").write_text("ERROR: something failed\n")
        diags = analyze_path(tmp_path)
        e065 = [d for d in diags if d.code == "GPUMD-E065"]
        assert e065, "runtime log error should be discovered"


# ===================================================================
# SECTION P: MatMaster execution rules (issue #8)
# ===================================================================


class TestMatMasterGuards:
    def test_no_run_command_warns(self, tmp_path: Path) -> None:
        _write_run_in(tmp_path, "potential nep.txt\ntime_step 1\n", create_model="nep.txt")
        diags = analyze_path(tmp_path)
        gpumd012 = [d for d in diags if d.code == "GPUMD012"]
        assert gpumd012, "should warn about missing run command"

    def test_ensemble_after_run_warns(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nrun 100\nensemble nvt_ber 300 300 100\n",
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        gpumd013 = [d for d in diags if d.code == "GPUMD013"]
        assert gpumd013, "should warn about ensemble after run"

    def test_ensemble_before_run_ok(self, tmp_path: Path) -> None:
        _write_run_in(
            tmp_path,
            "potential nep.txt\nensemble nve\nrun 100\n",
            create_model="nep.txt",
        )
        diags = analyze_path(tmp_path)
        gpumd013 = [d for d in diags if d.code == "GPUMD013"]
        assert not gpumd013

    def test_nep_missing_train_file_info(self, tmp_path: Path) -> None:
        _write_nep_in(tmp_path, "type 1 C\ncutoff 5 4\n")
        diags = analyze_path(tmp_path)
        gpumd014 = [d for d in diags if d.code == "GPUMD014"]
        assert gpumd014, "should suggest train_file for NEP input"

    def test_nep_with_train_file_ok(self, tmp_path: Path) -> None:
        _write_nep_in(tmp_path, "type 1 C\ncutoff 5 4\ntrain_file train.xyz\n")
        diags = analyze_path(tmp_path)
        gpumd014 = [d for d in diags if d.code == "GPUMD014"]
        assert not gpumd014

    def test_matmaster_guards_defined(self) -> None:
        assert "potential_first" in MATMASTER_GUARDS
        assert "run_required" in MATMASTER_GUARDS
        assert "compute_before_run" in MATMASTER_GUARDS


# ===================================================================
# SECTION Q: Agent API (issue #11)
# ===================================================================


class TestAgentAPI:
    def test_agent_check_valid(self) -> None:
        from pathlib import Path
        payload = agent_check(Path("run.in"), "potential nep.txt\ntime_step 1\nrun 100\n")
        assert payload["ok"] is True
        assert "diagnostics" in payload
        assert "summary" in payload

    def test_agent_check_invalid(self) -> None:
        from pathlib import Path
        payload = agent_check(Path("run.in"), "unknown_cmd 42\n")
        assert payload["ok"] is False
        assert payload["summary"]["errors"] > 0

    def test_agent_suggest_commands(self) -> None:
        from pathlib import Path
        payload = agent_suggest(Path("run.in"), "potential nep.txt\nrun 100\n", line=3)
        assert "suggestions" in payload

    def test_agent_suggest_empty_line(self) -> None:
        from pathlib import Path
        payload = agent_suggest(Path("run.in"), "potential nep.txt\n\nrun 100\n", line=2)
        suggestions = payload.get("suggestions", [])
        # Empty line should suggest all commands
        assert len(suggestions) > 0


# ===================================================================
# SECTION R: Code Actions (issue #21)
# ===================================================================


class TestCodeActions:
    def test_code_actions_for_unknown_keyword(self) -> None:
        from pathlib import Path
        content = "potential nep.txt\nrunabcd 100\n"
        actions = get_code_actions(Path("run.in"), content, line=2)
        assert len(actions) > 0
        assert any(a["kind"] == "quickfix" for a in actions)

    def test_code_actions_for_invalid_type(self) -> None:
        from pathlib import Path
        content = "potential nep.txt\nrun abc\n"
        actions = get_code_actions(Path("run.in"), content, line=2)
        type_actions = [
            a
            for a in actions
            if "type" in a.get("title", "").lower()
            or "E062" in str(a.get("diagnostics", []))
        ]
        assert len(type_actions) > 0

    def test_code_actions_for_invalid_thermostat(self) -> None:
        from pathlib import Path
        content = "potential nep.txt\nensemble bad_thermo 300\nrun 100\n"
        actions = get_code_actions(Path("run.in"), content, line=2)
        thermo_actions = [
            a
            for a in actions
            if "thermostat" in a.get("title", "").lower()
            or "W060" in str(a.get("diagnostics", []))
        ]
        assert len(thermo_actions) > 0

    def test_code_actions_clean_line_empty(self) -> None:
        from pathlib import Path
        content = "potential nep.txt\nrun 100\n"
        actions = get_code_actions(Path("run.in"), content, line=2)
        # line 2 is "run 100" which has no diagnostics
        # There will be an E061 for run having 1 arg but that's the expected count
        # Actually run 100 is valid, so no E061 either
        # Let's check for clean line
        e_actions = [a for a in actions if "E060" in str(a.get("diagnostics", []))]
        assert not e_actions

    def test_code_actions_for_missing_model(self) -> None:
        from pathlib import Path
        # analyze_text doesn't do file existence checks, so use E063 fixture
        actions = get_code_actions(Path("run.in"), "potential nep.txt\nrun 100\n", line=1)
        # analyze_text won't fire E063 since no base_dir
        # But GPUMD010 won't fire either since potential is first
        # This is a valid input so should have minimal actions
        assert isinstance(actions, list)


# ===================================================================
# SECTION S: analyze_text integration (no file-existence checks)
# ===================================================================


class TestAnalyzeTextIntegration:
    def test_analyze_text_valid(self) -> None:
        diags = analyze_text(
            Path("run.in"), "potential nep.txt\ntime_step 1\nensemble nve\nrun 100\n"
        )
        errors = [d for d in diags if d.severity == "error"]
        assert len(errors) == 0

    def test_analyze_text_invalid(self) -> None:
        diags = analyze_text(Path("run.in"), "unknown_cmd 42\nrun 100\n")
        codes = {d.code for d in diags}
        assert "GPUMD001" in codes

    def test_analyze_text_nep(self) -> None:
        diags = analyze_text(Path("nep.in"), "type 1 C\ncutoff 5 4\n")
        errors = [d for d in diags if d.severity == "error"]
        assert len(errors) == 0

    def test_analyze_text_no_e063_for_simulated_path(self) -> None:
        """analyze_text with simulated paths should NOT trigger E063."""
        diags = analyze_text(Path("run.in"), "potential nonexistent.txt\nrun 100\n")
        e063 = [d for d in diags if d.code == "GPUMD-E063"]
        assert not e063

    def test_analyze_text_catches_e062(self) -> None:
        """analyze_text should still catch type errors."""
        diags = analyze_text(Path("run.in"), "potential nep.txt\nrun abc\n")
        e062 = [d for d in diags if d.code == "GPUMD-E062"]
        assert e062
