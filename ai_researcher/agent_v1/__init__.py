"""Agent V1 - MCP-Enhanced AI Research Agent.

This package provides an AI research agent with Model Context Protocol (MCP)
integration capabilities.

Quick Start:
    # With MCP tools
    from ai_researcher.agent_v1.mcp_integration import get_all_tools
    tools = await get_all_tools(include_pexlib=True)

Modules:
    - mpc_servers: MCP server integration utilities
    - mcp_integration: High-level MCP integration helpers

Note: Other modules (agent, tools, llm, state) are available but not
automatically imported to avoid circular dependencies.
"""

from __future__ import annotations

__version__ = "1.0.0"

# MCP integration - these are the main modules converted for agent use
from . import mpc_servers
from . import mcp_integration

__all__ = [
    "mpc_servers",
    "mcp_integration",
]

