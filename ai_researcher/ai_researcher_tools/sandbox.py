from __future__ import annotations

"""Sandboxed command execution helpers.

This module enforces a strict allowlist and blocks dangerous patterns.
It is used by the public tools (git/fs/venv/etc.) to execute commands.

Design notes:
- Network access is intentionally disabled at the sandbox layer.
- Commands are allowlisted and checked for blocked patterns.
"""

import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import List, Set

# Allowlisted command prefixes (base commands that are permitted)
ALLOWED_COMMANDS: Set[str] = {
    # Version control
    "git",
    # Python tooling
    "python",
    "python3",
    "pip",
    "pip3",
    "uv",
    "pytest",
    "mypy",
    "ruff",
    "black",
    "isort",
    "flake8",
    "pylint",
    # Build tools
    "make",
    "cargo",
    "npm",
    "npx",
    "node",
    "yarn",
    "pnpm",
    # File inspection (read-only)
    "cat",
    "head",
    "tail",
    "less",
    "more",
    "wc",
    "diff",
    "ls",
    "find",
    "tree",
    "file",
    "stat",
    "grep",
    "egrep",
    "fgrep",
    "rg",
    "ag",
    "ack",
    # File and dir creation
    "mkdir",
    "touch",
    "chmod",
    "chown",
    "cd",
    # Text processing
    "sed",
    "awk",
    "cut",
    "sort",
    "uniq",
    "tr",
    "jq",
    "yq",
    # Archive (read)
    "tar",
    "unzip",
    "gzip",
    "gunzip",
    # Misc safe
    "echo",
    "printf",
    "true",
    "false",
    "test",
    "expr",
    "date",
    "env",
    "printenv",
    "which",
    "whereis",
    "type",
    "pwd",
    "basename",
    "dirname",
    "realpath",
}

