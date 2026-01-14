# Agent v3 Claude

A production-ready, modular planner-executor-reviewer agent system built with LangGraph and Claude.

## Overview

Agent v3 implements an autonomous workflow with automatic error recovery:

1. **Planner**: Creates step-by-step execution plans based on goals and feedback
2. **Executor**: Executes plan steps using 26+ tools, returns structured status
3. **Reviewer**: Evaluates goal progress and determines next actions
4. **Self-Healing**: Automatically replans on failures without LLM interpretation

### Key Features

- ✅ **Structured Output**: Executor returns typed `{success: bool, output: str}` 
- ✅ **Automatic Recovery**: Failures trigger immediate replanning
- ✅ **Context Management**: Intelligent message pruning handles large outputs
- ✅ **Comprehensive Tooling**: 26 tools across file system, Git, testing, and more
- ✅ **Type Safety**: Full TypedDict definitions with validation
- ✅ **Modular Architecture**: Clean separation across 9 specialized modules

## Architecture

### Module Structure

```
agent_v3_claude/
├── agent.py             # Main entry point: run(), print_results()
├── config.py            # System prompts, constants, configuration
├── state.py             # AgentState TypedDict, state management
├── nodes.py             # Role implementations (planner, executor, reviewer, advance)
├── routing.py           # Workflow routing logic
├── graph.py             # LangGraph construction
├── tools.py             # Tool registry and execution (26 tools)
├── pruning.py           # Context window management
└── __init__.py          # Package exports
```

### Design Principles

**Separation of Concerns**
- Configuration, state, business logic, and infrastructure cleanly separated
- Each module has a single, well-defined responsibility

**Context Window Management**
- **Tool Output Store**: Out-of-band storage for raw tool outputs
- **Message Pruning**: Intelligent truncation preserving recent context
- **Head/Tail Display**: Shows beginning/end of large outputs with metadata

**Error Handling**
- JSON parsing with graceful fallbacks
- Tool execution error handling with structured status
- Safe defaults for malformed LLM responses

## Usage

### Basic Usage

```python
from agent_v3_claude import run, print_results

# Run the agent
goal = "Run pytest and fix any failing tests"
state = run(goal, max_iters=10)

# Display results
print_results(state)
```

### Custom Configuration

```python
from agent_v3_claude import run, PruningConfig

# Configure context window management
pruning_cfg = PruningConfig(
    keep_last_messages=30,      # Keep more recent context
    tool_max_chars=8000,        # Allow larger tool outputs
    tool_head_chars=2000,       # Show more of output head
    tool_tail_chars=1000,       # Show more of output tail
)

state = run(
    goal="Your goal here",
    max_iters=15,
    pruning_cfg=pruning_cfg,
)
```

### Implementing LLM Provider

Before running, implement the `require_llm()` function in `nodes.py`:

```python
# In nodes.py

def require_llm() -> BaseChatModel:
    """Provide your LLM implementation."""
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model="claude-3-5-sonnet-latest",
        temperature=0
    )
```

Or for OpenAI:

```python
def require_llm() -> BaseChatModel:
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )
```

## Available Tools

The executor has access to these tool categories:

### File System
- `read_file`, `write_file`, `list_files`, `grep`

### Git Operations
- `git_diff`, `git_status`, `git_add`, `git_commit`, `git_log`
- `git_branch_list`, `git_checkout`, `git_remote_list`, `git_prepare_pr`

### Commands
- `apply_patch`, `run_pytest`, `run_cmd`, `run_terminal_command`, `get_errors`

### Virtual Environments
- `create_venv`, `run_in_venv`

### Memory (Cross-step Persistence)
- `memory_set`, `memory_get`, `memory_list`, `memory_delete`, `memory_append`
- `store_repo_map`, `store_test_results`, `clear_memory`

## Workflow

