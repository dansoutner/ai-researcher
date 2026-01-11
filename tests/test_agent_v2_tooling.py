from __future__ import annotations


def test_agent_v2_can_invoke_root_tools(tmp_path):
    # Import here so the test fails clearly if the integration is broken.
    from ai_researcher.agent_v2.tooling import ToolCall, build_tool_registry, invoke_tool

    registry = build_tool_registry()
    assert "write_file" in registry
    assert "read_file" in registry

    repo_root = tmp_path

    # write then read
    out_write = invoke_tool(
        registry,
        ToolCall(name="write_file", arguments={"repo_root": str(repo_root), "path": "a.txt", "content": "hi"}),
    )
    assert "Wrote a.txt" in out_write

    out_read = invoke_tool(
        registry,
        ToolCall(name="read_file", arguments={"repo_root": str(repo_root), "path": "a.txt"}),
    )
    assert out_read == "hi"


def test_agent_v2_repo_root_default(tmp_path):
    from ai_researcher.agent_v2.tooling import ToolCall, build_tool_registry, invoke_tool

    registry = build_tool_registry()

    # If caller omits repo_root, invoke_tool should fill it from default_repo_root.
    out_write = invoke_tool(
        registry,
        ToolCall(name="write_file", arguments={"path": "b.txt", "content": "yo"}),
        default_repo_root=str(tmp_path),
    )
    assert "Wrote b.txt" in out_write

    out_read = invoke_tool(
        registry,
        ToolCall(name="read_file", arguments={"path": "b.txt"}),
        default_repo_root=str(tmp_path),
    )
    assert out_read == "yo"

