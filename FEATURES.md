# Feature Implementation Guide

This document provides a comprehensive overview of key features implemented in Agent v3 Claude.

## Table of Contents

1. [Executor Structured Output](#executor-structured-output)
2. [Routing Logic](#routing-logic)
3. [Tools Integration](#tools-integration)
4. [Architecture Refactoring](#architecture-refactoring)

---

## Executor Structured Output

### Overview

The executor returns structured JSON output with automatic failure handling for faster recovery.

### Implementation

**ExecutorOutput TypedDict** (`state.py`):
```python
class ExecutorOutput(TypedDict):
    success: bool   # Execution status
    output: str     # Description of what happened
```

**Automatic Retry Logic** (`routing.py`):
```python
def route_after_executor(state: AgentState) -> Literal["reviewer", "planner"]:
    executor_output = state.get("executor_output")
    if executor_output and not executor_output["success"]:
        state["plan"] = []
        state["step_index"] = 0
        return "planner"
    return "reviewer"
```

### Workflow

**Before**: `planner → executor → reviewer → advance`  
*Problem*: Reviewer must interpret natural language

**After**: `planner → executor → [success → reviewer | failure → planner]`  
*Benefit*: Boolean status enables automatic recovery

### Benefits

- ⚡ Fast recovery - skip reviewer on failures
- ✅ Reliable status - no LLM interpretation  
- 📊 Structured output - consistent format
- 🔄 Self-healing - automatic retry on failure

📖 **See also**: [EXECUTOR_OUTPUT_SUMMARY.md](EXECUTOR_OUTPUT_SUMMARY.md), [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## Routing Logic

### Overview

Intelligent routing between agent nodes based on verdict and execution status.

### Key Routes

**After Planner** (`route_after_planner`):
- Has plan → executor
- No plan → END (safety)

**After Executor** (`route_after_executor`):
- `success=True` → reviewer
- `success=False` → planner (automatic retry)

**After Advance** (`route_after_advance`):
- `verdict="finish"` → END
- `verdict="retry"` → planner (with feedback)
- `verdict="replan"` → planner (fresh start)
- `verdict="continue"` → executor (next step)
- Max iterations → END

### Advance Node Logic

```python
def advance_node(state: AgentState) -> AgentState:
    state["iters"] += 1
    verdict = state["verdict"]

    if verdict == "finish":
        return state
    
    if verdict == "retry":
        # Clear plan, let planner fix with feedback
        state["plan"] = []
        state["step_index"] = 0
        return state
    
    if verdict == "replan":
        # Fresh start
        state["plan"] = []
        state["step_index"] = 0
        return state
    
    # verdict="continue" - advance to next step
    if state["step_index"] < len(state["plan"]) - 1:
        state["step_index"] += 1
    else:
        # Plan complete, need replan
        state["plan"] = []
        state["step_index"] = 0
    
    return state
```

📖 **See also**: [ROUTING_FIX_SUMMARY.md](ROUTING_FIX_SUMMARY.md)

---

## Tools Integration

### Overview

26 comprehensive tools organized into 5 categories, all sandboxed and safe.

### Tool Categories

**File System (4 tools)**
- `read_file`, `write_file`, `list_files`, `grep`
- UTF-8 text handling, automatic parent directory creation

**Git Operations (9 tools)**
- `git_diff`, `git_status`, `git_add`, `git_commit`, `git_log`
- `git_branch_list`, `git_checkout`, `git_remote_list`, `git_prepare_pr`
- Full version control workflow support

**Command Execution (3 tools)**
- `apply_patch` - Apply unified diff patches
- `run_pytest` - Run tests with timeout controls
- `run_cmd` - Sandboxed shell commands (allowlist + blocked patterns)

**Virtual Environments (2 tools)**
- `create_venv` - Create isolated Python environments
- `run_in_venv` - Execute commands in venv context

**Memory & Persistence (8 tools)**
- `memory_set`, `memory_get`, `memory_list`, `memory_delete`, `memory_append`
- `store_repo_map`, `store_test_results`, `clear_memory`
- Cross-step state persistence via `.agent_memory.json`

### Safety Features

- **Sandboxing**: Commands run with allowlist and pattern blocking
- **Path Resolution**: Safe `repo_root` parameter handling
- **Timeouts**: Configurable execution timeouts
- **Error Handling**: Structured error reporting

### Integration

Tools are registered in `tools.py`:
```python
from ai_researcher_tools import (
    read_file, write_file, list_files, grep,
    git_diff, git_status, git_add, git_commit,
    # ... all 26 tools
)

TOOLS = [read_file, write_file, ...]
TOOL_BY_NAME = {t.name: t for t in TOOLS}
```

📖 **See also**: [AGENT_V3_TOOLS_INTEGRATION.md](AGENT_V3_TOOLS_INTEGRATION.md)

---

## Architecture Refactoring

### Overview

Transformed monolithic 593-line `agent.py` into modular 9-file architecture.

### Module Breakdown

| Module | Lines | Responsibility |
|--------|-------|---------------|
| `config.py` | 72 | System prompts, constants, configuration |
| `state.py` | 72 | State management, TypedDict definitions |
| `pruning.py` | 95 | Context window management |
| `tools.py` | 152 | Tool registry and execution |
| `nodes.py` | 234 | Role implementations (planner, executor, reviewer, advance) |
| `routing.py` | 58 | Workflow routing logic |
| `graph.py` | 41 | LangGraph construction |
| `agent.py` | 109 | Public API (run, print_results) |
| `__init__.py` | 21 | Package exports |

### Design Principles

**Single Responsibility**
- Each module has one clear purpose
- Related functionality grouped together

**Maintainability**
- Smaller, focused files
- Clear boundaries between components
- Isolated changes

**Testability**
- Pure functions where possible
- Clear interfaces for mocking
- Independent component testing

**Extensibility**
- Clear plugin points
- Configuration-driven behavior
- Simple tool addition

### API Compatibility

Public API unchanged:
```python
from agent_v3_claude import run, print_results

state = run("Your goal", max_iters=10)
print_results(state)
```

Additional exports now available:
```python
from agent_v3_claude import (
    AgentState,
    ExecutorOutput,
    PruningConfig,
    create_initial_state,
    DEFAULT_MAX_ITERATIONS,
)
```

📖 **See also**: [agent_v3_claude/REFACTORING_SUMMARY.md](agent_v3_claude/REFACTORING_SUMMARY.md)

---

## Quick Reference

For fast lookup of executor structured output features, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md).

For visual workflow diagrams, see [EXECUTOR_WORKFLOW_DIAGRAM.md](EXECUTOR_WORKFLOW_DIAGRAM.md).

