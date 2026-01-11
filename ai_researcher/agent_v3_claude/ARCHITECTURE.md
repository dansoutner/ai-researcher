# Agent v3 Claude - Architecture

## Overview

Agent v3 Claude is a production-ready autonomous agent system implementing a planner-executor-reviewer pattern with automatic error recovery and comprehensive tooling.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      Agent v3 Claude                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐              │
│  │ Planner │───►│Executor │───►│Reviewer │              │
│  └─────────┘    └─────────┘    └────┬────┘              │
│       ▲              │                │                   │
│       │              │                ▼                   │
│       │              │           ┌─────────┐             │
│       │              └──────────►│ Advance │             │
│       │                          └────┬────┘             │
│       │                               │                   │
│       └───────────────────────────────┘                   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Tools (26 total)                     │   │
│  │  • File System    • Git Operations               │   │
│  │  • Commands       • Virtual Envs                 │   │
│  │  • Memory         • Persistence                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Planner Node

**Responsibility**: Generate step-by-step execution plans

**Inputs**:
- User's goal
- Feedback from previous iterations
- Executor failure messages

**Output**: JSON array of action steps

**Implementation**: `nodes.py::planner_node()`

**Key Features**:
- Incorporates failure context for better replanning
- Fallback handling for malformed JSON
- Clear, actionable step generation

### 2. Executor Node

**Responsibility**: Execute plan steps using available tools

**Inputs**:
- Current plan step
- Tool execution results
- Message history (pruned for context)

**Output**: Structured `ExecutorOutput` with success status

**Implementation**: `nodes.py::executor_node()` + `tools.py::run_executor_turn()`

**Key Features**:
- Structured JSON output: `{success: bool, output: str}`
- Tool execution loop with LLM interaction
- Context window management via message pruning
- Automatic failure detection

### 3. Reviewer Node

**Responsibility**: Evaluate progress toward goal

**Inputs**:
- Original goal
- Executor output
- Full execution history

**Output**: JSON verdict with one of four options

**Implementation**: `nodes.py::reviewer_node()`

**Verdicts**:
- `continue` - Proceed to next step
- `retry` - Try different approach
- `replan` - Start over
- `finish` - Goal achieved

### 4. Advance Node

**Responsibility**: Update state based on verdict

**Inputs**:
- Current verdict
- Iteration counters
- Plan state

**Output**: Updated state

**Implementation**: `nodes.py::advance_node()`

**Key Features**:
- Iteration counter management
- Step index advancement
- Plan clearing for retry/replan

## Module Architecture

### Configuration Layer (`config.py`)

```python
# System prompts for each role
PLANNER_SYSTEM_PROMPT
EXECUTOR_SYSTEM_PROMPT
REVIEWER_SYSTEM_PROMPT

# Pruning configuration
PruningConfig(
    keep_last_messages: int
    tool_max_chars: int
    tool_head_chars: int
    tool_tail_chars: int
)

# Constants
DEFAULT_MAX_ITERATIONS
DEFAULT_TEMPERATURE
VERDICT_OPTIONS
```

### State Layer (`state.py`)

```python
# Main state definition
class AgentState(TypedDict):
    goal: str
    plan: list[str]
    step_index: int
    verdict: str
    last_result: str
    executor_output: Optional[ExecutorOutput]
    messages: list[BaseMessage]
    iters: int
    max_iters: int
    tool_output_store: ToolOutputStore

# Structured executor output
class ExecutorOutput(TypedDict):
    success: bool
    output: str

# Out-of-band storage for large outputs
class ToolOutputStore:
    store: dict[str, str]
```

### Business Logic Layer (`nodes.py`, `routing.py`)

**Nodes** (`nodes.py`):
- `planner_node()` - Plan creation/adjustment
- `executor_node()` - Tool execution
- `reviewer_node()` - Progress evaluation
- `advance_node()` - State updates

**Routing** (`routing.py`):
- `route_after_planner()` - Planner → Executor/END
- `route_after_executor()` - Executor → Reviewer/Planner
- `route_after_advance()` - Advance → Planner/Executor/END

### Infrastructure Layer (`tools.py`, `pruning.py`)

**Tools** (`tools.py`):
- Tool registry and lookup
- Tool execution with error handling
- Executor turn management

**Pruning** (`pruning.py`):
- Message history truncation
- Tool output summarization
- Context window management

### Graph Layer (`graph.py`)

```python
def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("advance", advance_node)
    
    # Add edges
    graph.add_edge(START, "planner")
    graph.add_conditional_edges("planner", route_after_planner)
    graph.add_conditional_edges("executor", route_after_executor)
    graph.add_edge("reviewer", "advance")
    graph.add_conditional_edges("advance", route_after_advance)
    
    return graph.compile()
```

### API Layer (`agent.py`)

```python
def run(goal: str, max_iters: int = 10, ...) -> AgentState:
    """Main entry point for agent execution."""
    
def print_results(state: AgentState) -> None:
    """Display execution results."""
```

