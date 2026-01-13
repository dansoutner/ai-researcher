#!/usr/bin/env python3
"""Test reviewer JSON parsing fix."""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_researcher.agent_v3_claude.nodes import parse_reviewer_response

def test_direct_json():
    """Test parsing direct JSON response."""
    content = json.dumps({
        "verdict": "continue",
        "reason": "Step completed successfully",
        "fix_suggestion": ""
    })

    result = parse_reviewer_response(content)
    assert result["verdict"] == "continue"
    assert result["reason"] == "Step completed successfully"
    print("✓ Direct JSON test passed")

def test_json_with_surrounding_text():
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
    print("✓ JSON with surrounding text test passed")

def test_json_with_markdown():
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
    print("✓ JSON in markdown test passed")

def test_invalid_verdict():
    """Test that invalid verdicts raise an error."""
    content = json.dumps({
        "verdict": "invalid_verdict",
        "reason": "Test",
        "fix_suggestion": ""
    })

    try:
        parse_reviewer_response(content)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Verdict must be one of" in str(e)
        print("✓ Invalid verdict test passed")

def test_no_json():
    """Test that non-JSON content raises an error."""
    content = "This is just plain text with no JSON at all."

    try:
        parse_reviewer_response(content)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Could not find valid JSON" in str(e)
        print("✓ No JSON test passed")

if __name__ == "__main__":
    print("Testing reviewer JSON parsing...")
    test_direct_json()
    test_json_with_surrounding_text()
    test_json_with_markdown()
    test_invalid_verdict()
    test_no_json()
    print("\n✅ All tests passed!")

