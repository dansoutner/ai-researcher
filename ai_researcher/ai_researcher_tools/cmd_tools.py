from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool

from .sandbox import CommandNotAllowedError, run_sandboxed


@tool
def apply_patch(repo_root: str, unified_diff: str, check: bool = False) -> str:
    """Apply a unified diff patch to the git checkout at `repo_root` (optionally --check)."""
    root = Path(repo_root).resolve()
    patch_path = root / ".agent_patch.diff"
    patch_path.write_text(unified_diff, encoding="utf-8")

    cmd = "git apply --check .agent_patch.diff" if check else "git apply .agent_patch.diff"
    result = run_sandboxed(cmd, cwd=root)

    if "(exit=0)" in result and not check:
        try:
            patch_path.unlink()
        except Exception:
            pass
    return result


@tool
def run_pytest(repo_root: str, args: str = "-q", timeout_s: int = 300) -> str:
    """Run pytest in `repo_root` with optional args/timeout and return output."""
    root = Path(repo_root).resolve()
    return run_sandboxed(f"pytest {args}".strip(), cwd=root, timeout_s=timeout_s)


@tool
def run_cmd(repo_root: str, cmd: str, timeout_s: int = 60) -> str:
    """Run a sandboxed shell command in `repo_root` (allowlist + blocked patterns)."""
    root = Path(repo_root).resolve()

    try:
        return run_sandboxed(cmd, cwd=root, timeout_s=timeout_s, validate=True)
    except CommandNotAllowedError as e:
        return f"$ {cmd}\n(BLOCKED: {e})"

