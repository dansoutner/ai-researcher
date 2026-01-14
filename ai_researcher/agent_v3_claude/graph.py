"""LangGraph workflow construction for the agent system."""

from langgraph.graph import StateGraph

from .nodes import advance_node, executor_node, planner_node, reviewer_node
from .routing import route_after_advance, route_after_executor, route_after_planner
from .state import AgentState


def build_agent_graph():
    """Construct the LangGraph workflow for the agent system.

    The workflow follows this pattern:
    1. planner: Creates execution plan
    2. executor: Executes one plan step using tools, returns structured status
    3. reviewer: Evaluates results (detects failures, provides feedback)
    4. advance: Updates counters and determines next step
    5. Loop back to executor (continue), planner (retry/replan), or end (finish)

    Returns:
        Compiled LangGraph application
    """
    graph = StateGraph(AgentState)

    # Register all nodes
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("advance", advance_node)

    # Set an entry point
    graph.set_entry_point("planner")

    # Define edges with routing logic
    graph.add_conditional_edges("planner", route_after_planner)
    graph.add_conditional_edges("executor", route_after_executor)
    graph.add_edge("reviewer", "advance")
    graph.add_conditional_edges("advance", route_after_advance)

    return graph.compile()

