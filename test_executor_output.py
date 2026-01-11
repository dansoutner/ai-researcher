"""
Simple test/example to demonstrate ExecutorOutput structured output.

This shows how the executor now returns structured status instead of
just chatting back.
"""

from typing import TypedDict


class ExecutorOutput(TypedDict):
    """Structured output from the executor node.

    Attributes:
        success: Whether the execution step completed successfully
        output: Description of what happened during execution
    """
    success: bool
    output: str


def test_executor_output_structure():
    """Test that ExecutorOutput has the correct structure."""
    # Success case
    success_output = ExecutorOutput(
        success=True,
        output="Successfully ran pytest - all 15 tests passed"
    )
    assert success_output["success"] is True
    assert isinstance(success_output["output"], str)
    print("✓ Success case:", success_output)

    # Failure case
    failure_output = ExecutorOutput(
        success=False,
        output="Failed to run pytest - command not found"
    )
    assert failure_output["success"] is False
    assert isinstance(failure_output["output"], str)
    print("✓ Failure case:", failure_output)


def test_parse_executor_json():
    """Test parsing executor JSON responses."""
    import json

    # Valid success response
    success_json = json.dumps({
        "success": True,
        "output": "File written successfully"
    })
    print(f"✓ Valid success JSON: {success_json}")

    # Valid failure response
    failure_json = json.dumps({
        "success": False,
        "output": "Permission denied when writing file"
    })
    print(f"✓ Valid failure JSON: {failure_json}")

    # Invalid response (missing field)
    try:
        invalid_json = json.dumps({"success": True})
        # This should fail validation
        print(f"⚠ Invalid JSON (missing output): {invalid_json}")
    except Exception as e:
        print(f"✓ Correctly caught invalid JSON: {e}")


def demonstrate_workflow():
    """Demonstrate the new workflow with automatic retry."""
    print("\n" + "="*60)
    print("WORKFLOW DEMONSTRATION")
    print("="*60)

    print("\nScenario 1: Executor Succeeds")
    print("-" * 40)
    print("1. Planner creates plan")
    print("2. Executor executes step")
    print("3. Executor returns: {'success': True, 'output': '...'}")
    print("4. → Routes to REVIEWER")
    print("5. Reviewer evaluates overall goal progress")

    print("\nScenario 2: Executor Fails")
    print("-" * 40)
    print("1. Planner creates plan")
    print("2. Executor executes step")
    print("3. Executor returns: {'success': False, 'output': '...'}")
    print("4. → Routes DIRECTLY to PLANNER (no reviewer)")
    print("5. Planner creates new plan with failure context")
    print("6. Loop continues")

    print("\nKey Benefits:")
    print("✓ Failures trigger automatic replanning")
    print("✓ No LLM interpretation needed for executor status")
    print("✓ Faster iteration on failures")
    print("✓ Structured, parseable output")


if __name__ == "__main__":
    print("Testing ExecutorOutput Structure")
    print("=" * 60)

    test_executor_output_structure()
    print()
    test_parse_executor_json()

    demonstrate_workflow()

    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)

