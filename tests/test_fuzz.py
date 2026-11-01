"""Seeded, hand-written generators exercise malformed input and normalization properties."""

from __future__ import annotations

import random

import pytest

from postalcheck import InvalidPostalCodeError, example, is_valid, normalize, supported_countries


@pytest.mark.parametrize("seed", [0, 18731, 20261101])
def test_arbitrary_unicode_never_escapes_the_error_contract(seed: int) -> None:
    rng = random.Random(seed)
    countries = supported_countries()
    alphabet = "0123456789AZaz -\t\r\n\x00\x1b\ud800\udfff\u00b2\u0301\uff11\u0661\u2013"
    for _ in range(5000):
        country = rng.choice(countries)
        code = "".join(rng.choice(alphabet) for _ in range(rng.randrange(35)))
        valid = is_valid(country, code)
        try:
            normal = normalize(country, code)
        except InvalidPostalCodeError as error:
            assert not valid
            assert (error.country, error.code) == (country, code)
            assert str(error) == "invalid postal code format"
        else:
            assert valid and normal.isascii()
            assert normalize(country, normal) == normal


@pytest.mark.parametrize("seed", [123, 20261101])
def test_fullwidth_case_and_separators_preserve_all_examples(seed: int) -> None:
    rng = random.Random(seed)
    for country in supported_countries():
        canonical = example(country)
        for _ in range(20):
            chars = []
            for char in canonical:
                if char in " -":
                    chars.append(rng.choice(["", "\t", " - ", "\u00a0", "\u2013"]))
                elif rng.randrange(2):
                    chars.append(chr(ord(char) + 0xFEE0))
                else:
                    chars.append(char.lower())
            assert normalize(country, "".join(chars)) == canonical


@pytest.mark.parametrize("piece", ["0", " ", "-", "\t", "\u0661", "\ud800"])
def test_large_invalid_inputs_have_bounded_messages(piece: str) -> None:
    code = "A" + piece * 1_000_000
    assert is_valid("US", code) is False
    with pytest.raises(InvalidPostalCodeError) as caught:
        normalize("US", code)
    assert str(caught.value) == "invalid postal code format"


def test_long_separator_runs_are_linear_and_preserve_layout() -> None:
    assert normalize("US", "12345" + " -\t" * 100_000 + "6789") == "12345-6789"
