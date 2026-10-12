"""How raw input is folded: Unicode forms, digits, dashes, case and separators."""

from __future__ import annotations

import pytest

from postalcheck import is_valid, normalize


@pytest.mark.parametrize(
    ("country", "code", "normal"),
    [
        ("JP", "\uff11\uff15\uff14\uff0d\uff10\uff10\uff12\uff13", "154-0023"),
        ("JP", "154\u30fc0023", "154-0023"),
        ("JP", "154\uff70" + "0023", "154-0023"),
        ("DE", "\u0661\u0660\u0661\u0661\u0665", "10115"),
        ("IR", "\u06f1\u06f1\u06f9\u06f3\u06f6-\u06f1\u06f2\u06f3\u06f4\u06f5", "11936-12345"),
        ("IN", "\u0967\u0967\u0966\u0966\u0966\u0967", "110001"),
        ("GB", "\uff53\uff57\uff11\uff41 \uff11\uff41\uff41", "SW1A 1AA"),
        ("PL", "00\u2013950", "00-950"),
        ("PL", "00\u2212950", "00-950"),
        ("PT", "2725\u2011079", "2725-079"),
        ("CA", "K1A\u00a00B1", "K1A 0B1"),
        ("CA", "K1A\u30000B1", "K1A 0B1"),
        ("CA", "  k1a   0b1\t", "K1A 0B1"),
        ("US", "12345 - 6789", "12345-6789"),
        ("PL", "00\ufe63950", "00-950"),
        ("PL", "00\u00ad950", "00-950"),
        ("DE", "10115\r\n", "10115"),
    ],
)
def test_input_is_folded_to_ascii(country: str, code: str, normal: str) -> None:
    assert normalize(country, code) == normal


@pytest.mark.parametrize(
    ("country", "code"),
    [
        ("GB", "\u0131M2 1AA"),  # dotless i would upper-case to I
        ("DE", "1011\u00b2"),  # superscript two is a digit but not a decimal one
        ("DE", "10115."),
        ("DE", "10_115"),
        ("US", "-90210"),
        ("US", "90210-"),
        ("US", ""),
        ("US", "   "),
        ("US", " - "),
        ("NL", "1234 \u00c5B"),
        ("GB", "SW1A\n1AA"),  # line breaks and control characters are not separators
        ("GB", "SW1A\x1f1AA"),
        ("GB", "SW1A\x0b1AA"),
        ("GB", "SW1A\u20281AA"),
    ],
)
def test_other_characters_are_refused(country: str, code: str) -> None:
    assert not is_valid(country, code)


@pytest.mark.parametrize(
    ("country", "code"),
    [
        ("US", "9-0-2-1-0"),
        ("US", "902 10"),
        ("US", "1234-56789"),
        ("DE", "1 0 1 1 5"),
        ("GB", "SW 1A1AA"),
        ("GB", "SW1A1 AA"),
        ("JP", "1540-023"),
        ("LV", "10-73"),
        ("BR", "0131-0100"),
        ("FR", "750 08"),
        ("OM", "1 33"),
        ("OM", "13 3"),  # the extra position belongs to the PC prefix only
        ("OM", "13-3"),
        ("AI", "26-40"),  # and to the AI prefix only
        ("AI", "26 40"),
    ],
)
def test_separators_only_where_the_country_writes_one(country: str, code: str) -> None:
    assert not is_valid(country, code)


@pytest.mark.parametrize(
    ("country", "code", "normal"),
    [
        ("GB", "SW1A-1AA", "SW1A 1AA"),
        ("JP", "154 0023", "154-0023"),
        ("FR", "75 008", "75008"),
        ("BN", "BT 2328", "BT2328"),
        ("AI", "AI-2640", "2640"),
        ("OM", "PC 133", "133"),
        ("LV", "LV 1073", "LV-1073"),
        ("LV", "1073", "LV-1073"),
        ("PE", "callao 2", "CALLAO 2"),
    ],
)
def test_separators_are_optional_and_interchangeable(country: str, code: str, normal: str) -> None:
    assert normalize(country, code) == normal
