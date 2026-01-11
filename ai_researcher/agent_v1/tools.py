from __future__ import annotations
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Set, List

from langchain_core.tools import tool

# ============================================================================
# SANDBOX CONFIGURATION
# ============================================================================

# Allowlisted command prefixes (base commands that are permitted)
ALLOWED_COMMANDS: Set[str] = {
    # Version control
    "git",
    # Python tooling
    "python", "python3", "pip", "pip3", "uv",
    "pytest", "mypy", "ruff", "black", "isort", "flake8", "pylint",
    # Build tools
    "make", "cargo", "npm", "npx", "node", "yarn", "pnpm",
    # File inspection (read-only)
    "cat", "head", "tail", "less", "more", "wc", "diff",
    "ls", "find", "tree", "file", "stat",
    "grep", "egrep", "fgrep", "rg", "ag", "ack",
    # Text processing
    "sed", "awk", "cut", "sort", "uniq", "tr", "jq", "yq",
    # Archive (read)
    "tar", "unzip", "gzip", "gunzip",
    # Misc safe
    "echo", "printf", "true", "false", "test", "expr",
    "date", "env", "printenv", "which", "whereis", "type",
    "pwd", "basename", "dirname", "realpath",
}

# Patterns that are ALWAYS blocked (security risks)
BLOCKED_PATTERNS: List[re.Pattern] = [
    re.compile(r'\brm\s+-rf\s+/', re.IGNORECASE),           # rm -rf /
    re.compile(r'\brm\s+(-[a-z]*f[a-z]*\s+)?/'),            # rm with /
    re.compile(r'>\s*/dev/sd[a-z]'),                        # write to disk
    re.compile(r'\bdd\b.*of=/dev/'),                        # dd to device
    re.compile(r'\bmkfs\b'),                                # format filesystem
    re.compile(r'\b(sudo|su|doas)\b'),                      # privilege escalation
    re.compile(r'\bchmod\s+[0-7]*777\b'),                   # world-writable
    re.compile(r'\bchown\b.*root'),                         # chown to root
    re.compile(r'\b(curl|wget|nc|netcat|ncat)\b'),          # network tools
    re.compile(r'\b(ssh|scp|rsync|ftp|sftp|telnet)\b'),     # remote access
    re.compile(r'\beval\b'),                                # eval injection
    re.compile(r'`.*`'),                                    # command substitution
    re.compile(r'\$\(.*\)'),                                # command substitution
    re.compile(r'\|\s*sh\b'),                               # pipe to shell
    re.compile(r'\|\s*bash\b'),                             # pipe to bash
    re.compile(r'\|\s*zsh\b'),                              # pipe to zsh
    re.compile(r';\s*sh\b'),                                # chain to shell
    re.compile(r'&&\s*sh\b'),                               # chain to shell
    re.compile(r'\bexport\b.*\bPATH\b'),                    # PATH manipulation
    re.compile(r'\bsource\b'),                              # source scripts
    re.compile(r'\b\.\s+/'),                                # source with .
    re.compile(r'/etc/(passwd|shadow|sudoers)'),            # sensitive files
    re.compile(r'~/.ssh'),                                  # SSH keys
    re.compile(r'\bkill\b.*-9'),                            # force kill
    re.compile(r'\bpkill\b'),                               # process kill
    re.compile(r'\bkillall\b'),                             # kill all
    re.compile(r'\bnohup\b'),                               # background persistence
    re.compile(r'&\s*$'),                                   # background execution
    re.compile(r'\bdisown\b'),                              # disown process
]

# Maximum command timeout (seconds)
MAX_TIMEOUT_S = 300
DEFAULT_TIMEOUT_S = 60

# Environment variables to disable/restrict network access
SANDBOX_ENV_OVERRIDES = {
    "http_proxy": "http://0.0.0.0:0",
    "https_proxy": "http://0.0.0.0:0",
    "HTTP_PROXY": "http://0.0.0.0:0",
    "HTTPS_PROXY": "http://0.0.0.0:0",
    "no_proxy": "",
    "NO_PROXY": "",
    # Disable pip network access
    "PIP_NO_INDEX": "1",
    # Disable npm network
    "NPM_CONFIG_OFFLINE": "true",
}


