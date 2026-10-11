import pytest

from postalcheck import (
    InvalidPostalCodeError,
    UnknownCountryError,
    is_valid,
    normalize,
    supported_countries,
)


@pytest.mark.parametrize(
    ("country", "code"),
    [
        ("US", "90210"),
        ("US", "12345-6789"),
        ("GB", "SW1A 1AA"),
        ("CA", "K1A 0B1"),
        ("DE", "10115"),
        ("FR", "75008"),
        ("NL", "1234 AB"),
        ("BR", "01310-100"),
        ("JP", "123-4567"),
        ("AU", "2000"),
    ],
)
def test_valid_codes(country: str, code: str) -> None:
    assert is_valid(country, code) is True


@pytest.mark.parametrize(
    ("country", "code"),
    [
        ("US", "1234"),
        ("US", "ABCDE"),
        ("GB", "1A1 AA1"),
        ("CA", "123 456"),
        ("DE", "1011"),
        ("NL", "1234"),
        ("BR", "0131010"),
        ("JP", "123456"),
    ],
)
def test_invalid_codes(country: str, code: str) -> None:
    assert is_valid(country, code) is False


def test_normalize_adds_gb_spacing() -> None:
    assert normalize("GB", "sw1a1aa") == "SW1A 1AA"


def test_normalize_adds_br_hyphen() -> None:
    assert normalize("BR", "01310100") == "01310-100"


def test_normalize_handles_short_gb_code() -> None:
    assert normalize("GB", "m11aa") == "M1 1AA"


def test_normalize_adds_nl_spacing_and_uppercases() -> None:
    assert normalize("NL", "1234ab") == "1234 AB"


def test_normalize_us_zip_plus_four() -> None:
    assert normalize("US", "123456789") == "12345-6789"


def test_normalize_plain_zip_is_unchanged() -> None:
    assert normalize("US", "90210") == "90210"


def test_input_is_case_insensitive() -> None:
    assert is_valid("ca", "k1a 0b1") is True
    assert normalize("ca", "k1a0b1") == "K1A 0B1"


def test_country_code_is_case_insensitive() -> None:
    assert is_valid("de", "10115") is True


def test_normalize_rejects_invalid_code() -> None:
    with pytest.raises(InvalidPostalCodeError):
        normalize("DE", "abcde")


def test_unknown_country_is_rejected_by_is_valid() -> None:
    with pytest.raises(UnknownCountryError):
        is_valid("ZZ", "12345")


def test_unknown_country_is_rejected_by_normalize() -> None:
    with pytest.raises(UnknownCountryError):
        normalize("ZZ", "12345")


def test_unknown_country_error_is_a_value_error() -> None:
    assert issubclass(UnknownCountryError, ValueError)


def test_supported_countries_is_sorted_and_covers_common_ones() -> None:
    countries = supported_countries()
    assert countries == tuple(sorted(countries))
    for code in ("US", "CA", "GB", "DE", "FR", "ES", "IT", "NL", "BR", "JP", "AU"):
        assert code in countries
