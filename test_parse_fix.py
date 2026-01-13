"""Test the parsing fix for non-string content."""

import sys
sys.path.insert(0, '/Users/dan/pex/ai-researcher')

from ai_researcher.agent_v3_claude.tools import parse_executor_response
from ai_researcher.agent_v3_claude.nodes import parse_reviewer_response, parse_plan_response


def test_empty_list_handling():
    """Test that empty lists are handled properly."""
    print("Testing empty list handling...")

    # Test executor parser with empty list
    try:
        parse_executor_response([])
        print("❌ FAILED: Should have raised ValueError for empty list")
    except ValueError as e:
        print(f"✓ PASSED: Empty list caught with error: {e}")

    # Test reviewer parser with empty list
    try:
        parse_reviewer_response([])
        print("❌ FAILED: Should have raised ValueError for empty list")
    except ValueError as e:
        print(f"✓ PASSED: Empty list caught with error: {e}")

    # Test planner parser with empty list
    try:
        parse_plan_response([])
        print("❌ FAILED: Should have raised ValueError for empty list")
    except ValueError as e:
        print(f"✓ PASSED: Empty list caught with error: {e}")


def test_valid_json_strings():
    """Test that valid JSON strings still work."""
    print("\nTesting valid JSON strings...")

    # Test executor parser with valid JSON
    try:
        result = parse_executor_response('{"success": true, "output": "Test output"}')
        print(f"✓ PASSED: Executor parsed valid JSON: {result}")
    except Exception as e:
        print(f"❌ FAILED: {e}")

    # Test reviewer parser with valid JSON
    try:
        result = parse_reviewer_response('{"verdict": "continue", "reason": "Test reason", "fix_suggestion": ""}')
        print(f"✓ PASSED: Reviewer parsed valid JSON: {result}")
    except Exception as e:
        print(f"❌ FAILED: {e}")

    # Test planner parser with valid JSON
    try:
        result = parse_plan_response('{"plan": ["Step 1", "Step 2"]}')
        print(f"✓ PASSED: Planner parsed valid JSON: {result}")
    except Exception as e:
        print(f"❌ FAILED: {e}")


def test_empty_string_handling():
    """Test that empty strings are handled properly."""
    print("\nTesting empty string handling...")

    # Test executor parser with empty string
    try:
        parse_executor_response("")
        print("❌ FAILED: Should have raised ValueError for empty string")
    except ValueError as e:
        print(f"✓ PASSED: Empty string caught with error: {e}")

    # Test reviewer parser with empty string
    try:
        parse_reviewer_response("")
        print("❌ FAILED: Should have raised ValueError for empty string")
    except ValueError as e:
        print(f"✓ PASSED: Empty string caught with error: {e}")

    # Test planner parser with empty string
    try:
        parse_plan_response("")
        print("❌ FAILED: Should have raised ValueError for empty string")
    except ValueError as e:
        print(f"✓ PASSED: Empty string caught with error: {e}")


if __name__ == "__main__":
    test_empty_list_handling()
    test_valid_json_strings()
    test_empty_string_handling()
    print("\n✓ All tests completed!")

