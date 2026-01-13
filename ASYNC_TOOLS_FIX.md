# Fix for NotImplementedError: StructuredTool does not support sync invocation

## Problem
When using MCP tools with Agent V1, the following error occurred:
```
NotImplementedError: StructuredTool does not support sync invocation.
During task with name 'tools' and id 'a100069f-3a33-f37d-3617-14cf9bafdc3b'
```

Additionally, there was a RuntimeWarning:
```
RuntimeWarning: coroutine 'main' was never awaited
```

## Root Cause
1. **MCP tools are async-only**: MCP tools (StructuredTool) only support async invocation via `ainvoke()`, not sync invocation via `invoke()`
2. **Tools node was synchronous**: The `_tools_node_with_tools` function was calling `tool.invoke()` synchronously
3. **main() was async**: The `main()` function in run.py was async, causing issues when imported as a module

## Solution

### 1. Made Tools Node Async (agent.py)

Changed `_tools_node_with_tools` from synchronous to async and added logic to handle both sync and async tools:

```python
async def _tools_node_with_tools(state: AgentState) -> AgentState:
    # ...existing code...
    
    for call in tool_calls:
        # ...existing code...
        
        try:
            tool = tool_map[name]
            # Try async invocation first (for MCP tools), fall back to sync
            if hasattr(tool, 'ainvoke'):
                try:
                    result = await tool.ainvoke(args)
                except NotImplementedError:
                    # Tool doesn't support async, use sync
                    result = tool.invoke(args)
            else:
                result = tool.invoke(args)
        except TypeError as e:
            result = f"Tool error: {e}"
        except Exception as e:
            result = f"Tool error: {e}"
```

**Key changes:**
- Made the function `async`
- Check if tool has `ainvoke` method
- Use `await tool.ainvoke(args)` for async tools (MCP)
- Fall back to `tool.invoke(args)` for sync tools (built-in)
- Added comprehensive error handling

### 2. Fixed RuntimeWarning (run.py)

Renamed the async function and added a synchronous wrapper:

```python
async def async_main(argv: list[str] | None = None) -> int:
    # ...existing implementation...
    return 0


def main(argv: list[str] | None = None) -> int:
    """Synchronous wrapper for async_main."""
    return asyncio.run(async_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
```

**Key changes:**
- Renamed `main()` to `async_main()`
- Created synchronous `main()` wrapper that calls `asyncio.run(async_main(argv))`
- Ensures proper async handling when imported as a module

## Testing

Created comprehensive tests to verify the fix:

### test_async_mcp_tools.py
```bash
$ python tests/test_async_mcp_tools.py

Building agent with MCP tools...
✓ Loaded 2 pexlib MCP tools

✓ Agent built successfully with async tools node
✓ Async MCP tools (using ainvoke)
✓ Sync built-in tools (using invoke)
✓ Automatic fallback if ainvoke not supported

🎉 Success! The NotImplementedError is fixed.
```

### test_agent_v1_mcp.py
```bash
$ python tests/test_agent_v1_mcp.py

Testing Agent V1 with MCP integration...
1. Testing without MCP... ✓ Passed
2. Testing with pexlib MCP... ✓ Passed
3. Testing with custom tools... ✓ Passed
4. Testing async tools invocation... ✓ Passed

✅ All tests passed!
```

## Benefits

1. ✅ **MCP tools work correctly**: Async MCP tools can now be invoked without errors
2. ✅ **Backwards compatible**: Built-in sync tools continue to work
3. ✅ **Graceful fallback**: If a tool claims to support async but doesn't, falls back to sync
4. ✅ **Better error handling**: Catches and reports tool errors clearly
5. ✅ **No RuntimeWarning**: Proper async handling in run.py

## Files Modified

1. **ai_researcher/agent_v1/agent.py**
   - Made `_tools_node_with_tools` async
   - Added logic to detect and use `ainvoke` for async tools
   - Enhanced error handling

2. **ai_researcher/agent_v1/run.py**
   - Renamed `main()` to `async_main()`
   - Added synchronous `main()` wrapper
   - Fixed async invocation pattern

3. **tests/test_agent_v1_mcp.py**
   - Added test for async tools invocation

4. **tests/test_async_mcp_tools.py** (new)
   - Comprehensive test for async MCP tool support

## Technical Details

### How it works

1. When a tool call is made, the tools node checks if the tool has `ainvoke` method
2. If yes, it uses `await tool.ainvoke(args)` (for MCP tools)
3. If no, or if `ainvoke` raises NotImplementedError, it uses `tool.invoke(args)` (for built-in tools)
4. This allows mixing async MCP tools and sync built-in tools seamlessly

### Why this approach

- **Non-breaking**: Existing built-in tools continue to work without modification
- **Future-proof**: New async tools automatically work
- **Robust**: Multiple fallback mechanisms prevent failures
- **Simple**: Minimal code changes with maximum compatibility

## Verification

Run these commands to verify the fix:

```bash
# Test imports
python -c "from ai_researcher.agent_v1.run import main; print('✓ No RuntimeWarning')"

# Test MCP tools
python tests/test_async_mcp_tools.py

# Test full suite
python tests/test_agent_v1_mcp.py

# Run agent (will prompt for input)
python -m ai_researcher.agent_v1.run
```

## Status

✅ **FIXED** - Both the NotImplementedError and RuntimeWarning are resolved. Agent V1 now properly supports async MCP tools alongside sync built-in tools.

