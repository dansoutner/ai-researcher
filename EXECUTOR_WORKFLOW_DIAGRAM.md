# Executor Structured Output - Workflow Diagram

## Old Workflow (Before)

```
┌─────────┐
│ Planner │ Creates plan
└────┬────┘
     │
     ▼
┌─────────┐
│Executor │ Runs tools, chats back "I did X"
└────┬────┘
     │
     ▼
┌─────────┐
│Reviewer │ Reads chat, interprets success/failure
└────┬────┘ Decides: continue/retry/replan/finish
     │
     ▼
┌─────────┐
│ Advance │ Updates counters
└────┬────┘
     │
     └─────► Loop back or END
```

**Problems:**
- Executor just chats - no structured status
- Reviewer must interpret natural language
- Slow - extra LLM call to understand failures
- Unreliable - LLM might misinterpret


## New Workflow (After)

```
┌─────────┐
│ Planner │ Creates plan (with failure context if needed)
└────┬────┘
     │
     ▼
┌─────────────────────────────────┐
│       Executor                  │
│  Runs tools, returns JSON:      │
│  {"success": bool, "output": ""} │
└────┬────────────────────────────┘
     │
     ├─── success=True ───┐
     │                    ▼
     │              ┌─────────┐
     │              │Reviewer │ Evaluates goal progress
     │              └────┬────┘
     │                   │
     │                   ▼
     │              ┌─────────┐
     │              │ Advance │ Updates counters
     │              └────┬────┘
     │                   │
     │                   └─────► Continue to next step or END
     │
     └─── success=False ──┐
                         ▼
                    ┌─────────┐
                    │ Planner │ Automatic replan with failure context
                    └─────────┘
                         │
                         └─────► Try again (no reviewer overhead)
```

**Benefits:**
- ✓ Structured boolean status
- ✓ Automatic retry on failures
- ✓ No LLM interpretation needed
- ✓ Faster - skip reviewer on failures
- ✓ More reliable


## Code Flow

### Executor Success Path
```python
# Executor returns
{
  "success": true,
  "output": "Successfully ran pytest - 15 tests passed"
}

# Routing (routing.py)
route_after_executor() → checks success → returns "reviewer"

# Reviewer evaluates
reviewer_node() → checks if goal achieved → verdict

# Advance
advance_node() → updates counters → next step or replan
```

### Executor Failure Path
```python
# Executor returns
{
  "success": false,
  "output": "pytest failed - 3 tests failing"
}

# Routing (routing.py)
route_after_executor() → checks success → returns "planner"
# Also clears plan to force replanning

# Planner gets failure context
planner_node() → sees failure in state → creates new plan

# Loop continues without reviewer overhead
```

## Key Decision Point

The critical routing logic in `route_after_executor()`:

```python
def route_after_executor(state: AgentState) -> Literal["reviewer", "planner"]:
    executor_output = state.get("executor_output")
    
    if executor_output and not executor_output["success"]:
        # FAILURE: Skip reviewer, go straight to replan
        state["plan"] = []
        state["step_index"] = 0
        return "planner"
    
    # SUCCESS: Continue to reviewer
    return "reviewer"
```

This single function implements the automatic retry logic!


## State Changes

### Old State
```python
{
    "messages": [...],
    "plan": [...],
    "last_result": "I ran pytest and it passed",  # ← Just text
    "verdict": "continue",
    ...
}
```

### New State
```python
{
    "messages": [...],
    "plan": [...],
    "executor_output": {                           # ← NEW!
        "success": true,
        "output": "Ran pytest - 15 tests passed"
    },
    "last_result": "Ran pytest - 15 tests passed", # ← Still populated
    "verdict": "continue",
    ...
}
```


## Example Scenario: Fix Failing Tests

### Step 1: Initial execution
```
Planner: ["Run pytest to see which tests fail", "Fix the failing tests"]
Executor: Runs pytest
         → Returns: {"success": true, "output": "3 tests failing..."}
Reviewer: "Tests run successfully, move to fix them"
Verdict: "continue"
```

### Step 2: Try to fix tests
```
Executor: Edits test file
         → Returns: {"success": false, "output": "Permission denied"}
Routing: Detects failure → routes to Planner (skip Reviewer!)
Planner: Gets context "Previous execution failed: Permission denied"
         → Creates new plan with sudo or different approach
```

### Step 3: Retry
```
Executor: Uses different approach
         → Returns: {"success": true, "output": "Tests fixed"}
Reviewer: "Tests are now passing, goal achieved"
Verdict: "finish"
```

Notice: Step 2 failure didn't require reviewer - automatic retry!

