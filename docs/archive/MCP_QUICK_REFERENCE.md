# MCP Integration Quick Reference

## Import & Use

```python
# Main package import (recommended)
from ai_researcher import get_mcp_tools

# Get tools
tools = await get_mcp_tools(['pexlib', 'arxiv'])
```

## Agent-Specific

```python
# Agent V1
from ai_researcher.agent_v1.mcp_integration import get_all_tools
tools = await get_all_tools(include_pexlib=True, include_arxiv=True)

# Agent V2  
from ai_researcher.agent_v2.mcp_integration import get_agent_v2_tools_with_mcp
tools = await get_agent_v2_tools_with_mcp(include_pexlib=True)

# Agent V3
from ai_researcher.agent_v3_claude.mcp_integration import get_agent_v3_tools_with_mcp
tools = await get_agent_v3_tools_with_mcp(include_pexlib=True)
```

## All Available Functions

```python
from ai_researcher import (
    get_mcp_tools,           # Load tools from servers
    get_mcp_tools_by_name,   # Load by name (alias)
    get_all_mcp_servers,     # Get server configs
)

from ai_researcher.mcp_integration import (
    create_mcp_server_params,  # Create custom server
    get_pexlib_server_params,  # Get pexlib config
    get_arxiv_server_params,   # Get arxiv config
    MCPServerConfig,           # Config dataclass
    load_mcp_tools,            # Low-level loader
)
```

## Available Servers

- `'pexlib'` - Audio fingerprinting & asset management
- `'arxiv'` - Research paper search & retrieval

## Common Patterns

### Pattern 1: Simple Usage
```python
from ai_researcher import get_mcp_tools
tools = await get_mcp_tools(['pexlib'])
```

### Pattern 2: Get All Servers
```python
from ai_researcher import get_all_mcp_servers, get_mcp_tools
servers = get_all_mcp_servers()
tools = await get_mcp_tools(servers)
```

### Pattern 3: Custom Server
```python
from ai_researcher.mcp_integration import MCPServerConfig, get_mcp_tools

my_server = MCPServerConfig(
    name="myserver",
    command="node",
    args=["server.js"],
    description="My server"
)
tools = await get_mcp_tools([my_server])
```

### Pattern 4: Combine with Agent Tools
```python
from ai_researcher import get_mcp_tools

# Get your agent's base tools
base_tools = get_my_agent_tools()

# Add MCP tools
mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'])

# Combine
all_tools = base_tools + mcp_tools
```

## Documentation

- **Complete Guide**: `docs/MCP_ALL_AGENTS_GUIDE.md`
- **Module Docs**: `ai_researcher/mcp_integration/README.md`
- **Summary**: `MCP_INTEGRATION_SUCCESS.md`

## Troubleshooting

**Can't import?**
```bash
pip install -e .
```

**Server not found?**
- Check spelling
- See available: `get_all_mcp_servers()`

**Connection error?**
- Use `verbose=True`
- Check Node.js installed
- Build server: `cd mcp_servers/xxx && npm install && npm run build`

## Architecture

```
ai_researcher/
├── __init__.py              # Main exports
├── mcp_integration/         # Shared module
│   ├── servers.py           # Server configs
│   └── loader.py            # Tool loading
├── agent_v1/mcp_integration.py  # V1 helpers
├── agent_v2/mcp_integration.py  # V2 helpers
└── agent_v3_claude/mcp_integration.py  # V3 helpers
```

## Key Benefits

✅ Universal - Works with all agents  
✅ Simple - One import to use  
✅ Extensible - Easy to add servers  
✅ Type Safe - Full type hints  
✅ Future Proof - Ready for new agents

