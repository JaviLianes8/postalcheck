"""The pinned libaddressinput data and a sampler that writes strings a pattern accepts."""

from __future__ import annotations

import importlib
import json
import random
import re
from functools import cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parent / "data"
LIBADDRESSINPUT = DATA / "libaddressinput.jsonl"
LIBADDRESSINPUT_SHA256 = "f2417db82d928fe0b19c557ca97fd321f6498dfc775d6338e990f1b1981bc112"
EIRCODE_KEYS = DATA / "eircode-routing-keys.wiki"
EIRCODE_KEYS_SHA256 = "e5d46fe105832ebda145cc9bb538c4b5a041332d1587f7fbc26634e7d1e7dcbb"

# Python 3.11 moved the regular expression parser to a private module.
try:
    sre: Any = importlib.import_module("re._parser")
except ImportError:  # pragma: no cover - Python 3.10
    sre = importlib.import_module("sre_parse")


@cache
def records() -> dict[str, dict[str, str]]:
    """Every country record, keyed by its ISO code, exactly as fetched."""
    lines = LIBADDRESSINPUT.read_text(encoding="utf-8").splitlines()
    return {record["key"]: record for record in map(json.loads, lines)}


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
