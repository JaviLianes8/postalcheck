"""Hand-derived type boundaries and complete exception metadata round trips."""

from __future__ import annotations

import copy
import pickle
from collections.abc import Callable

import pytest

from postalcheck import UnknownCountryError, example, is_valid, normalize


class _ClassTrap:
    def __getattribute__(self, name: str) -> object:
        if name == "__class__":
            raise RuntimeError("PRIVATE-SENTINEL")
        return super().__getattribute__(name)


class _OddInteger(_ClassTrap, int):
    pass


class _OddBytes(_ClassTrap, bytes):
    pass


class _OddString(_ClassTrap, str):
    pass


@pytest.mark.parametrize("value_type", [_ClassTrap, _OddInteger, _OddBytes])
@pytest.mark.parametrize("operation", [example, is_valid, normalize])
def test_nontext_country_does_not_consult_class_hooks(
    value_type: type[_ClassTrap], operation: Callable[..., object]
) -> None:
    args = () if operation is example else ("95014",)
    with pytest.raises(TypeError, match=r"^country must be a str$"):
        operation(value_type(), *args)


@pytest.mark.parametrize("value_type", [_ClassTrap, _OddInteger, _OddBytes])
@pytest.mark.parametrize("operation", [is_valid, normalize])
def test_nontext_code_does_not_consult_class_hooks(
    value_type: type[_ClassTrap], operation: Callable[..., object]
) -> None:
    with pytest.raises(TypeError, match=r"^code must be a str$"):
        operation("US", value_type())


def test_actual_string_subclasses_remain_accepted() -> None:
    assert example(_OddString("us")) == "95014"
    assert is_valid(_OddString("us"), _OddString("95014")) is True
    assert normalize(_OddString("us"), _OddString("95014")) == "95014"


@pytest.mark.parametrize("metadata", [None, False, True])
def test_all_unknown_country_metadata_survives_copy_and_pickle(metadata: bool | None) -> None:
    error = UnknownCountryError(" supplied-country ", metadata)
    message = (
        "country does not use postal codes" if metadata is False else "unsupported country code"
    )
    clones = [error, copy.copy(error), copy.deepcopy(error)]
    clones.extend(pickle.loads(pickle.dumps(error, protocol)) for protocol in range(6))
    for clone in clones:
        assert type(clone) is UnknownCountryError
        assert clone.country == " supplied-country "
        assert clone.has_postal_codes is metadata
        assert clone.args == (message,)
        assert str(clone) == message
