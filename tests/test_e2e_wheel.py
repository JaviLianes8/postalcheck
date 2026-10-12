"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with POSTALCHECK_E2E=1.
"""

from __future__ import annotations

import os
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("POSTALCHECK_E2E") != "1", reason="set POSTALCHECK_E2E=1 to build and install"
)

PROGRAM = r"""
import importlib.metadata, importlib.resources, pickle
import postalcheck
from postalcheck import InvalidPostalCodeError, UnknownCountryError
from postalcheck import example, is_valid, normalize, supported_countries

assert "site-packages" in postalcheck.__file__, postalcheck.__file__
assert importlib.metadata.version("postalcheck") == postalcheck.__version__
assert importlib.resources.files("postalcheck").joinpath("py.typed").is_file()
assert len(supported_countries()) == 182
assert normalize("UK", "sw1a1aa") == "SW1A 1AA"
assert normalize("LV", "1073") == "LV-1073"
assert normalize("JP", "\uff11\uff15\uff14\uff0d\uff10\uff10\uff12\uff13") == "154-0023"
assert example("IE") == "A65 F4E2"
for country, bad in (("US", "9-0-2-1-0"), ("NL", "1234 SS"), ("GB", "QQ1 1AA")):
    assert not is_valid(country, bad), bad
try:
    normalize("HK", "1")
except UnknownCountryError as error:
    assert pickle.loads(pickle.dumps(error)).has_postal_codes is False
else:
    raise AssertionError("HK accepted")
try:
    normalize("DE", "1011")
except InvalidPostalCodeError as error:
    assert (error.country, error.code) == ("DE", "1011")
print("e2e ok")
"""


def _run(*cmd: str | Path, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, check=False
    )


def test_installed_wheel_end_to_end(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run(sys.executable, "-m", "build", "--outdir", dist, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel,) = dist.glob("postalcheck-*.whl")
    (sdist,) = dist.glob("postalcheck-*.tar.gz")
    names = zipfile.ZipFile(wheel).namelist()
    assert "postalcheck/py.typed" in names
    assert not any(name.startswith("tests/") for name in names)
    sdist_listing = _run(sys.executable, "-m", "tarfile", "-l", sdist).stdout
    assert "IMPROVEMENTS-round" not in sdist_listing
    assert "tests/data/libaddressinput.jsonl" in sdist_listing

    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    bindir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    installed = _run(python, "-m", "pip", "install", "-q", wheel)
    assert installed.returncode == 0, installed.stderr

    # Run from an empty folder so the source tree cannot shadow the install.
    work = tmp_path / "work"
    work.mkdir()
    result = _run(python, "-I", "-c", PROGRAM, cwd=work)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "e2e ok"

    script = bindir / ("postalcheck.exe" if sys.platform == "win32" else "postalcheck")
    cli = _run(script, "gb", "sw1a1aa", "QQ1 1AA", cwd=work)
    assert (cli.returncode, cli.stdout, cli.stderr) == (1, "SW1A 1AA\n", "invalid: QQ1 1AA\n")
    unknown = _run(python, "-m", "postalcheck", "ZZ", cwd=work)
    assert unknown.returncode == 2
