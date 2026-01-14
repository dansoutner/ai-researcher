"""Quick test to verify datetime is properly added to prompts."""

from ai_researcher.agent_v3_claude.config import (
    get_current_datetime,
    PLANNER_SYSTEM_PROMPT,
    EXECUTOR_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
)


def test_datetime_function():
    """Test that get_current_datetime returns a valid datetime string."""
    dt = get_current_datetime()
    print(f"✓ get_current_datetime() returns: {dt}")
    assert isinstance(dt, str)
    assert len(dt) > 0


def test_prompts_have_placeholder():
    """Test that all prompts have the {current_datetime} placeholder."""
    assert "{current_datetime}" in PLANNER_SYSTEM_PROMPT
    print("✓ PLANNER_SYSTEM_PROMPT has {current_datetime} placeholder")

    assert "{current_datetime}" in EXECUTOR_SYSTEM_PROMPT
    print("✓ EXECUTOR_SYSTEM_PROMPT has {current_datetime} placeholder")

    assert "{current_datetime}" in REVIEWER_SYSTEM_PROMPT
    print("✓ REVIEWER_SYSTEM_PROMPT has {current_datetime} placeholder")


def test_prompt_formatting():
    """Test that prompts can be formatted with current datetime."""
    dt = get_current_datetime()

    formatted_planner = PLANNER_SYSTEM_PROMPT.format(current_datetime=dt)
    assert dt in formatted_planner
    print(f"✓ PLANNER_SYSTEM_PROMPT formatted successfully with datetime: {dt}")

    formatted_executor = EXECUTOR_SYSTEM_PROMPT.format(current_datetime=dt)
    assert dt in formatted_executor
    print(f"✓ EXECUTOR_SYSTEM_PROMPT formatted successfully with datetime: {dt}")

    formatted_reviewer = REVIEWER_SYSTEM_PROMPT.format(current_datetime=dt)
    assert dt in formatted_reviewer
    print(f"✓ REVIEWER_SYSTEM_PROMPT formatted successfully with datetime: {dt}")


if __name__ == "__main__":
    print("Testing datetime integration in agent prompts...\n")

    test_datetime_function()
    print()

    test_prompts_have_placeholder()
    print()

    test_prompt_formatting()
    print()

    print("✅ All tests passed! Datetime is properly integrated into prompts.")

