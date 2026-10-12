"""Every rule against its own example, so each country is exercised without fetched data."""

from __future__ import annotations

import re

import pytest

from postalcheck import example, is_valid, normalize, supported_countries


@pytest.mark.parametrize("country", supported_countries())
def test_example_is_valid_and_already_normal(country: str) -> None:
    code = example(country)
    assert is_valid(country, code), (country, code)
    assert normalize(country, code) == code


@pytest.mark.parametrize("country", supported_countries())
def test_example_written_compact_and_lower_case_normalizes_back(country: str) -> None:
    code = example(country)
    compact = re.sub(r"[ -]", "", code).lower()
    assert normalize(country, compact) == code, (country, compact)
