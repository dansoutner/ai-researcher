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
def create_dir(repo_root: str, path: str) -> str:
    """Create a directory (and all parent directories) within `repo_root`.

    Args:
        repo_root: The root directory
        path: Relative path to the directory to create

    Returns:
        A success message or error if the operation fails
    """
    p = safe_path(repo_root, path)
    try:
        p.mkdir(parents=True, exist_ok=True)
        return f"Created directory '{path}'"
    except Exception as e:
        return f"Error creating directory '{path}': {str(e)}"


@tool
def list_dir(repo_root: str, path: str = ".") -> str:
    """List the contents of a directory within `repo_root` (non-recursive).

    Shows files and subdirectories with type indicators (/ for dirs, * for executables).

    Args:
        repo_root: The root directory
        path: Relative path to the directory to list (default: current directory)

    Returns:
        A formatted listing of directory contents
    """
    p = safe_path(repo_root, path)

    if not p.exists():
        return f"Error: Directory '{path}' does not exist"

    if not p.is_dir():
        return f"Error: '{path}' is not a directory"

    try:
        entries = sorted(p.iterdir())
        if not entries:
            return "(empty directory)"

        lines = []
        for entry in entries:
            rel_path = entry.name
            if entry.is_dir():
                lines.append(f"{rel_path}/")
            elif entry.is_file():
                # Check if file is executable
                if entry.stat().st_mode & 0o111:
                    lines.append(f"{rel_path}*")
                else:
                    lines.append(rel_path)
            else:
                lines.append(f"{rel_path} (special)")

        return "\n".join(lines)
    except Exception as e:
        return f"Error listing directory '{path}': {str(e)}"


@tool
def remove_dir(repo_root: str, path: str, recursive: bool = False) -> str:
    """Remove a directory within `repo_root`.

    Args:
        repo_root: The root directory
        path: Relative path to the directory to remove
        recursive: If True, remove directory and all contents; if False, only remove if empty

    Returns:
        A success message or error if the operation fails
    """
    p = safe_path(repo_root, path)

    if not p.exists():
        return f"Error: Directory '{path}' does not exist"

    if not p.is_dir():
        return f"Error: '{path}' is not a directory"

    try:
        if recursive:
            import shutil
            shutil.rmtree(p)
            return f"Removed directory '{path}' and all contents recursively"
        else:
            p.rmdir()
            return f"Removed empty directory '{path}'"
    except OSError as e:
        if not recursive and any(p.iterdir()):
            return f"Error: Directory '{path}' is not empty. Use recursive=True to remove with contents."
        return f"Error removing directory '{path}': {str(e)}"
    except Exception as e:
        return f"Error removing directory '{path}': {str(e)}"


@tool
def dir_exists(repo_root: str, path: str) -> str:
    """Check if a directory exists within `repo_root`.

    Args:
        repo_root: The root directory
        path: Relative path to check

    Returns:
        A message indicating whether the path exists and if it's a directory
    """
    p = safe_path(repo_root, path)

    if not p.exists():
        return f"'{path}' does not exist"
    elif p.is_dir():
        return f"'{path}' exists and is a directory"
    elif p.is_file():
        return f"'{path}' exists but is a file, not a directory"
    else:
        return f"'{path}' exists but is neither a file nor a directory"


@tool
def move_path(repo_root: str, src_path: str, dst_path: str) -> str:
    """Move or rename a file or directory within `repo_root`.

    Args:
        repo_root: The root directory
        src_path: Relative path to the source file or directory
        dst_path: Relative path to the destination

    Returns:
        A success message or error if the operation fails
    """
    src = safe_path(repo_root, src_path)
    dst = safe_path(repo_root, dst_path)

    if not src.exists():
        return f"Error: Source '{src_path}' does not exist"

    if dst.exists():
        return f"Error: Destination '{dst_path}' already exists"

    try:
        # Ensure destination parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)

        item_type = "directory" if src.is_dir() else "file"
        return f"Moved {item_type} from '{src_path}' to '{dst_path}'"
    except Exception as e:
        return f"Error moving '{src_path}' to '{dst_path}': {str(e)}"


