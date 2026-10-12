"""The README examples run and print what their comments say; docs and versions agree."""

from __future__ import annotations

import contextlib
import io
import re
import subprocess
import sys
from pathlib import Path

import postalcheck

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")


def _python_blocks() -> list[str]:
    return re.findall(r"```python\n(.*?)```", README, flags=re.DOTALL)


def test_every_readme_example_runs_and_prints_its_comment() -> None:
    checked = 0
    for block in _python_blocks():
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exec(compile(block, "README.md", "exec"), {"__name__": "readme"})
        expected = re.findall(r"^ *print\(.*\)  # (.+)$", block, flags=re.MULTILINE)
        assert expected, block
        assert out.getvalue().splitlines() == expected
        checked += len(expected)
    assert len(_python_blocks()) == 3
    assert checked >= 20


def test_the_command_line_example_prints_what_the_readme_shows() -> None:
    block = README.split("### Command line", 1)[1].split("```", 2)[1]
    command, *shown = block.strip().splitlines()
    args = command.split()[2:3] + re.findall(r'"([^"]+)"', command)
    result = subprocess.run(
        [sys.executable, "-m", "postalcheck", *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT / "src",
    )
    assert result.returncode == 1
    assert result.stdout.splitlines() + result.stderr.splitlines() == shown


def test_the_api_table_lists_every_public_name() -> None:
    table = README.split("## API", 1)[1].split("\n## ", 1)[0]
    for name in postalcheck.__all__:
        assert f"`{name}" in table, name


def test_the_country_table_matches_the_rules() -> None:
    section = README.split("### Countries\n", 1)[1].split("\n## ", 1)[0]
    table = section.strip().splitlines()[2:]
    cells = [cell.strip() for row in table for cell in row.strip("|").split("|")]
    pairs = [(c, e.strip("`")) for c, e in zip(cells[::2], cells[1::2], strict=True) if c]
    countries = postalcheck.supported_countries()
    assert pairs == [(c, postalcheck.example(c)) for c in countries]


def test_version_matches_pyproject() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, flags=re.MULTILINE)
    assert match is not None
    assert match.group(1) == postalcheck.__version__


def test_changelog_has_an_entry_for_this_version() -> None:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{postalcheck.__version__}]" in text


def test_no_em_dash_anywhere_in_the_tree() -> None:
    suffixes = {".py", ".md", ".toml", ".ps1", ".txt", ".jsonl", ".wiki"}
    for path in ROOT.rglob("*"):
        parts = path.relative_to(ROOT).parts
        if not path.is_file() or path.suffix not in suffixes:
            continue
        if any(part.startswith(".") or part == "__pycache__" for part in parts):
            continue
        assert chr(0x2014) not in path.read_text(encoding="utf-8"), path


def test_source_files_stay_under_two_hundred_lines() -> None:
    for path in [*ROOT.joinpath("src").rglob("*.py"), *ROOT.joinpath("tests").rglob("*.py")]:
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 200, path
