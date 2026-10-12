"""The command line prints normal forms, reports invalid codes and never crashes on input."""

from __future__ import annotations

import contextlib
import io
import os
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


def test_a_backslash_is_escaped_so_spellings_differ_from_escapes() -> None:
    backslash = chr(92)
    _, _, escape = _run("US", chr(27))
    _, _, spelled = _run("US", backslash + "x1b")
    assert escape == "invalid: " + backslash + "x1b\n"
    assert spelled == "invalid: " + backslash * 2 + "x1b\n"


class _ClosedPipe(io.StringIO):
    def write(self, text: str) -> int:
        raise BrokenPipeError


def test_a_closed_output_pipe_stops_quietly() -> None:
    err = io.StringIO()
    assert main(["US", "90210", "10001"], io.StringIO(), _ClosedPipe(), err) == 1
    assert err.getvalue() == ""


def test_stdin_is_processed_line_by_line() -> None:
    out = io.StringIO()

    def lines() -> object:
        yield "90210\n"
        assert out.getvalue() == "90210\n", "the first code was not written yet"
        yield "10001\n"

    stdin = lines()
    assert main(["US"], stdin, out, io.StringIO()) == 0  # type: ignore[arg-type]
    assert out.getvalue() == "90210\n10001\n"


def test_piped_stdin_is_read_as_utf8_whatever_the_console_code_page() -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHONUTF8", "PYTHONIO"))}
    env["PYTHONPATH"] = str(SRC)
    data = (
        "\ufeff\uff11\uff15\uff14\uff0d\uff10\uff10\uff12\uff13\r\n\u0661\u0660\u0661\u0661\u0665\n"
    )
    result = subprocess.run(
        [sys.executable, "-m", "postalcheck", "JP"],
        input=data.encode("utf-8"),
        capture_output=True,
        check=False,
        env=env,
    )
    assert result.returncode == 1
    assert result.stdout.splitlines() == [b"154-0023"]
    assert result.stderr.splitlines() == [rb"invalid: \u0661\u0660\u0661\u0661\u0665"]


def test_a_reader_that_goes_away_leaves_no_traceback() -> None:
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    with subprocess.Popen(
        [sys.executable, "-m", "postalcheck", "US"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    ) as process:
        assert process.stdin is not None and process.stdout is not None
        assert process.stderr is not None
        process.stdout.close()
        # The command stops at the first failed write, so it may close its end first.
        with contextlib.suppress(OSError):
            process.stdin.write(b"90210\n" * 200_000)
            process.stdin.close()
        err = process.stderr.read()
        assert process.wait(timeout=60) == 1
    assert err == b""
