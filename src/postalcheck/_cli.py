"""Command line: print the canonical form of each postal code, exit 1 if any is invalid."""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import sys
from collections.abc import Iterable, Iterator, Sequence
from typing import TextIO

from ._core import example, normalize, supported_countries
from ._errors import InvalidPostalCodeError, UnknownCountryError

_DESCRIPTION = (
    "Print the canonical form of each postal code of COUNTRY, one per line. Invalid codes "
    "go to stderr and make the exit status 1. With no CODE, codes are read from stdin "
    "as UTF-8."
)


def _shown(text: str) -> str:
    # Echoed input is untrusted: keep it on one line and printable on any console, and
    # escape the backslash too so that an escape sequence and its spelling differ.
    return "".join(
        c if " " <= c <= "~" and c != "\\" else c.encode("unicode_escape").decode() for c in text
    )


def _system_stdin() -> TextIO:
    # The console code page (cp1252 on many Windows machines) would garble UTF-8 input;
    # utf-8-sig also drops the byte order mark that Windows editors write.
    buffer = getattr(sys.stdin, "buffer", None)
    if buffer is None:
        return sys.stdin
    return io.TextIOWrapper(buffer, encoding="utf-8-sig", errors="replace")


def _lines(stream: Iterable[str]) -> Iterator[str]:
    for line in stream:
        if line.strip():
            yield line.rstrip("\r\n")


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the command line and return the exit status (0 ok, 1 invalid, 2 usage)."""
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
    codes: Iterable[str] = args.codes or _lines(stdin or _system_stdin())
    status = 0
    try:
        for code in codes:
            try:
                stdout.write(normalize(args.country, code) + "\n")
            except InvalidPostalCodeError:
                stderr.write(f"invalid: {_shown(code)}\n")
                status = 1
        stdout.flush()
    except OSError:
        # The reader went away (head, a closed pager): stop quietly, as Unix tools do, and
        # point stdout at devnull so the final flush at exit does not fail again.
        if stdout is sys.stdout:
            with contextlib.suppress(OSError, ValueError):
                os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 1
    return status
