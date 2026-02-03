# HuggingFace MCP Server Integration

## Overview

The AI Researcher project now includes integration with the HuggingFace MCP (Model Context Protocol) server, which provides HTTP-based access to HuggingFace models, datasets, and spaces.

## Configuration

The HuggingFace MCP server has been added to the project's MCP integration with the following configuration:

```python
{
  "name": "huggingface",
  "type": "http",
  "url": "https://huggingface.co/mcp?login",
  "metadata": {
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
  }
}
```

## Usage

### Basic Usage

```python
from ai_researcher.mcp_integration import get_mcp_tools

# Get HuggingFace MCP tools
hf_tools = await get_mcp_tools(['huggingface'], verbose=True)
```

### Combined with Other Servers

```python
from ai_researcher.mcp_integration import get_mcp_tools

# Get tools from multiple servers including HuggingFace
tools = await get_mcp_tools(['pexlib', 'arxiv', 'huggingface'], verbose=True)
```

### Get All Available Servers

```python
from ai_researcher.mcp_integration import get_all_mcp_servers, get_mcp_tools

# Get all available MCP servers (including HuggingFace)
all_servers = get_all_mcp_servers()
print(f"Available servers: {[s.name for s in all_servers]}")

# Load tools from all servers
all_tools = await get_mcp_tools(all_servers, verbose=True)
```

### Direct Server Configuration

```python
from ai_researcher.mcp_integration import get_huggingface_server_config

# Get the HuggingFace server configuration
hf_config = get_huggingface_server_config()
print(f"Server: {hf_config.name}")
print(f"URL: {hf_config.url}")
print(f"Type: {hf_config.type}")
print(f"Description: {hf_config.description}")
```

## Implementation Details

### New Classes

- **MCPHttpServerConfig**: A new dataclass for HTTP-based MCP server configurations
  - `name`: Server identifier
  - `url`: HTTP endpoint URL
  - `headers`: Optional HTTP headers (for authentication)
  - `metadata`: Optional metadata about the server
  - `description`: Human-readable description
  - `type`: Returns "http" (property)

### Updated Functions

- **get_all_mcp_servers()**: Now returns both stdio and HTTP server configurations
- **get_server_by_name()**: Can now return either `MCPServerConfig` or `MCPHttpServerConfig`
- **get_mcp_tools()**: Updated to handle both stdio and HTTP server types
- **load_mcp_tools_from_http_config()**: New function for loading tools from HTTP servers

### Server Registry

The HuggingFace server has been added to the server registry alongside existing servers:

1. **pexlib**: Audio fingerprinting and asset management (stdio)
2. **arxiv**: Research paper search and retrieval (stdio)
3. **huggingface**: HuggingFace models, datasets, and spaces (HTTP)

## Current Status

⚠️ **Note**: HTTP MCP server support is currently in development. The configuration and infrastructure are in place, but full HTTP client implementation is pending. When you attempt to load tools from the HuggingFace server, you'll see a warning message:

```
⚠ Warning: HTTP MCP server support is not yet implemented for huggingface
  The HuggingFace MCP server at https://huggingface.co/mcp?login requires HTTP client support.
  This feature will be added in a future update.
```

## Future Implementation

To complete HTTP MCP support, the following tasks remain:

1. Implement HTTP client functionality (may require MCP library updates)
2. Handle authentication for HTTP MCP servers
3. Convert HTTP MCP tool responses to LangChain tools
4. Test with the HuggingFace MCP server endpoint

## Architecture Changes

### File: `ai_researcher/mcp_integration/servers.py`

- Added `MCPHttpServerConfig` dataclass
- Added `get_huggingface_server_config()` function
- Updated type hints to support both config types

### File: `ai_researcher/mcp_integration/loader.py`

- Added `load_mcp_tools_from_http_config()` function
- Updated `get_mcp_tools()` to dispatch to appropriate loader based on config type
- Added warning for unimplemented HTTP support

### File: `ai_researcher/mcp_integration/__init__.py`

- Exported `MCPHttpServerConfig` class
- Exported `get_huggingface_server_config()` function
- Exported `load_mcp_tools_from_http_config()` function
- Updated documentation examples

## Agent Integration

The HuggingFace MCP server can be used with any agent version once HTTP support is fully implemented:

### Agent V1

```python
from ai_researcher.mcp_integration import get_mcp_tools
from ai_researcher.agent_v1.tools import DEFAULT_TOOLS

mcp_tools = await get_mcp_tools(['pexlib', 'arxiv', 'huggingface'])
all_tools = DEFAULT_TOOLS + mcp_tools
```

### Agent V2

```python
from ai_researcher.mcp_integration import get_mcp_tools
from ai_researcher.agent_v2.tooling import build_tool_registry

mcp_tools = await get_mcp_tools(['huggingface'])
all_tools = build_tool_registry() + mcp_tools
```

### Agent V3 (Claude)

```python
from ai_researcher.mcp_integration import get_mcp_tools

mcp_tools = await get_mcp_tools(['huggingface'])
# Pass to agent's tool registry
```

## References

- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [HuggingFace MCP Server](https://huggingface.co/mcp)
- [MCP GitHub API](https://api.mcp.github.com)

