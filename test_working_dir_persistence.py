"""Test that working directory is properly saved to memory and recalled."""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import the agent
sys.path.insert(0, str(Path(__file__).parent))

from ai_researcher.ai_researcher_tools import memory_get, memory_set, clear_memory
from ai_researcher.agent_v3_claude.state import create_initial_state


def test_working_dir_persistence():
    """Test that working directory is saved to memory and can be recalled."""

    # Clear any existing memory
    try:
        clear_memory.invoke({})
    except:
        pass

    # Create a temp directory to use as working directory
    with tempfile.TemporaryDirectory() as tmpdir:
        test_workdir = os.path.abspath(tmpdir)
        print(f"\n[TEST] Using test working directory: {test_workdir}")

        # Test 1: Manually save and retrieve
        print("\n[TEST] Test 1: Manual save and retrieve")
        memory_set.invoke({"key": "working_directory", "value": test_workdir})
        retrieved = memory_get.invoke({"key": "working_directory"})
        print(f"[TEST] Retrieved: {retrieved}")
        assert retrieved == test_workdir, f"Expected {test_workdir}, got {retrieved}"
        print("[TEST] ✓ Manual save and retrieve works")

        # Test 2: Create initial state and check repo_root
        print("\n[TEST] Test 2: Initial state repo_root")
        state = create_initial_state(
            goal="Test goal",
            repo_root=test_workdir
        )
        print(f"[TEST] State repo_root: {state['repo_root']}")
        assert state['repo_root'] == test_workdir, f"Expected {test_workdir}, got {state['repo_root']}"
        print("[TEST] ✓ Initial state repo_root is correct")

        # Test 3: Verify memory survives state creation
        print("\n[TEST] Test 3: Memory persists across operations")
        retrieved_after = memory_get.invoke({"key": "working_directory"})
        print(f"[TEST] Retrieved after state creation: {retrieved_after}")
        assert retrieved_after == test_workdir, f"Expected {test_workdir}, got {retrieved_after}"
        print("[TEST] ✓ Memory persists")

        print("\n[TEST] ✅ All tests passed!")
        return True


if __name__ == "__main__":
    # Set minimal env vars for testing
    os.environ.setdefault("LLM_PROVIDER", "openai")
    os.environ.setdefault("LLM_MODEL", "gpt-4")

    try:
        test_working_dir_persistence()
    except Exception as e:
        print(f"\n[TEST] ❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

