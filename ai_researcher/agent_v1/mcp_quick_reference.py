"""Quick Reference: MCP Module Usage

This file provides quick copy-paste examples for using the MCP module.
"""

# ============================================================================
# BASIC IMPORT
# ============================================================================

from ai_researcher.agent_v1.mcp_integration import get_all_tools, get_mcp_tools_only
from ai_researcher.agent_v1.mpc_servers import (
    create_mcp_server_params,
    load_mcp_tools,
    get_pexlib_server_params,
    get_arxiv_server_params,
)


# ============================================================================
# QUICK START: Load All Tools
# ============================================================================

async def quickstart():
    """Simplest way to get all tools including MCP."""
    tools = await get_all_tools(
        include_pexlib=True,
        include_arxiv=False,
        verbose=True
    )
    return tools


# ============================================================================
# LOAD SPECIFIC MCP SERVER
# ============================================================================

async def load_pexlib():
    """Load only pexlib MCP tools."""
    server_params = get_pexlib_server_params()
    tools = await load_mcp_tools(server_params, verbose=True)
    return tools


async def load_arxiv():
    """Load only arxiv MCP tools."""
    server_params = get_arxiv_server_params()
    tools = await load_mcp_tools(server_params, verbose=True)
    return tools


# ============================================================================
# CUSTOM MCP SERVER
# ============================================================================

async def load_custom_server():
    """Load tools from a custom MCP server."""
    server_params = create_mcp_server_params(
        command="node",  # or "python", "deno", etc.
        args=["path/to/your/server/index.js"],
        env=None,  # Optional: custom environment variables
        cwd=None,  # Optional: working directory
    )
    tools = await load_mcp_tools(server_params, verbose=True)
    return tools


# ============================================================================
# ERROR HANDLING
# ============================================================================

async def safe_load():
    """Load tools with error handling."""
    try:
        tools = await get_all_tools(include_pexlib=True, verbose=True)
    except Exception as e:
        print(f"Failed to load MCP tools: {e}")
        # Fallback to default tools
        from ai_researcher.agent_v1.tools import (
            read_file, write_file, list_files, grep
        )
        tools = [read_file, write_file, list_files, grep]
    return tools


# ============================================================================
# COMBINE WITH CUSTOM TOOLS
# ============================================================================

async def combine_tools():
    """Combine MCP tools with custom tools."""
    from ai_researcher.agent_v1.tools import read_file, write_file

    # Get MCP tools
    mcp_tools = await get_mcp_tools_only(include_pexlib=True)

    # Combine with custom tools
    all_tools = [read_file, write_file] + mcp_tools

    return all_tools


# ============================================================================
# WITH LANGCHAIN AGENT
# ============================================================================

async def create_agent_with_mcp():
    """Create a LangChain agent with MCP tools.

    Note: This requires additional dependencies that may not be installed.
    Install with: pip install langchain-openai
    """
    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import AgentExecutor, create_openai_tools_agent
        from langchain import hub
    except ImportError as e:
        print(f"This example requires additional dependencies: {e}")
        print("Install with: pip install langchain-openai")
        return None

    # Load tools
    tools = await get_all_tools(include_pexlib=True, verbose=True)

    # Create agent
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = hub.pull("hwchase17/openai-tools-agent")
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor


# ============================================================================
# LIST AVAILABLE TOOLS
# ============================================================================

async def list_tools():
    """List all available tools."""
    tools = await get_all_tools(include_pexlib=True, include_arxiv=True)

    print(f"Total tools: {len(tools)}\n")
    for tool in tools:
        name = getattr(tool, "name", str(tool))
        desc = getattr(tool, "description", "No description")
        print(f"- {name}: {desc[:60]}...")


# ============================================================================
# CONDITIONAL LOADING
# ============================================================================

async def conditional_load(use_pexlib: bool = False, use_arxiv: bool = False):
    """Load tools conditionally based on availability."""
    import os

    # Check if servers are available
    pexlib_available = os.path.exists("mcp_servers/pexlib-mcp-server/dist/index.js")
    arxiv_available = os.path.exists("mcp_servers/arxiv-mcp-server/dist/index.js")

    tools = await get_all_tools(
        include_pexlib=use_pexlib and pexlib_available,
        include_arxiv=use_arxiv and arxiv_available,
        verbose=True
    )

    return tools


# ============================================================================
# RUN EXAMPLES
# ============================================================================

if __name__ == "__main__":
    import asyncio

    # Choose one to run:
    asyncio.run(quickstart())
    # asyncio.run(load_pexlib())
    # asyncio.run(load_custom_server())
    # asyncio.run(list_tools())
    # asyncio.run(create_agent_with_mcp())

