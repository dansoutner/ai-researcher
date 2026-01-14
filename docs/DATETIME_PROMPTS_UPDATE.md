# DateTime Integration in Agent Prompts

## Summary
Added current date and time information to all agent system prompts for better temporal orientation.

## Changes Made

### 1. Config Module (`ai_researcher/agent_v3_claude/config.py`)

#### Added datetime import:
```python
from datetime import datetime
```

#### Added helper function:
```python
def get_current_datetime() -> str:
    """Get current datetime string for agent orientation."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

#### Updated all system prompts:
- `PLANNER_SYSTEM_PROMPT` - Added `**Current Date & Time:** {current_datetime}` near the top
- `EXECUTOR_SYSTEM_PROMPT` - Added `**Current Date & Time:** {current_datetime}` near the top  
- `REVIEWER_SYSTEM_PROMPT` - Added `**Current Date & Time:** {current_datetime}` near the top

All prompts now use Python's `.format()` string interpolation with the `{current_datetime}` placeholder.

### 2. Nodes Module (`ai_researcher/agent_v3_claude/nodes.py`)

#### Updated imports:
```python
from .config import (
    PLANNER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    VALID_VERDICTS,
    get_current_datetime,  # Added
)
```

#### Updated planner_node:
```python
SystemMessage(content=PLANNER_SYSTEM_PROMPT.format(current_datetime=get_current_datetime()))
```

#### Updated reviewer_node:
```python
SystemMessage(content=REVIEWER_SYSTEM_PROMPT.format(current_datetime=get_current_datetime()))
```

### 3. Tools Module (`ai_researcher/agent_v3_claude/tools.py`)

#### Updated imports:
```python
from .config import EXECUTOR_SYSTEM_PROMPT, get_current_datetime
```

#### Updated run_executor_turn:
```python
SystemMessage(content=EXECUTOR_SYSTEM_PROMPT.format(current_datetime=get_current_datetime()))
```

## Benefits

1. **Temporal Context**: Agents now know the current date and time when executing tasks
2. **Time-Sensitive Tasks**: Better handling of tasks that may be time-dependent
3. **Log Analysis**: Agents can better understand when files were modified relative to current time
4. **Deadline Awareness**: Can help with understanding urgency or time constraints
5. **Debugging**: Easier to correlate agent behavior with specific time periods

## Format

The datetime is formatted as: `YYYY-MM-DD HH:MM:SS` (e.g., "2026-01-14 15:30:45")

This format is:
- Human-readable
- Sortable
- Includes both date and time information
- Standard ISO-like format

## Testing

A test script was created at `/Users/dan/pex/ai-researcher/test_datetime_prompts.py` to verify:
1. The `get_current_datetime()` function works correctly
2. All prompts contain the `{current_datetime}` placeholder
3. Prompts can be successfully formatted with the current datetime

## No Breaking Changes

These changes are backward-compatible and only add information to the prompts. The agent behavior remains the same, with enhanced temporal awareness.

