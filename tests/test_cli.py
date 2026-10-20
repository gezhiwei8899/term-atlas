import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts._lib import REPO


@pytest.fixture
def checkout(tmp_path):
    for directory in ["scripts", "schemas", "data", "pending", "examples/data"]:
        shutil.copytree(REPO / directory, tmp_path / directory)
    return tmp_path


def run(checkout: Path, command: str, *args):
    return subprocess.run(
        [sys.executable, str(checkout / "scripts" / command), *args],
        cwd=checkout.parent,  # Scripts must work outside the repository's working directory.
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_smoke(checkout):
    for command, args in [
        ("validate.py", ["--examples"]),
        ("format.py", ["--check"]),
        ("build.py", []),
    ]:
        result = run(checkout, command, *args)
        assert result.returncode == 0, result.stdout + result.stderr
    assert (checkout / "dist/manifest.json").exists()


def test_cli_invalid_input_fails_without_traceback(checkout):
    (checkout / "data/sensitive/zh.jsonl").write_text("not json\n", encoding="utf-8")
    for command in ["validate.py", "build.py", "format.py"]:
        result = run(checkout, command)
        assert result.returncode != 0
        assert "zh.jsonl:1:" in result.stdout
        assert "Traceback" not in result.stderr
    assert not (checkout / "dist").exists()


def test_cli_format_check_and_fix_are_idempotent(checkout):
    path = checkout / "examples/data/sensitive/en.jsonl"
    path.write_text(path.read_text("utf-8").replace('":', '": '), encoding="utf-8")
    assert run(checkout, "format.py", "--check").returncode == 1
    assert run(checkout, "format.py").returncode == 0
    assert run(checkout, "format.py", "--check").returncode == 0


def test_cli_strict_warnings(checkout, term, write):
    import copy

    term.update(term="TEST", language="en", aliases=[])
    other = copy.deepcopy(term)
    other.update(id="st_d4d4c421-158f-402e-8364-14bbdb2b7fb9", term="test")
    write(checkout / "data", "sensitive/en.jsonl", term, other)
    assert run(checkout, "validate.py").returncode == 0
    result = run(checkout, "validate.py", "--strict")
    assert result.returncode == 1
    assert "warning:" in result.stdout
