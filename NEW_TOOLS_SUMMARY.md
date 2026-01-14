# New Tools Added to cmd_tools.py

## Summary

Two new tools have been successfully added to `ai_researcher/ai_researcher_tools/cmd_tools.py`:

1. **`run_terminal_command`** - Execute terminal commands with optional background process support
2. **`get_errors`** - Check Python files for compile and lint errors

## Tool Details

### 1. run_terminal_command

**Purpose**: Run terminal commands in a repository, with support for both synchronous and background execution.

**Function Signature**:
```python
@tool
def run_terminal_command(
    repo_root: str, 
    cmd: str, 
    is_background: bool = False, 
    timeout_s: int = 60
) -> str
```

**Parameters**:
- `repo_root`: The root directory to run the command in
- `cmd`: The command to execute
- `is_background`: If True, runs command in background (for servers, watch mode, etc.)
- `timeout_s`: Maximum execution time in seconds (ignored for background processes)

**Returns**: Command output or background process ID

**Features**:
- Supports background processes (e.g., for servers, watch mode)
- Uses sandboxed environment for security
- Returns PID for background processes
- Handles command validation and blocking via existing sandbox mechanism

### 2. get_errors

**Purpose**: Check Python files for syntax errors, compilation issues, and linting problems.

**Function Signature**:
```python
@tool
def get_errors(repo_root: str, file_paths: list[str]) -> str
```

**Parameters**:
- `repo_root`: The root directory of the repository
- `file_paths`: List of relative file paths to check for errors

**Returns**: Formatted string containing all errors found in the specified files

**Features**:
- **Syntax checking**: Uses Python's built-in `compile()` to catch syntax errors
- **Linting**: Runs `ruff check` if available
- **Type checking**: Runs `mypy` if available
- Handles non-existent files and non-Python files gracefully
- Returns formatted output with file-by-file error breakdown
- Returns success message if no errors found

## Implementation Details

### Changes Made

1. **cmd_tools.py**:
   - Added imports: `subprocess`, `Dict`, `build_sandbox_env`
   - Added `run_terminal_command` tool
   - Added `get_errors` tool

2. **__init__.py**:
   - Updated import statement to include new tools
   - Added new tools to `__all__` export list

### Dependencies

- Uses existing `sandbox.py` module for:
  - `run_sandboxed()` - Execute commands safely
  - `build_sandbox_env()` - Build sandboxed environment
  - `CommandNotAllowedError` - Handle blocked commands

### Security Considerations

Both tools maintain the existing security model:
- Commands are validated against allowlist
- Blocked patterns are checked
- Network access is disabled
- Commands run in sandboxed environment
- Path validation prevents directory traversal

## Usage Examples

### run_terminal_command (Synchronous)

```python
from ai_researcher.ai_researcher_tools import run_terminal_command

result = run_terminal_command.invoke({
    "repo_root": "/path/to/repo",
    "cmd": "pytest tests/",
    "is_background": False,
    "timeout_s": 300
})
```

### run_terminal_command (Background)

```python
result = run_terminal_command.invoke({
    "repo_root": "/path/to/repo",
    "cmd": "python -m http.server 8000",
    "is_background": True
})
# Returns: "$ python -m http.server 8000\n(Background process started, PID=12345)"
```

### get_errors

```python
from ai_researcher.ai_researcher_tools import get_errors

result = get_errors.invoke({
    "repo_root": "/path/to/repo",
    "file_paths": ["src/main.py", "src/utils.py"]
})
```

**Example Output**:
```
=== src/main.py ===
SyntaxError: unterminated string literal at line 42, col 15
Ruff linting:
src/main.py:10:1: F401 'os' imported but unused

=== src/utils.py ===
MyPy type checking:
src/utils.py:25: error: Argument 1 to "process" has incompatible type "str"; expected "int"
```

## Files Modified

- ✅ `/ai_researcher/ai_researcher_tools/cmd_tools.py` - Added 2 new tools
- ✅ `/ai_researcher/ai_researcher_tools/__init__.py` - Updated imports and exports

## Validation

- ✅ No syntax errors
- ✅ No import errors
- ✅ Tools properly decorated with `@tool`
- ✅ Tools exported in `__all__`
- ✅ Compatible with existing sandbox security model

