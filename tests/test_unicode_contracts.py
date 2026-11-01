"""Hand-derived Unicode input contracts, including separator placement."""

from __future__ import annotations

import unicodedata
from collections.abc import Callable

import pytest

from postalcheck import (
    InvalidPostalCodeError,
    UnknownCountryError,
    example,
    is_valid,
    normalize,
    supported_countries,
)

WHITESPACE = (
    "\t\n\v\f\r\x1c\x1d\x1e\x1f \x85\u00a0\u1680"
    + "".join(chr(c) for c in range(0x2000, 0x200B))
    + "\u2028\u2029\u202f\u205f\u3000"
)
DASHES = "-\u00ad\ufe63\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u30fc\uff70\uff0d"
SPACES = " \u00a0\u1680" + "".join(chr(c) for c in range(0x2000, 0x200B)) + "\u202f\u205f\u3000"


@pytest.mark.parametrize("country", supported_countries())
def test_multicharacter_width_folding_is_invalid(country: str) -> None:
    for code in ("\uffe3", "\uffe3" + example(country), example(country) + "\uffe3"):
        assert is_valid(country, code) is False
        with pytest.raises(InvalidPostalCodeError) as caught:
            normalize(country, code)
        assert (caught.value.country, caught.value.code) == (country, code)


@pytest.mark.parametrize("country", supported_countries())
def test_multicharacter_width_folding_is_invalid_inside_codes(country: str) -> None:
    compact = example(country).replace(" ", "").replace("-", "")
    for position in range(1, len(compact)):
        code = compact[:position] + "\uffe3" + compact[position:]
        assert is_valid(country, code) is False
        with pytest.raises(InvalidPostalCodeError) as caught:
            normalize(country, code)
        assert (caught.value.country, caught.value.code) == (country, code)


@pytest.mark.parametrize("space", WHITESPACE)
@pytest.mark.parametrize("operation", [example, is_valid, normalize])
def test_country_unicode_whitespace(space: str, operation: Callable[..., object]) -> None:
    args = () if operation is example else ("SW1A 1AA",)
    for key in ("gb", "UK"):
        result = operation(space + key + space, *args)
        assert result == operation(key, *args)
    for key, metadata in (("HK", False), ("ZZ", None)):
        country = space + key + space
        with pytest.raises(UnknownCountryError) as caught:
            operation(country, *args)
        assert caught.value.country == country
        assert caught.value.has_postal_codes is metadata


@pytest.mark.parametrize("separator", DASHES + SPACES + "\t")
@pytest.mark.parametrize(
    ("country", "compact", "canonical", "cuts"),
    [
        ("US", "95014", "95014", ()),
        ("US", "950141234", "95014-1234", (5,)),
        ("PL", "00950", "00-950", (2,)),
        ("CA", "K1A0B1", "K1A 0B1", (3,)),
        ("GB", "SW1A1AA", "SW1A 1AA", (4,)),
        ("JP", "1540023", "154-0023", (3,)),
        ("LV", "LV1073", "LV-1073", (2,)),
        ("FR", "75008", "75008", (2,)),
        ("AI", "AI2640", "2640", (2,)),
        ("OM", "PC133", "133", (2,)),
    ],
)
def test_every_separator_at_every_position(
    separator: str, country: str, compact: str, canonical: str, cuts: tuple[int, ...]
) -> None:
    for position in range(len(compact) + 1):
        for run in (separator, separator * 3):
            code = compact[:position] + run + compact[position:]
            accepted = position in cuts or (separator.isspace() and position in (0, len(compact)))
            assert is_valid(country, code) is accepted
            if accepted:
                assert normalize(country, code) == canonical
            else:
                with pytest.raises(InvalidPostalCodeError):
                    normalize(country, code)


def test_decimal_coverage_follows_the_runtime_unicode_database() -> None:
    code = "".join(chr(0x11F50 + int(digit)) for digit in "10115")
    known = unicodedata.category(chr(0x11F50)) == "Nd"
    assert is_valid("DE", code) is known
    if known:
        assert normalize("DE", code) == "10115"
    else:
        with pytest.raises(InvalidPostalCodeError):
            normalize("DE", code)
