"""Integration tests for package structure and imports."""

import pytest


def test_package_import():
    """Test that ai_researcher package can be imported."""
    import ai_researcher

    assert hasattr(ai_researcher, '__version__')


def test_main_exports():
    """Test that main package exports expected items."""
    from ai_researcher import run_v3, AgentState

    assert run_v3 is not None
    assert AgentState is not None


def test_tools_module():
    """Test that ai_researcher_tools module can be imported."""
    from ai_researcher.ai_researcher_tools import read_file, write_file

    assert read_file is not None
    assert write_file is not None


def test_agent_v3_tools():
    """Test that agent v3 has tools available."""
    from ai_researcher.agent_v3_claude.tools import TOOLS, TOOL_BY_NAME

    assert len(TOOLS) > 0
    assert len(TOOL_BY_NAME) > 0
    assert isinstance(TOOL_BY_NAME, dict)


def test_all_agent_versions_importable():
    """Test that all agent versions can be imported."""
    # These should not raise ImportError
    from ai_researcher import agent_v1
    from ai_researcher import agent_v2
    from ai_researcher import agent_v3_claude

    assert agent_v1 is not None
    assert agent_v2 is not None
    assert agent_v3_claude is not None

