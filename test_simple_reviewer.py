import json
from ai_researcher.agent_v3_claude.nodes import parse_reviewer_response

# Test with proper reviewer response with surrounding text
content = """The step was successful.

{
  "verdict": "continue",
  "reason": "Task completed successfully",
  "fix_suggestion": ""
}"""

try:
    result = parse_reviewer_response(content)
    print(f"✓ Test passed! Parsed verdict: {result['verdict']}")
    print(f"  Reason: {result['reason']}")
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()

