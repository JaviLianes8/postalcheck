"""Errors, examples and the country list."""

from __future__ import annotations

import pickle

import pytest

from postalcheck import (
    InvalidPostalCodeError,
    UnknownCountryError,
    example,
    is_valid,
    normalize,
    supported_countries,
)


def test_normalize_raises_with_the_inputs_attached() -> None:
    with pytest.raises(InvalidPostalCodeError) as caught:
        normalize("de", "abcde")
    assert (caught.value.country, caught.value.code) == ("DE", "abcde")
    assert str(caught.value) == "'abcde' is not a valid DE postal code"
    assert isinstance(caught.value, ValueError)


@pytest.mark.parametrize("call", [is_valid, normalize])
def test_an_unknown_country_is_refused(call: object) -> None:
    assert callable(call)
    with pytest.raises(UnknownCountryError) as caught:
        call("ZZ", "12345")
    assert caught.value.country == "ZZ"
    assert caught.value.has_postal_codes is None
    assert str(caught.value) == "'ZZ' is not a supported country code"


def test_a_country_without_postal_codes_says_so() -> None:
    with pytest.raises(UnknownCountryError) as caught:
        example("hk")
    assert caught.value.has_postal_codes is False
    assert str(caught.value) == "'hk' does not use postal codes"


def test_errors_survive_pickling() -> None:
    invalid = pickle.loads(pickle.dumps(InvalidPostalCodeError("DE", "x")))
    assert (invalid.country, invalid.code) == ("DE", "x")
    assert str(invalid) == "'x' is not a valid DE postal code"
    unknown = pickle.loads(pickle.dumps(UnknownCountryError("HK", False)))
    assert (unknown.country, unknown.has_postal_codes) == ("HK", False)
    assert str(unknown) == "'HK' does not use postal codes"


def test_both_errors_are_value_errors() -> None:
    assert issubclass(UnknownCountryError, ValueError)
    assert issubclass(InvalidPostalCodeError, ValueError)


def test_example_returns_a_valid_canonical_code() -> None:
    assert example("gb") == "EC1Y 8SY"
    assert example("UK") == "EC1Y 8SY"
    assert example("SE") == "114 55"
    for country in supported_countries():
        assert normalize(country, example(country)) == example(country)


def test_supported_countries_is_sorted_and_unique() -> None:
    countries = supported_countries()
    assert countries == tuple(sorted(set(countries)))
    assert all(len(c) == 2 and c.isupper() for c in countries)
    assert "UK" not in countries
    assert "HK" not in countries
