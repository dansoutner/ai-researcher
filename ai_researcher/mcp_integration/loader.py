"""MCP Tool Loading and Management.

This module provides utilities to load tools from MCP servers and convert them
to LangChain-compatible tools.
"""

from __future__ import annotations

import asyncio
from typing import List, Union, Optional

from langchain_core.tools import StructuredTool, BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .servers import MCPServerConfig, MCPHttpServerConfig, get_server_by_name, get_all_mcp_servers


async def load_mcp_tools(
    server_params: StdioServerParameters,
    verbose: bool = False
) -> List[StructuredTool]:
    """Load tools from an MCP server and convert them to LangChain tools.

    Args:
        server_params: Server parameters (StdioServerParameters)
        verbose: Whether to print debug information

    Returns:
        List of LangChain StructuredTool instances

    Example:
        ```python
        from ai_researcher.mcp_integration import create_mcp_server_params, load_mcp_tools

        server_params = create_mcp_server_params(
            command="node",
            args=["server/index.js"]
        )
        tools = await load_mcp_tools(server_params, verbose=True)
        ```
    """
    langchain_tools = []

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session and list available tools
            await session.initialize()
            result = await session.list_tools()

            # Convert MCP tools to LangChain tools
            for tool in result.tools:
                # Create a closure to capture the current tool name
                def make_tool_wrapper(tool_name: str):
                    async def _tool_wrapper(**kwargs):
                        return await session.call_tool(tool_name, arguments=kwargs)
                    return _tool_wrapper

                # Create the StructuredTool
                lc_tool = StructuredTool.from_function(
                    name=tool.name,
                    description=tool.description,
                    func=None,  # We only provide async implementation
                    coroutine=make_tool_wrapper(tool.name),
                )
                langchain_tools.append(lc_tool)

            if verbose:
                print(f"Loaded {len(langchain_tools)} MCP tools: {[t.name for t in langchain_tools]}")

    return langchain_tools


async def load_mcp_tools_from_config(
    config: MCPServerConfig,
    verbose: bool = False
) -> List[StructuredTool]:
    """Load tools from an MCP server using MCPServerConfig.

    Args:
        config: Server configuration
        verbose: Whether to print debug information

    Returns:
        List of LangChain StructuredTool instances
    """
    if verbose:
        print(f"Loading MCP tools from {config.name}: {config.description}")

    return await load_mcp_tools(config.to_stdio_params(), verbose=verbose)


async def load_mcp_tools_from_http_config(
    config: MCPHttpServerConfig,
    verbose: bool = False
) -> List[StructuredTool]:
    """Load tools from an HTTP-based MCP server.

    Note: This is a placeholder implementation. Full HTTP MCP support requires
    the MCP library to provide HTTP client functionality or a custom HTTP client
    implementation.

    Args:
        config: HTTP server configuration
        verbose: Whether to print debug information

    Returns:
        List of LangChain StructuredTool instances

    Raises:
        NotImplementedError: HTTP MCP servers are not yet fully supported
    """
    if verbose:
        print(f"Loading MCP tools from HTTP server {config.name}: {config.description}")
        print(f"  URL: {config.url}")

    # TODO: Implement HTTP MCP client support
    # For now, we return an empty list with a warning
    print(f"⚠ Warning: HTTP MCP server support is not yet implemented for {config.name}")
    print(f"  The HuggingFace MCP server at {config.url} requires HTTP client support.")
    print(f"  This feature will be added in a future update.")

    return []


async def get_mcp_tools(
    servers: Union[List[str], List[MCPServerConfig | MCPHttpServerConfig]],
    repo_root: Optional[str] = None,
    verbose: bool = False
) -> List[BaseTool]:
    """Get MCP tools from multiple servers.

    Args:
        servers: List of server names (e.g., ['pexlib', 'arxiv', 'huggingface'])
                 or server config objects (MCPServerConfig or MCPHttpServerConfig)
        repo_root: Root directory of the repository
        verbose: Whether to print debug information

    Returns:
        List of all tools from the specified servers

    Example:
        ```python
        from ai_researcher.mcp_integration import get_mcp_tools

        # Get tools by name
        tools = await get_mcp_tools(['pexlib', 'arxiv', 'huggingface'], verbose=True)

        # Get tools from all available servers
        from ai_researcher.mcp_integration import get_all_mcp_servers
        all_tools = await get_mcp_tools(get_all_mcp_servers())
        ```
    """
    all_tools = []

    for server in servers:
        try:
            # Convert string names to server config
            if isinstance(server, str):
                config = get_server_by_name(server, repo_root)
                if config is None:
                    print(f"⚠ Warning: Unknown MCP server '{server}', skipping...")
                    continue
            else:
                config = server

            # Load tools based on server type
            if isinstance(config, MCPHttpServerConfig):
                tools = await load_mcp_tools_from_http_config(config, verbose=verbose)
            elif isinstance(config, MCPServerConfig):
                tools = await load_mcp_tools_from_config(config, verbose=verbose)
            else:
                print(f"⚠ Warning: Unknown server config type for {getattr(config, 'name', 'unknown')}")
                continue

            all_tools.extend(tools)

            if verbose and tools:
                print(f"✓ Loaded {len(tools)} tools from {config.name}")

        except Exception as e:
            server_name = server if isinstance(server, str) else getattr(server, 'name', 'unknown')
            print(f"⚠ Warning: Failed to load tools from {server_name}: {e}")
            if verbose:
                import traceback
                traceback.print_exc()

    return all_tools


async def get_mcp_tools_by_name(
    server_names: List[str],
    repo_root: Optional[str] = None,
    verbose: bool = False
) -> List[BaseTool]:
    """Get MCP tools from servers specified by name.

    This is a convenience wrapper around get_mcp_tools that only accepts server names.

    Args:
        server_names: List of server names (e.g., ['pexlib', 'arxiv'])
        repo_root: Root directory of the repository
        verbose: Whether to print debug information

    Returns:
        List of all tools from the specified servers
    """
    return await get_mcp_tools(server_names, repo_root=repo_root, verbose=verbose)


async def demo():
    """Demo showing how to use MCP integration."""
    print("=== Shared MCP Integration Demo ===\n")

    # Get all available servers
    all_servers = get_all_mcp_servers()
    print(f"Available MCP servers: {[s.name for s in all_servers]}")
    for server in all_servers:
        print(f"  - {server.name}: {server.description}")

    print("\n" + "="*50 + "\n")

    # Load tools from specific servers
    print("Loading tools from pexlib and arxiv...")
    tools = await get_mcp_tools(['pexlib', 'arxiv'], verbose=True)

    print(f"\n✓ Total tools loaded: {len(tools)}")
    print(f"\nAvailable tools:")
    for tool in tools:
        tool_name = getattr(tool, "name", str(tool))
        tool_desc = getattr(tool, "description", "No description")
        # Truncate long descriptions
        if len(tool_desc) > 80:
            tool_desc = tool_desc[:77] + "..."
        print(f"  - {tool_name}: {tool_desc}")


if __name__ == "__main__":
    asyncio.run(demo())

