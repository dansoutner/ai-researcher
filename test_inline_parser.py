#!/usr/bin/env python3
"""Simple inline test for parse_executor_response."""

import json
import re
from typing import TypedDict


class ExecutorOutput(TypedDict):
    """Executor output structure."""
    success: bool
    output: str


def parse_executor_response(content: str) -> ExecutorOutput:
    """Parse executor response JSON to extract execution result."""
    # Try to parse as direct JSON first
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from surrounding text
        # Look for JSON object patterns
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, content, re.DOTALL)

        data = None
        for match in matches:
            try:
                parsed = json.loads(match)
                # Check if this looks like our executor response format
                if isinstance(parsed, dict) and "success" in parsed and "output" in parsed:
                    data = parsed
                    break
            except json.JSONDecodeError:
                continue

        if data is None:
            raise ValueError(f"Could not find valid JSON in response. Content: {content[:500]}")

    if "success" not in data or not isinstance(data["success"], bool):
        raise ValueError("Response must contain 'success' boolean field")

    if "output" not in data or not isinstance(data["output"], str):
        raise ValueError("Response must contain 'output' string field")

    return ExecutorOutput(
        success=data["success"],
        output=data["output"]
    )


# Test cases
print("Test 1: Direct JSON")
result1 = parse_executor_response('{"success": true, "output": "Done"}')
print(f"  Result: {result1}")
assert result1["success"] == True

print("\nTest 2: JSON with surrounding text")
content2 = """
Some text before

{"success": false, "output": "Failed"}

Some text after
"""
result2 = parse_executor_response(content2)
print(f"  Result: {result2}")
assert result2["success"] == False

print("\nTest 3: Complex case with tool calls")
content3 = """
Let me start by checking the current state.

<tool_calls>
<tool_call>
{"name": "list_files", "arguments": {"path": "."}}
</tool_call>
</tool_calls>

Result: {"success": true, "output": "Completed successfully"}

End of execution.
"""
result3 = parse_executor_response(content3)
print(f"  Result: {result3}")
assert result3["success"] == True
assert result3["output"] == "Completed successfully"

print("\n✅ All tests passed!")

