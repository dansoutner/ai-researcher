# MCP (Model Context Protocol) Integration for Agent V1

This module provides seamless integration of MCP servers with the Agent V1 research agent, allowing you to extend the agent's capabilities with external tools.

## Overview

The MCP integration consists of three main components:

1. **mpc_servers.py** - Core utilities for connecting to MCP servers
2. **mcp_integration.py** - High-level helpers for agent integration
3. Example MCP servers (pexlib, arxiv)

## Quick Start

### Basic Usage

```python
import asyncio
from ai_researcher.agent_v1.mcp_integration import get_all_tools

async def main():
    # Load all tools including MCP tools
    tools = await get_all_tools(
        include_pexlib=True,
        include_arxiv=True,
        verbose=True
    )
    
    # Use with your agent
    # (agent integration code here)
    print(f"Loaded {len(tools)} tools")

asyncio.run(main())
```

### Using Only MCP Tools

```python
from ai_researcher.agent_v1.mcp_integration import get_mcp_tools_only

async def main():
    # Get only MCP tools without default agent tools
    mcp_tools = await get_mcp_tools_only(
        include_pexlib=True,
        verbose=True
    )
    
    for tool in mcp_tools:
        print(f"- {tool.name}: {tool.description}")

asyncio.run(main())
```

## MCP Server Setup

### Creating Custom MCP Server Parameters

```python
from ai_researcher.agent_v1.mpc_servers import (
    create_mcp_server_params,
    load_mcp_tools
)

# Create server parameters
server_params = create_mcp_server_params(
    command="node",
    args=["path/to/your/mcp-server/dist/index.js"],
    env=os.environ.copy(),  # Optional: custom environment variables
    cwd="/path/to/working/directory"  # Optional: working directory
)

# Load tools from the server
tools = await load_mcp_tools(server_params, verbose=True)
```

### Using Built-in MCP Servers

#### Pexlib Server

```python
from ai_researcher.agent_v1.mpc_servers import (
    get_pexlib_server_params,
    load_mcp_tools
)

# Get pexlib server parameters
server_params = get_pexlib_server_params()

# Load pexlib tools
tools = await load_mcp_tools(server_params, verbose=True)
```

#### Arxiv Server

```python
from ai_researcher.agent_v1.mpc_servers import (
    get_arxiv_server_params,
    load_mcp_tools
)

# Get arxiv server parameters
server_params = get_arxiv_server_params()

# Load arxiv tools
tools = await load_mcp_tools(server_params, verbose=True)
```

## Advanced Usage

### Custom Tool Loading

```python
from ai_researcher.agent_v1.mpc_servers import (
    create_mcp_server_params,
    load_mcp_tools
)
from ai_researcher.agent_v1.tools import DEFAULT_TOOLS

async def load_custom_tools():
    # Start with default tools
    all_tools = DEFAULT_TOOLS.copy()
    
    # Add custom MCP server tools
    custom_server_params = create_mcp_server_params(
        command="python",
        args=["my_custom_server.py"]
    )
    
    custom_tools = await load_mcp_tools(
        custom_server_params,
        verbose=True
    )
    
    all_tools.extend(custom_tools)
    return all_tools
```

### Error Handling

```python
from ai_researcher.agent_v1.mcp_integration import get_all_tools

async def safe_tool_loading():
    try:
        tools = await get_all_tools(
            include_pexlib=True,
            include_arxiv=True,
            verbose=True
        )
        print(f"✓ Successfully loaded {len(tools)} tools")
    except Exception as e:
        print(f"✗ Failed to load tools: {e}")
        # Fall back to default tools
        from ai_researcher.agent_v1.tools import DEFAULT_TOOLS
        tools = DEFAULT_TOOLS
        print(f"✓ Using {len(tools)} default tools")
    
    return tools
```

## API Reference

### Core Functions

#### `create_mcp_server_params()`

Create MCP server parameters.

**Parameters:**
- `command` (str): The command to run (e.g., "node", "python")
- `args` (List[str]): Arguments for the command
- `env` (Optional[Dict[str, str]]): Environment variables
- `cwd` (Optional[str]): Working directory

**Returns:** `StdioServerParameters`

#### `load_mcp_tools()`

Load tools from an MCP server.

**Parameters:**
- `server_params` (StdioServerParameters): Server parameters
- `verbose` (bool): Whether to print debug information

**Returns:** `List[StructuredTool]`

#### `get_all_tools()`

Get all tools including optional MCP tools.

**Parameters:**
- `include_pexlib` (bool): Include pexlib MCP tools
- `include_arxiv` (bool): Include arxiv MCP tools
- `repo_root` (Optional[str]): Repository root directory
- `verbose` (bool): Print debug information

**Returns:** `List[BaseTool]`

#### `get_mcp_tools_only()`

Get only MCP tools without default agent tools.

**Parameters:**
- `include_pexlib` (bool): Include pexlib MCP tools
- `include_arxiv` (bool): Include arxiv MCP tools
- `repo_root` (Optional[str]): Repository root directory
- `verbose` (bool): Print debug information

**Returns:** `List[BaseTool]`

## Testing

Run the integration demo:

```bash
# Test MCP servers module
python -m ai_researcher.agent_v1.mpc_servers

# Test MCP integration
python -m ai_researcher.agent_v1.mcp_integration
```

## MCP Server Requirements

For MCP servers to work, ensure:

1. **Node.js** is installed (for Node-based servers)
2. MCP server files are built and available in the correct paths
3. Required environment variables are set (if needed by specific servers)

### Building MCP Servers

```bash
# Build pexlib server
cd mcp_servers/pexlib-mcp-server
npm install
npm run build

# Build arxiv server
cd mcp_servers/arxiv-mcp-server
npm install
npm run build
```

## Troubleshooting

### Server Not Found Error

If you get a "file not found" error:
1. Check that the MCP server is built (`dist/index.js` exists)
2. Verify the path to the server is correct
3. Use `repo_root` parameter to specify correct base directory

### Tool Loading Failures

The integration gracefully handles MCP server failures:
- Warnings are printed but don't crash the program
- Default tools are still available
- Individual server failures don't affect other servers

### Async Context Issues

Remember that MCP tools must be loaded in an async context:

```python
# ✓ Correct
async def main():
    tools = await get_all_tools()

# ✗ Incorrect (synchronous context)
def main():
    tools = get_all_tools()  # This will fail!
```

## Examples

See the demo functions in the modules for working examples:

- `ai_researcher/agent_v1/mpc_servers.py` - `demo_agent()`
- `ai_researcher/agent_v1/mcp_integration.py` - `demo()`

## Contributing

When adding new MCP servers:

1. Add server parameters function (like `get_pexlib_server_params`)
2. Update `mcp_integration.py` to support the new server
3. Add documentation and examples
4. Test with the demo functions

## License

See the main project LICENSE file.

