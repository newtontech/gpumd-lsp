"""LSP server for GPUMD input files using pygls."""

from __future__ import annotations

from pathlib import Path

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_FORMATTING,
    TEXT_DOCUMENT_HOVER,
    CompletionItem,
    CompletionList,
    CompletionParams,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DocumentFormattingParams,
    Hover,
    HoverParams,
    Position,
    Range,
    TextEdit,
)
from lsprotocol.types import (
    Diagnostic as LspDiagnostic,
)
from pygls.server import LanguageServer

from gpumd_lsp.analyzer import FILE_NAMES, analyze_text, format_text
from gpumd_lsp.completion import get_completions, get_nep_completions
from gpumd_lsp.hover import get_hover

SERVER = LanguageServer("gpumd-lsp", "v0.1.0")

_SEVERITY_MAP = {
    "error": DiagnosticSeverity.Error,
    "warning": DiagnosticSeverity.Warning,
    "information": DiagnosticSeverity.Information,
    "hint": DiagnosticSeverity.Hint,
}


def _is_gpumd_file(uri: str) -> bool:
    return Path(uri).name in FILE_NAMES


def _to_lsp_diagnostic(d: object) -> LspDiagnostic:
    line = max(getattr(d, "line", 1) - 1, 0)
    col = max(getattr(d, "column", 1) - 1, 0)
    sev = _SEVERITY_MAP.get(getattr(d, "severity", ""), DiagnosticSeverity.Warning)
    return LspDiagnostic(
        range=Range(
            start=Position(line=line, character=col), end=Position(line=line, character=col)
        ),
        message=f"[{getattr(d, 'code', '?')}] {getattr(d, 'message', '?')}",
        severity=sev,
        source="gpumd-lsp",
        code=getattr(d, "code", "?"),
    )


def _publish_diagnostics_from_content(ls: LanguageServer, uri: str, content: str) -> None:
    path = Path(uri.replace("file://", ""))
    if not _is_gpumd_file(uri):
        ls.publish_diagnostics(uri, [])
        return
    diags = analyze_text(path, content)
    ls.publish_diagnostics(uri, [_to_lsp_diagnostic(d) for d in diags])


@SERVER.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams) -> None:
    uri = params.text_document.uri
    content = params.text_document.text
    _publish_diagnostics_from_content(ls, uri, content)


@SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams) -> None:
    uri = params.text_document.uri
    content = params.content_changes[0].text if params.content_changes else ""
    _publish_diagnostics_from_content(ls, uri, content)


@SERVER.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls: LanguageServer, params: DidCloseTextDocumentParams) -> None:
    ls.publish_diagnostics(params.text_document.uri, [])


@SERVER.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls: LanguageServer, params: CompletionParams) -> CompletionList:
    uri = params.text_document.uri
    items = get_nep_completions() if "nep.in" in uri else get_completions()
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(
                label=item["label"],
                detail=item.get("detail", ""),
                documentation=item.get("documentation", ""),
            )
            for item in items
        ],
    )


@SERVER.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: LanguageServer, params: HoverParams) -> Hover | None:
    uri = params.text_document.uri
    path = Path(uri.replace("file://", ""))
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    line_idx = params.position.line
    if line_idx >= len(lines):
        return None
    tokens = lines[line_idx].strip().split()
    if not tokens or tokens[0].startswith(("#", "!", ";")):
        return None
    keyword = tokens[0].lower()
    doc = get_hover(keyword)
    if doc is None:
        return None
    return Hover(
        contents=doc,
        range=Range(
            start=Position(line=line_idx, character=0),
            end=Position(line=line_idx, character=len(keyword)),
        ),
    )


@SERVER.feature(TEXT_DOCUMENT_FORMATTING)
def formatting(ls: LanguageServer, params: DocumentFormattingParams) -> list[TextEdit]:
    uri = params.text_document.uri
    path = Path(uri.replace("file://", ""))
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    formatted = format_text(content)
    line_count = formatted.count("\n")
    return [
        TextEdit(
            range=Range(
                start=Position(line=0, character=0), end=Position(line=line_count + 1, character=0)
            ),
            new_text=formatted,
        )
    ]
