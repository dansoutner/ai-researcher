"""
LangGraph agent system with planner -> executor -> reviewer workflow.

This module provides the main entry point for running the agent system.
The agent follows a cycle:
1. Planner: Creates execution plan
2. Executor: Executes one step using tools
3. Reviewer: Evaluates results and decides next action
4. Loop continues until goal is achieved or max iterations reached

For implementation details, see the individual modules:
- config: Constants and configuration
- state: State management and data structures
- pruning: Context window management
- tools: Tool registry and execution
- nodes: Role implementations (planner, executor, reviewer)
- routing: Workflow routing logic
- graph: LangGraph construction
"""

from __future__ import annotations

from .config import DEFAULT_MAX_ITERATIONS, PruningConfig
from .graph import build_agent_graph
from .state import AgentState, ExecutorOutput, create_initial_state


# Re-export commonly used items for convenience
__all__ = [
    "run",
    "AgentState",
    "ExecutorOutput",
    "PruningConfig",
]


# =========================
# Main Entry Point
# =========================

def run(
    goal: str,
    max_iters: int = DEFAULT_MAX_ITERATIONS,
    pruning_cfg: PruningConfig | None = None,
) -> AgentState:
    """Run the agent system to completion.

    Args:
        goal: The objective for the agent to accomplish
        max_iters: Maximum number of iteration cycles before stopping
        pruning_cfg: Optional custom pruning configuration

    Returns:
        Final agent state containing results and message history

    Example:
        >>> state = run("Create a Python package with tests that pass")
        >>> print(state["verdict"])
        >>> print(state["last_result"])
    """
    app = build_agent_graph()
    initial_state = create_initial_state(
        goal=goal,
        max_iters=max_iters,
        pruning_cfg=pruning_cfg,
    )

    print(f"[DEBUG] Starting agent run with goal: {goal}")
    print(f"[DEBUG] Max iterations: {max_iters}")
    print(f"[DEBUG] Initial state keys: {list(initial_state.keys())}")

    final_state: AgentState = app.invoke(initial_state)
    return final_state


def print_results(state: AgentState, num_messages: int = 6) -> None:
    """Pretty-print agent results.

    Args:
        state: Final agent state
        num_messages: Number of recent messages to display
    """
    print("\n" + "=" * 60)
    print("AGENT EXECUTION COMPLETE")
    print("=" * 60)

    print(f"\nGoal: {state['goal']}")
    print(f"Iterations: {state['iters']}/{state['max_iters']}")
    print(f"Verdict: {state.get('verdict', 'N/A')}")

    executor_output = state.get("executor_output")
    if executor_output:
        status = "✓ SUCCESS" if executor_output["success"] else "✗ FAILED"
        print(f"Executor Status: {status}")

    print("\n" + "-" * 60)
    print("FINAL REVIEW")
    print("-" * 60)
    print(state.get("last_result", "No result"))

    print("\n" + "-" * 60)
    print(f"MESSAGE TRACE (last {num_messages})")
    print("-" * 60)

    for msg in state["messages"][-num_messages:]:
        role = msg.__class__.__name__
        content = getattr(msg, "content", "")
        print(f"\n[{role}]")
        print(content[:500] + ("..." if len(content) > 500 else ""))


if __name__ == "__main__":
    # Example usage
    goal = "Run `pytest` in the repo, fix failing tests, and summarize what changed."

    state = run(goal, max_iters=10)
    print_results(state)

