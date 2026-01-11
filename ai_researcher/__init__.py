"""
AI Researcher - Autonomous AI agent implementations for research and development tasks.

This package contains multiple agent architectures and supporting tools.
"""

__version__ = "0.1.0"

# Make key components easily importable
from ai_researcher.agent_v3_claude.agent import run as run_v3
from ai_researcher.agent_v3_claude.state import AgentState

__all__ = [
    "run_v3",
    "AgentState",
    "__version__",
]

