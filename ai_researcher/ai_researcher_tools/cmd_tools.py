from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict

from langchain_core.tools import tool

from .sandbox import CommandNotAllowedError, run_sandboxed, build_sandbox_env


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


@tool
def run_terminal_command(
    repo_root: str, cmd: str, is_background: bool = False, timeout_s: int = 60
) -> str:
    """Run a terminal command in `repo_root`, optionally as a background process.

    Args:
        repo_root: The root directory to run the command in
        cmd: The command to execute
        is_background: If True, runs command in background (for servers, watch mode, etc.)
        timeout_s: Maximum execution time in seconds (ignored for background processes)

    Returns:
        Command output or background process ID
    """
    root = Path(repo_root).resolve()

    if is_background:
        # Start background process
        env = build_sandbox_env(root)
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(root),
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            return f"$ {cmd}\n(Background process started, PID={proc.pid})"
        except Exception as e:
            return f"$ {cmd}\n(ERROR starting background process: {type(e).__name__}: {e})"
    else:
        # Run synchronously
        try:
            return run_sandboxed(cmd, cwd=root, timeout_s=timeout_s, validate=True)
        except CommandNotAllowedError as e:
            return f"$ {cmd}\n(BLOCKED: {e})"


@tool
def get_errors(repo_root: str, file_paths: list[str]) -> str:
    """Get Python compile/lint errors for specified files.

    Args:
        repo_root: The root directory of the repository
        file_paths: List of relative file paths to check for errors

    Returns:
        Compilation and linting errors found in the files
    """
    root = Path(repo_root).resolve()
    errors: Dict[str, list[str]] = {}

    for file_path in file_paths:
        file_full_path = root / file_path
        if not file_full_path.exists():
            errors[file_path] = [f"File not found: {file_path}"]
            continue

        if not file_full_path.suffix == ".py":
            errors[file_path] = [f"Not a Python file: {file_path}"]
            continue

        file_errors = []

        # Check for syntax errors (compile check)
        try:
            with open(file_full_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
        except SyntaxError as e:
            file_errors.append(
                f"SyntaxError: {e.msg} at line {e.lineno}, col {e.offset}"
            )
        except Exception as e:
            file_errors.append(f"CompileError: {type(e).__name__}: {e}")

        # Run ruff for linting (if available)
        ruff_result = run_sandboxed(
            f"ruff check {file_path}",
            cwd=root,
            timeout_s=30,
            validate=False
        )
        if "(exit=0)" not in ruff_result or "error" in ruff_result.lower():
            # Extract relevant error lines
            lines = ruff_result.split('\n')
            relevant_lines = [
                line for line in lines
                if file_path in line or 'error' in line.lower() or line.strip().startswith('-')
            ]
            if relevant_lines:
                file_errors.append("Ruff linting:\n" + "\n".join(relevant_lines))

        # Run mypy for type checking (if available)
        mypy_result = run_sandboxed(
            f"mypy {file_path} --no-error-summary",
            cwd=root,
            timeout_s=30,
            validate=False
        )
        if "(exit=0)" not in mypy_result:
            lines = mypy_result.split('\n')
            relevant_lines = [
                line for line in lines
                if file_path in line or 'error:' in line.lower()
            ]
            if relevant_lines:
                file_errors.append("MyPy type checking:\n" + "\n".join(relevant_lines))

        if file_errors:
            errors[file_path] = file_errors

    if not errors:
        return f"No errors found in {len(file_paths)} file(s)"

    # Format output
    output = []
    for file_path, file_errors in errors.items():
        output.append(f"\n=== {file_path} ===")
        for error in file_errors:
            output.append(error)

    return "\n".join(output)



