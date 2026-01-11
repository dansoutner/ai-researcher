# edit_file Tool Implementation

## Overview
Implemented a new `edit_file` tool that provides surgical file edits as a more precise alternative to `write_file` for making targeted changes to files.

## Implementation Details

### Location
- **Primary implementation**: `ai_researcher_tools/fs_tools.py`
- **Exported from**: `ai_researcher_tools/__init__.py`
- **Integrated into**: `agent_v3_claude/tools.py`

### Function Signature
```python
@tool
def edit_file(repo_root: str, path: str, old_string: str, new_string: str) -> str:
    """Replace occurrences of old_string with new_string in a file within `repo_root`.
    
    This provides surgical edits for large files without rewriting the entire content.
    The old_string must exist in the file exactly as specified (including whitespace).
    Returns the number of replacements made or an error message.
    """
```

## Key Features

### ✅ Surgical Edits
- Replace specific strings without rewriting entire files
- Ideal for large files where only small changes are needed
- Preserves exact formatting and whitespace of unchanged sections

### ✅ Robust Validation
1. **File existence check**: Validates the target file exists
2. **String presence check**: Ensures old_string is present before attempting replacement
3. **Whitespace sensitivity**: Requires exact match including all whitespace
4. **UTF-8 validation**: Ensures file is a valid text file

### ✅ Comprehensive Error Handling
- File not found errors
- String not found errors  
- UTF-8 decode errors
- Write permission errors

### ✅ Informative Feedback
- Reports number of occurrences replaced
- Warns when multiple occurrences are found
- Shows line count changes (e.g., "lines: 9 → 12, +3")
- Clear error messages with guidance

## Benefits Over write_file

| Aspect | write_file | edit_file |
|--------|-----------|-----------|
| **Precision** | Rewrites entire file | Surgical replacement of specific strings |
| **File Size** | Need to provide full content | Only need the string to change |
| **Validation** | No validation | Validates string exists before edit |
| **Feedback** | Only reports char count | Reports occurrences, warnings, line changes |
| **Risk** | Higher (can corrupt if content incomplete) | Lower (validates before writing) |
| **Use Case** | Creating new files, full rewrites | Targeted edits to existing files |

## Usage Examples

### Example 1: Rename a function
```python
edit_file.invoke({
    "repo_root": "/path/to/repo",
    "path": "src/utils.py",
    "old_string": "def old_function_name():",
    "new_string": "def new_function_name():"
})
# Output: Successfully replaced 1 occurrence(s) in 'src/utils.py'
```

### Example 2: Replace multiline code block
```python
edit_file.invoke({
    "repo_root": "/path/to/repo",
    "path": "src/api.py",
    "old_string": """    def get_user(self):
        return self.user""",
    "new_string": """    def get_user(self, include_metadata=False):
        if include_metadata:
            return {"user": self.user, "metadata": self.metadata}
        return self.user"""
})
# Output: Successfully replaced 1 occurrence(s) in 'src/api.py' (lines: 50 → 53, +3)
```

### Example 3: Error handling
```python
edit_file.invoke({
    "repo_root": "/path/to/repo",
    "path": "missing.py",
    "old_string": "foo",
    "new_string": "bar"
})
# Output: Error: File 'missing.py' does not exist
```

## Testing

### Test Suite
Created comprehensive test suite in `tests/test_edit_file.py` covering:
- ✅ Basic single replacement
- ✅ Multiple occurrences with warning
- ✅ Multiline string replacement
- ✅ Whitespace sensitivity
- ✅ File not found error
- ✅ String not found error
- ✅ Line count change reporting

### Test Results
```
7 passed, 1 warning in 0.11s
```

### Demo Script
Created `demo_edit_file.py` showcasing:
- Basic string replacement
- Multiline code block replacement  
- Error handling scenarios
- Multiple occurrence warnings

## Integration

The tool has been fully integrated into the agent system:

1. **ai_researcher_tools package**: Exported in `__init__.py`
2. **agent_v3_claude**: Added to tools registry in `tools.py`
3. **Available to all agents**: Can be used by any agent that imports from `ai_researcher_tools`

## When to Use

### Use `edit_file` when:
- Making targeted changes to existing files
- Working with large files where rewriting is inefficient
- Need validation that the target string exists
- Want to preserve exact formatting of unchanged sections
- Need detailed feedback about what changed

### Use `write_file` when:
- Creating new files from scratch
- Complete file rewrites are needed
- File content is dynamically generated
- File is small and rewriting is not a concern

## Future Enhancements

Possible improvements for future iterations:
- [ ] Regex pattern support for more flexible matching
- [ ] Line number-based editing (edit specific line ranges)
- [ ] Preview mode (show what would change without applying)
- [ ] Undo/rollback functionality
- [ ] Batch editing (multiple edits in one call)
- [ ] Diff output showing exact changes made

## Conclusion

The `edit_file` tool provides a more precise, safer, and more informative way to make targeted file changes compared to rewriting entire files with `write_file`. It's especially valuable for:
- Large files
- Precise refactoring operations
- Situations where validation is important
- When detailed feedback is needed

The tool is production-ready, fully tested, and integrated into the agent system.