# Patterns that are ALWAYS blocked (security risks)
BLOCKED_PATTERNS: List[re.Pattern] = [
    re.compile(r"\brm\s+-rf\s+/", re.IGNORECASE),  # rm -rf /
    re.compile(r"\brm\s+(-[a-z]*f[a-z]*\s+)?/"),  # rm with /
    re.compile(r">\s*/dev/sd[a-z]"),  # write to disk
    re.compile(r"\bdd\b.*of=/dev/"),  # dd to device
    re.compile(r"\bmkfs\b"),  # format filesystem
    re.compile(r"\b(sudo|su|doas)\b"),  # privilege escalation
    re.compile(r"\bchmod\s+[0-7]*777\b"),  # world-writable
    re.compile(r"\bchown\b.*root"),  # chown to root
    re.compile(r"\b(curl|wget|nc|netcat|ncat)\b"),  # network tools
    re.compile(r"\b(ssh|scp|rsync|ftp|sftp|telnet)\b"),  # remote access
    re.compile(r"\beval\b"),  # eval injection
    re.compile(r"`.*`"),  # command substitution
    re.compile(r"\$\(.*\)"),  # command substitution
    re.compile(r"\|\s*sh\b"),  # pipe to shell
    re.compile(r"\|\s*bash\b"),  # pipe to bash
    re.compile(r"\|\s*zsh\b"),  # pipe to zsh
    re.compile(r";\s*sh\b"),  # chain to shell
    re.compile(r"&&\s*sh\b"),  # chain to shell
    re.compile(r"\bexport\b.*\bPATH\b"),  # PATH manipulation
    re.compile(r"\bsource\b"),  # source scripts
    re.compile(r"\b\.\s+/"),  # source with .
    re.compile(r"/etc/(passwd|shadow|sudoers)"),  # sensitive files
    re.compile(r"~/.ssh"),  # SSH keys
    re.compile(r"\bkill\b.*-9"),  # force kill
    re.compile(r"\bpkill\b"),  # process kill
    re.compile(r"\bkillall\b"),  # kill all
    re.compile(r"\bnohup\b"),  # background persistence
    re.compile(r"&\s*$"),  # background execution
    re.compile(r"\bdisown\b"),  # disown process
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


def safe_path(repo_root: str, rel_path: str) -> Path:
    root = Path(repo_root).resolve()
    p = (root / rel_path).resolve()
    if root not in p.parents and p != root:
        raise ValueError("Path escapes repo_root")
    return p


def _extract_base_command(cmd: str) -> str:
    cmd = cmd.strip()

    # Handle env prefix: env VAR=val cmd ...
    if cmd.startswith("env "):
        parts = cmd.split()
        for i, part in enumerate(parts[1:], 1):
            if "=" not in part and not part.startswith("-"):
                cmd = " ".join(parts[i:])
                break

    try:
        tokens = shlex.split(cmd)
        if tokens:
            base = os.path.basename(tokens[0])
            if base.startswith("python3."):
                return "python3"
            if base.startswith("python2."):
                return "python"
            return base
    except ValueError:
        pass

    first = cmd.split()[0] if cmd.split() else ""
    return os.path.basename(first)


def validate_command(cmd: str, repo_root: Path) -> None:
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(cmd):
            print(f"\n⚠️  WARNING: Command matches security pattern: {pattern.pattern!r}")
            print(f"Command: {cmd}")
            response = input("Do you want to allow this command? (yes/no): ").strip().lower()
            if response not in ("yes", "y"):
                raise CommandNotAllowedError(f"Command blocked by user: security pattern {pattern.pattern!r}")

    base_cmd = _extract_base_command(cmd)
    if base_cmd not in ALLOWED_COMMANDS:
        print(f"\n⚠️  WARNING: Command '{base_cmd}' is not in the allowlist.")
        print(f"Command: {cmd}")
        print(f"Allowed commands: {sorted(ALLOWED_COMMANDS)}")
        response = input("Do you want to allow this command? (yes/no): ").strip().lower()
        if response not in ("yes", "y"):
            raise CommandNotAllowedError(
                f"Command '{base_cmd}' blocked by user. Not in allowlist."
            )

    repo_str = str(repo_root.resolve())
    try:
        tokens = shlex.split(cmd)
        for token in tokens[1:]:
            if token.startswith("/") and not token.startswith(repo_str):
                safe_prefixes = ("/dev/null", "/tmp", "/usr/bin", "/usr/local/bin")
                if not any(token.startswith(p) for p in safe_prefixes):
                    raise CommandNotAllowedError(
                        f"Path '{token}' is outside the repository. Commands must operate within: {repo_str}"
                    )
            if ".." in token:
                resolved = (repo_root / token).resolve()
                if not str(resolved).startswith(repo_str):
                    raise CommandNotAllowedError(f"Path '{token}' escapes the repository via '..'")
    except ValueError:
        pass


def build_sandbox_env(repo_root: Path, allow_network: bool = False) -> dict:
    env = os.environ.copy()
    if not allow_network:
        env.update(SANDBOX_ENV_OVERRIDES)

    # Define safe path prefixes (normalized without trailing slashes)
    safe_paths = ["/usr/local/bin", "/usr/bin", "/bin", "/usr/local/sbin", "/usr/sbin", "/sbin", "/opt/homebrew/bin"]
    home = os.path.expanduser("~")
    safe_paths.extend(
        [
            f"{home}/.local/bin",
            f"{home}/.cargo/bin",
            f"{home}/.pyenv/shims",
        ]
    )

    # Add node paths if they exist (handle wildcards)
    import glob
    nvm_pattern = f"{home}/.nvm/versions/node/*/bin"
    safe_paths.extend(glob.glob(nvm_pattern))

    # Filter existing PATH entries
    existing = env.get("PATH", "").split(":")
    filtered = []
    for path in existing:
        if not path:  # Skip empty paths
            continue
        # Normalize path (remove trailing slashes for comparison)
        normalized_path = path.rstrip("/")
        # Check if this path or its parent matches any safe path
        for safe in safe_paths:
            safe_normalized = safe.rstrip("/")
            if normalized_path == safe_normalized or normalized_path.startswith(safe_normalized + "/"):
                filtered.append(path)
                break

    venv_bin = repo_root / ".venv" / "bin"
    if venv_bin.exists():
        filtered.insert(0, str(venv_bin))

    env["PATH"] = ":".join(filtered) if filtered else "/usr/bin:/bin"
    env["UMASK"] = "077"
    return env


def run_sandboxed(cmd: str, cwd: Path, timeout_s: int = DEFAULT_TIMEOUT_S, validate: bool = True, allow_network: bool = False) -> str:
    timeout_s = min(timeout_s, MAX_TIMEOUT_S)

    if validate:
        validate_command(cmd, cwd)

    env = build_sandbox_env(cwd, allow_network=allow_network)

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


def run_sandboxed_with_env(
    cmd: str,
    cwd: Path,
    *,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    validate: bool = True,
    extra_env: dict[str, str] | None = None,
    allow_network: bool = False,
) -> str:
    timeout_s = min(timeout_s, MAX_TIMEOUT_S)

    if validate:
        validate_command(cmd, cwd)

    env = build_sandbox_env(cwd, allow_network=allow_network)
    if extra_env:
        env.update(extra_env)

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


def run_internal(cmd: str, cwd: Path, timeout_s: int = 120) -> str:
    """Internal runner for trusted commands (no sandbox validation)."""
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

