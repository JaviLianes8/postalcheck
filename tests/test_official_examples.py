"""Short cited examples from sources fetched on 2026-11-01, not generated fixtures."""

from __future__ import annotations

import pytest

from postalcheck import normalize


# UPU Sweden, revision 11/2024, fetched 2026-11-01:
# https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/sweEn.pdf
@pytest.mark.parametrize("code", ["123 45", "111 81", "120 35", "105 00", "114 55"])
def test_upu_sweden_codes_keep_the_published_spacing(code: str) -> None:
    assert normalize("SE", code) == code
    assert normalize("SE", code.replace(" ", "")) == code
