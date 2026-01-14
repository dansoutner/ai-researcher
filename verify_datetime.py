#!/usr/bin/env python3
"""Quick verification that the datetime integration works."""

import sys
sys.path.insert(0, '/Users/dan/pex/ai-researcher')

try:
    from ai_researcher.agent_v3_claude.config import (
        get_current_datetime,
        PLANNER_SYSTEM_PROMPT,
        EXECUTOR_SYSTEM_PROMPT,
        REVIEWER_SYSTEM_PROMPT,
    )

    print("✓ Imports successful")

    # Test datetime function
    dt = get_current_datetime()
    print(f"✓ get_current_datetime() works: {dt}")

    # Test that placeholders exist
    assert "{current_datetime}" in PLANNER_SYSTEM_PROMPT
    assert "{current_datetime}" in EXECUTOR_SYSTEM_PROMPT
    assert "{current_datetime}" in REVIEWER_SYSTEM_PROMPT
    print("✓ All prompts have {current_datetime} placeholder")

    # Test formatting
    formatted = PLANNER_SYSTEM_PROMPT.format(current_datetime=dt)
    assert dt in formatted
    print(f"✓ Prompt formatting works correctly")

    print("\n✅ All datetime integration tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

