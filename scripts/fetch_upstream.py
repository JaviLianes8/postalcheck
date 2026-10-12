"""Fetch the third-party test files listed in tests/upstream/MANIFEST.json.

The files are not part of the repository. Their tests skip until this script has fetched
them; each result is checked against the size and sha256 in the manifest.

An entry with a ``url`` is one download. An entry with ``index`` is assembled: the index
lists country keys, and the file holds one line per ``<index>/<key>`` response body, in
index order. The libaddressinput service is not versioned, so a mismatch there means the
service data changed since the manifest was written.

    python scripts/fetch_upstream.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

FOLDER = Path(__file__).resolve().parents[1] / "tests" / "upstream"


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
    manifest = json.loads((FOLDER / "MANIFEST.json").read_text(encoding="utf-8"))
    failed = 0
    for name, entry in manifest.items():
        body = _assemble(entry) if "index" in entry else _get(entry["url"])
        digest = hashlib.sha256(body).hexdigest()
        if len(body) != entry["size"] or digest != entry["sha256"]:
            print(f"{name}: got {len(body)} bytes, sha256 {digest}; manifest differs")
            failed += 1
            continue
        (FOLDER / name).write_bytes(body)
        print(f"{name}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
