#!/usr/bin/env python3
"""Example: Using MCP Integration with Agent V1

This script demonstrates how to load and use MCP tools with the agent.

Usage:
    python examples/example_mcp_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_researcher.agent_v1.mcp_integration import (
    get_all_tools,
    get_mcp_tools_only,
)


async def example_1_all_tools():
    """Example 1: Load all tools including MCP tools."""
    print("=" * 70)
    print("EXAMPLE 1: Loading all tools (default + MCP)")
    print("=" * 70)

    # Load all tools including MCP tools
    tools = await get_all_tools(
        include_pexlib=False,  # Set to True if pexlib server is available
        include_arxiv=False,   # Set to True if arxiv server is available
        verbose=True
    )

    print(f"\n✓ Total tools loaded: {len(tools)}")
    print("\nAvailable tools:")
    for tool in tools:
        tool_name = getattr(tool, "name", str(tool))
        print(f"  - {tool_name}")

    return tools


async def example_2_mcp_only():
    """Example 2: Load only MCP tools."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Loading only MCP tools")
    print("=" * 70)

    # Load only MCP tools
    mcp_tools = await get_mcp_tools_only(
        include_pexlib=False,  # Set to True if pexlib server is available
        include_arxiv=False,   # Set to True if arxiv server is available
        verbose=True
    )

    if mcp_tools:
        print(f"\n✓ MCP tools loaded: {len(mcp_tools)}")
        print("\nMCP tools:")
        for tool in mcp_tools:
            tool_name = getattr(tool, "name", str(tool))
            tool_desc = getattr(tool, "description", "No description")
            if len(tool_desc) > 60:
                tool_desc = tool_desc[:57] + "..."
            print(f"  - {tool_name}")
            print(f"    {tool_desc}")
    else:
        print("\n⚠ No MCP tools loaded (servers may not be available)")

    return mcp_tools


async def example_3_custom_loading():
    """Example 3: Custom tool loading with error handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Custom loading with error handling")
    print("=" * 70)

    try:
        # Attempt to load tools
        tools = await get_all_tools(
            include_pexlib=True,   # Try to load pexlib
            include_arxiv=True,    # Try to load arxiv
            verbose=True
        )
        print(f"\n✓ Successfully loaded {len(tools)} tools")
    except Exception as e:
        print(f"\n✗ Error loading tools: {e}")
        print("  Falling back to default tools...")

        # Import default tools as fallback
        from ai_researcher.agent_v1.tools import (
            read_file, write_file, list_files, grep
        )
        tools = [read_file, write_file, list_files, grep]
        print(f"✓ Using {len(tools)} default tools")

    return tools


async def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("MCP INTEGRATION EXAMPLES")
    print("=" * 70)
    print("\nNote: MCP servers must be built and available for full functionality.")
    print("To build servers:")
    print("  cd mcp_servers/pexlib-mcp-server && npm install && npm run build")
    print("  cd mcp_servers/arxiv-mcp-server && npm install && npm run build")
    print()

    # Run examples
    await example_1_all_tools()
    await example_2_mcp_only()
    await example_3_custom_loading()

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

