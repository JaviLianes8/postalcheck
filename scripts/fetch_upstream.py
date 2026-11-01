"""Fetch the third-party test files listed in tests/upstream/MANIFEST.json.

The files are not part of the repository. Their tests skip until this script has fetched
them; each result is checked against the size and sha256 in the manifest. The FAQ's
``faq-text-v1`` extraction verifies answer text without request-dependent HTML fields.

An entry with a ``url`` is one download. An entry with ``index`` is assembled: the index
lists country keys, and the file holds one line per ``<index>/<key>`` response body, in
index order. The libaddressinput service is not versioned, so a mismatch there means the
service data changed since the manifest was written.

    python scripts/fetch_upstream.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

FOLDER = Path(__file__).resolve().parents[1] / "tests" / "upstream"
DESTINATION = Path(os.environ.get("POSTALCHECK_UPSTREAM", str(FOLDER)))


class _FAQText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.hidden = 0
        self.parts: list[str] = []
        self.answers: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "div":
            if self.depth:
                self.depth += 1
            elif dict(attrs).get("data-sf-field") == "Content":
                self.depth = 1
                self.parts = []
        if self.depth and tag in ("script", "style"):
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if self.depth and tag in ("script", "style"):
            self.hidden -= 1
        if self.depth and tag == "div":
            self.depth -= 1
            if not self.depth:
                self.answers.append(" ".join(" ".join(self.parts).split()))

    def handle_data(self, data: str) -> None:
        if self.depth and not self.hidden:
            self.parts.append(data)


def _faq_text(body: bytes) -> bytes:
    parser = _FAQText()
    parser.feed(body.decode("utf-8"))
    parser.close()
    return "".join(answer + "\n" for answer in parser.answers).encode("utf-8")


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "postalcheck-tests"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body: bytes = response.read()
    return body


def _assemble(entry: dict[str, Any]) -> bytes:
    index = json.loads(_get(entry["index"]))
    keys = index[entry["index_field"]].split("~")
    return b"".join(_get(f"{entry['index']}/{key}").strip() + b"\n" for key in keys)


def main() -> int:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((FOLDER / "MANIFEST.json").read_text(encoding="utf-8"))
    failed = 0
    for name, entry in manifest.items():
        body = _assemble(entry) if "index" in entry else _get(entry["url"])
        if entry.get("extract") == "faq-text-v1":
            body = _faq_text(body)
        digest = hashlib.sha256(body).hexdigest()
        if len(body) != entry["size"] or digest != entry["sha256"]:
            print(f"{name}: got {len(body)} bytes, sha256 {digest}; manifest differs")
            failed += 1
            continue
        (DESTINATION / name).write_bytes(body)
        print(f"{name}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
