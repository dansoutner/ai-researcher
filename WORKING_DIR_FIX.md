# Working Directory Persistence Fix

## Problem
The agent was sometimes forgetting the working directory and hallucinating paths like `/tmp/xxx`, causing file operations to fail or occur in wrong locations.

## Root Cause
- Working directory (`repo_root`) was stored in the agent state
- However, it wasn't being persisted to memory between iterations
- When context got pruned or state was recreated, the working directory could be lost
- The agent's prompts mentioned using memory but didn't enforce it

## Solution Implemented

### 1. Updated README Template (`config.py`)
Added a dedicated "Working Directory" section to the `agent_readme.md` template:
```
## Working Directory
[Absolute path to working directory]
```

### 2. Enhanced Planner Prompt (`config.py`)
Updated the State Management Protocol to explicitly require saving the working directory:
- **CRITICAL:** On FIRST step, planner must save working directory to memory using `memory_set("working_directory", "<path>")`
- Must include working directory in `agent_readme.md` under "## Working Directory"

### 3. Enhanced Executor Prompt (`config.py`)
Updated "The Journaling Rule" to mandate working directory retrieval:
- **MANDATORY FIRST ACTION:** Use `memory_get("working_directory")` at start of EVERY execution
- If not set, check `agent_readme.md` or use the repo_root provided in context
- ALL file operations must be relative to this directory
- **NEVER hallucinate paths like /tmp/xxx**

### 4. Automated Memory Persistence (`nodes.py`)

#### Planner Node
Added automatic working directory save on first iteration:
```python
# CRITICAL: On first iteration, save working directory to memory
if state['iters'] == 0:
    from ai_researcher.ai_researcher_tools import memory_set
    repo_root = state['repo_root']
    print(f"[DEBUG] First iteration - saving working directory to memory: {repo_root}")
    memory_set.invoke({"key": "working_directory", "value": repo_root})
```

#### Executor Node
Added automatic working directory retrieval before each execution:
```python
# CRITICAL: Retrieve working directory from memory to prevent hallucinated paths
from ai_researcher.ai_researcher_tools import memory_get
try:
    saved_workdir = memory_get.invoke({"key": "working_directory"})
    if saved_workdir and saved_workdir != "Key 'working_directory' not found in memory.":
        print(f"[DEBUG] Retrieved working directory from memory: {saved_workdir}")
        # Update state with retrieved working directory to ensure consistency
        state["repo_root"] = saved_workdir
    else:
        print(f"[DEBUG] No working directory in memory, using state value: {state['repo_root']}")
except Exception as e:
    print(f"[DEBUG] Failed to retrieve working directory from memory: {e}")
    print(f"[DEBUG] Using state value: {state['repo_root']}")
```

### 5. Enhanced Executor Context (`tools.py`)
Added working directory information directly in the executor's context message:
```python
HumanMessage(
    content=f"GOAL: {state['goal']}\n"
            f"WORKING DIRECTORY: {state['repo_root']}\n"
            f"CURRENT STEP: {current_step}\n\n"
            f"REMINDER: Use memory_get('working_directory') to retrieve the working directory if needed. "
            f"Never hallucinate paths like /tmp/xxx."
)
```

## How It Works

### Flow
1. **Initialization**: When agent starts, `repo_root` is set in initial state
2. **First Planning**: Planner node automatically saves `repo_root` to memory with key "working_directory"
3. **Every Execution**: 
   - Executor node retrieves "working_directory" from memory
   - Updates state's `repo_root` to ensure consistency
   - Passes working directory in context message to LLM
4. **Tool Execution**: All tools receive `repo_root` from state for file operations

### Redundancy & Reliability
The fix implements multiple layers of protection:

1. **Automatic Memory Save**: Code-level guarantee that working directory is saved on first iteration
2. **Automatic Memory Retrieval**: Code-level guarantee that working directory is retrieved before each execution
3. **State Synchronization**: Retrieved value updates state to ensure consistency
4. **LLM Prompts**: Both planner and executor prompts explicitly instruct about memory usage
5. **Context Reminder**: Each executor message includes working directory and usage reminder
6. **Fallback**: If memory retrieval fails, falls back to state value with debug logging

### Benefits
- **No More Hallucinated Paths**: Working directory is always retrieved from memory, preventing /tmp/xxx hallucinations
- **Persistence**: Working directory survives context pruning and state changes
- **Transparency**: Debug logs show when working directory is saved and retrieved
- **Self-Healing**: If memory is somehow cleared, state value provides fallback
- **LLM Awareness**: Prompts and context messages keep LLM aware of working directory

## Files Changed
1. `/ai_researcher/agent_v3_claude/config.py` - Updated prompts and README template
2. `/ai_researcher/agent_v3_claude/nodes.py` - Added automatic save/retrieve logic
3. `/ai_researcher/agent_v3_claude/tools.py` - Enhanced executor context message

## Testing
Create a test file to verify the fix:
```python
from ai_researcher.ai_researcher_tools import memory_get, memory_set
from ai_researcher.agent_v3_claude.state import create_initial_state

# Save working directory
memory_set.invoke({"key": "working_directory", "value": "/path/to/project"})

# Retrieve it
workdir = memory_get.invoke({"key": "working_directory"})
print(f"Working directory: {workdir}")  # Should print: /path/to/project
```

## Debug Logging
When running the agent, you'll now see:
```
[DEBUG] First iteration - saving working directory to memory: /path/to/project
[DEBUG] Retrieved working directory from memory: /path/to/project
```

This confirms the working directory is being properly persisted and recalled.

