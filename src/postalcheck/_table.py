"""Per-country postal code rules: a validation pattern and a canonical formatter.

Each rule matches the *compact* code (uppercased, with spaces and hyphens removed)
and knows how to lay the canonical separators back in.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    """A validation pattern for the compact code and its canonical formatter."""

    pattern: re.Pattern[str]
    fmt: Callable[[str], str]


def _plain(code: str) -> str:
    return code


def _tail(sep: str, n: int) -> Callable[[str], str]:
    """Put ``sep`` before the last ``n`` characters (the inward part)."""

    def fmt(code: str) -> str:
        return code[:-n] + sep + code[-n:] if len(code) > n else code

    return fmt


def _zip4(code: str) -> str:
    return code if len(code) == 5 else f"{code[:5]}-{code[5:]}"


def _r(pattern: str, fmt: Callable[[str], str] = _plain) -> Rule:
    return Rule(re.compile(pattern), fmt)


RULES: dict[str, Rule] = {
    "US": _r(r"\d{5}(?:\d{4})?", _zip4),
    "CA": _r(r"[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z]\d[ABCEGHJ-NPRSTV-Z]\d", _tail(" ", 3)),
    "GB": _r(r"GIR0AA|[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}", _tail(" ", 3)),
    "IE": _r(r"[AC-FHKNPRTV-Y]\d[\dW][0-9AC-FHKNPRTV-Y]{4}", _tail(" ", 4)),
    "DE": _r(r"\d{5}"),
    "FR": _r(r"\d{5}"),
    "ES": _r(r"\d{5}"),
    "IT": _r(r"\d{5}"),
    "NL": _r(r"\d{4}[A-Z]{2}", _tail(" ", 2)),
    "BE": _r(r"\d{4}"),
    "LU": _r(r"\d{4}"),
    "AT": _r(r"\d{4}"),
    "CH": _r(r"\d{4}"),
    "PT": _r(r"\d{7}", _tail("-", 3)),
    "PL": _r(r"\d{5}", _tail("-", 3)),
    "SE": _r(r"\d{5}", _tail(" ", 2)),
    "NO": _r(r"\d{4}"),
    "DK": _r(r"\d{4}"),
    "FI": _r(r"\d{5}"),
    "IS": _r(r"\d{3}"),
    "CZ": _r(r"\d{5}", _tail(" ", 2)),
    "SK": _r(r"\d{5}", _tail(" ", 2)),
    "GR": _r(r"\d{5}", _tail(" ", 2)),
    "HU": _r(r"\d{4}"),
    "RO": _r(r"\d{6}"),
    "BG": _r(r"\d{4}"),
    "HR": _r(r"\d{5}"),
    "SI": _r(r"\d{4}"),
    "EE": _r(r"\d{5}"),
    "LV": _r(r"\d{4}"),
    "LT": _r(r"\d{5}"),
    "UA": _r(r"\d{5}"),
    "RU": _r(r"\d{6}"),
    "TR": _r(r"\d{5}"),
    "IL": _r(r"\d{7}"),
    "IN": _r(r"\d{6}"),
    "CN": _r(r"\d{6}"),
    "JP": _r(r"\d{7}", _tail("-", 4)),
    "KR": _r(r"\d{5}"),
    "SG": _r(r"\d{6}"),
    "MY": _r(r"\d{5}"),
    "TH": _r(r"\d{5}"),
    "PH": _r(r"\d{4}"),
    "ID": _r(r"\d{5}"),
    "VN": _r(r"\d{6}"),
    "AU": _r(r"\d{4}"),
    "NZ": _r(r"\d{4}"),
    "ZA": _r(r"\d{4}"),
    "BR": _r(r"\d{8}", _tail("-", 3)),
    "MX": _r(r"\d{5}"),
    "AR": _r(r"[A-Z]\d{4}[A-Z]{3}|\d{4}"),
}
