#!/usr/bin/env python
"""Demo script showing Agent V1 with MCP integration.

This script demonstrates how to use Agent V1 with MCP servers enabled.
"""
import asyncio
import os
from ai_researcher.agent_v1.agent import build_graph


async def demo_agent_with_mcp():
    """Demonstrate Agent V1 with MCP integration."""
    print("=" * 70)
    print("Agent V1 with MCP Integration - Demo")
    print("=" * 70)

    # Build agent with MCP tools
    print("\n📦 Building agent with MCP tools...")
    print("   - Loading pexlib MCP server...")

    app = await build_graph(
        include_mcp_pexlib=True,
        include_mcp_arxiv=False,
        verbose=True
    )

    print("\n✅ Agent built successfully!\n")

    # Example task
    print("📋 Example task:")
    print("   Goal: Create a simple Python hello world script")
    print("   Repo: ./experiments/demo-project\n")

    state = {
        "goal": "Create a new Python project called 'demo-project' with a hello.py file that prints 'Hello, World!'",
        "repo_root": "",
        "messages": [],
        "done": False
    }

    print("🚀 Running agent...\n")
    print("-" * 70)

    step = 0
    for event in app.stream(state, stream_mode="values"):
        msgs = event.get("messages", [])

        if msgs and msgs[-1]["type"] == "assistant":
            step += 1
            content = msgs[-1]["content"]
            # Truncate long content for demo
            if len(content) > 200:
                content = content[:197] + "..."
            print(f"\n[Step {step}] 🤖 Assistant:")
            print(f"  {content}")

        elif msgs and msgs[-1]["type"] == "tool":
            content = msgs[-1]["content"]
            # Truncate long output
            if len(content) > 150:
                content = content[:147] + "..."
            print(f"  🔧 Tool output: {content}")

        # Check if done
        if event.get("done"):
            print("\n" + "-" * 70)
            print("\n✅ Task completed!")
            break

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


async def demo_available_tools():
    """Show available tools including MCP tools."""
    print("=" * 70)
    print("Available Tools in Agent V1")
    print("=" * 70)

    from ai_researcher.agent_v1.mcp_integration import get_all_tools

    print("\n📦 Loading all tools (including MCP)...\n")

    tools = await get_all_tools(
        include_pexlib=True,
        include_arxiv=False,
        verbose=False
    )

    print(f"Total tools: {len(tools)}\n")

    print("Built-in tools:")
    builtin_count = 0
    for tool in tools:
        name = getattr(tool, "name", str(tool))
        if name not in ["generate_fingerprint", "match_fingerprints"]:
            builtin_count += 1
            desc = getattr(tool, "description", "No description")
            if len(desc) > 60:
                desc = desc[:57] + "..."
            print(f"  • {name}: {desc}")

    print(f"\nMCP tools (from pexlib server):")
    for tool in tools:
        name = getattr(tool, "name", str(tool))
        if name in ["generate_fingerprint", "match_fingerprints"]:
            desc = getattr(tool, "description", "No description")
            if len(desc) > 60:
                desc = desc[:57] + "..."
            print(f"  • {name}: {desc}")

    print("\n" + "=" * 70)


async def main():
    """Run demos."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--tools":
        await demo_available_tools()
    else:
        print("\n🎯 Agent V1 MCP Integration Demo\n")
        print("This demo shows how Agent V1 can use MCP servers.")
        print("The agent will have access to:")
        print("  • Built-in tools (file ops, git, pytest, etc.)")
        print("  • MCP tools (from pexlib server)")
        print("\nNote: This is a demonstration. The agent may not complete the full task.")
        print("\nStarting demo...\n")

        await demo_agent_with_mcp()

        print("\n💡 Tip: Run with --tools flag to see all available tools:")
        print("   python examples/demo_agent_v1_mcp.py --tools")


if __name__ == "__main__":
    asyncio.run(main())

