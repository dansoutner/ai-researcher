from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from langchain_core.tools import tool

_MEMORY_STORE: Dict[str, Any] = {}

MEMORY_KEY_REPO_MAP = "repo_map"
MEMORY_KEY_FAILING_TESTS = "failing_tests"
MEMORY_KEY_LAST_ERROR = "last_error"
MEMORY_KEY_TODO_LIST = "todo_list"
MEMORY_KEY_CONTEXT = "context"


def _get_memory_file(repo_root: str) -> Path:
    return Path(repo_root).resolve() / ".agent_memory.json"


def _load_memory(repo_root: str) -> Dict[str, Any]:
    global _MEMORY_STORE
    mem_file = _get_memory_file(repo_root)

    disk_mem: Dict[str, Any] = {}
    if mem_file.exists():
        try:
            disk_mem = json.loads(mem_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass

    return {**disk_mem, **_MEMORY_STORE}


def _save_memory(repo_root: str, memory: Dict[str, Any]) -> None:
    mem_file = _get_memory_file(repo_root)
    try:
        mem_file.write_text(json.dumps(memory, indent=2, default=str), encoding="utf-8")
    except IOError:
        pass


def memory_set_internal(repo_root: str, key: str, value: str) -> str:
    global _MEMORY_STORE

    _MEMORY_STORE[key] = {"value": value, "updated_at": datetime.now().isoformat()}

    memory = _load_memory(repo_root)
    memory[key] = _MEMORY_STORE[key]
    _save_memory(repo_root, memory)

    return f"Stored '{key}' ({len(value)} chars)"


def memory_get_internal(repo_root: str, key: str) -> str:
    memory = _load_memory(repo_root)

    if key in memory:
        entry = memory[key]
        if isinstance(entry, dict) and "value" in entry:
            return entry["value"]
        return str(entry)

    return "(not found)"


@tool
def memory_set(repo_root: str, key: str, value: str) -> str:
    """Set a memory key/value for this repo (persisted to `.agent_memory.json`)."""
    return memory_set_internal(repo_root, key, value)


@tool
def memory_get(repo_root: str, key: str) -> str:
    """Get a memory value by key for this repo (from in-memory + `.agent_memory.json`)."""
    return memory_get_internal(repo_root, key)


@tool
def memory_list(repo_root: str) -> str:
    """List stored memory keys for this repo."""
    memory = _load_memory(repo_root)
    if not memory:
        return "(memory is empty)"

    lines = ["Key | Size | Updated", "-" * 50]
    for k in sorted(memory.keys()):
        entry = memory[k]
        if isinstance(entry, dict) and "value" in entry:
            size = len(str(entry["value"]))
            updated = entry.get("updated_at", "unknown")
        else:
            size = len(str(entry))
            updated = "unknown"
        lines.append(f"{k} | {size} chars | {updated}")

    return "\n".join(lines)


@tool
def memory_delete(repo_root: str, key: str) -> str:
    """Delete a memory key for this repo (both in-memory and persisted if present)."""
    global _MEMORY_STORE

    memory = _load_memory(repo_root)

    deleted = False
    if key in _MEMORY_STORE:
        del _MEMORY_STORE[key]
        deleted = True
    if key in memory:
        del memory[key]
        _save_memory(repo_root, memory)
        deleted = True

    return f"Deleted '{key}'" if deleted else f"Key '{key}' not found"


@tool
def memory_append(repo_root: str, key: str, value: str, separator: str = "\n") -> str:
    """Append text to a memory key's existing value (creates key if missing)."""
    existing = memory_get_internal(repo_root, key)
    new_value = value if existing == "(not found)" else existing + separator + value
    return memory_set_internal(repo_root, key, new_value)


@tool
def store_repo_map(repo_root: str, max_depth: int = 3, include_sizes: bool = False) -> str:
    """Compute a repository tree summary and store it under the `repo_map` memory key."""
    from datetime import datetime as _dt

    root = Path(repo_root).resolve()

    structure_lines: list[str] = []
    file_counts: Dict[str, int] = {}
    key_files: list[str] = []

    key_patterns = [
        "README*",
        "readme*",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "package.json",
        "Cargo.toml",
        "Makefile",
        "Dockerfile",
        "*.config.js",
        "*.config.ts",
        "__init__.py",
        "main.py",
        "app.py",
    ]

    def is_key_file(name: str) -> bool:
        import fnmatch

        return any(fnmatch.fnmatch(name, pat) for pat in key_patterns)

    def walk_dir(path: Path, depth: int = 0, prefix: str = ""):
        if depth > max_depth:
            return

        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return

        ignored = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            ".mypy_cache",
            ".ruff_cache",
            ".pytest_cache",
            "dist",
            "build",
            ".egg-info",
        }
        entries = [e for e in entries if e.name not in ignored]

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "

            if entry.is_dir():
                structure_lines.append(f"{prefix}{connector}{entry.name}/")
                extension = "    " if is_last else "│   "
                walk_dir(entry, depth + 1, prefix + extension)
            else:
                size_str = ""
                if include_sizes:
                    try:
                        size_str = f" ({entry.stat().st_size} B)"
                    except Exception:
                        pass

                structure_lines.append(f"{prefix}{connector}{entry.name}{size_str}")

                ext = entry.suffix.lower() or "(no ext)"
                file_counts[ext] = file_counts.get(ext, 0) + 1

                if is_key_file(entry.name):
                    key_files.append(str(entry.relative_to(root)))

    structure_lines.append(f"{root.name}/")
    walk_dir(root)

    repo_map_parts = [
        "# Repository Map",
        f"Generated: {_dt.now().isoformat()}",
        "",
        "## Structure",
        "```",
        "\n".join(structure_lines[:100]),
    ]

    if len(structure_lines) > 100:
        repo_map_parts.append(f"... ({len(structure_lines) - 100} more entries)")

    repo_map_parts.extend(["```", "", "## File Types"])

    for ext, count in sorted(file_counts.items(), key=lambda x: -x[1])[:10]:
        repo_map_parts.append(f"- {ext}: {count} files")

    if key_files:
        repo_map_parts.extend(["", "## Key Files"])
        for kf in key_files[:20]:
            repo_map_parts.append(f"- {kf}")

    repo_map = "\n".join(repo_map_parts)
    memory_set_internal(repo_root, MEMORY_KEY_REPO_MAP, repo_map)

    return f"Stored repo map ({len(structure_lines)} entries, {len(file_counts)} file types, {len(key_files)} key files)"


