# HuggingFace MCP Integration - Quick Reference

## Quick Start

```python
from ai_researcher.mcp_integration import (
    get_huggingface_server_config,
    get_mcp_tools,
    get_all_mcp_servers
)

# Get HuggingFace server configuration
hf_config = get_huggingface_server_config()

# Load tools from HuggingFace (once HTTP support is implemented)
hf_tools = await get_mcp_tools(['huggingface'], verbose=True)

# Load from all servers including HuggingFace
all_tools = await get_mcp_tools(get_all_mcp_servers(), verbose=True)
```

## Server Details

- **Name**: `huggingface`
- **Type**: HTTP
- **URL**: `https://huggingface.co/mcp?login`
- **Registry**: `https://api.mcp.github.com` (v0.1)
- **Server Version**: 1.0.0

## Server Configuration Structure

```python
MCPHttpServerConfig(
    name="huggingface",
    url="https://huggingface.co/mcp?login",
    headers=None,  # Optional for authentication
    metadata={
        "registry": {
            "api": {
                "baseUrl": "https://api.mcp.github.com",
                "version": "v0.1"
            },
            "mcpServer": {
                "name": "huggingface/hf-mcp-server",
                "version": "1.0.0"
            }
        }
    },
    description="HuggingFace model, dataset, and space tools via HTTP MCP server"
)
```

## Usage Patterns

### 1. Get Server Config Only
```python
config = get_huggingface_server_config()
print(f"Name: {config.name}")
print(f"Type: {config.type}")
print(f"URL: {config.url}")
```

### 2. List All Available Servers
```python
all_servers = get_all_mcp_servers()
server_names = [s.name for s in all_servers]
# Output: ['pexlib', 'arxiv', 'huggingface']
```

### 3. Get Server by Name
```python
from ai_researcher.mcp_integration import get_server_by_name

hf_server = get_server_by_name('huggingface')
if hf_server:
    print(f"Found: {hf_server.name}")
```

### 4. Load HuggingFace Tools
```python
# Once HTTP support is implemented
hf_tools = await get_mcp_tools(['huggingface'], verbose=True)
```

### 5. Combine with Other Servers
```python
# Load from multiple servers
tools = await get_mcp_tools(
    ['pexlib', 'arxiv', 'huggingface'],
    verbose=True
)
```

### 6. Use with Agent V3
```python
from ai_researcher.agent_v3_claude.agent import run
from ai_researcher.mcp_integration import get_mcp_tools

# Get MCP tools including HuggingFace
mcp_tools = await get_mcp_tools(['huggingface'])

# Pass to agent (once HTTP support is implemented)
# agent = create_agent(tools=mcp_tools + other_tools)
```

## Current Status

⚠️ **HTTP support is in development**

When you attempt to load HuggingFace tools, you'll see:
```
⚠ Warning: HTTP MCP server support is not yet implemented for huggingface
  The HuggingFace MCP server at https://huggingface.co/mcp?login requires HTTP client support.
  This feature will be added in a future update.
```

## Files Modified

- `ai_researcher/mcp_integration/servers.py` - Added HTTP server support
- `ai_researcher/mcp_integration/loader.py` - Added HTTP loader
- `ai_researcher/mcp_integration/__init__.py` - Updated exports
- `ai_researcher/mcp_integration/README.md` - Updated docs

## Files Created

- `docs/HUGGINGFACE_MCP_INTEGRATION.md` - Full documentation
- `docs/HUGGINGFACE_MCP_INTEGRATION_SUMMARY.md` - Summary
- `examples/demo_huggingface_mcp.py` - Demo script

## Demo Script

Run the demo to see the integration:

```bash
python examples/demo_huggingface_mcp.py
```

## API Exports

From `ai_researcher.mcp_integration`:

```python
# HTTP Server Support
MCPHttpServerConfig           # HTTP server config dataclass
get_huggingface_server_config()  # Get HuggingFace config
load_mcp_tools_from_http_config()  # Load tools from HTTP server

# Existing (works with both STDIO and HTTP)
get_mcp_tools()              # Load from any server type
get_all_mcp_servers()        # Get all servers
get_server_by_name()         # Get specific server

# STDIO Server Support (unchanged)
MCPServerConfig              # STDIO server config
create_mcp_server_params()   # Create STDIO params
load_mcp_tools()             # Load from STDIO server
```

## Type Signatures

```python
def get_huggingface_server_config() -> MCPHttpServerConfig:
    """Get HuggingFace server configuration."""

async def load_mcp_tools_from_http_config(
    config: MCPHttpServerConfig,
    verbose: bool = False
) -> List[StructuredTool]:
    """Load tools from HTTP MCP server."""

async def get_mcp_tools(
    servers: Union[List[str], List[MCPServerConfig | MCPHttpServerConfig]],
    repo_root: Optional[str] = None,
    verbose: bool = False
) -> List[BaseTool]:
    """Load tools from multiple servers (STDIO or HTTP)."""
```

## Next Steps

1. Implement HTTP client for MCP
2. Test with HuggingFace endpoint
3. Add authentication support
4. Update documentation once complete

## References

- Full docs: `docs/HUGGINGFACE_MCP_INTEGRATION.md`
- MCP integration README: `ai_researcher/mcp_integration/README.md`
- Demo script: `examples/demo_huggingface_mcp.py`

