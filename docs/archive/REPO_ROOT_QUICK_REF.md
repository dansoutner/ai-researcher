# Quick Reference: Repo Root Unification

## What Changed?
✅ Unified `repo_root` and `working_directory` into a single field: `repo_root`

## Problem Fixed
```
ValidationError: repo_root Field required for memory_set
```

## Key Changes

### 1. State Definition
```python
# ❌ OLD - Had redundant field
class AgentState(TypedDict):
    repo_root: str
    working_directory: Optional[str]  # REMOVED

# ✅ NEW - Single source of truth
class AgentState(TypedDict):
    repo_root: str
```

### 2. Memory Tool Invocations

```python
# ❌ OLD - Missing repo_root parameter
memory_set.invoke({"key": "working_directory", "value": repo_root})
memory_get.invoke({"key": "working_directory"})

# ✅ NEW - Includes required parameter
memory_set.invoke({"repo_root": repo_root, "key": "working_directory", "value": repo_root})
memory_get.invoke({"repo_root": state["repo_root"], "key": "working_directory"})
```

## Usage Pattern

When calling memory tools, ALWAYS include `repo_root`:

```python
from ai_researcher.ai_researcher_tools import memory_set, memory_get

# Setting a value
memory_set.invoke({
    "repo_root": state["repo_root"],  # ← REQUIRED
    "key": "your_key",
    "value": "your_value"
})

# Getting a value
result = memory_get.invoke({
    "repo_root": state["repo_root"],  # ← REQUIRED
    "key": "your_key"
})
```

## Files Modified
- ✅ `ai_researcher/agent_v3_claude/state.py`
- ✅ `ai_researcher/agent_v3_claude/nodes.py` (2 locations)
- ✅ `test_working_dir_persistence.py`

## No Breaking Changes
- Memory key `"working_directory"` still works internally
- State field is consistently named `repo_root`
- All existing functionality preserved

