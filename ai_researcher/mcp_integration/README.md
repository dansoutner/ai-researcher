# MCP Integration for AI Researcher

This module provides shared MCP (Model Context Protocol) integration that works with all agent versions (v1, v2, v3, and future agents).

## Overview

The MCP integration allows you to:
- Connect to MCP servers and load their tools
- Convert MCP tools to LangChain-compatible tools
- Use MCP tools with any agent implementation
- Easily add new MCP servers

## Quick Start

### Basic Usage

```python
from ai_researcher.mcp_integration import get_mcp_tools

# Get tools from specific servers
tools = await get_mcp_tools(['pexlib', 'arxiv'], verbose=True)

# Use the tools with your agent...
```

### Get All Available Tools

```python
from ai_researcher.mcp_integration import get_mcp_tools, get_all_mcp_servers

# Load tools from all available MCP servers
all_tools = await get_mcp_tools(get_all_mcp_servers(), verbose=True)
```

## Agent-Specific Integration

### Agent V1

Agent V1 has built-in MCP integration through `mcp_integration.py`:

```python
from ai_researcher.agent_v1.mcp_integration import get_all_tools

# Get all tools including MCP tools
tools = await get_all_tools(
    include_pexlib=True,
    include_arxiv=True,
    verbose=True
)

# Use with agent
from ai_researcher.agent_v1.agent import create_agent
agent = create_agent(tools=tools)
```

Or use the shared module:

```python
from ai_researcher.mcp_integration import get_mcp_tools
from ai_researcher.agent_v1.tools import DEFAULT_TOOLS

# Get MCP tools
mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'])

# Combine with default agent tools
all_tools = DEFAULT_TOOLS + mcp_tools

# Use with agent
from ai_researcher.agent_v1.agent import create_agent
agent = create_agent(tools=all_tools)
```

### Agent V2

```python
from ai_researcher.mcp_integration import get_mcp_tools
from ai_researcher.agent_v2.tooling import build_tool_registry

# Get MCP tools
mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'])

# Combine with existing tools
all_tools = build_tool_registry() + mcp_tools

# Use with your agent...
```

### Agent V3 (Claude)

```python
from ai_researcher.mcp_integration import get_mcp_tools
from ai_researcher.agent_v3_claude.agent import run

# Get MCP tools
mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'])

# The tools can be passed to the agent's tool registry
# (Implementation depends on how agent_v3 manages tools)
```

## Available MCP Servers

### Pexlib
Audio fingerprinting and asset management tools.

```python
tools = await get_mcp_tools(['pexlib'])
```

### ArXiv
Research paper search and retrieval from arXiv.

```python
tools = await get_mcp_tools(['arxiv'])
```

## Advanced Usage

### Custom Server Parameters

```python
from ai_researcher.mcp_integration import create_mcp_server_params, load_mcp_tools

# Create custom server parameters
server_params = create_mcp_server_params(
    command="node",
    args=["path/to/your/server/index.js"],
    env={"CUSTOM_VAR": "value"},
    cwd="/path/to/working/dir"
)

# Load tools
tools = await load_mcp_tools(server_params, verbose=True)
```

### Using Server Configurations

```python
from ai_researcher.mcp_integration import MCPServerConfig, get_mcp_tools

# Create a custom server configuration
custom_server = MCPServerConfig(
    name="my_server",
    command="python",
    args=["server.py"],
    description="My custom MCP server"
)

# Load tools from multiple configurations
tools = await get_mcp_tools([custom_server, 'pexlib', 'arxiv'])
```

### Adding New MCP Servers

To add a new MCP server:

1. Add a configuration function to `servers.py`:

```python
def get_myserver_server_config(repo_root: Optional[str] = None) -> MCPServerConfig:
    """Get server configuration for my custom MCP server."""
    # ... implementation
    return MCPServerConfig(
        name="myserver",
        command="node",
        args=[str(server_path)],
        description="My custom server description"
    )
```

2. Update `get_all_mcp_servers()` in `servers.py`:

```python
def get_all_mcp_servers(repo_root: Optional[str] = None) -> List[MCPServerConfig]:
    return [
        get_pexlib_server_config(repo_root),
        get_arxiv_server_config(repo_root),
        get_myserver_server_config(repo_root),  # Add your server
    ]
```

3. Use it:

```python
tools = await get_mcp_tools(['myserver'])
```

## Module Structure

```
ai_researcher/mcp_integration/
├── __init__.py      # Public API exports
├── servers.py       # Server configuration and management
├── loader.py        # Tool loading from MCP servers
└── README.md        # This file
```

## API Reference

### High-Level Functions

- `get_mcp_tools(servers, repo_root=None, verbose=False)` - Load tools from multiple servers
- `get_mcp_tools_by_name(server_names, repo_root=None, verbose=False)` - Load tools by server name
- `get_all_mcp_servers(repo_root=None)` - Get all available server configurations

### Server Configuration

- `create_mcp_server_params(command, args, env=None, cwd=None)` - Create server parameters
- `get_pexlib_server_params(repo_root=None)` - Get pexlib server parameters
- `get_arxiv_server_params(repo_root=None)` - Get arxiv server parameters
- `MCPServerConfig` - Dataclass for server configuration

### Low-Level Functions

- `load_mcp_tools(server_params, verbose=False)` - Load tools from a single server
- `load_mcp_tools_from_config(config, verbose=False)` - Load tools using MCPServerConfig

## Testing

Run the demo to verify MCP integration:

```bash
# Demo the shared integration
python -m ai_researcher.mcp_integration.loader

# Demo agent v1 integration
python -m ai_researcher.agent_v1.mcp_integration
```

## Future Agents

This module is designed to be forward-compatible. Any new agent can use the shared MCP integration:

```python
from ai_researcher.mcp_integration import get_mcp_tools

# In your new agent
async def setup_agent_with_mcp():
    mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'])
    # Combine with your agent's tools...
```

## Troubleshooting

### Server Not Found

If you get "Unknown MCP server" warning:
- Check that the server name is correct
- Verify the server is added to `get_all_mcp_servers()`
- Check that the server files exist in `mcp_servers/` directory

### Connection Errors

If MCP tools fail to load:
- Verify Node.js is installed (for Node-based servers)
- Check that server files are built (check `dist/` directories)
- Use `verbose=True` to see detailed error messages

### Import Errors

Make sure required dependencies are installed:
```bash
pip install langchain-core mcp
```

## Related Documentation

- [Agent V1 MCP Usage](../agent_v1/MCP_USAGE.md)
- [Agent V1 MCP Quick Reference](../agent_v1/mcp_quick_reference.py)
- [MCP Quick Reference](../../QUICK_REFERENCE_MCP.md)