@tool
def store_test_results(repo_root: str, test_output: str) -> str:
    """Parse pytest output, store failing tests summary in memory, and return a status message."""
    lines = test_output.split("\n")

    failing_tests: list[dict[str, str]] = []
    current_failure: dict[str, str] | None = None

    for line in lines:
        if "FAILED" in line:
            match = re.search(r"FAILED\s+(\S+)", line)
            if match:
                failing_tests.append({"test": match.group(1), "error": ""})
                current_failure = failing_tests[-1]
        elif line.strip().startswith("E ") and current_failure:
            current_failure["error"] += line.strip()[2:] + "\n"
        elif "AssertionError" in line and current_failure:
            current_failure["error"] += line.strip() + "\n"
        elif any(err in line for err in ["Error:", "Exception:", "TypeError", "ValueError", "AttributeError"]):
            if current_failure:
                current_failure["error"] += line.strip() + "\n"

    if not failing_tests:
        if "passed" in test_output.lower() and "failed" not in test_output.lower():
            memory_set_internal(repo_root, MEMORY_KEY_FAILING_TESTS, "All tests passed!")
            return "All tests passed! Cleared failing tests from memory."

        return "No test failures detected in output."

    result_lines = [f"# Failing Tests ({len(failing_tests)} failures)", ""]
    for i, failure in enumerate(failing_tests, 1):
        result_lines.append(f"## {i}. {failure['test']}")
        if failure.get("error"):
            result_lines.append("```")
            result_lines.append(failure["error"].strip())
            result_lines.append("```")
        result_lines.append("")

    result = "\n".join(result_lines)
    memory_set_internal(repo_root, MEMORY_KEY_FAILING_TESTS, result)

    return f"Stored {len(failing_tests)} failing test(s) in memory"


@tool
def clear_memory(repo_root: str) -> str:
    """Clear all agent memory for this repo (in-memory and `.agent_memory.json` if present)."""
    global _MEMORY_STORE
    _MEMORY_STORE = {}

    mem_file = _get_memory_file(repo_root)
    if mem_file.exists():
        try:
            mem_file.unlink()
            return "Cleared all memory (in-memory and disk)"
        except IOError as e:
            return f"Cleared in-memory, but failed to delete disk file: {e}"

    return "Cleared all memory"

