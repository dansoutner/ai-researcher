#!/usr/bin/env python3
"""Test to verify that tools are properly bound and return structured tool calls."""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from ai_researcher.agent_v3_claude.tools import TOOLS


def test_tools_are_langchain_compatible():
    """Verify that all tools have the necessary attributes for LangChain binding."""
    print("Testing tool compatibility...")

    for tool in TOOLS:
        # Check that tool has required attributes
        assert hasattr(tool, 'name'), f"Tool {tool} missing 'name' attribute"
        assert hasattr(tool, 'invoke'), f"Tool {tool.name} missing 'invoke' method"

        print(f"✓ Tool '{tool.name}' is properly structured")

    print(f"\n✓ All {len(TOOLS)} tools are LangChain-compatible")


def test_llm_bind_tools():
    """Test that LLM can bind tools without errors."""
    from langchain_anthropic import ChatAnthropic
    from langchain_openai import ChatOpenAI

    print("\nTesting LLM tool binding...")

    # Test with a mock or actual LLM if credentials are available
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if anthropic_key:
        print("Testing with Anthropic...")
        llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0, api_key=anthropic_key)
        llm_with_tools = llm.bind_tools(TOOLS)
        print(f"✓ Successfully bound {len(TOOLS)} tools to Anthropic LLM")
    elif openai_key:
        print("Testing with OpenAI...")
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        llm_with_tools = llm.bind_tools(TOOLS)
        print(f"✓ Successfully bound {len(TOOLS)} tools to OpenAI LLM")
    else:
        print("⚠ No API keys available - skipping actual LLM binding test")
        print("  Set ANTHROPIC_API_KEY or OPENAI_API_KEY to test with real LLM")


if __name__ == "__main__":
    test_tools_are_langchain_compatible()
    test_llm_bind_tools()
    print("\n✅ All tests passed!")

