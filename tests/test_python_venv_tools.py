from __future__ import annotations

from pathlib import Path

import pytest

from agent_tools import create_venv, run_in_venv


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


def test_create_venv_persists_path(repo: Path):
    out = create_venv.invoke({"repo_root": str(repo), "venv_dir": ".venv"})
    assert out.startswith("VENV_CREATED=true")
    assert (repo / ".venv").exists()
    assert (repo / ".agent_memory.json").exists()

    mem = (repo / ".agent_memory.json").read_text(encoding="utf-8")
    assert "venv_path" in mem


def test_run_in_venv_uses_venv_python(repo: Path):
    out_create = create_venv.invoke({"repo_root": str(repo), "venv_dir": ".venv"})
    assert out_create.startswith("VENV_CREATED=true")

    out = run_in_venv.invoke(
        {
            "repo_root": str(repo),
            "cmd": 'python -c "import sys; print(sys.prefix)"',
        }
    )
    assert "(exit=0)" in out
    assert str(repo / ".venv") in out


def test_run_in_venv_errors_when_missing(repo: Path):
    out = run_in_venv.invoke({"repo_root": str(repo), "cmd": "python -V"})
    assert out.startswith("VENV_RUN_FAILED=no_venv_configured")

