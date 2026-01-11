from __future__ import annotations

import re
from pathlib import Path

from langchain_core.tools import tool

from .sandbox import run_sandboxed, safe_path


@tool
def read_file(repo_root: str, path: str) -> str:
    """Read a UTF-8 text file from within `repo_root` and return its contents."""
    p = safe_path(repo_root, path)
    return p.read_text(encoding="utf-8")


@tool
def write_file(repo_root: str, path: str, content: str) -> str:
    """Write UTF-8 text content to a file within `repo_root` (creating parent dirs)."""
    p = safe_path(repo_root, path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {path} ({len(content)} chars)"


@tool
def edit_file(repo_root: str, path: str, old_string: str, new_string: str) -> str:
    """Replace occurrences of old_string with new_string in a file within `repo_root`.

    This provides surgical edits for large files without rewriting the entire content.
    The old_string must exist in the file exactly as specified (including whitespace).
    Returns the number of replacements made or an error message.

    Args:
        repo_root: The root directory containing the file
        path: Relative path to the file from repo_root
        old_string: The exact string to find and replace
        new_string: The string to replace with

    Returns:
        A message indicating success with the number of replacements made
    """
    p = safe_path(repo_root, path)

    # Validate file exists
    if not p.exists():
        return f"Error: File '{path}' does not exist"

    if not p.is_file():
        return f"Error: '{path}' is not a file"

    try:
        # Read current content
        content = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: '{path}' is not a valid UTF-8 text file"
    except Exception as e:
        return f"Error reading '{path}': {str(e)}"

    # Validate old_string exists
    if old_string not in content:
        return f"Error: old_string not found in '{path}'. Please verify the exact string including whitespace."

    # Count occurrences for validation
    count = content.count(old_string)

    # Warn if multiple occurrences (but still proceed)
    if count > 1:
        warning = f"Warning: Found {count} occurrences of old_string. All will be replaced. "
    else:
        warning = ""

    # Perform replacement
    new_content = content.replace(old_string, new_string)

    try:
        # Write back atomically
        p.write_text(new_content, encoding="utf-8")
    except Exception as e:
        return f"Error writing to '{path}': {str(e)}"

    # Calculate changes
    old_lines = len(content.splitlines())
    new_lines = len(new_content.splitlines())
    line_diff = new_lines - old_lines

    result = f"{warning}Successfully replaced {count} occurrence(s) in '{path}'"
    if line_diff != 0:
        result += f" (lines: {old_lines} → {new_lines}, {line_diff:+d})"

    return result


@tool
def list_files(repo_root: str, path: str = ".", max_entries: int = 200) -> str:
    """Recursively list files under `path` (relative to `repo_root`), up to `max_entries`."""
    base = safe_path(repo_root, path)
    out: list[str] = []
    count = 0
    for p in sorted(base.rglob("*")):
        if count >= max_entries:
            out.append("... (truncated)")
            break
        if p.is_file():
            out.append(str(p.relative_to(Path(repo_root).resolve())))
            count += 1
    return "\n".join(out) if out else "(no files)"


@tool
def grep(repo_root: str, pattern: str, path: str = ".", flags: str = "") -> str:
    """Search for a regex `pattern` under `path` within `repo_root` and return matches."""
    root = Path(repo_root).resolve()
    base = safe_path(repo_root, path)

    try:
        cmd = f'rg -n {flags} -- "{pattern}" "{base}"'
        return run_sandboxed(cmd, cwd=root, validate=True)
    except Exception:
        rx = re.compile(pattern)
        hits: list[str] = []
        for f in base.rglob("*"):
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), start=1):
                if rx.search(line):
                    rel = f.relative_to(root)
                    hits.append(f"{rel}:{i}:{line}")
                    if len(hits) >= 200:
                        hits.append("... (truncated)")
                        return "\n".join(hits)
        return "\n".join(hits) if hits else "(no matches)"

