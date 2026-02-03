# grep_search Tool Fix - File Support

## Problem
The `grep_search` tool was failing with the error:
```
Error: Path 'agent_readme.md' is not a directory
```

This occurred when users tried to search within a specific file instead of a directory.

## Root Cause
The tool had a validation check that rejected any path that wasn't a directory:
```python
if not base.is_dir():
    return f"Error: Path '{path}' is not a directory"
```

## Solution
Updated `grep_search` in `/ai_researcher/ai_researcher_tools/fs_tools.py` to accept both files and directories:

### Changes Made

1. **Updated docstring** to clarify that path can be a file or directory:
   ```python
   """Search for text in files within a directory/file and its subdirectories.
   
   If path is a file, searches only that file. If path is a directory, 
   searches all files recursively.
   ```

2. **Replaced directory check** with file detection:
   ```python
   # OLD:
   if not base.is_dir():
       return f"Error: Path '{path}' is not a directory"
   
   # NEW:
   is_single_file = base.is_file()
   ```

3. **Updated Python fallback** to handle single files:
   ```python
   # Handle single file vs directory
   if is_single_file:
       files_to_search = [base]
   else:
       files_to_search = sorted(base.rglob("*"))
   
   for f in files_to_search:
       # ... search logic
   ```

4. **ripgrep (rg) command unchanged** - it already handles both files and directories correctly

## Usage Examples

### Search within a specific file
```python
grep_search.invoke({
    "repo_root": "/path/to/repo",
    "query": "def my_function",
    "path": "src/module.py",  # Now works with files!
    "case_sensitive": True
})
```

### Search within a directory (existing behavior)
```python
grep_search.invoke({
    "repo_root": "/path/to/repo",
    "query": "TODO",
    "path": "src",  # Still works with directories
    "case_sensitive": False
})
```

### Search entire repository
```python
grep_search.invoke({
    "repo_root": "/path/to/repo",
    "query": "import numpy",
    "path": ".",  # Search from root
})
```

## Benefits
- **More flexible**: Users can now search in specific files or entire directories
- **Better UX**: No confusing error messages when path happens to be a file
- **Backward compatible**: All existing directory searches continue to work
- **Consistent with grep/rg**: Standard grep tools accept both files and directories

## Testing
The fix handles:
- ✅ Single file searches
- ✅ Directory searches (recursive)
- ✅ Case-sensitive and case-insensitive searches
- ✅ Max results limiting
- ✅ Non-existent path errors
- ✅ Both ripgrep and Python fallback implementations

