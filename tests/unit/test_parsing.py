"""Unit tests for JSON parsing utilities in agent v3."""

import json
import pytest

from ai_researcher.agent_v3_claude.tools import parse_executor_response
from ai_researcher.agent_v3_claude.nodes import parse_reviewer_response


class TestExecutorResponseParsing:
    """Tests for parse_executor_response function."""

    def test_direct_json(self):
        """Test with direct JSON format."""
        content = '{"success": true, "output": "Task completed successfully"}'
        result = parse_executor_response(content)
        assert result["success"] is True
        assert result["output"] == "Task completed successfully"

    def test_json_with_surrounding_text(self):
        """Test with JSON wrapped in additional text."""
        content = """
Let me start by checking the current state of the directory.

{"success": true, "output": "Directory initialized successfully"}

Now the task is complete.
"""
        result = parse_executor_response(content)
        assert result["success"] is True
        assert result["output"] == "Directory initialized successfully"

    def test_json_with_complex_surrounding_text(self):
        """Test with the example format from the user."""
        content = """
Let me start by checking the current state of the directory and then initialize the Git repository.

<tool_calls>
<tool_call>
{"name": "list_files", "arguments": {"path": "."}}
</tool_call>
</tool_calls>

After reviewing the files, here's the result:

{"success": true, "output": "Git repository initialized and files listed"}

Let me verify the initialization was successful.
"""
        result = parse_executor_response(content)
        assert result["success"] is True
        assert result["output"] == "Git repository initialized and files listed"

    def test_json_with_nested_objects(self):
        """Test with JSON containing nested objects in output."""
        content = """
Here is the result:

{"success": false, "output": "Error: Failed with status {'code': 1, 'message': 'failure'}"}

End of execution.
"""
        result = parse_executor_response(content)
        assert result["success"] is False
        assert "Error: Failed with status" in result["output"]

    def test_multiple_json_objects(self):
        """Test when there are multiple JSON objects - should pick the one with success/output."""
        content = """
First we have: {"name": "test", "value": 123}

Then the result: {"success": true, "output": "Completed"}

And some more data: {"data": "extra"}
"""
        result = parse_executor_response(content)
        assert result["success"] is True
        assert result["output"] == "Completed"

    def test_invalid_content(self):
        """Test with content that has no valid JSON."""
        content = "This is just plain text with no JSON"
        with pytest.raises(ValueError, match="Could not find valid JSON"):
            parse_executor_response(content)


class TestReviewerResponseParsing:
    """Tests for parse_reviewer_response function."""

    def test_direct_json(self):
        """Test parsing direct JSON response."""
        content = json.dumps({
            "verdict": "continue",
            "reason": "Step completed successfully",
            "fix_suggestion": ""
        })

        result = parse_reviewer_response(content)
        assert result["verdict"] == "continue"
        assert result["reason"] == "Step completed successfully"

    def test_json_with_surrounding_text(self):
        """Test parsing JSON embedded in text."""
        content = """The step looks good!

Here's my decision:

{
  "verdict": "retry",
  "reason": "The command failed",
  "fix_suggestion": "Try using a different approach"
}

That's my analysis."""

        result = parse_reviewer_response(content)
        assert result["verdict"] == "retry"
        assert result["reason"] == "The command failed"
        assert result["fix_suggestion"] == "Try using a different approach"

    def test_json_with_markdown(self):
        """Test parsing JSON in markdown code block."""
        content = """```json
{
  "verdict": "finish",
  "reason": "Goal completed",
  "fix_suggestion": ""
}
```"""

        # This should extract the JSON from the markdown
        result = parse_reviewer_response(content)
        assert result["verdict"] == "finish"

    def test_invalid_verdict(self):
        """Test that invalid verdicts raise an error."""
        content = json.dumps({
            "verdict": "invalid_verdict",
            "reason": "Test",
            "fix_suggestion": ""
        })

        with pytest.raises(ValueError, match="Verdict must be one of"):
            parse_reviewer_response(content)

    def test_no_json(self):
        """Test that non-JSON content raises an error."""
        content = "This is just plain text with no JSON at all."

        with pytest.raises(ValueError, match="Could not find valid JSON"):
            parse_reviewer_response(content)

    def test_verdict_continue(self):
        """Test with 'continue' verdict."""
        content = """The step was successful.

{
  "verdict": "continue",
  "reason": "Task completed successfully",
  "fix_suggestion": ""
}"""

        result = parse_reviewer_response(content)
        assert result["verdict"] == "continue"
        assert result["reason"] == "Task completed successfully"

