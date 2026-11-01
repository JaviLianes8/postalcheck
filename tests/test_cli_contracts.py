"""Hand-written subprocess checks for streaming and malformed input recovery."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

import pytest
from cli_process import check_streaming

SRC = Path(__file__).resolve().parents[1] / "src"
CWD = SRC if SRC.exists() else None


@pytest.mark.parametrize("invalid_first", [False, True])
def test_results_arrive_before_stdin_eof(invalid_first: bool) -> None:
    asyncio.run(
        check_streaming([sys.executable, "-m", "postalcheck"], CWD, invalid_first=invalid_first)
    )


@pytest.mark.parametrize("argv", [False, True])
def test_multicharacter_width_folding_does_not_abort_batches(argv: bool) -> None:
    codes = ["95014", "\uffe3", "12345"]
    command = [sys.executable, "-m", "postalcheck", "US"]
    result = subprocess.run(
        command + codes if argv else command,
        input=None if argv else ("\n".join(codes) + "\n").encode(),
        capture_output=True,
        cwd=CWD,
        timeout=20,
    )
    assert result.returncode == 1
    assert result.stdout.splitlines() == [b"95014", b"12345"]
    assert result.stderr.splitlines() == [b"invalid postal code format"]


@pytest.mark.parametrize("argv", [False, True])
@pytest.mark.parametrize(
    ("country", "compact", "canonical"),
    [
        ("US", "95014", "95014"),
        ("US", "950141234", "95014-1234"),
        ("PL", "00950", "00-950"),
        ("CA", "K1A0B1", "K1A 0B1"),
        ("GB", "SW1A1AA", "SW1A 1AA"),
        ("JP", "1540023", "154-0023"),
        ("LV", "LV1073", "LV-1073"),
        ("FR", "75008", "75008"),
        ("AI", "AI2640", "2640"),
        ("OM", "PC133", "133"),
    ],
)
def test_embedded_width_expansions_are_rejected_in_batches(
    argv: bool, country: str, compact: str, canonical: str
) -> None:
    invalid = [compact[:cut] + "\uffe3" + compact[cut:] for cut in range(1, len(compact))]
    codes = [compact, *invalid, compact]
    command = [sys.executable, "-m", "postalcheck", country]
    result = subprocess.run(
        command + codes if argv else command,
        input=None if argv else ("\n".join(codes) + "\n").encode(),
        capture_output=True,
        cwd=CWD,
        timeout=20,
    )
    assert result.returncode == 1
    assert result.stdout.splitlines() == [canonical.encode()] * 2
    assert result.stderr.splitlines() == [b"invalid postal code format"] * len(invalid)


@pytest.mark.parametrize("bad", [b"\xff", b"\xc0\xaf", b"\xe2\x82", b"\xed\xa0\x80"])
def test_embedded_malformed_utf8_is_rejected(bad: bytes) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "postalcheck", "US"],
        input=b"95" + bad + b"014\n",
        capture_output=True,
        cwd=CWD,
        timeout=20,
    )
    assert (result.returncode, result.stdout) == (1, b"")
    assert result.stderr.splitlines() == [b"invalid postal code format"]
