#!/usr/bin/env python3
"""Quick test to verify agent_v3_claude has all tools from ai_researcher_tools."""

def test_tools_imported():
    """Verify that all expected tools are imported and available."""
    from agent_v3_claude.agent import TOOLS, TOOL_BY_NAME

    expected_tools = {
        # File system
        'read_file', 'write_file', 'list_files', 'grep',
        # Git
        'git_diff', 'git_status', 'git_add', 'git_commit', 'git_log',
        'git_branch_list', 'git_checkout', 'git_remote_list', 'git_prepare_pr',
        # Commands
        'apply_patch', 'run_pytest', 'run_cmd',
        # Virtual environment
        'create_venv', 'run_in_venv',
        # Memory
        'memory_set', 'memory_get', 'memory_list', 'memory_delete',
        'memory_append', 'store_repo_map', 'store_test_results', 'clear_memory',
    }

    actual_tools = set(TOOL_BY_NAME.keys())

    print(f"Expected {len(expected_tools)} tools, found {len(actual_tools)} tools")

    missing = expected_tools - actual_tools
    extra = actual_tools - expected_tools

    if missing:
        print(f"❌ Missing tools: {missing}")
        assert False, f"Missing tools: {missing}"

    if extra:
        print(f"⚠️  Extra tools: {extra}")

    if not missing and not extra:
        print("✅ All expected tools are present!")

    print("\nAvailable tools:")
    for name in sorted(actual_tools):
        tool = TOOL_BY_NAME[name]
        print(f"  - {name}: {tool.description[:80]}...")

    assert len(TOOLS) == len(expected_tools), f"Expected {len(expected_tools)} tools, got {len(TOOLS)}"
    print(f"\n✅ Tool count matches: {len(TOOLS)} tools")

if __name__ == "__main__":
    test_tools_imported()
    print("\n🎉 All tests passed!")

