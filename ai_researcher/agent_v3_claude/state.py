"""Agent state management and tool output storage."""

import os
from typing import Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage

from .config import PruningConfig, Verdict


class ExecutorOutput(TypedDict):
    """Structured output from the executor node.

    Attributes:
        success: Whether the execution step completed successfully
        output: Description of what happened during execution
    """
    success: bool
    output: str


class ToolOutputStore:
    """Out-of-band storage for raw tool outputs keyed by tool_call_id.

    This allows us to keep full tool outputs available while only showing
    truncated versions to the LLM to save context window space.
    """

    def __init__(self) -> None:
        self._store: Dict[str, str] = {}

    def put(self, tool_call_id: str, content: str) -> None:
        """Store tool output. First write wins to preserve original content."""
        if tool_call_id:
            self._store.setdefault(tool_call_id, content)

    def get(self, tool_call_id: str) -> Optional[str]:
        """Retrieve stored tool output by ID."""
        return self._store.get(tool_call_id)

    def __len__(self) -> int:
        return len(self._store)


class AgentState(TypedDict):
    """Shared state passed between all agent nodes.

    This is the "blackboard" that all roles (planner, executor, reviewer) read from
    and write to.
    """

    # Conversation history
    messages: List[BaseMessage]

    # Goal and planning
    goal: str
    plan: List[str]
    step_index: int

    # Working directory for tools
    repo_root: str

    # Executor results
    executor_output: Optional[ExecutorOutput]

    # Review loop metadata
    last_result: Optional[str]
    verdict: Optional[Verdict]

    # Iteration control
    max_iters: int
    iters: int

    # Context management
    tool_output_store: ToolOutputStore
    pruning_cfg: PruningConfig


def create_initial_state(
    goal: str,
    max_iters: int = 12,
    pruning_cfg: Optional[PruningConfig] = None,
    repo_root: Optional[str] = None,
) -> AgentState:
    """Create a fresh agent state for a new goal.

    Args:
        goal: The objective for the agent to accomplish
        max_iters: Maximum number of iteration cycles
        pruning_cfg: Optional custom pruning configuration
        repo_root: Working directory for tools (defaults to current directory)
    """
    return {
        "messages": [],
        "goal": goal,
        "plan": [],
        "step_index": 0,
        "repo_root": repo_root or os.getcwd(),
        "executor_output": None,
        "last_result": None,
        "verdict": None,
        "max_iters": max_iters,
        "iters": 0,
        "tool_output_store": ToolOutputStore(),
        "pruning_cfg": pruning_cfg or PruningConfig(),
    }