## Data Flow

### Typical Execution Flow

```
1. User calls run(goal="Fix failing tests")
   ↓
2. Initial state created with goal
   ↓
3. Planner receives goal, creates plan:
   ["Run pytest to identify failures",
    "Read failing test file",
    "Fix the issue",
    "Run pytest again to verify"]
   ↓
4. Executor takes step 0, runs pytest tool
   Returns: {success: true, output: "Test test_auth failed"}
   ↓
5. Reviewer evaluates: verdict="continue"
   ↓
6. Advance increments step_index to 1
   ↓
7. Executor takes step 1, reads test file
   Returns: {success: true, output: "File contents..."}
   ↓
8. Reviewer evaluates: verdict="continue"
   ↓
9. Advance increments step_index to 2
   ↓
10. Executor takes step 2, writes fix
    Returns: {success: false, output: "Permission denied"}
    ↓
11. Routing detects failure, goes to Planner
    ↓
12. Planner creates new plan with failure context
    ...cycle continues until goal achieved or max_iters reached
```

## Key Design Patterns

### 1. Structured Output

Executor returns typed data instead of natural language:

```python
# Before: "I successfully ran pytest and found 3 failures"
# After: {"success": true, "output": "pytest found 3 failures"}
```

**Benefits**:
- Type-safe status checking
- No LLM interpretation needed
- Faster failure detection

### 2. Automatic Recovery

Failures trigger replanning without manual intervention:

```python
if executor_output["success"] == False:
    return "planner"  # Automatic replan
```

**Benefits**:
- Self-healing on errors
- No reviewer overhead for failures
- Faster recovery cycles

### 3. Context Window Management

Large tool outputs handled via pruning:

```python
# Keep recent messages intact
# Summarize old tool outputs
# Store full outputs out-of-band
```

**Benefits**:
- Stay within token limits
- Preserve critical context
- Access full outputs when needed

### 4. Separation of Concerns

Each module has a single, clear responsibility:

```python
config.py    # What to say (prompts)
state.py     # What to remember (data)
nodes.py     # What to do (actions)
routing.py   # Where to go (flow)
tools.py     # How to act (capabilities)
pruning.py   # How to fit (optimization)
graph.py     # How to connect (structure)
agent.py     # How to use (interface)
```

**Benefits**:
- Easy to understand
- Simple to modify
- Straightforward to test

## Error Handling Strategy

### Level 1: Tool Execution

```python
try:
    result = tool.invoke(params)
except Exception as e:
    return f"Error: {str(e)}"
```

### Level 2: Executor Response Parsing

```python
try:
    output = parse_executor_response(content)
except Exception as e:
    output = ExecutorOutput(success=False, output=str(e))
```

### Level 3: JSON Fallbacks

```python
try:
    plan = json.loads(response)
except json.JSONDecodeError:
    plan = [response]  # Treat as single step
```

### Level 4: Routing Safety

```python
if state["iters"] >= state["max_iters"]:
    return END  # Prevent infinite loops
```

## Performance Characteristics

### Token Usage

- **With Pruning**: ~1000-2000 tokens per executor turn
- **Without Pruning**: Can exceed 10000+ tokens with large outputs
- **Message Retention**: Last 20-30 messages kept intact
- **Tool Output Compression**: Head (1000) + tail (500) + metadata

### Iteration Efficiency

- **Successful Path**: Planner → Executor → Reviewer → Advance (1 iter)
- **Retry Path**: Planner → Executor (fail) → Planner (1 iter)
- **Typical Task**: 5-15 iterations for moderate complexity

### Failure Recovery

- **Automatic Recovery**: 1 iteration overhead (planner only)
- **Manual Recovery**: 2+ iterations (reviewer + planner)
- **Speedup**: ~50% faster failure handling

## Extension Points

### Adding New Tools

```python
# In ai_researcher_tools/
def my_new_tool(repo_root: str, param: str) -> str:
    """Tool description."""
    # Implementation
    return result

# In agent_v3_claude/tools.py
from ai_researcher_tools import my_new_tool
TOOLS = [..., my_new_tool]
```

### Custom LLM Provider

```python
# In nodes.py
def require_llm() -> BaseChatModel:
    return YourCustomLLM(...)
```

### Custom Pruning Strategy

```python
# Modify pruning.py
def prune_messages_for_llm(
    messages: list[BaseMessage],
    config: PruningConfig
) -> list[BaseMessage]:
    # Your custom pruning logic
    return pruned_messages
```

### Additional Nodes

```python
# Add to graph.py
def my_custom_node(state: AgentState) -> AgentState:
    # Your logic
    return state

graph.add_node("my_node", my_custom_node)
graph.add_edge("some_node", "my_node")
```

## Related Documentation

- [README.md](README.md) - User guide and quick start
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Evolution history
- [../FEATURES.md](../FEATURES.md) - Feature implementations
- [../readme.md](../readme.md) - Project overview

