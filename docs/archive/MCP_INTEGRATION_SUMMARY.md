# Agent V1 MCP Integration - Summary

## Overview
Agent V1 now supports Model Context Protocol (MCP) servers, allowing the agent to use external tools dynamically. This integration enables the agent to access specialized capabilities beyond its built-in tools.

## What Changed

### 1. **agent.py** - Core Agent Module
- **Made `build_graph()` async**: The function now properly handles async MCP tool loading
- **Added MCP parameters**: New parameters `include_mcp_pexlib`, `include_mcp_arxiv`, and `verbose`
- **Tool injection**: Tools are now injected as closures within `build_graph()` for better flexibility
- **Removed module-level async call**: Fixed the incorrect `await get_all_tools()` at module import time

Key changes:
```python
async def build_graph(
    tools: Optional[List[BaseTool]] = None,
    include_mcp_pexlib: bool = False,
    include_mcp_arxiv: bool = False,
    verbose: bool = False
):
    """Build the agent graph with optional MCP tools."""
    if tools is None:
        if include_mcp_pexlib or include_mcp_arxiv:
            from ai_researcher.agent_v1.mcp_integration import get_all_tools
            tools = await get_all_tools(
                include_pexlib=include_mcp_pexlib,
                include_arxiv=include_mcp_arxiv,
                verbose=verbose
            )
        else:
            tools = TOOLS
    # ... rest of function
```

### 2. **run.py** - CLI Entry Point
- **Made `main()` async**: Now uses `asyncio.run()` to support async operations
- **Added environment variables**: 
  - `USE_MCP_PEXLIB` (default: true) - Enable/disable pexlib MCP tools
  - `USE_MCP_ARXIV` (default: false) - Enable/disable arxiv MCP tools
  - `VERBOSE` (default: true) - Show detailed tool loading info
- **Enhanced feedback**: Shows which MCP servers are being loaded

### 3. **mpc_servers.py** - MCP Server Configuration
- **Fixed path resolution**: Now correctly locates MCP servers in the `ai_researcher` package
- **Changed from `os.getcwd()`** to `Path(__file__).parent.parent` for reliable path resolution
- **Better error handling**: Gracefully handles missing MCP servers

### 4. **New Files Created**

#### **MCP_USAGE.md**
Comprehensive documentation on how to use MCP servers with Agent V1, including:
- Quick start guide
- Environment variable reference
- Programmatic usage examples
- Custom tools integration
- Troubleshooting tips

#### **tests/test_agent_v1_mcp.py**
Test suite for MCP integration with three test cases:
- Building graph without MCP tools
- Building graph with pexlib MCP tools
- Building graph with custom tools

## How to Use

### Basic Usage (CLI)
```bash
# Run with default settings (pexlib enabled)
python -m ai_researcher.agent_v1.run

# Disable all MCP tools
USE_MCP_PEXLIB=false python -m ai_researcher.agent_v1.run

# Enable both pexlib and arxiv
USE_MCP_PEXLIB=true USE_MCP_ARXIV=true python -m ai_researcher.agent_v1.run
```

### Programmatic Usage
```python
import asyncio
from ai_researcher.agent_v1.agent import build_graph

async def run_agent():
    # Build with MCP tools
    app = await build_graph(
        include_mcp_pexlib=True,
        include_mcp_arxiv=False,
        verbose=True
    )
    
    # Run agent
    state = {
        "goal": "Your task here",
        "repo_root": "",
        "messages": [],
        "done": False
    }
    
    for event in app.stream(state, stream_mode="values"):
        # Process events
        pass

asyncio.run(run_agent())
```

## Benefits

1. **Extensibility**: Easy to add new MCP servers without modifying core agent code
2. **Graceful Degradation**: If MCP servers fail to load, agent continues with default tools
3. **Flexible Configuration**: Control MCP servers via environment variables or function parameters
4. **Type Safety**: Proper async/await patterns and type hints
5. **Backwards Compatible**: Can still use agent without MCP servers

## Available MCP Tools

### Pexlib MCP Server
- `generate_fingerprint`: Generate audio fingerprints
- `match_fingerprints`: Match audio fingerprints against database

### Arxiv MCP Server (when enabled)
- Search and retrieve academic papers
- Access paper metadata
- Download PDFs

## Testing

Run the test suite:
```bash
# Manual tests
python tests/test_agent_v1_mcp.py

# With pytest
pytest tests/test_agent_v1_mcp.py -v
```

## Technical Details

### Architecture
- **Async by default**: All tool loading is async to support MCP's async nature
- **Closure pattern**: Tools are captured in closures within `build_graph()` for proper scoping
- **Error handling**: MCP server failures are caught and logged, allowing fallback to default tools
- **Path resolution**: Uses `Path(__file__).parent.parent` for reliable package-relative paths

### Error Handling
The integration includes robust error handling:
```python
try:
    pexlib_tools = await load_mcp_tools(pexlib_params, verbose=verbose)
    all_tools.extend(pexlib_tools)
except Exception as e:
    print(f"⚠ Warning: Failed to load pexlib tools: {e}")
```

This ensures the agent can still function even if MCP servers are unavailable.

## Future Enhancements

Possible improvements:
1. Hot-reload MCP servers during runtime
2. Add more MCP servers (web search, code execution, etc.)
3. Per-tool enable/disable configuration
4. MCP server health monitoring
5. Tool usage analytics

## Migration Guide

If you were using Agent V1 before this change:

**Old way (synchronous):**
```python
from ai_researcher.agent_v1.agent import build_graph
app = build_graph()
```

**New way (async):**
```python
import asyncio
from ai_researcher.agent_v1.agent import build_graph

async def main():
    app = await build_graph()
    
asyncio.run(main())
```

Or use the default settings which enable MCP automatically:
```python
app = await build_graph(include_mcp_pexlib=True)
```

## Summary

The agent can now use MCP servers! 🎉

- ✅ Async support for MCP tool loading
- ✅ Environment variable configuration
- ✅ Graceful error handling
- ✅ Comprehensive documentation
- ✅ Test coverage
- ✅ Backwards compatible