@tool
def copy_path(repo_root: str, src_path: str, dst_path: str) -> str:
    """Copy a file or directory within `repo_root`.

    Args:
        repo_root: The root directory
        src_path: Relative path to the source file or directory
        dst_path: Relative path to the destination

    Returns:
        A success message or error if the operation fails
    """
    import shutil

    src = safe_path(repo_root, src_path)
    dst = safe_path(repo_root, dst_path)

    if not src.exists():
        return f"Error: Source '{src_path}' does not exist"

    if dst.exists():
        return f"Error: Destination '{dst_path}' already exists"

    try:
        # Ensure destination parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        if src.is_dir():
            shutil.copytree(src, dst)
            return f"Copied directory from '{src_path}' to '{dst_path}'"
        else:
            shutil.copy2(src, dst)
            return f"Copied file from '{src_path}' to '{dst_path}'"
    except Exception as e:
        return f"Error copying '{src_path}' to '{dst_path}': {str(e)}"


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


@tool
def grep_search(
    repo_root: str,
    query: str,
    path: str = ".",
    case_sensitive: bool = False,
    max_results: int = 200,
) -> str:
    """Search for text in files within a directory/file and its subdirectories.

    This tool searches for the exact text query in all files under the specified path.
    If path is a file, searches only that file. If path is a directory, searches all files recursively.
    Returns matching lines with file names and line numbers.

    Args:
        repo_root: The root directory
        query: The text string to search for
        path: Relative path to search within (can be a file or directory; default: current directory)
        case_sensitive: If True, search is case-sensitive; if False (default), case-insensitive
        max_results: Maximum number of matching lines to return (default: 200)

    Returns:
        A formatted list of matches showing file:line_number:matching_line
        or "(no matches)" if nothing is found

    Example:
        grep_search("/path/to/repo", "def my_function", "src", case_sensitive=True)
        Returns lines like: src/module.py:42:def my_function(arg1, arg2):
    """
    root = Path(repo_root).resolve()
    base = safe_path(repo_root, path)

    if not base.exists():
        return f"Error: Path '{path}' does not exist"

    # Handle both files and directories
    is_single_file = base.is_file()

    # Try using ripgrep (rg) first for better performance
    try:
        flags = "-n"  # Show line numbers
        if not case_sensitive:
            flags += " -i"  # Case-insensitive search
        flags += f" -m {max_results}"  # Limit results

        # Use fixed strings mode (not regex) for exact text search
        cmd = f'rg {flags} -F -- "{query}" "{base}"'
        result = run_sandboxed(cmd, cwd=root, validate=True)

        # Make paths relative to repo_root
        lines = result.splitlines()
        adjusted_lines = []
        for line in lines[:max_results]:
            adjusted_lines.append(line)

        if len(lines) > max_results:
            adjusted_lines.append(f"... (showing first {max_results} of {len(lines)} matches)")

        return "\n".join(adjusted_lines) if adjusted_lines else "(no matches)"

    except Exception:
        # Fallback to pure Python implementation if ripgrep is not available
        hits: list[str] = []
        search_query = query if case_sensitive else query.lower()

        try:
            # Handle single file vs directory
            if is_single_file:
                files_to_search = [base]
            else:
                files_to_search = sorted(base.rglob("*"))

            for f in files_to_search:
                if not f.is_file():
                    continue

                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                for i, line in enumerate(text.splitlines(), start=1):
                    search_line = line if case_sensitive else line.lower()
                    if search_query in search_line:
                        rel = f.relative_to(root)
                        hits.append(f"{rel}:{i}:{line}")

                        if len(hits) >= max_results:
                            hits.append(f"... (truncated at {max_results} results)")
                            return "\n".join(hits)

            return "\n".join(hits) if hits else "(no matches)"

        except Exception as e:
            return f"Error during search: {str(e)}"



