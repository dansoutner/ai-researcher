# MCP Integration Guide - All Agents

This guide explains how to use MCP (Model Context Protocol) integration with all AI Researcher agents (v1, v2, v3, and future agents).

## Quick Overview

The AI Researcher package now includes a **shared MCP integration module** that works with all agent versions. This means:

1. ✅ **Single source of truth** - One module manages all MCP servers
2. ✅ **Easy to use** - Same API across all agents
3. ✅ **Future-proof** - New agents can use it immediately
4. ✅ **Extensible** - Easy to add new MCP servers

## Installation

```bash
# Install the ai_researcher package (if not already installed)
pip install -e .

# Make sure MCP dependencies are installed
pip install langchain-core mcp
```

## Basic Usage (Any Agent)

```python
# Import from the main package
from ai_researcher import get_mcp_tools

# Get MCP tools from specific servers
mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'], verbose=True)

# Use with your agent...
```

## Agent-Specific Examples

### Agent V1 - Built-in Integration

Agent V1 has the most mature integration with convenience functions:

```python
from ai_researcher.agent_v1.mcp_integration import get_all_tools

# Method 1: Use the convenience function
tools = await get_all_tools(
    include_pexlib=True,
    include_arxiv=True,
    verbose=True
)

# Method 2: Use the shared module directly
from ai_researcher import get_mcp_tools
from ai_researcher.agent_v1.mcp_integration import DEFAULT_TOOLS

mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'])
all_tools = DEFAULT_TOOLS + mcp_tools

# Use with agent
from ai_researcher.agent_v1.agent import create_agent
agent = create_agent(tools=all_tools)
```

### Agent V2 - Simple Integration

```python
from ai_researcher import get_mcp_tools
from ai_researcher.agent_v2.tooling import build_tool_registry

# Get your base tools
base_tools = build_tool_registry()

# Add MCP tools
mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'], verbose=True)
all_tools = base_tools + mcp_tools

# Use with Agent V2...
```

Or use the integration helper:

```python
from ai_researcher.agent_v2.mcp_integration import get_agent_v2_tools_with_mcp

tools = await get_agent_v2_tools_with_mcp(
    include_pexlib=True,
    include_arxiv=True,
    verbose=True
)
```

### Agent V3 (Claude) - Simple Integration

```python
from ai_researcher import get_mcp_tools

# Get MCP tools
mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'], verbose=True)

# Integrate with Agent V3's tool system
# (Depends on how agent_v3 manages tools)
```

Or use the integration helper:

```python
from ai_researcher.agent_v3_claude.mcp_integration import get_agent_v3_tools_with_mcp

tools = await get_agent_v3_tools_with_mcp(
    include_pexlib=True,
    include_arxiv=True,
    verbose=True
)
```

### Future Agents - Ready to Go

Any new agent can immediately use MCP integration:

```python
from ai_researcher import get_mcp_tools

# In your new agent setup
async def setup_my_new_agent():
    # Get MCP tools
    mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'])
    
    # Combine with your agent's tools
    my_tools = get_my_agent_tools()
    all_tools = my_tools + mcp_tools
    
    # Initialize agent with all tools
    agent = MyAgent(tools=all_tools)
    return agent
```

## Available MCP Servers

### 1. Pexlib
**Audio fingerprinting and asset management**

```python
tools = await get_mcp_tools(['pexlib'])
```

Provides tools for:
- Audio fingerprinting
- Asset management
- Database operations

### 2. ArXiv
**Research paper search and retrieval**

```python
tools = await get_mcp_tools(['arxiv'])
```

Provides tools for:
- Searching arXiv papers
- Retrieving paper metadata
- Downloading papers

### 3. Get All Servers

```python
from ai_researcher import get_all_mcp_servers, get_mcp_tools

# Get configurations for all available servers
all_servers = get_all_mcp_servers()

# Load tools from all servers
all_tools = await get_mcp_tools(all_servers, verbose=True)
```

## Advanced Usage

### Custom Server Parameters

```python
from ai_researcher.mcp_integration import create_mcp_server_params, load_mcp_tools

# Create custom server configuration
server_params = create_mcp_server_params(
    command="node",
    args=["path/to/your/server.js"],
    env={"CUSTOM_VAR": "value"},
    cwd="/path/to/working/dir"
)

# Load tools
tools = await load_mcp_tools(server_params, verbose=True)
```

### Using Server Configurations

```python
from ai_researcher.mcp_integration import MCPServerConfig, get_mcp_tools

# Define a custom server
custom_server = MCPServerConfig(
    name="my_custom_server",
    command="python",
    args=["my_server.py"],
    description="My custom MCP server"
)

# Load tools from multiple sources
tools = await get_mcp_tools([
    'pexlib',           # Built-in server by name
    'arxiv',            # Another built-in server
    custom_server,      # Custom server config
], verbose=True)
```

## Adding New MCP Servers

Want to add a new MCP server? It's easy!

### Step 1: Add Server Configuration

Edit `ai_researcher/mcp_integration/servers.py`:

```python
def get_myserver_server_config(repo_root: Optional[str] = None) -> MCPServerConfig:
    """Get configuration for my custom server."""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    else:
        repo_root = Path(repo_root)

    server_path = repo_root / "mcp_servers" / "my-server" / "dist" / "index.js"
    
    return MCPServerConfig(
        name="myserver",
        command="node",
        args=[str(server_path)],
        env=os.environ.copy(),
        description="Description of what my server does"
    )
```

