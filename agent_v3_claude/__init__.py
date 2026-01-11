"""Agent v3 with Claude: A planner-executor-reviewer workflow using LangGraph.

This package provides a modular agent system that:
- Plans: Creates step-by-step execution plans
- Executes: Runs each step using available tools
- Reviews: Evaluates results and decides on next actions

The workflow is built using LangGraph and supports multiple LLM providers.
"""

from .agent import run, print_results
from .config import PruningConfig, DEFAULT_MAX_ITERATIONS
from .state import AgentState, ExecutorOutput, create_initial_state

__version__ = "3.0.0"

__all__ = [
    "run",
    "print_results",
    "AgentState",
    "ExecutorOutput",
    "PruningConfig",
    "create_initial_state",
    "DEFAULT_MAX_ITERATIONS",
]

