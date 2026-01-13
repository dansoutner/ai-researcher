"""MCP Integration Example for Agent V2.

This example shows how to integrate MCP tools with Agent V2.
"""

from __future__ import annotations

import asyncio
from typing import List
from langchain_core.tools import BaseTool


async def get_agent_v2_tools_with_mcp(
    include_pexlib: bool = False,
    include_arxiv: bool = False,
    verbose: bool = False,
) -> List[BaseTool]:
    """Get Agent V2 tools combined with MCP tools.

    Args:
        include_pexlib: Whether to include pexlib MCP tools
        include_arxiv: Whether to include arxiv MCP tools
        verbose: Whether to print debug information

    Returns:
        List of all tools for Agent V2
    """
    from ai_researcher.mcp_integration import get_mcp_tools_by_name

    # Get base agent v2 tools
    # TODO: Import agent v2 base tools here when available
    base_tools = []

    # Build list of MCP servers
    server_names = []
    if include_pexlib:
        server_names.append('pexlib')
    if include_arxiv:
        server_names.append('arxiv')

    # Load MCP tools if requested
    if server_names:
        try:
            mcp_tools = await get_mcp_tools_by_name(server_names, verbose=verbose)
            base_tools.extend(mcp_tools)
            if verbose:
                print(f"✓ Added {len(mcp_tools)} MCP tools to Agent V2")
        except Exception as e:
            print(f"⚠ Warning: Failed to load MCP tools: {e}")
            if verbose:
                import traceback
                traceback.print_exc()

    return base_tools


async def demo():
    """Demo Agent V2 with MCP tools."""
    print("=== Agent V2 + MCP Integration Demo ===\n")

    tools = await get_agent_v2_tools_with_mcp(
        include_pexlib=True,
        include_arxiv=True,
        verbose=True
    )

    print(f"\n✓ Total tools: {len(tools)}")
    for tool in tools:
        tool_name = getattr(tool, "name", str(tool))
        print(f"  - {tool_name}")


if __name__ == "__main__":
    asyncio.run(demo())

