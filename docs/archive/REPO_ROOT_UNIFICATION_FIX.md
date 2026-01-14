# Repo Root / Working Directory Unification Fix

## Problem
The agent was experiencing a Pydantic validation error:
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for memory_set
repo_root
  Field required [type=missing, input_value={'key': 'working_director...x/ai-agent-experiments'}, input_type=dict]
```

This error occurred because:
1. The `AgentState` TypedDict had both `repo_root` and `working_directory` fields
2. The memory tools (`memory_set` and `memory_get`) require a `repo_root` parameter
3. The code was invoking memory tools without passing the required `repo_root` parameter

## Solution
Unified the fields to use only `repo_root` consistently throughout the codebase.

## Changes Made

### 1. `/ai_researcher/agent_v3_claude/state.py`
**Removed** the unused `working_directory` field from `AgentState`:
```python
# Before:
    repo_root: str
    working_directory: Optional[str]

# After:
    repo_root: str
```

### 2. `/ai_researcher/agent_v3_claude/nodes.py`
**Fixed planner_node** to pass `repo_root` parameter when saving to memory:
```python
# Before:
memory_set.invoke({"key": "working_directory", "value": repo_root})

# After:
memory_set.invoke({"repo_root": repo_root, "key": "working_directory", "value": repo_root})
```

**Fixed executor_node** to pass `repo_root` parameter when retrieving from memory:
```python
# Before:
saved_workdir = memory_get.invoke({"key": "working_directory"})

# After:
saved_workdir = memory_get.invoke({"repo_root": state["repo_root"], "key": "working_directory"})
```

### 3. `/test_working_dir_persistence.py`
**Updated test** to pass `repo_root` parameter in memory tool invocations:
```python
# Before:
memory_set.invoke({"key": "working_directory", "value": test_workdir})
memory_get.invoke({"key": "working_directory"})

# After:
memory_set.invoke({"repo_root": test_workdir, "key": "working_directory", "value": test_workdir})
memory_get.invoke({"repo_root": test_workdir, "key": "working_directory"})
```

## Impact
- ✅ Eliminated Pydantic validation errors
- ✅ Simplified state management by using a single field for working directory
- ✅ Maintained backward compatibility (the memory key "working_directory" is still used)
- ✅ All memory tool invocations now properly pass the required `repo_root` parameter

## Testing
The fix has been validated by:
1. Removing the `working_directory` field from `AgentState` TypedDict
2. Ensuring all memory tool invocations include the required `repo_root` parameter
3. Updating tests to match the new signature

## Notes
- The memory system internally stores the working directory under the key "working_directory"
- The state only maintains `repo_root` as the single source of truth
- This unification ensures consistency and prevents validation errors