### Step 2: Register Server

Update `get_all_mcp_servers()` in the same file:

```python
def get_all_mcp_servers(repo_root: Optional[str] = None) -> List[MCPServerConfig]:
    """Get all available MCP server configurations."""
    return [
        get_pexlib_server_config(repo_root),
        get_arxiv_server_config(repo_root),
        get_myserver_server_config(repo_root),  # Add your server here
    ]
```

### Step 3: Use It

```python
from ai_researcher import get_mcp_tools

# Now you can use it by name
tools = await get_mcp_tools(['myserver', 'pexlib'], verbose=True)
```

## Testing

### Test the Shared Integration

```bash
# Run the shared module demo
python -m ai_researcher.mcp_integration.loader
```

### Test Agent-Specific Integration

```bash
# Agent V1
python -m ai_researcher.agent_v1.mcp_integration

# Agent V2
python -m ai_researcher.agent_v2.mcp_integration

# Agent V3
python -m ai_researcher.agent_v3_claude.mcp_integration
```

## Troubleshooting

### "Unknown MCP server" Warning

**Problem:** You see: `⚠ Warning: Unknown MCP server 'xxx', skipping...`

**Solution:**
1. Check the server name is correct
2. Verify it's added to `get_all_mcp_servers()` in `servers.py`
3. Check the server files exist in `mcp_servers/` directory

### Connection Errors

**Problem:** MCP tools fail to load with connection errors

**Solutions:**
- Verify Node.js is installed: `node --version`
- Check server files are built (look for `dist/` directories)
- Build servers if needed: `cd mcp_servers/xxx && npm install && npm run build`
- Use `verbose=True` for detailed error messages

### Import Errors

**Problem:** Cannot import MCP integration modules

**Solutions:**
```bash
# Make sure dependencies are installed
pip install langchain-core mcp

# Reinstall package in development mode
pip install -e .
```

### Server Not Starting

**Problem:** Server process fails to start

**Solutions:**
1. Check server logs (use `verbose=True`)
2. Verify command and args are correct
3. Check environment variables are set properly
4. Ensure working directory exists

## Architecture

```
ai_researcher/
├── __init__.py              # Exports get_mcp_tools, etc.
├── mcp_integration/         # ✨ Shared MCP integration
│   ├── __init__.py          # Public API
│   ├── servers.py           # Server configurations
│   ├── loader.py            # Tool loading
│   └── README.md            # Detailed documentation
├── agent_v1/
│   └── mcp_integration.py   # Agent V1 convenience wrappers
├── agent_v2/
│   └── mcp_integration.py   # Agent V2 integration example
└── agent_v3_claude/
    └── mcp_integration.py   # Agent V3 integration example
```

## API Reference

### High-Level API

```python
from ai_researcher import (
    get_mcp_tools,           # Load tools from servers
    get_mcp_tools_by_name,   # Load tools by server names
    get_all_mcp_servers,     # Get all server configs
)
```

### Detailed API

See the [MCP Integration README](../ai_researcher/mcp_integration/README.md) for complete API documentation.

## Best Practices

1. **Use server names when possible** - More readable than config objects
   ```python
   # Good
   tools = await get_mcp_tools(['pexlib', 'arxiv'])
   
   # Also good, but more verbose
   tools = await get_mcp_tools([get_pexlib_server_config(), ...])
   ```

2. **Enable verbose mode during development** - Helps debug issues
   ```python
   tools = await get_mcp_tools(['pexlib'], verbose=True)
   ```

3. **Handle errors gracefully** - MCP servers might not be available
   ```python
   try:
       tools = await get_mcp_tools(['pexlib'])
   except Exception as e:
       print(f"Warning: Could not load MCP tools: {e}")
       tools = []  # Fall back to no MCP tools
   ```

4. **Cache tools when possible** - Don't reload for every request
   ```python
   # Load once at startup
   MCP_TOOLS = await get_mcp_tools(['pexlib', 'arxiv'])
   
   # Reuse in agent
   agent = create_agent(tools=DEFAULT_TOOLS + MCP_TOOLS)
   ```

## Related Documentation

- [MCP Integration Module README](../ai_researcher/mcp_integration/README.md) - Complete API reference
- [Agent V1 MCP Usage](../ai_researcher/agent_v1/MCP_USAGE.md) - Agent V1 specific guide
- [MCP Quick Reference](../QUICK_REFERENCE_MCP.md) - Quick reference card

## Future Work

- [ ] Add more MCP servers (e.g., Brave Search, Filesystem, etc.)
- [ ] Implement tool caching/persistence
- [ ] Add server health checks
- [ ] Support for custom tool name prefixes to avoid conflicts
- [ ] Tool composition and chaining

## Contributing

To contribute a new MCP server:

1. Add your server to `mcp_servers/` directory
2. Add configuration in `ai_researcher/mcp_integration/servers.py`
3. Update `get_all_mcp_servers()` to include your server
4. Add tests in `tests/`
5. Update this documentation

---

**Questions?** Check the detailed documentation in the `mcp_integration` module or open an issue on GitHub.

