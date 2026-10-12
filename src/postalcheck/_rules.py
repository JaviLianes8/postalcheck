"""A postal code rule: the pattern of the compact code, a real example and its layout."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

Layout = Callable[[str], str]

_SEPARATORS = " -"


@dataclass(frozen=True)
class Rule:
    """How one country writes its postal codes."""

    pattern: re.Pattern[str]
    example: str
    layout: Layout
    extra_cuts: frozenset[int]

    def matches(self, compact: str) -> bool:
        return self.pattern.fullmatch(compact) is not None

    def allowed_cuts(self, compact: str, canonical: str) -> frozenset[int]:
        """Positions in ``compact`` where the input may carry a separator."""
        cuts: set[int] = set()
        # Canonical separators only map back to the input when the layout kept every
        # character: a layout that adds or drops a prefix would shift the positions.
        if "".join(ch for ch in canonical if ch not in _SEPARATORS) == compact:
            kept = 0
            for ch in canonical:
                if ch in _SEPARATORS:
                    cuts.add(kept)
                else:
                    kept += 1
        return frozenset(cuts) | self.extra_cuts


def plain(code: str) -> str:
    return code


def tail(sep: str, n: int) -> Layout:
    """Put ``sep`` before the last ``n`` characters (the inward or local part)."""

    def layout(code: str) -> str:
        return f"{code[:-n]}{sep}{code[-n:]}"

    return layout


def when_length(length: int, inner: Layout) -> Layout:
    """Apply ``inner`` only to codes of ``length`` characters (the long form)."""

    def layout(code: str) -> str:
        return inner(code) if len(code) == length else code

    return layout


def zip_plus_four(code: str) -> str:
    return code if len(code) == 5 else f"{code[:5]}-{code[5:]}"


def split_letters(code: str) -> str:
    """Put a space between a leading run of letters and the digits after it."""
    head = len(code) - len(code.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    return f"{code[:head]} {code[head:]}" if 0 < head < len(code) else code


def drop_prefix(prefix: str) -> Layout:
    """Remove an optional ``prefix`` that the national form leaves out."""

    def layout(code: str) -> str:
        return code[len(prefix) :] if code.startswith(prefix) else code

    return layout


def add_prefix(prefix: str, sep: str) -> Layout:
    """Write a mandatory ``prefix`` that the input may have left out."""

    def layout(code: str) -> str:
        return prefix + sep + (code[len(prefix) :] if code.startswith(prefix) else code)

    return layout


def british(code: str) -> str:
    return split_letters(code) if code.startswith("BFPO") else f"{code[:-3]} {code[-3:]}"


def rule(pattern: str, example: str, layout: Layout = plain, extra: tuple[int, ...] = ()) -> Rule:
    return Rule(re.compile(pattern, re.ASCII), example, layout, frozenset(extra))


def digits(count: int, example: str) -> Rule:
    return rule(rf"\d{{{count}}}", example)
