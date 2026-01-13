"""Test the parse_executor_response function with various input formats."""

from ai_researcher.agent_v3_claude.tools import parse_executor_response


def test_direct_json():
    """Test with direct JSON format."""
    content = '{"success": true, "output": "Task completed successfully"}'
    result = parse_executor_response(content)
    assert result["success"] == True
    assert result["output"] == "Task completed successfully"
    print("✓ Direct JSON test passed")


def test_json_with_surrounding_text():
    """Test with JSON wrapped in additional text."""
    content = """
Let me start by checking the current state of the directory.

{"success": true, "output": "Directory initialized successfully"}

Now the task is complete.
"""
    result = parse_executor_response(content)
    assert result["success"] == True
    assert result["output"] == "Directory initialized successfully"
    print("✓ JSON with surrounding text test passed")


def test_json_with_complex_surrounding_text():
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
    assert result["success"] == True
    assert result["output"] == "Git repository initialized and files listed"
    print("✓ Complex surrounding text test passed")


def test_json_with_nested_objects():
    """Test with JSON containing nested objects in output."""
    content = """
Here is the result:

{"success": false, "output": "Error: Failed with status {'code': 1, 'message': 'failure'}"}

End of execution.
"""
    result = parse_executor_response(content)
    assert result["success"] == False
    assert "Error: Failed with status" in result["output"]
    print("✓ Nested objects test passed")


def test_multiple_json_objects():
    """Test when there are multiple JSON objects - should pick the one with success/output."""
    content = """
First we have: {"name": "test", "value": 123}

Then the result: {"success": true, "output": "Completed"}

And some more data: {"data": "extra"}
"""
    result = parse_executor_response(content)
    assert result["success"] == True
    assert result["output"] == "Completed"
    print("✓ Multiple JSON objects test passed")


def test_invalid_content():
    """Test with content that has no valid JSON."""
    content = "This is just plain text with no JSON"
    try:
        result = parse_executor_response(content)
        print("✗ Should have raised ValueError")
        assert False
    except ValueError as e:
        assert "Could not find valid JSON" in str(e)
        print("✓ Invalid content test passed")


if __name__ == "__main__":
    test_direct_json()
    test_json_with_surrounding_text()
    test_json_with_complex_surrounding_text()
    test_json_with_nested_objects()
    test_multiple_json_objects()
    test_invalid_content()
    print("\n✅ All tests passed!")

