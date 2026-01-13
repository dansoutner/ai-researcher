"""MCP Integration Module for Agent V1.

This module provides easy integration of MCP tools with agent_v1.
It handles loading MCP tools and merging them with existing agent tools.

NOTE: This module now uses the shared MCP integration from ai_researcher.mcp_integration.
      The shared module can be used with any agent version (v1, v2, v3, and future agents).

Usage:
    from ai_researcher.agent_v1.mcp_integration import get_all_tools

    # Get all tools including MCP tools
    tools = await get_all_tools(include_pexlib=True, include_arxiv=True)

    # Use tools with your agent
    from ai_researcher.agent_v1.agent import create_agent
    agent = create_agent(tools=tools)

Alternative (using shared module directly):
    from ai_researcher.mcp_integration import get_mcp_tools
    from ai_researcher.agent_v1.mcp_integration import DEFAULT_TOOLS

    # Get MCP tools
    mcp_tools = await get_mcp_tools(['pexlib', 'arxiv'])

    # Combine with default agent tools
    all_tools = DEFAULT_TOOLS + mcp_tools
"""

from __future__ import annotations

import asyncio
from typing import List, Optional
from langchain_core.tools import BaseTool

# Use shared MCP integration
from ai_researcher.mcp_integration import (
    get_mcp_tools_by_name,
    get_pexlib_server_params,
    get_arxiv_server_params,
    load_mcp_tools,
)

from .tools import (
    create_project,
    read_file,
    write_file,
    list_files,
    grep,
    git_diff,
    git_status,
    git_add,
    git_commit,
    git_log,
    git_branch_list,
    git_checkout,
    git_remote_list,
    git_prepare_pr,
    apply_patch,
    run_pytest,
    run_cmd,
)


# Default agent tools
DEFAULT_TOOLS = [
    create_project,
    read_file,
    write_file,
    list_files,
    grep,
    git_status,
    git_diff,
    git_add,
    git_commit,
    git_log,
    git_branch_list,
    git_checkout,
    git_remote_list,
    git_prepare_pr,
    apply_patch,
    run_pytest,
    run_cmd,
]


async def get_all_tools(
    include_pexlib: bool = False,
    include_arxiv: bool = False,
    repo_root: Optional[str] = None,
    verbose: bool = False,
) -> List[BaseTool]:
    """Get all tools for the agent, including optional MCP tools.

    Args:
        include_pexlib: Whether to include pexlib MCP tools
        include_arxiv: Whether to include arxiv MCP tools
        repo_root: Root directory of the repository (defaults to current working directory)
        verbose: Whether to print debug information

    Returns:
        List of all LangChain tools to use with the agent

    Example:
        # Get all tools including pexlib
        tools = await get_all_tools(include_pexlib=True, verbose=True)

        # Use with agent
        from ai_researcher.agent_v1.agent import create_agent
        agent = create_agent(tools=tools)
    """
    all_tools = DEFAULT_TOOLS.copy()

    # Build list of MCP servers to load
    server_names = []
    if include_pexlib:
        server_names.append('pexlib')
    if include_arxiv:
        server_names.append('arxiv')

    # Load MCP tools if any servers are requested
    if server_names:
        try:
            mcp_tools = await get_mcp_tools_by_name(
                server_names,
                repo_root=repo_root,
                verbose=verbose
            )
            all_tools.extend(mcp_tools)
        except Exception as e:
            print(f"⚠ Warning: Failed to load MCP tools: {e}")
            if verbose:
                import traceback
                traceback.print_exc()

    return all_tools


async def get_mcp_tools_only(
    include_pexlib: bool = True,
    include_arxiv: bool = False,
    repo_root: Optional[str] = None,
    verbose: bool = False,
) -> List[BaseTool]:
    """Get only MCP tools without default agent tools.

    Args:
        include_pexlib: Whether to include pexlib MCP tools
        include_arxiv: Whether to include arxiv MCP tools
        repo_root: Root directory of the repository (defaults to current working directory)
        verbose: Whether to print debug information

    Returns:
        List of MCP tools
    """
    # Build list of MCP servers to load
    server_names = []
    if include_pexlib:
        server_names.append('pexlib')
    if include_arxiv:
        server_names.append('arxiv')

    # Load MCP tools if any servers are requested
    if server_names:
        try:
            return await get_mcp_tools_by_name(
                server_names,
                repo_root=repo_root,
                verbose=verbose
            )
        except Exception as e:
            print(f"⚠ Warning: Failed to load MCP tools: {e}")
            if verbose:
                import traceback
                traceback.print_exc()

    return []


async def demo():
    """Demo showing how to use MCP integration."""
    print("=== MCP Integration Demo ===\n")

    # Get all tools including MCP tools
    print("Loading tools...")
    tools = await get_all_tools(
        include_pexlib=True,
        include_arxiv=True,
        verbose=True
    )

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

