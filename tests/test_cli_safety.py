"""CLI diagnostics never expose input, including argparse errors and large inputs."""

from __future__ import annotations

import io

import pytest

from postalcheck._cli import main


@pytest.mark.parametrize("args", [["US", "--password=secret"], ["password=secret"], []])
def test_usage_errors_omit_values(args: list[str]) -> None:
    out, err = io.StringIO(), io.StringIO()
    assert main(args, io.StringIO(), out, err) == 2
    assert not out.getvalue()
    assert "password" not in err.getvalue() and "secret" not in err.getvalue()
    assert len(err.getvalue()) < 1000


def test_huge_invalid_code_is_not_echoed() -> None:
    out, err = io.StringIO(), io.StringIO()
    assert main(["US", "secret" * 100_000], io.StringIO(), out, err) == 1
    assert err.getvalue() == "invalid postal code format\n"


def test_double_dash_allows_an_argument_starting_with_a_dash() -> None:
    out, err = io.StringIO(), io.StringIO()
    assert main(["US", "--", "-95014"], io.StringIO(), out, err) == 1
    assert err.getvalue() == "invalid postal code format\n"


def test_empty_stdin_succeeds_without_output() -> None:
    out, err = io.StringIO(), io.StringIO()
    assert main(["US"], io.StringIO("\r\n \n"), out, err) == 0
    assert out.getvalue() == err.getvalue() == ""
