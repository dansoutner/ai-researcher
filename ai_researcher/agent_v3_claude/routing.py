"""Graph routing logic for the agent workflow."""

from typing import Literal

from langgraph.graph import END

from .state import AgentState


def route_after_planner(state: AgentState) -> Literal["executor", END]:
    """Route from planner to executor or end.

    Args:
        state: Current agent state

    Returns:
        "executor" if plan exists, END otherwise
    """
    return "executor" if state["plan"] else END


def route_after_executor(state: AgentState) -> Literal["reviewer", "planner"]:
    """Route from executor to reviewer or directly to planner on failure.

    If the executor reports failure (success=False), automatically trigger
    a replan without requiring the reviewer to intervene.

    Args:
        state: Current agent state

    Returns:
        "planner" if executor failed, "reviewer" otherwise
    """
    executor_output = state.get("executor_output")

    if executor_output and not executor_output["success"]:
        # Executor failed - automatically trigger replan
        # Clear the plan to force replanning with the failure context
        state["plan"] = []
        state["step_index"] = 0
        return "planner"

    return "reviewer"


def route_after_advance(state: AgentState) -> Literal["planner", "executor", END]:
    """Route from advance node to planner, executor, or end.

    Routing logic:
    1. If verdict is "finish" or max iterations reached: END
    2. If verdict is "retry": loop back to "planner" for replanning
    3. If verdict is "replan" or no valid plan: "planner"
    4. If plan exists and step_index is valid: "executor"

    Args:
        state: Current agent state

    Returns:
        Next node name or END
    """
    # Stop conditions
    if state["verdict"] == "finish":
        return END

    if state["iters"] >= state["max_iters"]:
        return END

    # On retry, loop back to planner to replan
    if state["verdict"] == "retry":
        return "planner"

    # If we have a valid plan and step, execute it
    if state["plan"] and state["step_index"] < len(state["plan"]):
        return "executor"

    # No plan or out of steps - need to (re)plan
    return "planner"

