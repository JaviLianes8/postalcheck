"""Real-pipe CLI contracts shared by source and installed consumers."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path


async def check_streaming(command: list[str], cwd: Path | None) -> None:
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
    assert process.stdin is not None and process.stdout is not None
    try:
        for code in (b"95014", b"12345"):
            process.stdin.write(code + b"\n")
            await process.stdin.drain()
            line = await asyncio.wait_for(process.stdout.readline(), timeout=5)
            assert line.rstrip(b"\r\n") == code
            assert process.returncode is None
        process.stdin.close()
        out, err = await asyncio.wait_for(process.communicate(), timeout=10)
        assert (process.returncode, out, err) == (0, b"", b"")
    finally:
        if process.returncode is None:
            process.kill()
        await process.communicate()
