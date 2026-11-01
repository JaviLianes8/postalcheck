"""Real-pipe CLI contracts shared by source and installed consumers."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path


async def check_streaming(
    command: list[str], cwd: Path | None, *, invalid_first: bool = False
) -> None:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("PYTHONUNBUFFERED", "PYTHONPATH")
    }
    process = await asyncio.create_subprocess_exec(
        *command,
        "US",
        cwd=cwd,
        env=env,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stdin is not None and process.stdout is not None and process.stderr is not None
    try:
        if invalid_first:
            process.stdin.write(b"bad\n")
            await process.stdin.drain()
            error = await asyncio.wait_for(process.stderr.readline(), timeout=5)
            assert error.rstrip(b"\r\n") == b"invalid postal code format"
        for code in (b"95014", b"12345"):
            process.stdin.write(code + b"\n")
            await process.stdin.drain()
            line = await asyncio.wait_for(process.stdout.readline(), timeout=5)
            assert line.rstrip(b"\r\n") == code
            assert process.returncode is None
        process.stdin.close()
        out, err = await asyncio.wait_for(process.communicate(), timeout=10)
        assert (process.returncode, out, err) == (int(invalid_first), b"", b"")
    finally:
        if process.returncode is None:
            process.kill()
        await process.communicate()
