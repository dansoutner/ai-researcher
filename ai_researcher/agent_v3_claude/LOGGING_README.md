# Agent V3 Colored Logging System 🎨

## Overview

The agent_v3_claude package now features a professional, color-coded logging system that makes it easy to understand what's happening at each stage of agent execution.

## Quick Start

```python
from ai_researcher.agent_v3_claude import run

# Run the agent - logging happens automatically!
state = run(
    goal="Create a Python package with tests",
    max_iters=10
)
```

The agent will now output color-coded logs showing:
- 🟢 **GREEN** - Progress and state changes
- 🟣 **MAGENTA** - Plans and user-facing results  
- 🔷 **BLUE** - Tool execution details
- 🔵 **CYAN** - Debug information
- 🟡 **YELLOW** - Warnings
- 🔴 **RED** - Errors

## Log Levels

| Level | Color | When to Use | Example |
|-------|-------|-------------|---------|
| `DEBUG` | 🔵 Cyan | System internals, debugging | `"Retrieved working directory from memory"` |
| `TOOL` | 🔷 Blue | Tool calls and results | `"Calling tool: git_status"` |
| `INFO` | 🟢 Green | State transitions, progress | `"=== EXECUTOR NODE (iteration 1) ==="` |
| `USER` | 🟣 Magenta | Plans, results, summaries | `"PLAN GENERATED"` |
| `WARNING` | 🟡 Yellow | Potential issues | `"Executor failed, setting verdict to retry"` |
| `ERROR` | 🔴 Red | Errors, failures | `"Tool exception: FileNotFoundError"` |

## Usage in Your Code

### Get a Logger
```python
from ai_researcher.agent_v3_claude.logging_utils import get_logger

logger = get_logger(__name__)
```

### Log Messages
```python
# Different log levels
logger.debug("Detailed debugging information")
logger.tool("Executing tool with args: {...}")
logger.info("Important state change")
logger.user("This message is for the end user")
logger.warning("Something unexpected happened")
logger.error("An error occurred")
```

### Format Headers
```python
from ai_researcher.agent_v3_claude.logging_utils import (
    format_section_header,
    format_subsection_header
)

logger.user(format_section_header("PLAN GENERATED"))
logger.user("1. First step")
logger.user("2. Second step")

logger.user(format_subsection_header("Execution Results"))
logger.user("All steps completed")
```

## Adjusting Verbosity

Control what you see by setting the log level:

```python
from ai_researcher.agent_v3_claude import setup_logger
import logging

# Development mode - show everything
logger = setup_logger("agent", level=logging.DEBUG)
# Shows: DEBUG, TOOL, INFO, USER, WARNING, ERROR

# Production mode - important info only  
logger = setup_logger("agent", level=logging.INFO)
# Shows: INFO, USER, WARNING, ERROR

# Quiet mode - problems only
logger = setup_logger("agent", level=logging.WARNING)
# Shows: WARNING, ERROR
```

## Examples

### Agent Workflow Output
```
INFO  | Starting agent run with goal: Create a Python package
INFO  | === PLANNER NODE (iteration 0) ===
DEBUG | First iteration - saving working directory to memory

USER  | ============================================================
USER  | PLAN GENERATED
USER  | ============================================================
USER  | 1. Verify environment (git status, python version)
USER  | 2. Create package structure
USER  | 3. Write tests
USER  | 4. Run tests to verify
USER  | ============================================================

INFO  | === EXECUTOR NODE (iteration 0, step 1/4) ===
INFO  | Executing step: Verify environment
DEBUG | Retrieved working directory from memory

TOOL  | Calling tool: git_status
TOOL  | Tool args: {'repo_root': '/path/to/repo'}
TOOL  | Tool result: On branch main, nothing to commit

INFO  | === REVIEWER NODE (iteration 0) ===
DEBUG | Executor output: {'success': True, 'output': '...'}
INFO  | Reviewer verdict: CONTINUE
```

### Error Handling
```
TOOL  | Calling tool: read_file
TOOL  | Tool args: {'path': 'missing.py'}
ERROR | Tool exception: FileNotFoundError: missing.py not found

WARNING | Executor failed, automatically setting verdict to 'retry'

INFO  | === PLANNER NODE (iteration 1) ===
USER  | Replanning with error context...
```

## Demo Scripts

Two demo scripts are provided:

1. **`test_logging.py`** - Simple test of all log levels
   ```bash
   python test_logging.py
   ```

2. **`demo_logging.py`** - Comprehensive demo with simulated agent workflow
   ```bash
   python demo_logging.py
   ```

## Benefits

✅ **Visual Clarity** - Colors help you quickly scan logs  
✅ **Professional** - Uses Python's standard logging module  
✅ **Flexible** - Adjust verbosity based on your needs  
✅ **Consistent** - All modules use the same logging system  
✅ **Tool Visibility** - Dedicated level for tracking tool execution  
✅ **User-Focused** - Separate level for end-user messages  

## Technical Details

For detailed technical documentation, see:
- `docs/AGENT_V3_LOGGING_UPDATE.md` - Implementation details
- `docs/AGENT_V3_LOGGING_EXAMPLES.md` - Visual examples  
- `docs/AGENT_V3_LOGGING_SUMMARY.md` - Migration summary

## Backward Compatibility

The logging system is fully backward compatible. No changes needed to existing scripts:

```python
# This still works exactly as before
from ai_researcher.agent_v3_claude import run

state = run(goal="...", max_iters=10)
```

The only difference is you now get beautiful, color-coded output! 🎨

