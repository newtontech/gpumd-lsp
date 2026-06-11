"""Small Python API wrapper around the Diagnostic Engine v1 CLI contract."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib.parse import urlparse

from .rich_diagnostics import agent_check_payload
from .tool import SOFTWARE, check_path


class AgentLSP:
    """Agent-facing wrapper for non-editor LSP diagnostics."""

    def __init__(self, text: str | None = None, uri: str = "file:///input") -> None:
        self.text = text
        self.uri = uri

    @classmethod
    def from_text(cls, text: str, uri: str = "file:///input") -> AgentLSP:
        return cls(text=text, uri=uri)

    @classmethod
    def from_path(cls, path: str | Path) -> AgentLSP:
        return cls(text=None, uri=Path(path).resolve().as_uri())

    def check(self) -> dict[str, Any]:
        parsed = urlparse(self.uri)
        if self.text is None and parsed.scheme == "file":
            return check_path(Path(parsed.path))
        suffix = Path(parsed.path).suffix if parsed.path else ""
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / f"input{suffix}"
            path.write_text(self.text or "", encoding="utf-8")
            payload = check_path(path)
            payload["uri"] = self.uri
            return payload

    def context(self, line: int = 0, character: int = 0) -> dict[str, Any]:
        payload = agent_check_payload(software=SOFTWARE, uri=self.uri, operation="context")
        payload["position"] = {"line": line, "character": character}
        return payload

    def complete(self, line: int = 0, character: int = 0) -> dict[str, Any]:
        payload = agent_check_payload(software=SOFTWARE, uri=self.uri, operation="complete")
        payload["position"] = {"line": line, "character": character}
        payload["items"] = []
        return payload

    def hover(self, line: int = 0, character: int = 0) -> dict[str, Any]:
        payload = agent_check_payload(software=SOFTWARE, uri=self.uri, operation="hover")
        payload["position"] = {"line": line, "character": character}
        payload["contents"] = None
        return payload

    def symbols(self) -> dict[str, Any]:
        payload = agent_check_payload(software=SOFTWARE, uri=self.uri, operation="symbols")
        payload["items"] = []
        return payload

    def suggest(self, line: int = 1) -> dict[str, Any]:
        """Issue #11: Agent JSON suggest operation."""
        from .agent_api import agent_suggest

        parsed = urlparse(self.uri)
        path = Path(parsed.path) if parsed.path else Path("input")
        if self.text is None and parsed.scheme == "file":
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                content = ""
        else:
            content = self.text or ""

        return agent_suggest(path, content, line)

    def code_actions(self, line: int = 1, character: int = 0) -> list[dict[str, Any]]:
        """Issue #21: Get code actions for a position."""
        from .agent_api import get_code_actions

        parsed = urlparse(self.uri)
        path = Path(parsed.path) if parsed.path else Path("input")
        if self.text is None and parsed.scheme == "file":
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                content = ""
        else:
            content = self.text or ""

        return get_code_actions(path, content, line, character)
