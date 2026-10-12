"""is_valid and normalize: the promises users rely on, and the 0.1.0 mistakes fixed."""

from __future__ import annotations

import pytest

from postalcheck import UnknownCountryError, is_valid, normalize


@pytest.mark.parametrize(
    ("country", "code", "normal"),
    [
        ("GB", "sw1a1aa", "SW1A 1AA"),
        ("GB", "m11aa", "M1 1AA"),
        ("GB", "gir0aa", "GIR 0AA"),
        ("GB", "bfpo 61", "BFPO 61"),
        ("BR", "01310100", "01310-100"),
        ("US", "123456789", "12345-6789"),
        ("US", "90210", "90210"),
        ("NL", "1234ab", "1234 AB"),
        ("CA", "k1a0b1", "K1A 0B1"),
        ("JP", "1234567", "123-4567"),
        ("PL", "00950", "00-950"),
        ("PT", "2725079", "2725-079"),
        ("CZ", "10000", "100 00"),
        ("IR", "1193612345", "11936-12345"),
        ("CR", "1234567", "123-4567"),
        ("CR", "10101", "10101"),
        ("LB", "20383054", "2038 3054"),
        ("LB", "1000", "1000"),
        ("KY", "ky11100", "KY1-1100"),
        ("MT", "bzn1130", "BZN 1130"),
        ("SO", "jh09010", "JH 09010"),
        ("BM", "hmgx", "HM GX"),
        ("PE", "lima23", "LIMA 23"),
        ("PE", "02001", "02001"),
        ("IE", "a65f4e2", "A65 F4E2"),
        ("SH", "sthl1zz", "STHL 1ZZ"),
        ("PR", "009301234", "00930-1234"),
        ("AR", "c1070aam", "C1070AAM"),
        ("AR", "1070", "1070"),
    ],
)
def test_normalize_writes_the_canonical_layout(country: str, code: str, normal: str) -> None:
    assert is_valid(country, code) is True
    assert normalize(country, code) == normal
    assert normalize(country, normal) == normal


@pytest.mark.parametrize(
    ("country", "code"),
    [
        ("LV", "LV-1073"),  # refused by 0.1.0
        ("VN", "70010"),  # five-digit codes since 2018, refused by 0.1.0
        ("IL", "96143"),
        ("MT", "VCT 1753"),  # Malta was not covered
        ("GG", "GY1 1AA"),
    ],
)
def test_real_codes_are_accepted(country: str, code: str) -> None:
    assert is_valid(country, code) is True


# Hand-written invalid samples, each breaking one rule of the country format.
@pytest.mark.parametrize(
    ("country", "code"),
    [
        ("US", "1234"),
        ("US", "ABCDE"),
        ("US", "1234567"),
        ("GB", "1A1 AA1"),
        ("GB", "QQ1 1AA"),  # no QQ postcode area
        ("GB", "SW1A 1CI"),  # C and I are never inward letters
        ("CA", "123 456"),
        ("CA", "D1A 0B1"),  # D is never a first letter
        ("DE", "1011"),
        ("NL", "0123 AB"),
        ("NL", "1234 SS"),
        ("NL", "1234 SA"),
        ("NL", "1234 SD"),
        ("BR", "0131010"),
        ("JP", "123456"),
        ("AR", "I1070AAM"),  # I and O are not province letters
        ("AR", "O1070AAM"),
        ("VN", "7001"),
        ("LI", "9499"),
        ("SV", "1801"),
        ("PE", "LIMA 123"),
        ("OM", "PC1333"),
    ],
)
def test_impossible_codes_are_refused(country: str, code: str) -> None:
    assert is_valid(country, code) is False


def test_the_country_code_is_case_and_space_insensitive() -> None:
    assert is_valid(" de ", "10115") is True
    assert normalize("ca", "k1a0b1") == "K1A 0B1"


def test_uk_is_read_as_gb() -> None:
    assert normalize("UK", "sw1a1aa") == "SW1A 1AA"
    assert normalize("uk", "M1 1AA") == "M1 1AA"


def test_code_must_be_a_string() -> None:
    with pytest.raises(TypeError, match="code must be a str"):
        is_valid("US", 90210)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="code must be a str"):
        normalize("US", None)  # type: ignore[arg-type]


def test_country_must_be_a_string() -> None:
    with pytest.raises(TypeError, match="country must be a str"):
        is_valid(None, "90210")  # type: ignore[arg-type]


@pytest.mark.parametrize("country", ["\u0131t", "\u017fe", "\u00df", "\ufb05", "\uff27\uff22"])
def test_non_ascii_country_codes_are_unknown(country: str) -> None:
    # str.upper() would turn these into IT, SE, SS, ST and nothing: none may match.
    with pytest.raises(UnknownCountryError) as caught:
        is_valid(country, "00144")
    assert caught.value.has_postal_codes is None
    assert caught.value.country == country