class CommandNotAllowedError(Exception):
    """Raised when a command is not in the allowlist or matches a blocked pattern."""
    pass


def _extract_base_command(cmd: str) -> str:
    """Extract the base command from a shell command string."""
    cmd = cmd.strip()

    # Handle env prefix: env VAR=val cmd ...
    if cmd.startswith("env "):
        parts = cmd.split()
        for i, part in enumerate(parts[1:], 1):
            if "=" not in part and not part.startswith("-"):
                cmd = " ".join(parts[i:])
                break

    # Get first word (the command)
    try:
        tokens = shlex.split(cmd)
        if tokens:
            base = os.path.basename(tokens[0])
            # Handle python3.11 -> python3
            if base.startswith("python3."):
                return "python3"
            if base.startswith("python2."):
                return "python"
            return base
    except ValueError:
        # shlex failed, try simple split
        pass

    # Fallback: first whitespace-separated token
    first = cmd.split()[0] if cmd.split() else ""
    return os.path.basename(first)


def _validate_command(cmd: str, repo_root: Path) -> None:
    """
    Validate a command against security rules.
    Raises CommandNotAllowedError if the command is not permitted.
    """
    # Check blocked patterns first
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(cmd):
            raise CommandNotAllowedError(
                f"Command blocked by security pattern: {pattern.pattern!r}"
            )

    # Check allowlist
    base_cmd = _extract_base_command(cmd)
    if base_cmd not in ALLOWED_COMMANDS:
        raise CommandNotAllowedError(
            f"Command '{base_cmd}' is not in the allowlist. "
            f"Allowed: {sorted(ALLOWED_COMMANDS)}"
        )

    # Check for path escapes in arguments
    repo_str = str(repo_root.resolve())
    try:
        tokens = shlex.split(cmd)
        for token in tokens[1:]:  # skip command itself
            # Check if it looks like an absolute path outside repo
            if token.startswith("/") and not token.startswith(repo_str):
                # Allow some safe system paths
                safe_prefixes = ("/dev/null", "/tmp", "/usr/bin", "/usr/local/bin")
                if not any(token.startswith(p) for p in safe_prefixes):
                    raise CommandNotAllowedError(
                        f"Path '{token}' is outside the repository. "
                        f"Commands must operate within: {repo_str}"
                    )
            # Check for .. escapes
            if ".." in token:
                resolved = (repo_root / token).resolve()
                if not str(resolved).startswith(repo_str):
                    raise CommandNotAllowedError(
                        f"Path '{token}' escapes the repository via '..'"
                    )
    except ValueError:
        pass  # shlex parse error, continue with other checks


def _build_sandbox_env(repo_root: Path) -> dict:
    """Build a sandboxed environment for command execution."""
    env = os.environ.copy()

    # Apply sandbox overrides (network blocking, etc.)
    env.update(SANDBOX_ENV_OVERRIDES)

    # Restrict PATH to common safe locations
    safe_paths = [
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/local/sbin",
        "/usr/sbin",
        "/sbin",
    ]
    # Add common tool paths
    home = os.path.expanduser("~")
    safe_paths.extend([
        f"{home}/.local/bin",
        f"{home}/.cargo/bin",
        f"{home}/.pyenv/shims",
        f"{home}/.nvm/versions/node/*/bin",  # won't expand but that's ok
    ])
    # Keep existing PATH entries that are in safe locations or repo
    existing = env.get("PATH", "").split(":")
    filtered = [p for p in existing if any(p.startswith(s.rstrip("*")) for s in safe_paths)]
    # Add repo's venv if present
    venv_bin = repo_root / ".venv" / "bin"
    if venv_bin.exists():
        filtered.insert(0, str(venv_bin))

    env["PATH"] = ":".join(filtered) if filtered else "/usr/bin:/bin"

    # Set restrictive umask via environment (some tools respect this)
    env["UMASK"] = "077"

    return env


