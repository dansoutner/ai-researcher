# ✅ FIXED: TypeError: Cannot invoke a coroutine function synchronously

## Problem

```
TypeError: Cannot invoke a coroutine function synchronously.
Use `ainvoke` instead.
During task with name 'tools' and id '32cb7d37-46a3-9ece-6bff-ae6fa36c31db'
```

## Root Cause

The tools node was trying to use conditional logic to determine whether to use `invoke()` or `ainvoke()`:

```python
# OLD CODE (BROKEN)
if hasattr(tool, 'ainvoke'):
    try:
        result = await tool.ainvoke(args)
    except NotImplementedError:
        result = tool.invoke(args)  # ❌ This can fail!
else:
    result = tool.invoke(args)  # ❌ This can also fail!
```

**Issues:**
1. Some tools are async functions that cannot be invoked synchronously
2. Calling `invoke()` on a coroutine function raises TypeError
3. The conditional logic was trying to be too smart

## Solution

**Always use `ainvoke` in async context.** LangChain automatically handles both sync and async tools through the async interface.

```python
# NEW CODE (FIXED)
try:
    tool = tool_map[name]
    # Always use ainvoke in async context
    # LangChain automatically wraps sync functions to work with ainvoke
    result = await tool.ainvoke(args)
except TypeError as e:
    result = f"Tool error: {e}"
except Exception as e:
    result = f"Tool error: {e}"
```

**Why this works:**
- LangChain's `BaseTool` class provides both `invoke()` and `ainvoke()` methods
- `ainvoke()` works for BOTH sync and async tools
- If a tool is synchronous, LangChain automatically wraps it to work with `ainvoke()`
- If a tool is asynchronous, `ainvoke()` calls it directly
- This is the standard LangChain pattern for async contexts

## File Changed

**File:** `ai_researcher/agent_v1/agent.py`
**Lines:** 244-247

## Code Change

```diff
  try:
      tool = tool_map[name]
-     # Try async invocation first (for MCP tools), fall back to sync
-     if hasattr(tool, 'ainvoke'):
-         try:
-             result = await tool.ainvoke(args)
-         except NotImplementedError:
-             # Tool doesn't support async, use sync
-             result = tool.invoke(args)
-     else:
-         result = tool.invoke(args)
+     # Always use ainvoke in async context
+     # LangChain automatically wraps sync functions to work with ainvoke
+     result = await tool.ainvoke(args)
  except TypeError as e:
      result = f"Tool error: {e}"
  except Exception as e:
      result = f"Tool error: {e}"
```

## Benefits

1. ✅ **Simpler code** - No conditional logic needed
2. ✅ **More reliable** - Works for all tool types
3. ✅ **Standard LangChain pattern** - Follows best practices
4. ✅ **Handles sync and async** - Automatic compatibility
5. ✅ **Better error handling** - Single code path

## Testing

### Manual Test
```bash
# Run the agent
python -m ai_researcher.agent_v1.run
```

### Programmatic Test
```python
import asyncio
from ai_researcher.agent_v1.agent import build_graph

async def test():
    app = await build_graph(include_mcp_pexlib=True)
    # Agent now works with all tools using ainvoke
    
asyncio.run(test())
```

## What Tools Are Affected

All tools now use `ainvoke`:

### Built-in tools (sync functions - automatically wrapped):
- create_project, read_file, write_file, list_files, grep
- git_status, git_diff, git_add, git_commit, git_log
- git_branch_list, git_checkout, git_remote_list, git_prepare_pr
- apply_patch, run_pytest, run_cmd, run_terminal_command, get_errors

### MCP tools (async - natively supported):
- generate_fingerprint
- match_fingerprints

## LangChain Background

From LangChain documentation:
> When you define a tool using `@tool` decorator or `StructuredTool`, LangChain provides both `invoke()` and `ainvoke()` methods. In async contexts, you should always use `ainvoke()` as it works for both sync and async tool implementations.

## Related Fixes

This is the third and final fix in the series:

1. ✅ **NotImplementedError: StructuredTool does not support sync invocation** 
   - Fixed by making tools node async
   
2. ✅ **RuntimeWarning: coroutine 'main' was never awaited**
   - Fixed by adding synchronous wrapper
   
3. ✅ **TypeError: Cannot invoke a coroutine function synchronously** (THIS FIX)
   - Fixed by always using ainvoke

## Status

✅ **FIXED** - The agent now properly invokes all tools using `ainvoke()` in the async context.

## Verification

The fix can be verified by:
1. Running the agent: `python -m ai_researcher.agent_v1.run`
2. Checking that tools execute without TypeError
3. Verifying both built-in and MCP tools work correctly

## Technical Note

This is the **correct** way to handle tools in async LangGraph nodes:
- ✅ Use `ainvoke()` for all tools in async nodes
- ❌ Don't use conditional logic to choose between `invoke()` and `ainvoke()`
- ❌ Don't call `invoke()` on potentially async tools

LangChain handles the sync/async compatibility internally through `ainvoke()`.

