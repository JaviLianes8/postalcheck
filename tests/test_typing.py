"""The public API is typed: mypy infers the documented types and rejects wrong ones."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

api = pytest.importorskip("mypy.api")

SRC = Path(__file__).resolve().parents[1] / "src"

SNIPPET = """
from postalcheck import InvalidPostalCodeError, UnknownCountryError, example
from postalcheck import is_valid, normalize, supported_countries
reveal_type(is_valid("US", "90210"))
reveal_type(normalize("US", "90210"))
reveal_type(example("US"))
reveal_type(supported_countries())
reveal_type(UnknownCountryError("HK", False).has_postal_codes)
reveal_type(InvalidPostalCodeError("US", "1").code)
normalize("US", 90210)
is_valid(b"US", "90210")
example()
"""


@pytest.fixture(scope="module")
def mypy_output(tmp_path_factory: pytest.TempPathFactory) -> str:
    folder = tmp_path_factory.mktemp("typing")
    target = folder / "snippet.py"
    target.write_text(SNIPPET, encoding="utf-8")
    config = folder / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {SRC.as_posix()}\n", encoding="utf-8")
    cache = str(folder / "cache")
    out, err, _ = api.run(
        ["--strict", "--config-file", str(config), "--cache-dir", cache, str(target)]
    )
    return str(out) + str(err)


def test_functions_return_plain_types(mypy_output: str) -> None:
    assert _revealed(mypy_output, 4) == "bool"
    assert _revealed(mypy_output, 5) == "str"
    assert _revealed(mypy_output, 6) == "str"
    assert _revealed(mypy_output, 7) == "tuple[str, ...]"


def test_error_attributes_are_typed(mypy_output: str) -> None:
    assert _revealed(mypy_output, 8) == "bool | None"
    assert _revealed(mypy_output, 9) == "str"


def test_misuse_is_rejected(mypy_output: str) -> None:
    assert re.search(r"snippet\.py:10: error: .*\[arg-type\]", mypy_output), mypy_output
    assert re.search(r"snippet\.py:11: error: .*\[arg-type\]", mypy_output), mypy_output
    assert re.search(r"snippet\.py:12: error: .*\[call-arg\]", mypy_output), mypy_output


def _revealed(output: str, line: int) -> str:
    match = re.search(rf"snippet\.py:{line}: note: Revealed type is \"(.+)\"", output)
    assert match, output
    # Older mypy releases spell builtins with their module prefix.
    return match.group(1).replace("builtins.", "")
