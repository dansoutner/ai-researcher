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


def route_after_executor(state: AgentState) -> Literal["reviewer"]:
    """Route from executor to reviewer.

    The reviewer will check if the executor succeeded or failed and
    decide the appropriate next action.

    Args:
        state: Current agent state

    Returns:
        Always "reviewer"
    """

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

