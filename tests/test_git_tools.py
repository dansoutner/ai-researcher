from __future__ import annotations

from pathlib import Path

import pytest

from agent_tools import (
    git_add,
    git_branch_list,
    git_checkout,
    git_commit,
    git_log,
    git_prepare_pr,
    git_status,
)


def _run(cmd: str, cwd: Path) -> None:
    import subprocess

    subprocess.run(cmd, cwd=str(cwd), shell=True, check=True, text=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run("git init", repo)
    # Ensure commits work even if user has no global git config
    _run("git config user.email test@example.com", repo)
    _run("git config user.name Test User", repo)

    (repo / "README.md").write_text("hi\n", encoding="utf-8")
    _run("git add README.md", repo)
    _run("git commit -m init", repo)

    return repo


def test_git_status_clean(repo: Path):
    out = git_status.invoke({"repo_root": str(repo)})
    assert "(exit=0)" in out
    lines = out.splitlines()
    assert len(lines) <= 3


def test_git_add_commit_and_log(repo: Path):
    (repo / "a.txt").write_text("a\n", encoding="utf-8")

    out_add = git_add.invoke({"repo_root": str(repo), "paths": "a.txt"})
    assert "(exit=0)" in out_add

    out_commit = git_commit.invoke({"repo_root": str(repo), "message": "add a"})
    assert "(exit=0)" in out_commit

    out_log = git_log.invoke({"repo_root": str(repo), "max_count": 5, "oneline": True})
    assert "add a" in out_log


def test_git_checkout_and_branch_list(repo: Path):
    out = git_checkout.invoke({"repo_root": str(repo), "branch": "feature/x", "create": True})
    assert "(exit=0)" in out

    branches = git_branch_list.invoke({"repo_root": str(repo)})
    assert "feature/x" in branches


def test_git_prepare_pr_requires_clean(repo: Path):
    (repo / "dirty.txt").write_text("x\n", encoding="utf-8")

    out = git_prepare_pr.invoke(
        {
            "repo_root": str(repo),
            "branch": "feature/pr",
            "title": "My PR",
            "body": "Body",
            "base": "main",
            "ensure_branch": True,
            "require_clean": True,
        }
    )
    assert out.startswith("PR_PREP_FAILED=")


def test_git_prepare_pr_success_when_clean(repo: Path):
    out = git_prepare_pr.invoke(
        {
            "repo_root": str(repo),
            "branch": "feature/pr2",
            "title": "My PR 2",
            "body": "Body",
            "base": "main",
            "ensure_branch": True,
            "require_clean": True,
        }
    )
    assert out.startswith("PR_PREPARED=true")
    assert "git push -u origin feature/pr2" in out

