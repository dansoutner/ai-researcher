"""Tests for Agent v3 tool binding and compatibility."""

import os
import pytest


def test_tools_are_langchain_compatible():
    """Verify that all tools have the necessary attributes for LangChain binding."""
    from ai_researcher.agent_v3_claude.tools import TOOLS

    for tool in TOOLS:
        # Check that tool has required attributes
        assert hasattr(tool, 'name'), f"Tool {tool} missing 'name' attribute"
        assert hasattr(tool, 'invoke'), f"Tool {tool.name} missing 'invoke' method"


@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
    reason="No API keys available"
)
def test_llm_bind_tools():
    """Test that LLM can bind tools without errors."""
    from ai_researcher.agent_v3_claude.tools import TOOLS

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if anthropic_key:
        from langchain_anthropic import ChatAnthropic

        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0,
            api_key=anthropic_key
        )
        llm_with_tools = llm.bind_tools(TOOLS)
        assert llm_with_tools is not None

    elif openai_key:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4", temperature=0)
        llm_with_tools = llm.bind_tools(TOOLS)
        assert llm_with_tools is not None

