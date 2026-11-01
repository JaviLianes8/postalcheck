"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with POSTALCHECK_E2E=1.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

import pytest
from packaging.requirements import Requirement
from upgrade_program import CHECK_NEW_PICKLES, CHECK_OLD_PICKLES, DIFFERENCES, SNAPSHOT

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
else:
    raise AssertionError("invalid code accepted")
print("e2e ok")
"""


def _run(*cmd: str | Path, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, check=False, timeout=240
    )


@pytest.fixture(scope="module")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    folder = tmp_path_factory.mktemp("built")
    dist = folder / "dist"
    built = _run(sys.executable, "-m", "build", "--outdir", dist, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel_path,) = dist.glob("postalcheck-*.whl")
    (sdist,) = dist.glob("postalcheck-*.tar.gz")
    with zipfile.ZipFile(wheel_path) as archive:
        names = archive.namelist()
        assert "postalcheck/py.typed" in names
        assert any(name.endswith("/licenses/LICENSE") for name in names)
        assert all(
            name.startswith(("postalcheck/", "postalcheck-1.0.0.dist-info/")) for name in names
        )
        metadata = archive.read("postalcheck-1.0.0.dist-info/METADATA").decode()
        assert "Version: 1.0.0" in metadata
        assert "Development Status :: 5 - Production/Stable" in metadata
        for line in metadata.splitlines():
            if line.startswith("Requires-Dist:"):
                marker = Requirement(line.split(":", 1)[1].strip()).marker
                assert marker is not None and not marker.evaluate({"extra": ""})
    with tarfile.open(sdist) as archive:
        contents = [name.split("/", 1)[-1] for name in archive.getnames()]
    for required in ["LICENSE", "GUIDE.md", "tests/upstream/MANIFEST.json"]:
        assert required in contents
    for name in contents:
        assert not any(
            part in name
            for part in ["__pycache__", ".pyc", "CERT-", "IMPROVEMENTS", ".venv", "scratch"]
        )
        if name.startswith("tests/upstream/"):
            assert name == "tests/upstream/MANIFEST.json"
    return wheel_path


def test_installed_wheel_end_to_end(tmp_path: Path, wheel: Path) -> None:
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
    assert (cli.returncode, cli.stdout, cli.stderr) == (
        1,
        "SW1A 1AA\n",
        "invalid postal code format\n",
    )
    unknown = _run(python, "-m", "postalcheck", "ZZ", cwd=work)
    assert unknown.returncode == 2


@pytest.mark.skipif(os.environ.get("POSTALCHECK_PYPI") != "1", reason="set POSTALCHECK_PYPI=1")
def test_upgrade_from_the_live_pypi_release(tmp_path: Path, wheel: Path) -> None:
    env_dir = tmp_path / "upgrade"
    venv.create(env_dir, with_pip=True)
    bindir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    work = tmp_path / "consumer"
    work.mkdir()
    old = _run(python, "-m", "pip", "install", "--no-deps", "postalcheck==0.2.1")
    assert old.returncode == 0, old.stderr
    before = _run(python, "-I", "-c", SNAPSHOT, cwd=work)
    assert before.returncode == 0, before.stderr
    changes = _run(python, "-I", "-c", DIFFERENCES, cwd=work)
    assert changes.returncode == 0, changes.stderr
    cli = _run(python, "-I", "-m", "postalcheck", "US", "bad", cwd=work)
    assert (cli.returncode, cli.stderr) == (1, "invalid: bad\n")
    upgrade = _run(python, "-m", "pip", "install", "--no-deps", "--upgrade", wheel)
    assert upgrade.returncode == 0, upgrade.stderr
    after = _run(python, "-I", "-c", SNAPSHOT, cwd=work)
    assert after.returncode == 0, after.stderr
    assert before.stdout == after.stdout
    for program in [PROGRAM, DIFFERENCES, CHECK_OLD_PICKLES]:
        result = _run(python, "-I", "-c", program, cwd=work)
        assert result.returncode == 0, result.stderr
    script = bindir / ("postalcheck.exe" if sys.platform == "win32" else "postalcheck")
    cli = _run(script, "US", "bad", cwd=work)
    assert (cli.returncode, cli.stderr) == (1, "invalid postal code format\n")
    downgrade = _run(python, "-m", "pip", "install", "--no-deps", "postalcheck==0.2.1")
    assert downgrade.returncode == 0, downgrade.stderr
    compatible = _run(python, "-I", "-c", CHECK_NEW_PICKLES, cwd=work)
    assert compatible.returncode == 0, compatible.stderr
