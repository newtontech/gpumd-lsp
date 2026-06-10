"""Tests for the GPUMD LSP server."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from lsprotocol.types import (
    CompletionParams,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DocumentFormattingParams,
    HoverParams,
    Position,
    TextDocumentIdentifier,
    TextDocumentItem,
    VersionedTextDocumentIdentifier,
)

from gpumd_lsp.diagnostics import Diagnostic
from gpumd_lsp.server import (
    _is_gpumd_file,
    _to_lsp_diagnostic,
    completions,
    did_change,
    did_close,
    did_open,
    formatting,
    hover,
)


class TestIsGpumdFile:
    def test_run_in_detected(self) -> None:
        assert _is_gpumd_file("file:///path/to/run.in")

    def test_nep_in_detected(self) -> None:
        assert _is_gpumd_file("file:///path/to/nep.in")

    def test_other_file_ignored(self) -> None:
        assert not _is_gpumd_file("file:///path/to/file.txt")

    def test_nested_run_in(self) -> None:
        assert _is_gpumd_file("file:///path/to/subdir/run.in")


class TestToLspDiagnostic:
    def test_error_severity(self) -> None:
        d = Diagnostic("GPUMD010", "error", "test", "/path/file.in", 5, column=3)
        lsp_d = _to_lsp_diagnostic(d)
        assert lsp_d.severity == 1
        assert lsp_d.range.start.line == 4
        assert lsp_d.range.start.character == 2

    def test_warning_severity(self) -> None:
        d = Diagnostic("GPUMD001", "warning", "test", "/path/file.in", 10)
        lsp_d = _to_lsp_diagnostic(d)
        assert lsp_d.severity == 2

    def test_code_in_message(self) -> None:
        d = Diagnostic("GPUMD001", "warning", "unknown keyword", "/path/file.in", 1)
        lsp_d = _to_lsp_diagnostic(d)
        assert "[GPUMD001]" in lsp_d.message


class TestDidOpen:
    def _make_did_open(self, uri: str, text: str) -> DidOpenTextDocumentParams:
        return DidOpenTextDocumentParams(
            text_document=TextDocumentItem(uri=uri, language_id="gpumd", version=1, text=text)
        )

    def test_publishes_diagnostics_for_run_in(self) -> None:
        mock_ls = MagicMock()
        params = self._make_did_open("file:///fake/run.in", "time_step 1\nrun 100\n")
        did_open(mock_ls, params)
        assert mock_ls.publish_diagnostics.called
        args, _ = mock_ls.publish_diagnostics.call_args
        uri, diags = args
        assert "run.in" in uri
        assert len(diags) > 0

    def test_empty_diagnostics_for_valid_file(self) -> None:
        mock_ls = MagicMock()
        params = self._make_did_open(
            "file:///fake/run.in", "potential nep.txt\ntime_step 1\nensemble nve\nrun 100\n"
        )
        did_open(mock_ls, params)
        assert mock_ls.publish_diagnostics.called
        args, _ = mock_ls.publish_diagnostics.call_args
        _, diags = args
        errors = [d for d in diags if d.severity == 1]
        assert len(errors) == 0

    def test_publishes_warning_for_missing_potential(self) -> None:
        mock_ls = MagicMock()
        params = self._make_did_open("file:///fake/run.in", "time_step 1\nrun 100\n")
        did_open(mock_ls, params)
        args, _ = mock_ls.publish_diagnostics.call_args
        _, diags = args
        codes = {d.code for d in diags}
        assert "GPUMD101" in codes

    def test_publishes_error_for_potential_not_first(self) -> None:
        mock_ls = MagicMock()
        params = self._make_did_open(
            "file:///fake/run.in", "time_step 1\npotential nep.txt\nrun 100\n"
        )
        did_open(mock_ls, params)
        args, _ = mock_ls.publish_diagnostics.call_args
        _, diags = args
        codes = {d.code for d in diags}
        assert "GPUMD010" in codes

    def test_ignores_unsupported_file_types(self) -> None:
        mock_ls = MagicMock()
        params = self._make_did_open("file:///fake/random.txt", "some random content\n")
        did_open(mock_ls, params)
        assert mock_ls.publish_diagnostics.called
        args, _ = mock_ls.publish_diagnostics.call_args
        _, diags = args
        assert len(diags) == 0

    def test_publishes_diagnostics_for_nep_in(self) -> None:
        mock_ls = MagicMock()
        params = self._make_did_open("file:///fake/nep.in", "type 1 C\ncutoff 5 4\n")
        did_open(mock_ls, params)
        assert mock_ls.publish_diagnostics.called

    def test_nep_in_does_not_trigger_run_in_checks(self) -> None:
        mock_ls = MagicMock()
        params = self._make_did_open("file:///fake/nep.in", "cutoff 5 4\n")
        did_open(mock_ls, params)
        args, _ = mock_ls.publish_diagnostics.call_args
        _, diags = args
        codes = {d.code for d in diags}
        assert "GPUMD010" not in codes

    def test_unknown_keyword_diagnostic(self) -> None:
        mock_ls = MagicMock()
        params = self._make_did_open(
            "file:///fake/run.in", "potential nep.txt\nrun 100\nunknown_cmd 42\n"
        )
        did_open(mock_ls, params)
        args, _ = mock_ls.publish_diagnostics.call_args
        _, diags = args
        codes = {d.code for d in diags}
        assert "GPUMD001" in codes


class TestDidChange:
    def test_publishes_diagnostics_on_change(self) -> None:
        mock_ls = MagicMock()
        params = DidChangeTextDocumentParams(
            text_document=VersionedTextDocumentIdentifier(uri="file:///fake/run.in", version=2),
            content_changes=[SimpleNamespace(text="time_step 1\n")],
        )
        did_change(mock_ls, params)
        assert mock_ls.publish_diagnostics.called
        args, _ = mock_ls.publish_diagnostics.call_args
        _, diags = args
        assert len(diags) > 0

    def test_introducing_potential_resolves_warnings(self) -> None:
        mock_ls = MagicMock()
        bad_params = DidChangeTextDocumentParams(
            text_document=VersionedTextDocumentIdentifier(uri="file:///fake/run.in", version=1),
            content_changes=[SimpleNamespace(text="time_step 1\n")],
        )
        did_change(mock_ls, bad_params)
        args, _ = mock_ls.publish_diagnostics.call_args
        _, bad_diags = args
        bad_codes = {d.code for d in bad_diags}

        mock_ls.reset_mock()
        good_params = DidChangeTextDocumentParams(
            text_document=VersionedTextDocumentIdentifier(uri="file:///fake/run.in", version=2),
            content_changes=[SimpleNamespace(text="potential nep.txt\ntime_step 1\nrun 100\n")],
        )
        did_change(mock_ls, good_params)
        args, _ = mock_ls.publish_diagnostics.call_args
        _, good_diags = args
        good_codes = {d.code for d in good_diags}

        assert "GPUMD101" in bad_codes
        assert "GPUMD101" not in good_codes

    def test_empty_change_gives_no_crash(self) -> None:
        mock_ls = MagicMock()
        params = DidChangeTextDocumentParams(
            text_document=VersionedTextDocumentIdentifier(uri="file:///fake/run.in", version=3),
            content_changes=[],
        )
        did_change(mock_ls, params)


class TestDidClose:
    def test_clears_diagnostics_on_close(self) -> None:
        mock_ls = MagicMock()
        params = DidCloseTextDocumentParams(
            text_document=TextDocumentIdentifier(uri="file:///fake/run.in")
        )
        did_close(mock_ls, params)
        assert mock_ls.publish_diagnostics.called
        args, _ = mock_ls.publish_diagnostics.call_args
        uri, diags = args
        assert diags == []


class TestCompletions:
    def test_run_in_completions(self) -> None:
        mock_ls = MagicMock()
        params = CompletionParams(
            text_document=TextDocumentIdentifier(uri="file:///fake/run.in"),
            position=Position(line=0, character=0),
        )
        result = completions(mock_ls, params)
        assert result.is_incomplete is False
        labels = {item.label for item in result.items}
        assert "potential" in labels
        assert "run" in labels
        assert "ensemble" in labels
        assert "type" not in labels  # type is NEP-only

    def test_nep_in_completions(self) -> None:
        mock_ls = MagicMock()
        params = CompletionParams(
            text_document=TextDocumentIdentifier(uri="file:///fake/nep.in"),
            position=Position(line=0, character=0),
        )
        result = completions(mock_ls, params)
        labels = {item.label for item in result.items}
        assert "type" in labels
        assert "cutoff" in labels
        assert "n_max" in labels
        assert "potential" not in labels  # potential is run.in-only

    def test_completions_have_detail(self) -> None:
        mock_ls = MagicMock()
        params = CompletionParams(
            text_document=TextDocumentIdentifier(uri="file:///fake/run.in"),
            position=Position(line=0, character=0),
        )
        result = completions(mock_ls, params)
        for item in result.items:
            assert item.label
            assert item.detail

    def test_completions_have_documentation(self) -> None:
        mock_ls = MagicMock()
        params = CompletionParams(
            text_document=TextDocumentIdentifier(uri="file:///fake/nep.in"),
            position=Position(line=0, character=0),
        )
        result = completions(mock_ls, params)
        for item in result.items:
            assert item.documentation


class TestHover:
    def test_hover_known_keyword(self, tmp_path: Path) -> None:
        mock_ls = MagicMock()
        p = tmp_path / "run.in"
        p.write_text("potential nep.txt\nrun 100\n", encoding="utf-8")
        params = HoverParams(
            text_document=TextDocumentIdentifier(uri=f"file://{p}"),
            position=Position(line=0, character=0),
        )
        result = hover(mock_ls, params)
        assert result is not None
        assert "potential" in result.contents.lower()

    def test_hover_unknown_keyword(self, tmp_path: Path) -> None:
        mock_ls = MagicMock()
        p = tmp_path / "run.in"
        p.write_text("not_a_keyword 42\n", encoding="utf-8")
        params = HoverParams(
            text_document=TextDocumentIdentifier(uri=f"file://{p}"),
            position=Position(line=0, character=0),
        )
        result = hover(mock_ls, params)
        assert result is None

    def test_hover_on_comment_line(self, tmp_path: Path) -> None:
        mock_ls = MagicMock()
        p = tmp_path / "run.in"
        p.write_text("# just a comment\n", encoding="utf-8")
        params = HoverParams(
            text_document=TextDocumentIdentifier(uri=f"file://{p}"),
            position=Position(line=0, character=0),
        )
        result = hover(mock_ls, params)
        assert result is None

    def test_hover_nep_keyword(self, tmp_path: Path) -> None:
        mock_ls = MagicMock()
        p = tmp_path / "nep.in"
        p.write_text("cutoff 5 4\n", encoding="utf-8")
        params = HoverParams(
            text_document=TextDocumentIdentifier(uri=f"file://{p}"),
            position=Position(line=0, character=0),
        )
        result = hover(mock_ls, params)
        assert result is not None
        assert "cutoff" in result.contents.lower()

    def test_hover_out_of_bounds_line(self, tmp_path: Path) -> None:
        mock_ls = MagicMock()
        p = tmp_path / "run.in"
        p.write_text("potential nep.txt\n", encoding="utf-8")
        params = HoverParams(
            text_document=TextDocumentIdentifier(uri=f"file://{p}"),
            position=Position(line=99, character=0),
        )
        result = hover(mock_ls, params)
        assert result is None


class TestFormatting:
    def test_formats_run_in(self, tmp_path: Path) -> None:
        mock_ls = MagicMock()
        p = tmp_path / "run.in"
        p.write_text("potential nep.txt\ntime_step 1\n", encoding="utf-8")
        params = DocumentFormattingParams(
            text_document=TextDocumentIdentifier(uri=f"file://{p}"),
            options=MagicMock(),
        )
        result = formatting(mock_ls, params)
        assert result is not None
        assert len(result) > 0
        assert "potential" in result[0].new_text
        # Keyword should be padded
        assert "  " in result[0].new_text

    def test_formatting_no_crash_on_missing_file(self) -> None:
        mock_ls = MagicMock()
        params = DocumentFormattingParams(
            text_document=TextDocumentIdentifier(uri="file:///nonexistent/run.in"),
            options=MagicMock(),
        )
        result = formatting(mock_ls, params)
        assert result == []


class TestServerStartup:
    def test_lsp_main_starts_server(self) -> None:
        """lsp_main with --stdio should start the pygls server."""
        from gpumd_lsp.cli import lsp_main

        with patch("gpumd_lsp.server.SERVER.start_io") as mock_start:
            rc = lsp_main(["--stdio"])
            assert rc == 0
            mock_start.assert_called_once()

    def test_lsp_main_errors_without_stdio(self) -> None:
        from gpumd_lsp.cli import lsp_main

        with pytest.raises(SystemExit):
            lsp_main([])


class TestAnalyzeTextIntegration:
    def test_analyze_text_valid(self) -> None:
        from gpumd_lsp.analyzer import analyze_text

        diags = analyze_text(
            Path("run.in"), "potential nep.txt\ntime_step 1\nensemble nve\nrun 100\n"
        )
        errors = [d for d in diags if d.severity == "error"]
        assert len(errors) == 0

    def test_analyze_text_invalid(self) -> None:
        from gpumd_lsp.analyzer import analyze_text

        diags = analyze_text(Path("run.in"), "unknown_cmd 42\nrun 100\n")
        codes = {d.code for d in diags}
        assert "GPUMD001" in codes

    def test_analyze_text_nep(self) -> None:
        from gpumd_lsp.analyzer import analyze_text

        diags = analyze_text(Path("nep.in"), "type 1 C\ncutoff 5 4\n")
        errors = [d for d in diags if d.severity == "error"]
        assert len(errors) == 0
