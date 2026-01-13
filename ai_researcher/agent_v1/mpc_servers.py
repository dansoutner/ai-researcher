"""MCP (Model Context Protocol) Server Integration Module.

This module provides utilities to connect to MCP servers and convert their tools
to LangChain-compatible tools that can be used with agents.

Usage:
    from ai_researcher.agent_v1.mpc_servers import load_mcp_tools, create_mcp_server_params

    # Create server params
    server_params = create_mcp_server_params(
        command="node",
        args=["path/to/server/index.js"]
    )

    # Load tools
    tools = await load_mcp_tools(server_params)
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import List, Optional, Dict
from langchain_core.tools import StructuredTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def create_mcp_server_params(
    command: str,
    args: List[str],
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[str] = None
) -> StdioServerParameters:
    """Create MCP server parameters.

    Args:
        command: The command to run (e.g., "node", "python")
        args: Arguments for the command (e.g., ["server.js"])
        env: Environment variables (defaults to current environment)
        cwd: Working directory for the server process

    Returns:
        StdioServerParameters configured for the server
    """
    if env is None:
        env = os.environ.copy()

    return StdioServerParameters(
        command=command,
        args=args,
        env=env,
        cwd=cwd
    )


async def load_mcp_tools(
    server_params: StdioServerParameters,
    verbose: bool = False
) -> List[StructuredTool]:
    """Load tools from an MCP server and convert them to LangChain tools.

    Args:
        server_params: Server parameters created with create_mcp_server_params
        verbose: Whether to print debug information

    Returns:
        List of LangChain StructuredTool instances

    Example:
        server_params = create_mcp_server_params(
            command="node",
            args=["server/index.js"]
        )
        tools = await load_mcp_tools(server_params, verbose=True)
    """
    langchain_tools = []

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session and list available tools
            await session.initialize()
            result = await session.list_tools()

            # Convert MCP tools to LangChain tools
            for tool in result.tools:
                # Create a closure to capture the current tool name
                def make_tool_wrapper(tool_name: str):
                    async def _tool_wrapper(**kwargs):
                        return await session.call_tool(tool_name, arguments=kwargs)
                    return _tool_wrapper

                # Create the StructuredTool
                lc_tool = StructuredTool.from_function(
                    name=tool.name,
                    description=tool.description,
                    func=None,  # We only provide async implementation
                    coroutine=make_tool_wrapper(tool.name),
                )
                langchain_tools.append(lc_tool)

            if verbose:
                print(f"Loaded {len(langchain_tools)} MCP tools: {[t.name for t in langchain_tools]}")

    return langchain_tools


def get_pexlib_server_params(repo_root: Optional[str] = None) -> StdioServerParameters:
    """Get server parameters for the pexlib MCP server.

    Args:
        repo_root: Root directory of the repository (defaults to ai_researcher package directory)

    Returns:
        StdioServerParameters for the pexlib server
    """
    if repo_root is None:
        # Default to ai_researcher package directory
        repo_root = Path(__file__).parent.parent
    else:
        repo_root = Path(repo_root)

    server_path = repo_root / "mcp_servers" / "pexlib-mcp-server" / "dist" / "index.js"

    return create_mcp_server_params(
        command="node",
        args=[str(server_path)],
        env=os.environ.copy()
    )


def get_arxiv_server_params(repo_root: Optional[str] = None) -> StdioServerParameters:
    """Get server parameters for the arxiv MCP server.

    Args:
        repo_root: Root directory of the repository (defaults to ai_researcher package directory)

    Returns:
        StdioServerParameters for the arxiv server
    """
    if repo_root is None:
        # Default to ai_researcher package directory
        repo_root = Path(__file__).parent.parent
    else:
        repo_root = Path(repo_root)

    server_path = repo_root / "mcp_servers" / "arxiv-mcp-server" / "dist" / "index.js"
    return create_mcp_server_params(
        command="node",
        args=[str(server_path)],
        env=os.environ.copy()
    )


async def demo_agent():
    """Demo function showing how to use MCP tools with a LangChain agent.

    Note: This requires additional dependencies that may not be installed.
    Install with: pip install langchain-openai
    """
    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import AgentExecutor, create_openai_tools_agent
        from langchain import hub
    except ImportError as e:
        print(f"Demo requires additional dependencies: {e}")
        print("Install with: pip install langchain-openai")
        return

    # Get pexlib server params
    server_params = get_pexlib_server_params()

    # Load MCP tools
    mcp_tools = await load_mcp_tools(server_params, verbose=True)

    # Set up the LLM and Agent
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = hub.pull("hwchase17/openai-tools-agent")

    agent = create_openai_tools_agent(llm, mcp_tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=mcp_tools, verbose=True)

    # Run a query
    query = "Generate an audio fingerprint for 'test_audio.wav' and check if it matches 'asset_db.json'."

    print(f"\n--- Running Query: {query} ---\n")
    response = await agent_executor.ainvoke({"input": query})

    print("\n--- Final Response ---")
    print(response["output"])


if __name__ == "__main__":
    asyncio.run(demo_agent())
