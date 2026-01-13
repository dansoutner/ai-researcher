"""
AI Researcher - Autonomous AI agent implementations for research and development tasks.

This package contains multiple agent architectures and supporting tools.
"""

__version__ = "0.1.0"

# Make key components easily importable
from ai_researcher.agent_v3_claude.agent import run as run_v3
from ai_researcher.agent_v3_claude.state import AgentState

# MCP Integration (shared across all agents)
from ai_researcher.mcp_integration import (
    get_mcp_tools,
    get_mcp_tools_by_name,
    get_all_mcp_servers,
)

__all__ = [
    # Agent V3
    "run_v3",
    "AgentState",
    # MCP Integration
    "get_mcp_tools",
    "get_mcp_tools_by_name",
    "get_all_mcp_servers",
    # Version
    "__version__",
]

