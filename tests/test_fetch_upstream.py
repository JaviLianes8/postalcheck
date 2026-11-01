"""Hand-written HTML verifies extraction independently of live website sessions."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture
def fetcher(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "scripts" / "fetch_upstream.py"
    spec = importlib.util.spec_from_file_location("fetch_upstream", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected = b"First answer.\nSecond answer.\n"
    manifest = {
        "faq.txt": {
            "url": "https://example.invalid/faq",
            "extract": "faq-text-v1",
            "size": len(expected),
            "sha256": hashlib.sha256(expected).hexdigest(),
        }
    }
    (tmp_path / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(module, "FOLDER", tmp_path)
    monkeypatch.setattr(module, "DESTINATION", tmp_path / "data")
    return module


def _page(session: str, answer: str = "Second answer.") -> bytes:
    return (
        f'<input type="hidden" value="{session}"><script>{session}</script>'
        '<div data-sf-field="Content"><p>First <strong>answer.</strong></p>'
        f"<script>{session}</script><style>{session}</style></div>"
        f'<div data-sf-field="Content"><div>{answer}</div></div>'
        f'<script src="/{session}"></script>'
    ).encode()


def test_faq_integrity_ignores_session_fields(
    fetcher: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    for session in ("session-one", "session-two"):
        monkeypatch.setattr(fetcher, "_get", lambda url, session=session: _page(session))
        assert fetcher.main() == 0
        assert (fetcher.DESTINATION / "faq.txt").read_bytes() == b"First answer.\nSecond answer.\n"


@pytest.mark.parametrize("body", [_page("session", "Changed answer."), b"<html>No FAQ</html>"])
def test_faq_integrity_rejects_changed_or_missing_content(
    fetcher: ModuleType, monkeypatch: pytest.MonkeyPatch, body: bytes
) -> None:
    monkeypatch.setattr(fetcher, "_get", lambda url: body)
    assert fetcher.main() == 1
    assert not (fetcher.DESTINATION / "faq.txt").exists()
