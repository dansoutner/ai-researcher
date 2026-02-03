# LLM Usage Logging Implementation

## Overview
Added detailed logging of LLM input/output character counts and token usage (when available) to help debug and monitor LLM API calls across all agent roles.

## Changes Made

### 1. New Function: `log_llm_usage` in `logging_utils.py`

Added a new utility function that logs:
- **Character counts**: Input and output message character counts
- **Token counts**: Input, output, and total tokens (when available from LLM provider)

The function handles both Anthropic-style (`usage_metadata`) and OpenAI-style (`response_metadata`) token reporting.

```python
def log_llm_usage(logger, role: str, messages: list, response) -> None:
    """Log LLM input/output character and token counts for debugging."""
```

### 2. Updated `nodes.py`

Added logging calls after LLM invocations in:
- **Planner Node** (line ~211): Logs planning request/response statistics
- **Reviewer Node** (line ~320): Logs review request/response statistics

Example log output:
```
[Planner] LLM Usage - Input: 1234 chars, Output: 567 chars
[Planner] LLM Tokens - Input: 300, Output: 120, Total: 420
```

### 3. Updated `tools.py`

Added logging call after LLM invocation in:
- **Executor Node** (line ~290): Logs executor request/response statistics

Example log output:
```
[Executor] LLM Usage - Input: 2345 chars, Output: 890 chars
[Executor] LLM Tokens - Input: 450, Output: 200, Total: 650
```

## Benefits

1. **Cost Monitoring**: Track token usage to estimate API costs
2. **Performance Analysis**: Identify which roles use the most tokens
3. **Debugging**: Understand context window usage and potential overflow issues
4. **Optimization**: Identify opportunities to reduce prompt sizes

## Log Level

All usage statistics are logged at **DEBUG** level, so they won't clutter normal INFO-level logs but are available when needed.

## Token Support

The function automatically detects and reports tokens from:
- **Anthropic**: `usage_metadata.input_tokens`, `usage_metadata.output_tokens`
- **OpenAI**: `response_metadata.usage.prompt_tokens`, `response_metadata.usage.completion_tokens`

If token information is not available (e.g., custom LLM providers), only character counts are logged.

## Files Modified

1. `/ai_researcher/agent_v3_claude/logging_utils.py` - Added `log_llm_usage()` function
2. `/ai_researcher/agent_v3_claude/nodes.py` - Added logging calls in planner and reviewer nodes
3. `/ai_researcher/agent_v3_claude/tools.py` - Added logging call in executor node

## Example Usage

When running the agent with DEBUG logging enabled, you'll see output like:

```
[Planner] LLM Usage - Input: 1234 chars, Output: 567 chars
[Planner] LLM Tokens - Input: 300, Output: 120, Total: 420
=== PLANNER NODE (iteration 0) ===
============================================================
PLAN GENERATED
============================================================
1. Create a new file
2. Test the implementation
============================================================

[Executor] LLM Usage - Input: 2345 chars, Output: 890 chars
[Executor] LLM Tokens - Input: 450, Output: 200, Total: 650
=== EXECUTOR NODE (iteration 0, step 1/2) ===
Executing step: Create a new file

[Reviewer] LLM Usage - Input: 1567 chars, Output: 234 chars
[Reviewer] LLM Tokens - Input: 380, Output: 55, Total: 435
=== REVIEWER NODE (iteration 0) ===
Reviewer verdict: CONTINUE
```

This provides visibility into LLM usage at each step of the agent workflow.

