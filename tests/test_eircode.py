"""Ireland: every published routing key is accepted, and the stricter rule is sourced."""

from __future__ import annotations

import re

import pytest
from upstream import EIRCODE_KEYS

from postalcheck import is_valid, normalize


def _routing_keys() -> list[str]:
    text = EIRCODE_KEYS.read_text(encoding="utf-8")
    return sorted(set(re.findall(r"^\| *([A-Z0-9]{3}) *\|\|", text, flags=re.MULTILINE)))


def test_the_pinned_page_lists_139_routing_keys() -> None:
    assert len(_routing_keys()) == 139


@pytest.mark.parametrize("key", _routing_keys())
def test_every_routing_key_is_accepted(key: str) -> None:
    assert normalize("IE", f"{key}ab12") == f"{key} AB12"


def test_routing_key_letters_are_exactly_those_in_use() -> None:
    used = sorted({key[0] for key in _routing_keys()})
    allowed = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if is_valid("IE", f"{c}12 AB12")]
    assert allowed == used


def test_d6w_is_the_only_routing_key_ending_in_a_letter() -> None:
    assert [key for key in _routing_keys() if not key[2].isdigit()] == ["D6W"]
    assert is_valid("IE", "D6W PV38")
    assert not is_valid("IE", "D6X PV38")
    assert not is_valid("IE", "A6W PV38")


@pytest.mark.parametrize("code", ["A65 O4E2", "A65 F4EO", "O65 F4E2"])
def test_the_letter_o_is_never_used(code: str) -> None:
    assert not is_valid("IE", code)
    assert is_valid("IE", code.replace("O", "0").replace("065", "A65"))
