# Parsing Error Fix - Empty List Content Handling

## Problem

The agent was experiencing a JSON parsing error when the LLM returned responses with empty content:

```
[DEBUG] Executor output: {'success': False, 'output': 'Executor response parse error: the JSON object must be str, bytes or bytearray, not list. Raw response: []'}
```

**Root Cause:** When an LLM (like Claude via LangChain) makes only tool calls without providing any text content, the `ai_message.content` field can be an empty list `[]` instead of a string. The JSON parser (`json.loads()`) expects a string and raises a `TypeError` when given a list.

## Solution

Added defensive type checking and conversion in all three response parsers before attempting JSON parsing:

### Files Modified

1. **`ai_researcher/agent_v3_claude/tools.py`** - `parse_executor_response()`
2. **`ai_researcher/agent_v3_claude/nodes.py`** - `parse_reviewer_response()` and `parse_plan_response()`

### Changes Applied

Each parser now includes:

```python
# Handle non-string content (e.g., empty list from LLM with only tool calls)
if not isinstance(content, str):
    if isinstance(content, list):
        # If it's a list, convert to string or raise if empty
        if not content:
            raise ValueError("Empty content list - [role] provided no text response")
        content = str(content)
    else:
        content = str(content)

# Handle empty or whitespace-only content
if not content or not content.strip():
    raise ValueError("Empty content - [role] provided no response")
```

## Benefits

1. **Prevents TypeError**: Converts non-string content to string before JSON parsing
2. **Clear Error Messages**: Provides specific error messages for empty or missing responses
3. **Consistent Handling**: Applied to all three parser functions (executor, reviewer, planner)
4. **Graceful Degradation**: When parsing fails, the error is caught and the executor output is marked as failed with a descriptive message

## Error Flow

**Before Fix:**
```
LLM returns [] → json.loads([]) → TypeError → Generic parse error
```

**After Fix:**
```
LLM returns [] → Type check catches list → Raises ValueError with clear message
→ Exception handler in tools.py catches it → Returns ExecutorOutput with success=False
→ Reviewer automatically sets verdict to 'retry'
```

## Testing

The fix ensures:
- ✅ Empty lists are caught and produce clear error messages
- ✅ Empty strings are caught and produce clear error messages  
- ✅ Valid JSON strings continue to work normally
- ✅ The error is propagated correctly through the agent system

## Impact

This fix resolves the immediate parsing error and allows the agent to:
1. Detect when an LLM provides no textual response
2. Automatically retry the step with a clear error message
3. Avoid cascading failures from type mismatches

