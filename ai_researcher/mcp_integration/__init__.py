"""Shared MCP (Model Context Protocol) Integration for all AI Researcher agents.

This module provides MCP server integration that can be used with any agent version
(v1, v2, v3, or future agents). It handles loading MCP tools and converting them to
LangChain-compatible tools.

Quick Start:
    ```python
    from ai_researcher.mcp_integration import get_mcp_tools, get_all_mcp_servers

    # Get tools from specific servers (including HTTP servers like HuggingFace)
    tools = await get_mcp_tools(['pexlib', 'arxiv', 'huggingface'])

    # Get tools from all available servers
    all_tools = await get_mcp_tools(get_all_mcp_servers())
    ```

For agent-specific examples, see the respective agent documentation.
"""

from .servers import (
    create_mcp_server_params,
    get_pexlib_server_params,
    get_arxiv_server_params,
    get_huggingface_server_config,
    get_all_mcp_servers,
    MCPServerConfig,
    MCPHttpServerConfig,
)

from .loader import (
    load_mcp_tools,
    load_mcp_tools_from_http_config,
    get_mcp_tools,
    get_mcp_tools_by_name,
)

__all__ = [
    # Server configuration
    "create_mcp_server_params",
    "get_pexlib_server_params",
    "get_arxiv_server_params",
    "get_huggingface_server_config",
    "get_all_mcp_servers",
    "MCPServerConfig",
    "MCPHttpServerConfig",
    # Tool loading
    "load_mcp_tools",
    "load_mcp_tools_from_http_config",
    "get_mcp_tools",
    "get_mcp_tools_by_name",
]