def _run_sandboxed(
    cmd: str,
    cwd: Path,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    validate: bool = True
) -> str:
    """
    Run a command in a sandboxed environment.

    Security measures:
    - Command allowlisting
    - Blocked pattern detection
    - Path escape prevention
    - Network access disabled via proxy env vars
    - Timeout enforcement
    - Restricted PATH
    """
    # Enforce maximum timeout
    timeout_s = min(timeout_s, MAX_TIMEOUT_S)

    # Validate command if requested
    if validate:
        _validate_command(cmd, cwd)

    # Build sandboxed environment
    env = _build_sandbox_env(cwd)

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout_s,
            env=env,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return f"$ {cmd}\n(exit={proc.returncode})\n{out}"
    except subprocess.TimeoutExpired:
        return f"$ {cmd}\n(TIMEOUT after {timeout_s}s)"
    except Exception as e:
        return f"$ {cmd}\n(ERROR: {type(e).__name__}: {e})"


def _safe_path(repo_root: str, rel_path: str) -> Path:
    root = Path(repo_root).resolve()
    p = (root / rel_path).resolve()
    if root not in p.parents and p != root:
        raise ValueError("Path escapes repo_root")
    return p


def _run_internal(cmd: str, cwd: Path, timeout_s: int = 120) -> str:
    """
    Internal command runner for TRUSTED commands only (e.g., git init in create_project).
    Does NOT apply sandbox validation - use only for known-safe internal operations.
    """
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout_s,
        env={**os.environ},
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return f"$ {cmd}\n(exit={proc.returncode})\n{out}"


def _run(cmd: str, cwd: Path, timeout_s: int = 120) -> str:
    """Run a command with sandbox validation."""
    return _run_sandboxed(cmd, cwd, timeout_s, validate=True)

