"""Turn user input into the compact code and the places where it had separators."""

from __future__ import annotations

import unicodedata

# Dashes pasted from word processors, and the katakana prolonged sound mark that Japanese
# input methods often produce in place of a hyphen (154ー0023).
_DASHES = frozenset("-\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u30fc")
_ASCII = frozenset("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


def split(code: str) -> tuple[str, tuple[int, ...]] | None:
    """Return the compact upper-case code and its separator positions, or ``None``.

    NFKC folds full-width forms, native decimal digits become ASCII, and any run of
    spaces and dashes counts as one separator. Anything else that is not an ASCII letter
    or digit, and a separator at either end, makes the input unusable.
    """
    chars: list[str] = []
    cuts: list[int] = []
    pending = False
    for ch in unicodedata.normalize("NFKC", code).strip():
        if ch.isspace() or ch in _DASHES:
            pending = True
            continue
        if ch.isdecimal():
            ch = str(unicodedata.decimal(ch))
        elif ch not in _ASCII:
            return None
        if pending:
            if not chars:
                return None
            cuts.append(len(chars))
            pending = False
        chars.append(ch)
    if pending:
        return None
    return "".join(chars).upper(), tuple(cuts)
