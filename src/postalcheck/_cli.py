"""Command line: print the canonical form of each postal code, exit 1 if any is invalid."""

from __future__ import annotations

import argparse
import contextlib
import sys
from collections.abc import Sequence
from typing import TextIO

from ._core import example, normalize, supported_countries
from ._errors import InvalidPostalCodeError, UnknownCountryError

_DESCRIPTION = (
    "Print the canonical form of each postal code of COUNTRY, one per line. Invalid codes "
    "go to stderr and make the exit status 1. With no CODE, codes are read from stdin."
)


def _shown(text: str) -> str:
    # Echoed input is untrusted: keep it on one line and printable on any console.
    return "".join(c if " " <= c <= "~" else c.encode("unicode_escape").decode() for c in text)


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the command line and return the exit status (0 ok, 1 invalid, 2 usage)."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = argparse.ArgumentParser(prog="postalcheck", description=_DESCRIPTION)
    parser.add_argument("country", help="ISO 3166-1 alpha-2 code, such as GB or us")
    parser.add_argument("codes", nargs="*", metavar="CODE")
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            args = parser.parse_args(argv)
    except SystemExit as exit_:
        return 0 if exit_.code is None else int(exit_.code)
    try:
        example(args.country)
    except UnknownCountryError as error:
        stderr.write(f"postalcheck: {_shown(str(error))}\n")
        stderr.write(f"supported: {' '.join(supported_countries())}\n")
        return 2
    codes: list[str] = args.codes or [line.rstrip("\r\n") for line in stdin if line.strip()]
    status = 0
    for code in codes:
        try:
            stdout.write(normalize(args.country, code) + "\n")
        except InvalidPostalCodeError:
            stderr.write(f"invalid: {_shown(code)}\n")
            status = 1
    return status