@tool
def create_project(base_dir: str, project_name: str) -> str:
    """
    Create a new Python project folder under base_dir and initialize a git repo.

    Returns a machine-readable line:
      REPO_ROOT=<absolute_path>
    plus logs.

    Notes:
    - Does not force an initial commit (git may lack user.name/email).
    """
    base = Path(base_dir).expanduser().resolve()
    repo = (base / project_name).resolve()
    repo.mkdir(parents=True, exist_ok=True)

    # basic structure
    (repo / "src" / project_name).mkdir(parents=True, exist_ok=True)
    (repo / "tests").mkdir(parents=True, exist_ok=True)

    (repo / "README.md").write_text(
        f"# {project_name}\n\nGenerated by the coding agent.\n",
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text(
        "\n".join([
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            ".venv/",
            "dist/",
            "build/",
            "*.egg-info/",
            ".DS_Store",
        ]) + "\n",
        encoding="utf-8",
    )

    (repo / "pyproject.toml").write_text(
        f"""\
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
""",
        encoding="utf-8",
    )

    # a tiny module + test
    (repo / "src" / project_name / "__init__.py").write_text(
        "__all__ = ['add']\n\nfrom .core import add\n",
        encoding="utf-8",
    )
    (repo / "src" / project_name / "core.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_core.py").write_text(
        f"from {project_name} import add\n\n\ndef test_add():\n    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )

    logs = []
    logs.append(_run_internal("git init", cwd=repo))
    logs.append(_run_internal("git status --porcelain", cwd=repo))

    return "REPO_ROOT=" + str(repo) + "\n" + "\n".join(logs)

@tool
def read_file(repo_root: str, path: str) -> str:
    """Read a text file relative to repo_root."""
    p = _safe_path(repo_root, path)
    return p.read_text(encoding="utf-8")

@tool
def write_file(repo_root: str, path: str, content: str) -> str:
    """Write a text file relative to repo_root (creates parents)."""
    p = _safe_path(repo_root, path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {path} ({len(content)} chars)"

@tool
def list_files(repo_root: str, path: str = ".", max_entries: int = 200) -> str:
    """List files under a directory (relative to repo_root)."""
    base = _safe_path(repo_root, path)
    out = []
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
    """
    Grep/ripgrep a pattern in repo_root/path.
    flags: pass extra rg flags like "-n -S" (default includes line numbers).
    Falls back to a simple Python search if rg isn't available.
    """
    root = Path(repo_root).resolve()
    base = _safe_path(repo_root, path)

    # try ripgrep
    try:
        cmd = f'rg -n {flags} -- "{pattern}" "{base}"'
        return _run(cmd, cwd=root)
    except Exception:
        # fallback
        rx = re.compile(pattern)
        hits = []
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
def git_diff(repo_root: str, args: str = "") -> str:
    """
    Show git diff. args examples:
      "" (working tree)
      "--staged"
      "HEAD~1..HEAD"
    """
    root = Path(repo_root).resolve()
    return _run(f"git diff {args}".strip(), cwd=root)


@tool
def git_status(repo_root: str, porcelain: bool = True, untracked: bool = True) -> str:
    """Show git status for the repo.

    Args:
        porcelain: if True, uses --porcelain for machine-readable output.
        untracked: if False, uses -uno to hide untracked files.
    """
    root = Path(repo_root).resolve()
    args = []
    if porcelain:
        args.append("--porcelain")
    if not untracked:
        args.append("-uno")
    return _run("git status " + " ".join(args), cwd=root)


@tool
def git_add(repo_root: str, paths: list[str] | str = ".") -> str:
    """Stage files (git add).

    Notes:
    - `paths` may be a single path string or a list of path strings.
    - Paths are interpreted relative to repo_root.
    """
    root = Path(repo_root).resolve()
    if isinstance(paths, str):
        path_list = [paths]
    else:
        path_list = paths

    # Use -- to avoid interpreting paths starting with '-' as flags.
    quoted = " ".join(shlex.quote(p) for p in path_list) if path_list else "."
    cmd = f"git add -- {quoted}".strip()
    return _run(cmd, cwd=root)


@tool
def git_commit(repo_root: str, message: str, add_all: bool = False) -> str:
    """Create a git commit.

    Args:
        message: commit message.
        add_all: if True, runs `git add -A` before committing.

    Notes:
    - This does not attempt to set user.name/user.email.
    - If those aren't configured, git may fail with a helpful error.
    """
    root = Path(repo_root).resolve()
    logs: list[str] = []
    if add_all:
        logs.append(_run("git add -A", cwd=root))
    logs.append(_run(f"git commit -m {shlex.quote(message)}", cwd=root))
    return "\n".join(logs)


@tool
def git_log(repo_root: str, max_count: int = 20, oneline: bool = True, path: str | None = None) -> str:
    """Show git log."""
    root = Path(repo_root).resolve()
    args: list[str] = [f"-n {int(max_count)}"]
    if oneline:
        args.append("--oneline")
    if path:
        args.append("--")
        args.append(shlex.quote(path))
    return _run("git log " + " ".join(args), cwd=root)


@tool
def git_branch_list(repo_root: str, all: bool = False) -> str:
    """List branches."""
    root = Path(repo_root).resolve()
    return _run("git branch" + (" -a" if all else ""), cwd=root)


@tool
def git_checkout(repo_root: str, branch: str, create: bool = False) -> str:
    """Checkout a branch.

    Args:
        branch: branch name.
        create: if True, uses `git checkout -b <branch>`.
    """
    root = Path(repo_root).resolve()
    flag = "-b " if create else ""
    return _run(f"git checkout {flag}{shlex.quote(branch)}", cwd=root)


@tool
def git_remote_list(repo_root: str, verbose: bool = True) -> str:
    """List configured remotes."""
    root = Path(repo_root).resolve()
    return _run("git remote -v" if verbose else "git remote", cwd=root)


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
    """Prepare a pull request workflow (local-only).

    This tool does NOT create a remote PR (network/auth are disabled).

    It validates local repo state and prints a ready-to-run command sequence:
    - create/switch to branch
    - show status
    - (optionally) commit instructions
    - push command
    - PR creation instructions (web or `gh` if you choose to run it outside sandbox)
    """
    root = Path(repo_root).resolve()

    logs: list[str] = []

    # sanity: ensure it's a git repo
    logs.append(_run("git rev-parse --is-inside-work-tree", cwd=root))

    # optionally create/switch branch
    if ensure_branch:
        # best-effort: if checkout -b fails because branch exists, fall back to checkout
        out = _run(f"git checkout -b {shlex.quote(branch)}", cwd=root)
        logs.append(out)
        if "(exit=0)" not in out:
            logs.append(_run(f"git checkout {shlex.quote(branch)}", cwd=root))

    # status
    status = _run("git status --porcelain", cwd=root)
    logs.append(status)

    if require_clean and "(exit=0)" in status:
        # status output includes cmd+exit line; detect additional lines after that
        lines = status.splitlines()
        dirty_lines = [ln for ln in lines[2:] if ln.strip()]
        if dirty_lines:
            return (
                "PR_PREP_FAILED=working_tree_not_clean\n"
                + "\n".join(logs)
                + "\n\n"
                + "Working tree has uncommitted changes. Commit or stash before preparing a PR."
            )

    # determine upstream/remote (best effort)
    remotes = _run("git remote", cwd=root)
    logs.append(remotes)

    # output instructions (no network)
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

@tool
def apply_patch(repo_root: str, unified_diff: str, check: bool = False) -> str:
    """
    Apply a unified diff to the repo using `git apply`.
    If check=True, runs `git apply --check` only.

    The diff should include paths like:
      --- a/file.py
      +++ b/file.py
    """
    root = Path(repo_root).resolve()
    patch_path = root / ".agent_patch.diff"
    patch_path.write_text(unified_diff, encoding="utf-8")

    cmd = "git apply --check .agent_patch.diff" if check else "git apply .agent_patch.diff"
    result = _run(cmd, cwd=root)

    # keep patch file for debugging if it fails; remove if success
    if "(exit=0)" in result and not check:
        try:
            patch_path.unlink()
        except Exception:
            pass
    return result

@tool
def run_pytest(repo_root: str, args: str = "-q", timeout_s: int = 300) -> str:
    """Run pytest in the repo."""
    root = Path(repo_root).resolve()
    return _run(f"pytest {args}".strip(), cwd=root, timeout_s=timeout_s)

@tool
def run_cmd(repo_root: str, cmd: str, timeout_s: int = 60) -> str:
    """
    Run a shell command in repo_root with sandbox restrictions.

    SECURITY:
    - Only allowlisted commands can run (git, python, pytest, grep, etc.)
    - Network access is disabled
    - Commands cannot escape the repository directory
    - Maximum timeout: 300s
    - Dangerous patterns are blocked (rm -rf /, sudo, eval, etc.)

    Returns combined stdout/stderr with exit code.
    """
    root = Path(repo_root).resolve()

    try:
        return _run_sandboxed(cmd, cwd=root, timeout_s=timeout_s, validate=True)
    except CommandNotAllowedError as e:
        return f"$ {cmd}\n(BLOCKED: {e})"


# ============================================================================
# MEMORY / STATE MANAGEMENT
# ============================================================================

import json
from datetime import datetime
from typing import Any, Dict

# In-memory storage (persists across tool calls within a session)
_MEMORY_STORE: Dict[str, Any] = {}

# Well-known memory keys
MEMORY_KEY_REPO_MAP = "repo_map"
MEMORY_KEY_FAILING_TESTS = "failing_tests"
MEMORY_KEY_LAST_ERROR = "last_error"
MEMORY_KEY_TODO_LIST = "todo_list"
MEMORY_KEY_CONTEXT = "context"


def _get_memory_file(repo_root: str) -> Path:
    """Get the path to the memory file for a repo."""
    return Path(repo_root).resolve() / ".agent_memory.json"


def _load_memory(repo_root: str) -> Dict[str, Any]:
    """Load memory from disk, merging with in-memory store."""
    global _MEMORY_STORE
    mem_file = _get_memory_file(repo_root)

    disk_mem = {}
    if mem_file.exists():
        try:
            disk_mem = json.loads(mem_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass

    # Merge: in-memory takes precedence
    merged = {**disk_mem, **_MEMORY_STORE}
    return merged


def _save_memory(repo_root: str, memory: Dict[str, Any]) -> None:
    """Persist memory to disk."""
    mem_file = _get_memory_file(repo_root)
    try:
        mem_file.write_text(json.dumps(memory, indent=2, default=str), encoding="utf-8")
    except IOError:
        pass


@tool
def memory_set(repo_root: str, key: str, value: str) -> str:
    """
    Store a value in agent memory.

    Well-known keys:
    - repo_map: Overview of repository structure and important files
    - failing_tests: List of tests that failed in last run
    - last_error: Most recent error encountered
    - todo_list: Current task list
    - context: Any relevant context for the current task

    Values are stored as strings. Use JSON for complex data.
    """
    global _MEMORY_STORE

    _MEMORY_STORE[key] = {
        "value": value,
        "updated_at": datetime.now().isoformat(),
    }

    # Persist to disk
    memory = _load_memory(repo_root)
    memory[key] = _MEMORY_STORE[key]
    _save_memory(repo_root, memory)

    return f"Stored '{key}' ({len(value)} chars)"


@tool
def memory_get(repo_root: str, key: str) -> str:
    """
    Retrieve a value from agent memory.

    Returns the stored value, or "(not found)" if the key doesn't exist.
    """
    memory = _load_memory(repo_root)

    if key in memory:
        entry = memory[key]
        if isinstance(entry, dict) and "value" in entry:
            return entry["value"]
        return str(entry)

    return "(not found)"


@tool
def memory_list(repo_root: str) -> str:
    """
    List all keys stored in agent memory with their metadata.

    Returns a summary of all stored keys, their sizes, and last update times.
    """
    memory = _load_memory(repo_root)

    if not memory:
        return "(memory is empty)"

    lines = ["Key | Size | Updated"]
    lines.append("-" * 50)

    for key in sorted(memory.keys()):
        entry = memory[key]
        if isinstance(entry, dict) and "value" in entry:
            size = len(str(entry["value"]))
            updated = entry.get("updated_at", "unknown")
        else:
            size = len(str(entry))
            updated = "unknown"
        lines.append(f"{key} | {size} chars | {updated}")

    return "\n".join(lines)


@tool
def memory_delete(repo_root: str, key: str) -> str:
    """
    Delete a key from agent memory.
    """
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


def _memory_set_internal(repo_root: str, key: str, value: str) -> str:
    """Internal memory set - use this from other tools to avoid invoke() issues."""
    global _MEMORY_STORE

    _MEMORY_STORE[key] = {
        "value": value,
        "updated_at": datetime.now().isoformat(),
    }

    # Persist to disk
    memory = _load_memory(repo_root)
    memory[key] = _MEMORY_STORE[key]
    _save_memory(repo_root, memory)

    return f"Stored '{key}' ({len(value)} chars)"


def _memory_get_internal(repo_root: str, key: str) -> str:
    """Internal memory get - use this from other tools to avoid invoke() issues."""
    memory = _load_memory(repo_root)

    if key in memory:
        entry = memory[key]
        if isinstance(entry, dict) and "value" in entry:
            return entry["value"]
        return str(entry)

    return "(not found)"


@tool
def memory_append(repo_root: str, key: str, value: str, separator: str = "\n") -> str:
    """
    Append to an existing value in memory (useful for logs, lists).

    If the key doesn't exist, creates it with the given value.
    """
    existing = _memory_get_internal(repo_root, key)

    if existing == "(not found)":
        new_value = value
    else:
        new_value = existing + separator + value

    return _memory_set_internal(repo_root, key, new_value)


@tool
def store_repo_map(repo_root: str, max_depth: int = 3, include_sizes: bool = False) -> str:
    """
    Generate and store a map of the repository structure.

    Automatically creates a repo_map in memory containing:
    - Directory structure
    - Key files (README, config files, main modules)
    - File counts by type

    Args:
        max_depth: Maximum directory depth to traverse
        include_sizes: Whether to include file sizes
    """
    root = Path(repo_root).resolve()

    structure_lines = []
    file_counts: Dict[str, int] = {}
    key_files = []

    # Key file patterns
    key_patterns = [
        "README*", "readme*",
        "pyproject.toml", "setup.py", "setup.cfg",
        "package.json", "Cargo.toml",
        "Makefile", "Dockerfile",
        "*.config.js", "*.config.ts",
        "__init__.py", "main.py", "app.py",
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

        # Filter out common ignored directories
        ignored = {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".ruff_cache", ".pytest_cache", "dist", "build", ".egg-info"}
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
                        size = entry.stat().st_size
                        size_str = f" ({size} B)"
                    except:
                        pass

                structure_lines.append(f"{prefix}{connector}{entry.name}{size_str}")

                # Track file types
                ext = entry.suffix.lower() or "(no ext)"
                file_counts[ext] = file_counts.get(ext, 0) + 1

                # Track key files
                if is_key_file(entry.name):
                    key_files.append(str(entry.relative_to(root)))

    structure_lines.append(f"{root.name}/")
    walk_dir(root)

    # Build the repo map
    repo_map_parts = [
        "# Repository Map",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Structure",
        "```",
        "\n".join(structure_lines[:100]),  # Limit to first 100 lines
    ]

    if len(structure_lines) > 100:
        repo_map_parts.append(f"... ({len(structure_lines) - 100} more entries)")

    repo_map_parts.extend([
        "```",
        "",
        "## File Types",
    ])

    for ext, count in sorted(file_counts.items(), key=lambda x: -x[1])[:10]:
        repo_map_parts.append(f"- {ext}: {count} files")

    if key_files:
        repo_map_parts.extend([
            "",
            "## Key Files",
        ])
        for kf in key_files[:20]:
            repo_map_parts.append(f"- {kf}")

    repo_map = "\n".join(repo_map_parts)

    # Store in memory
    _memory_set_internal(repo_root, MEMORY_KEY_REPO_MAP, repo_map)

    return f"Stored repo map ({len(structure_lines)} entries, {len(file_counts)} file types, {len(key_files)} key files)"


@tool
def store_test_results(repo_root: str, test_output: str) -> str:
    """
    Parse pytest output and store failing tests in memory.

    Extracts:
    - Failed test names
    - Error messages
    - Failure locations

    Stores in 'failing_tests' memory key.
    """
    lines = test_output.split("\n")

    failing_tests = []
    current_failure = None

    # Parse pytest output for failures
    for line in lines:
        # Match FAILED test lines
        if "FAILED" in line:
            # Extract test name (e.g., "tests/test_foo.py::test_bar")
            match = re.search(r'FAILED\s+(\S+)', line)
            if match:
                failing_tests.append({
                    "test": match.group(1),
                    "error": "",
                })
                current_failure = failing_tests[-1]

        # Match short test summary lines
        elif line.strip().startswith("E ") and current_failure:
            current_failure["error"] += line.strip()[2:] + "\n"

        # Match assertion errors
        elif "AssertionError" in line and current_failure:
            current_failure["error"] += line.strip() + "\n"

        # Match other common errors
        elif any(err in line for err in ["Error:", "Exception:", "TypeError", "ValueError", "AttributeError"]):
            if current_failure:
                current_failure["error"] += line.strip() + "\n"

    if not failing_tests:
        # Check if all tests passed
        if "passed" in test_output.lower() and "failed" not in test_output.lower():
            _memory_set_internal(repo_root, MEMORY_KEY_FAILING_TESTS, "All tests passed!")
            return "All tests passed! Cleared failing tests from memory."

        return "No test failures detected in output."

    # Format and store
    result_lines = [f"# Failing Tests ({len(failing_tests)} failures)", ""]
    for i, failure in enumerate(failing_tests, 1):
        result_lines.append(f"## {i}. {failure['test']}")
        if failure["error"]:
            result_lines.append("```")
            result_lines.append(failure["error"].strip())
            result_lines.append("```")
        result_lines.append("")

    result = "\n".join(result_lines)
    _memory_set_internal(repo_root, MEMORY_KEY_FAILING_TESTS, result)

    return f"Stored {len(failing_tests)} failing test(s) in memory"


@tool
def run_pytest(repo_root: str, args: str = "-q", timeout_s: int = 300) -> str:
    """
    Run pytest in the repo.

    Args:
        repo_root: Absolute path to the repository root
        args: Pytest arguments as a single string (e.g., "-q", "-v", "--tb=short")
        timeout_s: Maximum time to wait for tests to complete
    """
    root = Path(repo_root).resolve()
    return _run(f"pytest {args}".strip(), cwd=root, timeout_s=timeout_s)


@tool
def clear_memory(repo_root: str) -> str:
    """
    Clear all agent memory (both in-memory and on disk).
    """
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

