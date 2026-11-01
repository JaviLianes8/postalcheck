"""Stable signatures, executable docstrings and complete error contracts."""

from __future__ import annotations

import copy
import doctest
import importlib
import inspect
import pickle
from collections.abc import Callable
from pathlib import Path
from typing import get_type_hints

import pytest

import postalcheck as p


def test_no_accidental_public_names() -> None:
    assert {n for n in vars(p) if not n.startswith("_")} == set(p.__all__)
    assert len(p.__all__) == len(set(p.__all__))


@pytest.mark.parametrize("name", p.__all__)
def test_public_names_have_runnable_docstrings(name: str) -> None:
    assert ">>>" in inspect.getdoc(getattr(p, name))  # type: ignore[operator]


@pytest.mark.parametrize("module", ["postalcheck", "postalcheck._core"])
def test_doctests(module: str) -> None:
    failed, attempted = doctest.testmod(importlib.import_module(module), raise_on_error=True)
    assert failed == 0 and attempted > 0


def test_signatures_defaults_and_annotations() -> None:
    expected = {
        "example": ("country",),
        "is_valid": ("country", "code"),
        "normalize": ("country", "code"),
        "supported_countries": (),
        "UnknownCountryError": ("country", "has_postal_codes"),
        "InvalidPostalCodeError": ("country", "code"),
    }
    for name, arguments in expected.items():
        symbol = getattr(p, name)
        params = inspect.signature(symbol).parameters
        assert tuple(params) == arguments
        for key, parameter in params.items():
            assert parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            default = None if key == "has_postal_codes" else inspect.Parameter.empty
            assert parameter.default is default
        hints = get_type_hints(vars(symbol)["__init__"] if isinstance(symbol, type) else symbol)
        assert all(key in hints for key in (*arguments, "return"))


@pytest.mark.parametrize("operation", [p.is_valid, p.normalize, p.example])
def test_country_failure_precedes_code_validation(operation: Callable[..., object]) -> None:
    args: tuple[object, ...] = () if operation is p.example else (None,)
    with pytest.raises(p.UnknownCountryError) as caught:
        operation(" zz ", *args)
    assert caught.value.country == " zz "
    assert caught.value.has_postal_codes is None
    with pytest.raises(TypeError, match=r"^country must be a str$"):
        operation(None, *args)


def test_keywords_and_unknown_country_default() -> None:
    assert p.normalize(country=" uk ", code="m11aa") == "M1 1AA"
    assert p.is_valid(code="95014", country="US") is True
    assert p.example(country="us") == "95014"
    assert p.UnknownCountryError("ZZ").has_postal_codes is None
    with pytest.raises(p.InvalidPostalCodeError) as caught:
        p.normalize(" uk ", "bad")
    assert (caught.value.country, caught.value.code) == ("GB", "bad")


@pytest.mark.parametrize("size", [8, 1_000_000])
def test_errors_never_echo_input(size: int) -> None:
    secret = "password=" + "x" * size
    errors = [p.UnknownCountryError(secret), p.UnknownCountryError(secret, False)]
    errors.append(p.InvalidPostalCodeError(secret, secret))  # type: ignore[arg-type]
    for error in errors:
        assert len(str(error)) < 80
        assert "password" not in str(error) and "xxx" not in str(error)
        assert error.country == secret
    with pytest.raises(p.InvalidPostalCodeError) as caught:
        p.normalize("US", secret)
    assert caught.value.code == secret


@pytest.mark.parametrize(
    "error", [p.UnknownCountryError("HK", False), p.InvalidPostalCodeError("GB", "bad")]
)
def test_errors_copy_pickle_and_public_module(error: ValueError) -> None:
    assert type(error).__module__ == "postalcheck"
    for clone in [copy.copy(error), copy.deepcopy(error), pickle.loads(pickle.dumps(error))]:
        assert type(clone) is type(error)
        assert vars(clone) == vars(error)
        assert clone.args == error.args


class _Misleading(str):
    def strip(self, chars: str | None = None) -> str:
        raise AssertionError("overridden string method called")


def test_string_subclasses_use_their_underlying_value() -> None:
    assert p.normalize(_Misleading("us"), _Misleading("95014")) == "95014"


def test_guide_examples_execute() -> None:
    import re

    guide = Path(__file__).resolve().parents[1] / "GUIDE.md"
    blocks = re.findall(r"```python\n(.*?)```", guide.read_text(encoding="utf-8"), re.DOTALL)
    assert len(blocks) == 2
    for block in blocks:
        exec(compile(block, "GUIDE.md", "exec"), {})
