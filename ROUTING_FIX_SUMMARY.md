# Routing Logic Fix - Summary

## Overview
Fixed the reviewer output and routing logic to allow looping back to the planner when things go wrong (retry verdict).

## Changes Made

### 1. Updated `routing.py` - `route_after_advance()` function

**Before:** The "retry" verdict would route to "executor" to retry the current step.

**After:** The "retry" verdict now routes to "planner" for replanning with feedback.

```python
def route_after_advance(state: AgentState) -> Literal["planner", "executor", END]:
    """Route from advance node to planner, executor, or end.

    Routing logic:
    1. If verdict is "finish" or max iterations reached: END
    2. If verdict is "retry": loop back to "planner" for replanning
    3. If verdict is "replan" or no valid plan: "planner"
    4. If plan exists and step_index is valid: "executor"
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
```

### 2. Updated `nodes.py` - `advance_node()` function

**Before:** On "retry", the step_index was kept the same but the plan was not cleared.

**After:** On "retry", both the plan and step_index are reset to 0, allowing the planner to create a new plan based on the reviewer's feedback.

```python
def advance_node(state: AgentState) -> AgentState:
    """Update iteration counters and step index based on reviewer verdict.

    This node handles the control flow logic:
    - Increment iteration counter
    - Advance step index on "continue"
    - Reset plan for "replan" to trigger replanning
    - Reset plan for "retry" to allow planner to fix the issue
    - Keep everything on "finish"
    """
    state["iters"] += 1
    verdict = state["verdict"]

    if verdict == "finish":
        return state

    if verdict == "retry":
        # Clear plan and reset index so planner can replan with feedback
        # Don't increment step_index - start fresh
        state["plan"] = []
        state["step_index"] = 0
        return state

    if verdict == "replan":
        # Clear plan to trigger replanning
        state["plan"] = []
        state["step_index"] = 0
        return state

    # Verdict is "continue" - advance to next step
    if state["step_index"] < len(state["plan"]) - 1:
        state["step_index"] += 1
    else:
        # Plan complete but not marked "finish" - replan to verify/extend
        state["plan"] = []
        state["step_index"] = 0

    return state
```

## Workflow Flow

The complete workflow now works as follows:

1. **planner** → Creates or adjusts execution plan
2. **executor** → Executes one plan step using tools
3. **reviewer** → Evaluates results and decides next action (returns verdict)
4. **advance** → Updates counters and state based on verdict
5. **routing** → Determines next node:
   - `finish` → END
   - `retry` → planner (NEW: loop back with feedback)
   - `replan` → planner (clear plan and start over)
   - `continue` → executor (move to next step)
   - no plan or out of steps → planner

## Benefits

1. **Better Error Recovery**: When the executor fails, the reviewer can issue a "retry" verdict, causing the system to loop back to the planner with feedback about what went wrong.

2. **Feedback Loop**: The planner receives the reviewer's feedback (`state["last_result"]`) which includes:
   - The verdict reason
   - Fix suggestions
   
3. **Flexible Planning**: The planner can now create a completely new plan that addresses the issues identified by the reviewer, rather than being stuck retrying the same failing step.

## Example Scenario

### Before (without fix):
1. Executor tries to run tests → fails
2. Reviewer detects failure → verdict="retry"
3. Routing sends back to executor
4. Executor retries same step → likely fails again
5. Loop continues until max iterations

### After (with fix):
1. Executor tries to run tests → fails
2. Reviewer detects failure → verdict="retry", provides feedback "Tests failed because dependencies not installed"
3. Advance node clears plan
4. Routing sends to planner
5. Planner creates new plan incorporating feedback: ["Install dependencies", "Run tests"]
6. Executor executes new plan → success!

## Testing

All routing scenarios have been tested and verified:
- ✓ Retry correctly routes to planner
- ✓ Replan correctly routes to planner
- ✓ Continue correctly routes to executor
- ✓ Finish correctly ends workflow
- ✓ Max iterations correctly ends workflow
- ✓ No plan correctly routes to planner

See `test_routing_fix.py` for complete test suite.

