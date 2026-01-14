# Quick Reference: Installing Packages with Network Access

## Problem Fixed

The agent could not install packages from PyPI or custom indexes because network access was blocked by default in the sandbox environment.

## Solution

Use the `allow_network=True` parameter when calling `run_in_venv()` for pip install commands.

## Examples

### Install from PyPI
```python
run_in_venv(
    repo_root="/path/to/repo",
    cmd="pip install numpy pandas scikit-learn",
    allow_network=True
)
```

### Install from Custom Index (Python 3.14 nightly wheels)
```python
run_in_venv(
    repo_root="/path/to/repo",
    cmd="pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple scikit-learn",
    allow_network=True
)
```

### Install with Extra Options
```python
run_in_venv(
    repo_root="/path/to/repo",
    cmd="pip install --upgrade --pre scikit-learn",
    allow_network=True,
    timeout_s=300  # Longer timeout for large packages
)
```

## Important Notes

1. **Always set `allow_network=True`** when installing packages from remote sources
2. The default is `allow_network=False` for security reasons
3. Local operations (like `pip list`, `pip show`) don't need network access
4. The `PIP_NO_INDEX=1` environment variable is what was blocking network access

## Related Files

- `ai_researcher/ai_researcher_tools/venv_tools.py` - Contains `run_in_venv()`
- `ai_researcher/ai_researcher_tools/sandbox.py` - Contains `run_sandboxed_with_env()` and `build_sandbox_env()`

