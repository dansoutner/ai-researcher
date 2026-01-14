# Network Access Fix for pip install

## Problem

The agent could not install packages like `scikit-learn` even when using custom PyPI indexes because the sandbox blocked all network access by default.

### Root Cause

The sandbox's `build_sandbox_env()` function sets environment variables that block network access:
- `PIP_NO_INDEX=1` - Prevents pip from using ANY package index (including custom ones)
- Invalid proxy settings that block all network traffic

This was enforced in two places:
1. `run_sandboxed()` - had an `allow_network` parameter (defaults to `False`)
2. `run_sandboxed_with_env()` - **missing** the `allow_network` parameter

The `run_in_venv()` function uses `run_sandboxed_with_env()`, which meant all pip install commands were blocked from network access, even with custom index URLs like `-i https://pypi.anaconda.org/...`.

### Error Observed

```
$ pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple scikit-learn
(exit=1)
ERROR: Could not find a version that satisfies the requirement scikit-learn (from versions: none)
```

This happened because `PIP_NO_INDEX=1` overrode the `-i` flag.

## Solution

Added `allow_network` parameter support through the entire call chain:

1. **sandbox.py**: Added `allow_network` parameter to `run_sandboxed_with_env()`
2. **venv_tools.py**: Added `allow_network` parameter to `run_in_venv()`

### Usage

To install packages from PyPI or custom indexes, use:

```python
run_in_venv(
    repo_root="/path/to/repo",
    cmd="pip install scikit-learn",
    allow_network=True  # Enable network access
)
```

Or with a custom index:

```python
run_in_venv(
    repo_root="/path/to/repo",
    cmd="pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple scikit-learn",
    allow_network=True  # Required to access the custom index
)
```

### Default Behavior

By default, `allow_network=False` to maintain security. The agent must explicitly request network access when needed for package installation.

## Files Modified

1. `/ai_researcher/ai_researcher_tools/sandbox.py`
   - Added `allow_network: bool = False` parameter to `run_sandboxed_with_env()`
   - Pass `allow_network` to `build_sandbox_env()`

2. `/ai_researcher/ai_researcher_tools/venv_tools.py`
   - Added `allow_network: bool = False` parameter to `run_in_venv()`
   - Pass `allow_network` to `run_sandboxed_with_env()`
   - Updated docstring to explain the parameter

## Testing

The agent should now be able to:
1. Install packages from PyPI: `run_in_venv(..., cmd="pip install numpy", allow_network=True)`
2. Use custom indexes: `run_in_venv(..., cmd="pip install -i https://... package", allow_network=True)`
3. Install Python 3.14 pre-release packages from nightly wheels repositories