```
┌─────────┐
│ Planner │ Creates plan with feedback
└────┬────┘
     │
     ▼
┌─────────────────────┐
│   Executor          │
│ Returns structured: │
│ {success, output}   │
└────┬────────────────┘
     │
     ├─ success=True ──► Reviewer ──► Advance ──┐
     │                                           │
     └─ success=False ─► Planner (auto-retry) ──┘
                              │
                         Loop continues
```

### Node Details

**Planner**
- Receives goal and feedback from previous iterations
- Generates JSON plan with concrete, actionable steps
- Fallback: Treats entire response as single step on parse error

**Executor**
- Takes current plan step and enters tool-execution loop
- Structured output: `{success: bool, output: str}`
- Automatic failure detection triggers replanning
- Loop process:
  1. Prune message history for context window
  2. Invoke LLM with current step
  3. Execute requested tools
  4. Feed results back to LLM
  5. Repeat until final summary (no more tool calls)

**Reviewer**
- Examines executor results against original goal
- Returns JSON verdict:
  - `continue` - Step succeeded, advance to next
  - `retry` - Step needs replanning
  - `replan` - Discard plan, start over
  - `finish` - Goal achieved
- Fallback: Defaults to `continue` on parse error

**Advance**
- Updates iteration counter and step index
- Handles verdict-based state transitions
- Resets plan when retry/replan needed
  - `retry`: Step failed, try again without advancing
  - `replan`: Current approach isn't working, create new plan
  - `finish`: Goal is complete

### Advance Node
- Updates iteration counter
- Adjusts step index based on verdict
- Handles plan completion and replanning logic

## Benefits of Refactoring

### Maintainability
- **Clear module boundaries**: Each file has a single, well-defined purpose
- **Easy to locate code**: Know exactly where to look for specific functionality
- **Reduced cognitive load**: Smaller files are easier to understand

### Testability
- **Isolated components**: Test individual modules independently
- **Mock-friendly**: Clear interfaces between modules
- **Pure functions**: Many utilities have no side effects

### Extensibility
- **Add new tools**: Simply register in `tools.py`
- **Modify prompts**: All in `config.py`
- **Custom routing**: Easy to adjust logic in `routing.py`
- **Alternative nodes**: Swap out implementations in `nodes.py`

### Readability
- **Self-documenting**: Module names clearly indicate purpose
- **Comprehensive docstrings**: Every function explains its role
- **Type hints**: Clear contracts for all functions
- **Logical organization**: Related code lives together

## Migration from Old Code

The original monolithic `agent.py` (593 lines) has been split into:
- `config.py` (72 lines): Configuration
- `state.py` (72 lines): State definitions
- `pruning.py` (95 lines): Context management
- `tools.py` (152 lines): Tool execution
- `nodes.py` (234 lines): Core logic
- `routing.py` (58 lines): Workflow routing
- `graph.py` (41 lines): Graph construction
- `agent.py` (109 lines): Main entry point
- `__init__.py` (21 lines): Package interface

**Total**: ~854 lines (vs 593 in original) with significantly better organization and documentation.

The public API remains the same:
```python
# Old
from agent_v3_claude.agent import run, print_results

# New (still works, plus cleaner import)
from agent_v3_claude import run, print_results
```

## Future Enhancements

Potential improvements enabled by this structure:

1. **Multiple LLM Support**: Pass LLM as parameter instead of global function
2. **Pluggable Tool Sets**: Allow different tool configurations per goal
3. **Streaming Support**: Add streaming node implementations
4. **Checkpointing**: Easier to save/restore state at module boundaries
5. **Observability**: Add hooks for logging/metrics at each node
6. **Testing**: Unit tests for each module independently

## Contributing

When adding new features:
- Put configuration in `config.py`
- Define new state fields in `state.py`
- Implement new tools in `tools.py`
- Add node logic in `nodes.py`
- Update routing if needed in `routing.py`
- Keep `agent.py` as a clean facade

## License

See parent project license.

