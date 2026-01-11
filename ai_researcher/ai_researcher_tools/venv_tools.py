from __future__ import annotations

import shlex
from pathlib import Path

from langchain_core.tools import tool

from .memory_tools import memory_get_internal, memory_set_internal
from .sandbox import (
    MAX_TIMEOUT_S,
    build_sandbox_env,
    run_sandboxed_with_env,
    safe_path,
    run_sandboxed,
)

MEMORY_KEY_VENV_PATH = "venv_path"


def _is_probably_abs_path(s: str) -> bool:
    try:
        return bool(s) and Path(s).is_absolute()
    except Exception:
        return False


def _get_venv_path_from_memory(repo_root: str) -> Path | None:
    """Return stored venv path if present and exists; otherwise None."""
    raw = memory_get_internal(repo_root, MEMORY_KEY_VENV_PATH)
    if not raw or raw == "(not found)":
        return None

    candidate = raw.strip()

    if _is_probably_abs_path(candidate):
        p = Path(candidate)
        return p if p.exists() else None

    try:
        p = safe_path(repo_root, candidate)
    except Exception:
        return None

    return p if p.exists() else None


@tool
def create_venv(
    repo_root: str,
    venv_dir: str = ".venv",
    python: str = "python3",
    recreate: bool = False,
) -> str:
    """Create a virtualenv within repo_root and store its absolute path in memory.

    Notes:
    - Uses stdlib venv: `python3 -m venv ...`.
    - Does not activate the environment; use `run_in_venv` to run commands.
    """

    root = Path(repo_root).resolve()

    try:
        venv_path = safe_path(repo_root, venv_dir)
    except ValueError as e:
        return f"VENV_CREATE_FAILED=invalid_path\n{e}"

    if recreate and venv_path.exists():
        import shutil

        try:
            shutil.rmtree(venv_path)
        except Exception as e:
            return f"VENV_CREATE_FAILED=delete_failed\n{type(e).__name__}: {e}"

    venv_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = f"{shlex.quote(python)} -m venv {shlex.quote(str(venv_path))}"
    out = run_sandboxed(cmd, cwd=root, timeout_s=MAX_TIMEOUT_S, validate=True)

    if "(exit=0)" not in out:
        return "VENV_CREATE_FAILED=true\n" + out

    memory_set_internal(repo_root, MEMORY_KEY_VENV_PATH, str(venv_path))

    bin_dir = venv_path / "bin"
    py_bin = bin_dir / "python"

    return (
        "VENV_CREATED=true\n"
        + f"VENV_PATH={venv_path}\n"
        + (f"VENV_PYTHON={py_bin}\n" if py_bin.exists() else "")
        + out
    )


@tool
def run_in_venv(
    repo_root: str,
    cmd: str,
    timeout_s: int = 60,
    venv_path: str | None = None,
) -> str:
    """Run a sandboxed command with the configured virtualenv on PATH.

    If `venv_path` is not provided, uses the stored `venv_path` value from memory.
    """

    root = Path(repo_root).resolve()

    resolved_venv: Path | None
    if venv_path:
        try:
            p = Path(venv_path)
            resolved_venv = p if p.is_absolute() else safe_path(repo_root, venv_path)
        except Exception as e:
            return f"VENV_RUN_FAILED=invalid_venv_path\n{type(e).__name__}: {e}"
        if not resolved_venv.exists():
            return f"VENV_RUN_FAILED=venv_not_found\nVENV_PATH={resolved_venv}"
    else:
        resolved_venv = _get_venv_path_from_memory(repo_root)
        if not resolved_venv:
            return (
                "VENV_RUN_FAILED=no_venv_configured\n"
                "Create a venv first with create_venv(repo_root, venv_dir='.venv')"
            )

    bin_dir = resolved_venv / "bin"
    if not bin_dir.exists():
        return f"VENV_RUN_FAILED=invalid_venv\nMissing bin dir: {bin_dir}"

    extra_env = {"PATH": f"{bin_dir}:{build_sandbox_env(root).get('PATH', '')}"}

    return run_sandboxed_with_env(cmd, cwd=root, timeout_s=timeout_s, validate=True, extra_env=extra_env)
