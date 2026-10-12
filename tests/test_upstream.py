"""The rules agree with the pinned libaddressinput data, country by country."""

from __future__ import annotations

import pytest
from upstream import (
    examples,
    records,
    upstream_pattern,
    zip_countries,
)

from postalcheck import UnknownCountryError, example, is_valid, normalize, supported_countries
from postalcheck._countries import RULES

# Sweden: canonical layout with a space (kept from 0.1.0), examples upstream have none.
LAYOUT_DIFFERS = {"SE"}


def test_the_pinned_data_lists_every_country_key() -> None:
    assert len(records()) == 252


def test_every_country_with_a_format_upstream_has_a_rule() -> None:
    assert list(supported_countries()) == zip_countries()
    assert len(supported_countries()) == 182


def test_countries_without_a_format_upstream_are_known_to_have_none() -> None:
    without = [key for key in records() if key not in zip_countries()]
    assert len(without) == 70
    for country in without:
        with pytest.raises(UnknownCountryError) as caught:
            is_valid(country, "12345")
        assert caught.value.has_postal_codes is False, country


@pytest.mark.parametrize("country", supported_countries())
def test_every_upstream_example_is_valid_and_keeps_its_layout(country: str) -> None:
    for code in examples(country):
        assert is_valid(country, code), (country, code)
        normal = normalize(country, code)
        assert upstream_pattern(country).fullmatch(normal), (country, normal)
        if country not in LAYOUT_DIFFERS:
            assert normal == code, (country, code)


@pytest.mark.parametrize("country", supported_countries())
def test_example_is_the_first_upstream_example_in_canonical_layout(country: str) -> None:
    assert example(country) == normalize(country, examples(country)[0])


def test_patterns_match_ascii_digits_only() -> None:
    arabic_indic = "".join(chr(0x0660 + int(d)) for d in "1234567890")
    for country, rule in RULES.items():
        for length in range(3, 11):
            assert not rule.matches(arabic_indic[:length]), country


def test_sweden_uses_the_postnord_layout() -> None:
    assert normalize("SE", "11455") == "114 55"
    assert example("SE") == "114 55"
