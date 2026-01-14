# Agent V3 Logging System Update

## Overview
Updated agent_v3_claude to use a proper structured logging system with color-coded output to distinguish between different types of messages.

## Changes Made

### 1. Created New Logging Utility Module
**File:** `ai_researcher/agent_v3_claude/logging_utils.py`

This module provides:
- **Colored output** using ANSI color codes
- **Custom log levels**:
  - `DEBUG` (Cyan): Internal system operations and detailed debugging
  - `TOOL` (Blue): Tool execution details
  - `INFO` (Green): Important state changes and progress
  - `USER` (Magenta): Messages intended for end users (results, summaries)
  - `WARNING` (Yellow): Potential issues
  - `ERROR` (Red): Errors and failures
  - `CRITICAL` (Bold Red): Critical errors

- **Custom logging methods**:
  - `logger.debug()` - Debug information
  - `logger.tool()` - Tool execution info
  - `logger.info()` - General information
  - `logger.user()` - User-facing messages
  - `logger.warning()` - Warnings
  - `logger.error()` - Errors

- **Formatting utilities**:
  - `format_section_header(title)` - Creates section headers with === borders
  - `format_subsection_header(title)` - Creates subsection headers with --- borders

### 2. Updated All Agent Files

#### agent.py
- Replaced all `print()` statements with appropriate logger calls
- `[DEBUG]` prints → `logger.debug()`
- Agent execution status → `logger.info()`
- User-facing results → `logger.user()`

#### nodes.py
- Added logger to all three node functions:
  - `planner_node()`: Uses `logger.info()` for node entry, `logger.user()` for plan display
  - `executor_node()`: Uses `logger.info()` for execution status, `logger.warning()` for errors
  - `reviewer_node()`: Uses `logger.info()` for verdicts, `logger.debug()` for details
- Replaced JSON parsing debug prints with `logger.debug()`

#### tools.py
- Added `logger.tool()` for tool execution details:
  - Tool name and arguments
  - Tool result length and preview
  - Tool errors
- Replaced executor response parsing debug with `logger.debug()`

#### cli.py
- Updated to use logger for .env loading status
- User-facing output uses `logger.user()`

#### __init__.py
- Exported logging utilities: `setup_logger`, `get_logger`, `agent_logger`

### 3. Color Scheme

The color scheme is designed to make it easy to distinguish different types of output:

```
DEBUG  (Cyan)    → System internals, detailed debugging
TOOL   (Blue)    → Tool calls, args, and results
INFO   (Green)   → State changes, node transitions
USER   (Magenta) → Results, summaries, plans (user-facing)
WARNING(Yellow)  → Potential issues
ERROR  (Red)     → Errors and failures
```

## Usage Examples

### Basic Usage
```python
from ai_researcher.agent_v3_claude.logging_utils import get_logger

logger = get_logger(__name__)

# Different log levels
logger.debug("Detailed debug info")
logger.tool("Executing tool: list_files")
logger.info("Entering executor node")
logger.user("Plan step completed successfully")
logger.warning("File not found, using default")
logger.error("Failed to parse response")
```

### With Formatted Headers
```python
from ai_researcher.agent_v3_claude.logging_utils import (
    get_logger,
    format_section_header,
    format_subsection_header
)

logger = get_logger(__name__)

logger.user(format_section_header("PLAN GENERATED"))
logger.user("1. First step")
logger.user("2. Second step")
logger.user("=" * 60)

logger.user(format_subsection_header("Execution Results"))
logger.user("All tests passed")
```

### Setting Log Level
```python
from ai_researcher.agent_v3_claude.logging_utils import setup_logger
import logging

# Show only INFO and above (hides DEBUG and TOOL)
logger = setup_logger("my_module", level=logging.INFO)

# Show everything including DEBUG
logger = setup_logger("my_module", level=logging.DEBUG)

# Show only warnings and errors
logger = setup_logger("my_module", level=logging.WARNING)
```

## Benefits

1. **Better Organization**: Structured logging instead of scattered print statements
2. **Visual Clarity**: Color-coded output makes it easy to scan logs
3. **Filterable**: Can adjust log level to hide/show different message types
4. **Professional**: Standard Python logging interface
5. **User Experience**: Clear distinction between debug info and user-facing messages
6. **Debugging**: TOOL level specifically for tracking tool execution
7. **Consistent**: All modules use the same logging system

## Testing

A test script has been created at `test_logging.py` to demonstrate all logging levels and colors.

Run it with:
```bash
python test_logging.py
```

## Migration Notes

All previous `print()` statements have been replaced with appropriate logger calls:
- `print(f"[DEBUG] ...")` → `logger.debug(...)`
- Status messages → `logger.info(...)`
- User-facing output → `logger.user(...)`
- Tool execution → `logger.tool(...)`
- Errors → `logger.error(...)`

## Future Enhancements

Possible future improvements:
1. Add log file output in addition to console
2. Add structured logging (JSON format) for machine parsing
3. Add log rotation for long-running agents
4. Add performance metrics logging
5. Add configurable color themes

