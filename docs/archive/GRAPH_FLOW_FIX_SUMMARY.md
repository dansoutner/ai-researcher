# Graph Flow Fix Summary

## Problem
The user reported seeing "a lot of planning running the agent but not the execution", indicating the graph was stuck in excessive planning loops without proper execution.

## Root Causes Identified

### 1. State Mutation in Routing Function (CRITICAL)
**Location**: `routing.py`, `route_after_executor()`

**Issue**: The routing function was mutating state by clearing the plan when executor failed:
```python
if executor_output and not executor_output["success"]:
    state["plan"] = []  # ← State mutation in routing function!
    state["step_index"] = 0
    return "planner"
```

**Problem**: In LangGraph, routing functions should be **pure** (read-only). They should only determine the next node to visit, not modify state. This violates the framework's design principles.

### 2. Infinite Replanning Loop
**Location**: `nodes.py`, `advance_node()`

**Issue**: When a plan completed with verdict "continue" (instead of "finish"), the advance node would clear the plan and force replanning:
```python
else:
    # Plan complete but not marked "finish" - replan to verify/extend
    state["plan"] = []
    state["step_index"] = 0
```

**Problem**: This created an infinite loop:
- Execute all plan steps successfully
- Reviewer says "continue" after last step
- Advance clears plan → routes to planner
- Planner creates new plan
- Execute all steps again...
- Repeat forever (or until max iterations)

### 3. Iteration Counter Bypass
**Location**: Graph structure

**Issue**: When executor failed, it routed directly to planner, bypassing the advance node which increments the iteration counter.

**Problem**: This could cause infinite loops that don't respect max_iters limits.

## Changes Made

### 1. Fixed Routing Function Purity
**File**: `ai_researcher/agent_v3_claude/routing.py`

Changed `route_after_executor` to always route to reviewer:
```python
def route_after_executor(state: AgentState) -> Literal["reviewer"]:
    """Route from executor to reviewer.
    
    The reviewer will check if the executor succeeded or failed and
    decide the appropriate next action.
    """
    return "reviewer"
```

**Benefits**:
- Routing function is now pure (no state mutations)
- All paths go through advance node (proper iteration counting)
- Cleaner separation of concerns

### 2. Enhanced Reviewer to Handle Executor Failures
**File**: `ai_researcher/agent_v3_claude/nodes.py`

Added automatic failure detection in reviewer_node:
```python
def reviewer_node(state: AgentState) -> AgentState:
    # Check if executor failed - if so, automatically set retry verdict
    executor_output = state.get("executor_output")
    if executor_output and not executor_output["success"]:
        print(f"[DEBUG] Executor failed, automatically setting verdict to 'retry'")
        state["verdict"] = "retry"
        state["last_result"] = f"RETRY: Executor failed - {executor_output['output']}"
        return state
    
    # ... rest of reviewer logic
```

**Benefits**:
- Reviewer handles both success and failure cases
- Consistent flow through all nodes
- Better error context preservation

### 3. Fixed Infinite Replanning Loop
**File**: `ai_researcher/agent_v3_claude/nodes.py`

Changed advance_node to treat plan completion as goal completion:
```python
# Verdict is "continue" - advance to next step
if state["plan"] and state["step_index"] < len(state["plan"]) - 1:
    state["step_index"] += 1
elif state["plan"] and state["step_index"] == len(state["plan"]) - 1:
    # Plan complete with "continue" verdict - treat as goal completion
    state["verdict"] = "finish"
else:
    # No plan or invalid state - will trigger replanning via routing
    pass
```

**Benefits**:
- Plans that complete successfully end the workflow
- No infinite replanning loops
- Reviewer can still explicitly request replanning with "replan" verdict if needed

### 4. Updated Documentation
**File**: `ai_researcher/agent_v3_claude/graph.py`

Updated docstring to reflect the corrected flow:
```python
"""Construct the LangGraph workflow for the agent system.

The workflow follows this pattern:
1. planner: Creates execution plan
2. executor: Executes one plan step using tools, returns structured status
3. reviewer: Evaluates results (detects failures, provides feedback)
4. advance: Updates counters and determines next step
5. Loop back to executor (continue), planner (retry/replan), or end (finish)
```

## Testing

### Test Results
All routing tests pass:
```
tests/test_routing_fix.py::test_retry_routes_to_planner PASSED
tests/test_routing_fix.py::test_replan_routes_to_planner PASSED
tests/test_routing_fix.py::test_continue_routes_to_executor PASSED
tests/test_routing_fix.py::test_finish_ends PASSED
tests/test_routing_fix.py::test_max_iters_ends PASSED
tests/test_routing_fix.py::test_no_plan_routes_to_planner PASSED
```

### Flow Visualization
Created `test_graph_flow.py` to trace execution paths:

**Before fix**: Normal flow would loop infinitely
```
Step 9: advance → Routes to: planner  (plan complete, replanning)
Step 10: planner → Routes to: executor
Step 11: executor → Routes to: reviewer
... (infinite loop)
```

**After fix**: Normal flow completes correctly
```
Step 9: advance → Routes to: __end__
Step 10: __end__ → ENDED
```

## Impact

### Fixed Issues
✅ Eliminated state mutation in routing functions  
✅ Fixed infinite replanning loops  
✅ Ensured iteration counter is always incremented  
✅ Proper flow through all nodes for all cases  

### Behavior Changes
- Plans that complete successfully now automatically finish (can be overridden by reviewer setting "replan" verdict)
- Executor failures always flow through reviewer and advance nodes
- More predictable execution patterns

### Backward Compatibility
- API unchanged
- State structure unchanged
- All existing tests pass
- Behavior is more intuitive (less unexpected replanning)

## Recommendations for Future Improvements

1. **Add execution tracking**: Log each node transition to help debug flow issues
2. **Add circuit breakers**: Detect and break infinite loops more explicitly
3. **Improve reviewer prompts**: Give clearer instructions about when to use "finish" vs "continue"
4. **Add metrics**: Track planning vs execution ratio to detect imbalances
5. **Consider plan validation**: Reject empty or invalid plans earlier

## Files Modified

1. `ai_researcher/agent_v3_claude/routing.py` - Fixed state mutation, simplified routing
2. `ai_researcher/agent_v3_claude/nodes.py` - Enhanced reviewer, fixed replanning loop
3. `ai_researcher/agent_v3_claude/graph.py` - Updated documentation

## Testing Files Created

- `test_graph_flow.py` - Flow visualization and testing tool

