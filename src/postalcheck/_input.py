"""Turn user input into the compact code and the places where it had separators."""

from __future__ import annotations

import unicodedata

# Dashes pasted from word processors (and the soft and small hyphens), and the katakana
# prolonged sound mark that Japanese input methods often produce in place of a hyphen.
_DASHES = frozenset("-\u00ad\ufe63\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u30fc")
_WIDTH_FORMS = ("<wide>", "<narrow>")
_ASCII = frozenset("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


def split(code: str) -> tuple[str, tuple[int, ...]] | None:
    """Return the compact upper-case code and its separator positions, or ``None``.

    Full-width and half-width forms fold to their plain form (other compatibility
    characters such as superscripts do not), every Unicode decimal digit becomes its ASCII
    digit, and any run of spaces (including tabs and no-break spaces) and dashes counts as
    one separator. Line breaks and control characters, anything else that is not an ASCII
    letter or digit, and a dash at either end make the input unusable.
    """
    chars: list[str] = []
    cuts: list[int] = []
    pending = False
    for ch in code.strip():
        if unicodedata.decomposition(ch).startswith(_WIDTH_FORMS):
            ch = unicodedata.normalize("NFKC", ch)
        if ch == "\t" or ch in _DASHES or unicodedata.category(ch) == "Zs":
            pending = True
            continue
        if ch.isdecimal():
            ch = str(unicodedata.decimal(ch))
        elif ch not in _ASCII:
            return None
        if pending:
            # A leading separator records a cut at 0, which no country allows.
            cuts.append(len(chars))
            pending = False
        chars.append(ch)
    if pending:
        return None
    return "".join(chars).upper(), tuple(cuts)
