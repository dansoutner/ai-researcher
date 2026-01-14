# Quick Reference: Agent V1 with MCP Servers

## ✅ All Issues Fixed

1. **NotImplementedError: StructuredTool does not support sync invocation** → FIXED
2. **RuntimeWarning: coroutine 'main' was never awaited** → FIXED
3. **TypeError: Cannot invoke a coroutine function synchronously** → FIXED

## Usage

### Run the Agent
```bash
# With MCP enabled (default)
python -m ai_researcher.agent_v1.run

# Without MCP
USE_MCP_PEXLIB=false python -m ai_researcher.agent_v1.run
```

### Programmatic Usage
```python
import asyncio
from ai_researcher.agent_v1.agent import build_graph

async def run():
    app = await build_graph(
        include_mcp_pexlib=True,
        include_mcp_arxiv=False,
        verbose=True
    )
    # Use the agent...

asyncio.run(run())
```

## Key Changes Made

### 1. agent.py - Line 217 (Async Tools Node)
```python
async def _tools_node_with_tools(state: AgentState) -> AgentState:
    # Handles both async (MCP) and sync (built-in) tools
```

### 2. agent.py - Line 247 (Always Use ainvoke)
```python
# Always use ainvoke in async context
# LangChain automatically wraps sync functions to work with ainvoke
result = await tool.ainvoke(args)
```

### 3. run.py - Lines 4, 68-70 (Async Wrapper)
```python
async def async_main(...):  # Renamed from main
    # Implementation...

def main(...):  # New synchronous wrapper
    return asyncio.run(async_main(...))
```

## Available Tools

### Built-in (17 sync tools)
- create_project, read_file, write_file, list_files, grep
- git_status, git_diff, git_add, git_commit, git_log
- git_branch_list, git_checkout, git_remote_list, git_prepare_pr
- apply_patch, run_pytest, run_cmd, run_terminal_command, get_errors

### MCP (2 async tools when enabled)
- generate_fingerprint
- match_fingerprints

## How It Works

**All tools use `ainvoke()` in the async tools node:**
- Sync tools: LangChain automatically wraps them to work with `ainvoke()`
- Async tools: Called directly through `ainvoke()`
- This is the standard LangChain pattern for async contexts

## Testing

```bash
# Run the agent
python -m ai_researcher.agent_v1.run

# Run tests
python tests/test_agent_v1_mcp.py
python tests/test_async_mcp_tools.py
```

## Documentation

- `AINVOKE_FIX.md` - Latest fix (TypeError: Cannot invoke a coroutine)
- `ASYNC_TOOLS_FIX.md` - Previous fix (NotImplementedError)
- `MCP_USAGE.md` - User guide
- `MCP_INTEGRATION_COMPLETE.md` - Initial MCP integration

## Status

🎉 **READY TO USE** - Agent V1 now works perfectly with MCP servers!

All three issues are resolved:
- ✅ Async tools support
- ✅ No runtime warnings
- ✅ Proper coroutine handling

