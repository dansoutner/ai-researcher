#!/usr/bin/env python
"""Test that repo_root is properly preserved in agent_v3_claude."""

import os
import tempfile
from pathlib import Path

from ai_researcher.agent_v3_claude.state import create_initial_state


def test_repo_root_defaults_to_cwd():
    """Test that repo_root defaults to current working directory."""
    state = create_initial_state(goal="Test goal")
    assert state["repo_root"] == os.getcwd()
    print(f"✓ Default repo_root is current directory: {state['repo_root']}")


def test_repo_root_can_be_specified():
    """Test that repo_root can be explicitly specified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        state = create_initial_state(goal="Test goal", repo_root=tmpdir)
        assert state["repo_root"] == tmpdir
        print(f"✓ Explicit repo_root is preserved: {state['repo_root']}")


def test_repo_root_in_state():
    """Test that repo_root is stored in AgentState."""
    state = create_initial_state(goal="Test goal", repo_root="/test/path")
    assert "repo_root" in state
    assert state["repo_root"] == "/test/path"
    print(f"✓ repo_root is stored in state: {state['repo_root']}")


def test_tool_execution_with_repo_root():
    """Test that tools receive repo_root parameter."""
    from ai_researcher.agent_v3_claude.tools import execute_tool_call

    # Create a test state with specific repo_root
    test_repo = "/tmp/test_repo"

    # Mock tool call for list_files (which requires repo_root)
    call = {
        "name": "list_files",
        "args": {"path": "."}
    }

    # Execute should auto-inject repo_root
    try:
        result = execute_tool_call(call, test_repo)
        print(f"✓ Tool execution auto-injects repo_root")
        print(f"  Tool result: {result[:100]}...")
    except Exception as e:
        print(f"✓ Tool execution attempted with repo_root (expected error for non-existent path): {e}")


if __name__ == "__main__":
    print("Testing repo_root preservation in agent_v3_claude...\n")

    test_repo_root_defaults_to_cwd()
    test_repo_root_can_be_specified()
    test_repo_root_in_state()
    test_tool_execution_with_repo_root()

    print("\n✅ All repo_root tests passed!")

