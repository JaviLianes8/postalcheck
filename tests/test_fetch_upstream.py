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
    monkeypatch.setattr(module, "FOLDER", tmp_path)
    monkeypatch.setattr(module, "DESTINATION", tmp_path / "data")
    _manifest(module, b"First answer.\nSecond answer.\n")
    return module


def _manifest(fetcher: ModuleType, expected: bytes) -> None:
    manifest = {
        "faq.txt": {
            "url": "https://example.invalid/faq",
            "extract": "faq-text-v1",
            "size": len(expected),
            "sha256": hashlib.sha256(expected).hexdigest(),
        }
    }
    (fetcher.FOLDER / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")


def _check_extraction(
    fetcher: ModuleType, monkeypatch: pytest.MonkeyPatch, body: bytes, expected: bytes
) -> None:
    assert fetcher._faq_text(body) == expected
    _manifest(fetcher, expected)
    monkeypatch.setattr(fetcher, "_get", lambda url: body)
    assert fetcher.main() == 0
    assert (fetcher.DESTINATION / "faq.txt").read_bytes() == expected


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


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        (
            "A&amp;B &lt;C&gt; &quot;D&quot; &apos;E&apos; &copy;",
            "A&B <C> \"D\" 'E' \u00a9\n",
        ),
        ("A&#38;B &#233;", "A&B \u00e9\n"),
        ("A&#x26;B &#x1F4EE;", "A&B \U0001f4ee\n"),
    ],
    ids=["named", "decimal", "hexadecimal"],
)
def test_faq_character_references_are_decoded(
    fetcher: ModuleType, monkeypatch: pytest.MonkeyPatch, answer: str, expected: str
) -> None:
    body = f'<div data-sf-field="Content">{answer}</div>'.encode()
    _check_extraction(fetcher, monkeypatch, body, expected.encode())


@pytest.mark.parametrize(
    "space",
    [
        "\t\t",
        "\r\n\n",
        "\u00a0\u1680",
        "".join(chr(c) for c in range(0x2000, 0x200B)),
        "\u2028\u2029\u202f",
        "\u205f\u3000",
        " \t\r\n\u202f\t ",
    ],
)
def test_faq_unicode_whitespace_is_collapsed(
    fetcher: ModuleType, monkeypatch: pytest.MonkeyPatch, space: str
) -> None:
    body = f'<div data-sf-field="Content">{space}Caf\u00e9{space}answer.{space}</div>'.encode()
    _check_extraction(fetcher, monkeypatch, body, b"Caf\xc3\xa9 answer.\n")


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("A<div>B</div>C", "A B C"),
        ("A<div>B<div>C</div>D</div>E", "A B C D E"),
        ("A<div>B</div>C<div>D</div>E", "A B C D E"),
    ],
    ids=["nested", "deeply-nested", "siblings"],
)
def test_faq_text_surrounding_nested_divs_is_preserved(
    fetcher: ModuleType, monkeypatch: pytest.MonkeyPatch, answer: str, expected: str
) -> None:
    body = (
        f'<div>Outside<div data-sf-field="Content">{answer}</div>Outside</div>'
        '<div data-sf-field="Content">Second answer.</div>'
    ).encode()
    _check_extraction(fetcher, monkeypatch, body, f"{expected}\nSecond answer.\n".encode())
