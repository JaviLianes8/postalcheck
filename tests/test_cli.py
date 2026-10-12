"""The command line prints normal forms, reports invalid codes and never crashes on input."""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

from postalcheck._cli import main

SRC = Path(__file__).resolve().parents[1] / "src"


def _run(*argv: str, stdin: str = "") -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    status = main(list(argv), io.StringIO(stdin), out, err)
    return status, out.getvalue(), err.getvalue()


def test_valid_codes_print_their_canonical_form() -> None:
    assert _run("gb", "sw1a1aa", "m1 1aa") == (0, "SW1A 1AA\nM1 1AA\n", "")


def test_invalid_codes_go_to_stderr_and_set_status_one() -> None:
    assert _run("US", "90210", "9021", "12345-6789") == (
        1,
        "90210\n12345-6789\n",
        "invalid: 9021\n",
    )


def test_codes_are_read_from_stdin_skipping_blank_lines() -> None:
    assert _run("NL", stdin="1234ab\r\n\n  \n0000 AA\n") == (1, "1234 AB\n", "invalid: 0000 AA\n")


def test_an_unknown_country_is_a_usage_error_even_without_codes() -> None:
    status, out, err = _run("HK")
    assert (status, out) == (2, "")
    assert err.startswith("postalcheck: 'HK' does not use postal codes\nsupported: AC AD ")


def test_echoed_input_is_escaped() -> None:
    status, _, err = _run("US", "\x1b[2J9021\n\u202e")
    assert status == 1
    assert err == r"invalid: \x1b[2J9021\n\u202e" + "\n"


def test_usage_errors_and_help_go_to_the_given_streams() -> None:
    status, out, err = _run()
    assert (status, out) == (2, "")
    assert "the following arguments are required: country" in err
    status, out, err = _run("--help")
    assert (status, err) == (0, "")
    assert "usage: postalcheck" in out


def test_python_dash_m_runs_the_command_line() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "postalcheck",
            "JP",
            "\uff11\uff15\uff14\uff0d\uff10\uff10\uff12\uff13",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        cwd=SRC,
    )
    assert (result.returncode, result.stdout, result.stderr) == (0, "154-0023\n", "")
