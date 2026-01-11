#!/usr/bin/env python3
"""Simple script to test the package structure."""

print("Testing ai_researcher package...")

try:
    import ai_researcher
    print(f"✓ ai_researcher imported successfully (version {ai_researcher.__version__})")
except Exception as e:
    print(f"✗ Failed to import ai_researcher: {e}")
    exit(1)

try:
    from ai_researcher import run_v3, AgentState
    print("✓ Can import run_v3 and AgentState")
except Exception as e:
    print(f"✗ Failed to import from ai_researcher: {e}")
    exit(1)

try:
    from ai_researcher.ai_researcher_tools import read_file, write_file
    print("✓ Can import tools from ai_researcher.ai_researcher_tools")
except Exception as e:
    print(f"✗ Failed to import tools: {e}")
    exit(1)

try:
    from ai_researcher.agent_v3_claude.agent import TOOLS, TOOL_BY_NAME
    print(f"✓ Agent v3 has {len(TOOLS)} tools available")
except Exception as e:
    print(f"✗ Failed to import agent v3 tools: {e}")
    exit(1)

print("\n✅ All imports successful! Package structure is correct.")

