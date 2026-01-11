from __future__ import annotations

import shlex
from pathlib import Path

from langchain_core.tools import tool

from .sandbox import run_sandboxed


@tool
def git_diff(repo_root: str, args: str = "") -> str:
    """Run `git diff` in `repo_root` and return the output."""
    root = Path(repo_root).resolve()
    return run_sandboxed(f"git diff {args}".strip(), cwd=root)


@tool
def git_status(repo_root: str, porcelain: bool = True, untracked: bool = True) -> str:
    """Run `git status` in `repo_root` (porcelain by default) and return the output."""
    root = Path(repo_root).resolve()
    args: list[str] = []
    if porcelain:
        args.append("--porcelain")
    if not untracked:
        args.append("-uno")
    return run_sandboxed("git status " + " ".join(args), cwd=root)


@tool
def git_add(repo_root: str, paths: list[str] | str = ".") -> str:
    """Stage files with `git add` in `repo_root`."""
    root = Path(repo_root).resolve()
    path_list = [paths] if isinstance(paths, str) else paths
    quoted = " ".join(shlex.quote(p) for p in path_list) if path_list else "."
    return run_sandboxed(f"git add -- {quoted}".strip(), cwd=root)


@tool
def git_commit(repo_root: str, message: str, add_all: bool = False) -> str:
    """Create a git commit in `repo_root` with the given message (optionally add -A first)."""
    root = Path(repo_root).resolve()
    logs: list[str] = []
    if add_all:
        logs.append(run_sandboxed("git add -A", cwd=root))
    logs.append(run_sandboxed(f"git commit -m {shlex.quote(message)}", cwd=root))
    return "\n".join(logs)


@tool
def git_log(repo_root: str, max_count: int = 20, oneline: bool = True, path: str | None = None) -> str:
    """Show git log for `repo_root` (optionally for a specific path)."""
    root = Path(repo_root).resolve()
    args: list[str] = [f"-n {int(max_count)}"]
    if oneline:
        args.append("--oneline")
    if path:
        args.append("--")
        args.append(shlex.quote(path))
    return run_sandboxed("git log " + " ".join(args), cwd=root)


@tool
def git_branch_list(repo_root: str, all: bool = False) -> str:
    """List branches in `repo_root` (local by default, optionally include remotes)."""
    root = Path(repo_root).resolve()
    return run_sandboxed("git branch" + (" -a" if all else ""), cwd=root)


@tool
def git_checkout(repo_root: str, branch: str, create: bool = False) -> str:
    """Checkout a branch in `repo_root` (optionally create it with -b)."""
    root = Path(repo_root).resolve()
    flag = "-b " if create else ""
    return run_sandboxed(f"git checkout {flag}{shlex.quote(branch)}", cwd=root)


@tool
def git_remote_list(repo_root: str, verbose: bool = True) -> str:
    """List git remotes for `repo_root` (verbose by default)."""
    root = Path(repo_root).resolve()
    return run_sandboxed("git remote -v" if verbose else "git remote", cwd=root)


@tool
def git_prepare_pr(
    repo_root: str,
    branch: str,
    title: str,
    body: str = "",
    base: str = "main",
    ensure_branch: bool = True,
    require_clean: bool = True,
) -> str:
    """Prepare a branch for a PR and print next-step commands (does not push)."""
    root = Path(repo_root).resolve()

    logs: list[str] = []
    logs.append(run_sandboxed("git rev-parse --is-inside-work-tree", cwd=root))

    if ensure_branch:
        out = run_sandboxed(f"git checkout -b {shlex.quote(branch)}", cwd=root)
        logs.append(out)
        if "(exit=0)" not in out:
            logs.append(run_sandboxed(f"git checkout {shlex.quote(branch)}", cwd=root))

    status = run_sandboxed("git status --porcelain", cwd=root)
    logs.append(status)

    if require_clean and "(exit=0)" in status:
        lines = status.splitlines()
        dirty_lines = [ln for ln in lines[2:] if ln.strip()]
        if dirty_lines:
            return (
                "PR_PREP_FAILED=working_tree_not_clean\n"
                + "\n".join(logs)
                + "\n\n"
                + "Working tree has uncommitted changes. Commit or stash before preparing a PR."
            )

    remotes = run_sandboxed("git remote", cwd=root)
    logs.append(remotes)

    push_remote = "origin"
    cmd_lines = [
        "# Next commands to run (outside this tool if desired):",
        f"git checkout {shlex.quote(branch)}",
        "git status",
        f"git push -u {push_remote} {shlex.quote(branch)}",
        "# Then open a PR on your hosting provider (GitHub/GitLab/etc.)",
        f"# Base: {base}",
        f"# Title: {title}",
    ]
    if body.strip():
        cmd_lines.append(f"# Body: {body}")

    cmd_lines.extend(
        [
            "# If you have GitHub CLI installed and configured, you can run:",
            f"# gh pr create --base {shlex.quote(base)} --head {shlex.quote(branch)} --title {shlex.quote(title)} --body {shlex.quote(body)}",
        ]
    )

    header = "PR_PREPARED=true\n" + f"BRANCH={branch}\n" + f"BASE={base}\n"
    return header + "\n".join(logs) + "\n\n" + "\n".join(cmd_lines)

