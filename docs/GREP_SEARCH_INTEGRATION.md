# grep_search Tool Integration

## Summary

Added a new `grep_search` tool to the ai-researcher toolkit that provides text search functionality across directories and subdirectories.

## Files Modified

### 1. `/ai_researcher/ai_researcher_tools/fs_tools.py`
- Added new `grep_search` function (lines 333-425)
- Provides a user-friendly interface for searching text in files
- Supports case-sensitive and case-insensitive search
- Uses ripgrep (rg) for performance when available, with pure Python fallback
- Returns formatted results: `file:line_number:matching_line`

### 2. `/ai_researcher/ai_researcher_tools/__init__.py`
- Added `grep_search` to imports from `fs_tools`
- Added `grep_search` to `__all__` exports list

### 3. `/ai_researcher/agent_v3_claude/tools.py`
- Added `grep_search` to imports from `ai_researcher_tools`
- Added `grep_search` to the `TOOLS` list
- Tool is now available for agent_v3 to use

## Tool Signature

```python
def grep_search(
    repo_root: str,
    query: str,
    path: str = ".",
    case_sensitive: bool = False,
    max_results: int = 200,
) -> str:
    """Search for text in files within a directory and its subdirectories.
    
    Args:
        repo_root: The root directory
        query: The text string to search for
        path: Relative path to search within (default: current directory)
        case_sensitive: If True, search is case-sensitive (default: False)
        max_results: Maximum number of matching lines to return (default: 200)
    
    Returns:
        Formatted list of matches or "(no matches)" if nothing found
    """
```

## Usage Example

```python
# Case-insensitive search (default)
result = grep_search("/path/to/repo", "TODO", "src")

# Case-sensitive search
result = grep_search("/path/to/repo", "def my_function", ".", case_sensitive=True)

# Search with custom max results
result = grep_search("/path/to/repo", "import", path=".", max_results=50)
```

## Features

1. **Recursive search**: Searches all files in directory and subdirectories
2. **Case sensitivity control**: Optional case-sensitive or case-insensitive matching
3. **Result limiting**: Configurable maximum number of results
4. **Performance optimized**: Uses ripgrep when available, falls back to Python
5. **Error handling**: Gracefully handles missing paths, invalid files, etc.
6. **Clear output format**: Returns `file:line_number:content` for easy parsing

## Differences from existing `grep` tool

- **grep**: Accepts regex patterns, uses flags parameter, more flexible but complex
- **grep_search**: Accepts plain text strings, has explicit parameters, easier to use

Both tools are available in agent_v3, allowing the agent to choose based on the task.

## Integration Status

✅ Tool implemented in `fs_tools.py`
✅ Exported from `ai_researcher_tools` package
✅ Integrated into agent_v3 tools registry
✅ No errors or conflicts detected
✅ Ready for use by agent_v3

