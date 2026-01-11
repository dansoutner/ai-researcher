# Executor Structured Output - Quick Reference

## What Changed?

### ExecutorOutput Structure
```python
class ExecutorOutput(TypedDict):
    success: bool   # True if step succeeded, False if failed
    output: str     # Description of what happened
```

### Automatic Routing
```python
if executor_output["success"] == False:
    → Route to PLANNER (automatic retry)
else:
    → Route to REVIEWER (normal flow)
```

## Code Locations

| Feature | File | Function/Class |
|---------|------|----------------|
| ExecutorOutput definition | `state.py` | `class ExecutorOutput(TypedDict)` |
| State field | `state.py` | `AgentState["executor_output"]` |
| Executor prompt | `config.py` | `EXECUTOR_SYSTEM_PROMPT` |
| Response parser | `tools.py` | `parse_executor_response()` |
| Executor integration | `tools.py` | `run_executor_turn()` |
| **Auto-retry logic** | `routing.py` | `route_after_executor()` |
| Planner feedback | `nodes.py` | `planner_node()` |
| Graph routing | `graph.py` | `add_conditional_edges("executor", ...)` |

## Usage

### Checking Executor Status
```python
state = run("Some goal", max_iters=10)

if state["executor_output"]:
    if state["executor_output"]["success"]:
        print("✓", state["executor_output"]["output"])
    else:
        print("✗", state["executor_output"]["output"])
```

### Executor JSON Response Format
```json
{
  "success": true,
  "output": "Successfully ran pytest - all 15 tests passed"
}
```

or

```json
{
  "success": false,
  "output": "Failed to run pytest - command not found"
}
```

## Workflow

```
                    ┌─────────┐
                    │ Planner │
                    └────┬────┘
                         │
                         ▼
                    ┌─────────┐
                    │Executor │
                    │ Returns │
                    │  JSON   │
                    └────┬────┘
                         │
            ┌────────────┴────────────┐
            │                         │
       success=True             success=False
            │                         │
            ▼                         ▼
      ┌─────────┐              ┌─────────┐
      │Reviewer │              │ Planner │
      └────┬────┘              │ (retry) │
           │                   └─────────┘
           ▼
      ┌─────────┐
      │ Advance │
      └─────────┘
```

## Key Points

- ✅ Executor returns structured JSON (not chat)
- ✅ `success: false` triggers automatic replan
- ✅ No LLM needed to interpret failures
- ✅ Faster recovery from failures
- ✅ Backward compatible

## Error Handling

- Invalid JSON → Treated as failure
- Missing fields → Treated as failure
- Parse error → Treated as failure
- Tool exception → Executor marks success=false

## Benefits

1. **Fast**: Skip reviewer on failures
2. **Reliable**: Boolean status, no interpretation
3. **Clear**: Structured output
4. **Automatic**: Self-healing on failures
5. **Debuggable**: Easy to check success status

