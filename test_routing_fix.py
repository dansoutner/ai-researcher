"""Test the updated routing logic for retry verdict."""

from agent_v3_claude.routing import route_after_advance
from agent_v3_claude.nodes import advance_node
from agent_v3_claude.state import create_initial_state


def test_retry_routes_to_planner():
    """Test that retry verdict routes back to planner."""
    state = create_initial_state(goal="Test goal", max_iters=10)
    state["verdict"] = "retry"
    state["plan"] = ["step 1", "step 2"]
    state["step_index"] = 0

    # Simulate the flow: advance_node runs first
    state = advance_node(state)
    result = route_after_advance(state)

    assert result == "planner", f"Expected 'planner' but got '{result}'"
    print("✓ Retry correctly routes to planner")


def test_replan_routes_to_planner():
    """Test that replan verdict routes to planner."""
    state = create_initial_state(goal="Test goal", max_iters=10)
    state["verdict"] = "replan"
    state["plan"] = ["step 1"]
    state["step_index"] = 0

    # Simulate the flow: advance_node runs first
    state = advance_node(state)
    result = route_after_advance(state)

    assert result == "planner", f"Expected 'planner' but got '{result}'"
    print("✓ Replan correctly routes to planner")


def test_continue_routes_to_executor():
    """Test that continue verdict routes to executor when plan has steps."""
    state = create_initial_state(goal="Test goal", max_iters=10)
    state["verdict"] = "continue"
    state["plan"] = ["step 1", "step 2"]
    state["step_index"] = 0

    # Simulate the flow: advance_node runs first
    state = advance_node(state)
    result = route_after_advance(state)

    assert result == "executor", f"Expected 'executor' but got '{result}'"
    print("✓ Continue correctly routes to executor")


def test_finish_ends():
    """Test that finish verdict ends the workflow."""
    from langgraph.graph import END

    state = create_initial_state(goal="Test goal", max_iters=10)
    state["verdict"] = "finish"
    state["plan"] = ["step 1"]
    state["step_index"] = 0

    # Simulate the flow: advance_node runs first
    state = advance_node(state)
    result = route_after_advance(state)

    assert result == END, f"Expected END but got '{result}'"
    print("✓ Finish correctly ends workflow")


def test_max_iters_ends():
    """Test that max iterations reached ends the workflow."""
    from langgraph.graph import END

    state = create_initial_state(goal="Test goal", max_iters=5)
    state["iters"] = 4  # Will be 5 after advance_node increments
    state["verdict"] = "continue"
    state["plan"] = ["step 1"]
    state["step_index"] = 0

    # Simulate the flow: advance_node runs first
    state = advance_node(state)
    result = route_after_advance(state)

    assert result == END, f"Expected END but got '{result}'"
    print("✓ Max iterations correctly ends workflow")


def test_no_plan_routes_to_planner():
    """Test that no plan routes to planner."""
    state = create_initial_state(goal="Test goal", max_iters=10)
    state["verdict"] = "continue"
    state["plan"] = []
    state["step_index"] = 0

    # Simulate the flow: advance_node runs first
    state = advance_node(state)
    result = route_after_advance(state)

    assert result == "planner", f"Expected 'planner' but got '{result}'"
    print("✓ No plan correctly routes to planner")


if __name__ == "__main__":
    print("Testing routing logic fixes...\n")

    test_retry_routes_to_planner()
    test_replan_routes_to_planner()
    test_continue_routes_to_executor()
    test_finish_ends()
    test_max_iters_ends()
    test_no_plan_routes_to_planner()

    print("\n✅ All routing tests passed!")

