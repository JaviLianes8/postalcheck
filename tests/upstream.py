"""The pinned libaddressinput data and a sampler that writes strings a pattern accepts.

The third-party files are not committed: `python scripts/fetch_upstream.py` fetches them
into tests/upstream/. Tests that need them skip while a file is absent and fail if it
differs from tests/upstream/MANIFEST.json.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import random
import re
from functools import cache
from pathlib import Path
from typing import Any

import pytest

FOLDER = Path(__file__).resolve().parent / "upstream"


def read_upstream(name: str) -> str:
    """Return a fetched third-party file, or skip the calling test when it is absent."""
    path = FOLDER / name
    if not path.is_file():
        pytest.skip(f"{name} is not fetched; run python scripts/fetch_upstream.py")
    entry = json.loads((FOLDER / "MANIFEST.json").read_text(encoding="utf-8"))[name]
    body = path.read_bytes()
    assert hashlib.sha256(body).hexdigest() == entry["sha256"], f"{name} differs from MANIFEST"
    return body.decode("utf-8")


# Python 3.11 moved the regular expression parser to a private module.
try:
    sre: Any = importlib.import_module("re._parser")
except ImportError:  # pragma: no cover - Python 3.10
    sre = importlib.import_module("sre_parse")


@cache
def records() -> dict[str, dict[str, str]]:
    """Every country record, keyed by its ISO code, exactly as fetched."""
    lines = read_upstream("libaddressinput.jsonl").splitlines()
    return {record["key"]: record for record in map(json.loads, lines)}


def eircode_page() -> str:
    """The pinned Wikipedia wikitext listing the Eircode routing keys."""
    return read_upstream("eircode-routing-keys.wiki")


def zip_countries() -> list[str]:
    return sorted(key for key, record in records().items() if "zip" in record)


def upstream_pattern(country: str) -> re.Pattern[str]:
    return re.compile(records()[country]["zip"], re.ASCII)


def examples(country: str) -> list[str]:
    return records()[country]["zipex"].split(",")


def sample(pattern: str, rng: random.Random) -> str:
    """Return a random string that ``pattern`` fully matches."""
    out: list[str] = []
    _walk(sre.parse(pattern), rng, out)
    return "".join(out)


def _walk(tree: Any, rng: random.Random, out: list[str]) -> None:
    for op, arg in tree:
        name = str(op)
        if name == "LITERAL":
            out.append(chr(arg))
        elif name == "IN":
            out.append(_pick(arg, rng))
        elif name in ("MAX_REPEAT", "MIN_REPEAT"):
            low, high, sub = arg
            high = min(high, low + 3)
            for _ in range(rng.randint(low, high)):
                _walk(sub, rng, out)
        elif name == "SUBPATTERN":
            _walk(arg[-1], rng, out)
        elif name == "BRANCH":
            _walk(rng.choice(arg[1]), rng, out)
        elif name != "AT":
            raise NotImplementedError(name)


def _pick(items: Any, rng: random.Random) -> str:
    choices: list[str] = []
    for op, arg in items:
        name = str(op)
        if name == "LITERAL":
            choices.append(chr(arg))
        elif name == "RANGE":
            choices.extend(chr(c) for c in range(arg[0], arg[1] + 1))
        elif name == "CATEGORY" and str(arg) == "CATEGORY_DIGIT":
            choices.extend("0123456789")
        else:
            raise NotImplementedError(name)
    return rng.choice(choices)
