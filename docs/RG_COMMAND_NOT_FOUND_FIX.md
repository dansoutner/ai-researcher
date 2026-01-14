# Fix for "rg: command not found" Issue

## Problem

The `grep_search` tool was failing with the error:
```
/bin/sh: rg: command not found
```

Even though `rg` (ripgrep) was installed on the system, the sandboxed environment couldn't find it.

## Root Cause

The issue was in the `build_sandbox_env()` function in `ai_researcher/ai_researcher_tools/sandbox.py`.

### Original Problematic Code

```python
safe_paths = ["/usr/local/bin", "/usr/bin", "/bin", ..., "/opt/homebrew/bin/"]
# ...
filtered = [p for p in existing if any(p.startswith(s.rstrip("*")) for s in safe_paths)]
```

### Problems with Original Implementation

1. **Trailing Slash Mismatch**: The `safe_paths` list had paths with trailing slashes (e.g., `/opt/homebrew/bin/`), but the actual PATH entries don't have trailing slashes. The `startswith()` check would fail:
   - Safe path: `/opt/homebrew/bin/` 
   - Actual PATH entry: `/opt/homebrew/bin`
   - Result: `/opt/homebrew/bin`.startswith(`/opt/homebrew/bin`) = ✅ MATCH
   - BUT after `rstrip("/")`: `/opt/homebrew/bin`.startswith(`/opt/homebrew/bin`) would work
   - However, the logic was: `p.startswith(s.rstrip("*"))` which would strip `*` but not handle the `/` properly

2. **Wildcard Pattern Not Expanded**: The pattern `~/.nvm/versions/node/*/bin` was never expanded to actual directories, so it couldn't match anything.

3. **Over-restrictive Filtering**: The logic only allowed paths that **started with** safe paths, not paths that **matched** safe paths. This meant exact matches could fail.

## Solution

### Fixed Implementation

```python
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
```

### Key Improvements

1. **Removed Trailing Slashes**: All safe paths are defined without trailing slashes
2. **Proper Normalization**: Both the PATH entry and safe path are normalized (trailing slashes removed) before comparison
3. **Exact Match + Prefix Match**: The new logic checks for both exact matches and prefix matches:
   - `normalized_path == safe_normalized` - allows exact matches like `/opt/homebrew/bin`
   - `normalized_path.startswith(safe_normalized + "/")` - allows subdirectories
4. **Wildcard Expansion**: Node version paths are expanded using `glob.glob()` to find actual directories
5. **Empty Path Handling**: Skips empty PATH entries explicitly

## Testing

Run the test script to verify the fix:

```bash
python3 test_rg_path_fix.py
```

This will show:
- Original PATH entries
- Sandboxed PATH entries  
- Whether `rg` is found in the sandboxed PATH
- If not found, where `rg` actually exists and why it's not included

## Impact

This fix ensures that all tools installed in standard locations can be found:
- Homebrew tools in `/opt/homebrew/bin`
- System tools in `/usr/local/bin`, `/usr/bin`, `/bin`
- User-local tools in `~/.local/bin`, `~/.cargo/bin`
- Python environment tools in `~/.pyenv/shims`
- Node version manager tools in `~/.nvm/versions/node/*/bin`

The `grep_search` tool and other tools that rely on external commands should now work correctly.

