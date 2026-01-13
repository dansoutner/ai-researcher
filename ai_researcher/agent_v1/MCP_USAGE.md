# Using MCP Servers with Agent V1

Agent V1 now supports Model Context Protocol (MCP) servers, allowing you to extend the agent's capabilities with external tools.

## Quick Start

The agent will automatically load MCP tools by default. You can control this behavior with environment variables:

```bash
# Run with pexlib MCP tools (enabled by default)
python -m ai_researcher.agent_v1.run

# Disable MCP tools
USE_MCP_PEXLIB=false python -m ai_researcher.agent_v1.run

# Enable arxiv MCP tools
USE_MCP_ARXIV=true python -m ai_researcher.agent_v1.run

# Enable both pexlib and arxiv
USE_MCP_PEXLIB=true USE_MCP_ARXIV=true python -m ai_researcher.agent_v1.run

# Disable verbose output
VERBOSE=false python -m ai_researcher.agent_v1.run
```

## Environment Variables

- `USE_MCP_PEXLIB` (default: `true`) - Enable/disable pexlib MCP server
- `USE_MCP_ARXIV` (default: `false`) - Enable/disable arxiv MCP server  
- `VERBOSE` (default: `true`) - Show detailed tool loading information
- `GOAL` - Set initial goal for the agent
- `REPO_ROOT` - Set repository root directory

## Programmatic Usage

You can also use MCP tools programmatically:

```python
import asyncio
from ai_researcher.agent_v1.agent import build_graph

async def run_agent():
    # Build graph with MCP tools
    app = await build_graph(
        include_mcp_pexlib=True,
        include_mcp_arxiv=True,
        verbose=True
    )
    
    # Run the agent
    state = {
        "goal": "Create a Python calculator module",
        "repo_root": "",
        "messages": [],
        "done": False
    }
    
    for event in app.stream(state, stream_mode="values"):
        # Process events
        pass

asyncio.run(run_agent())
```

## Custom Tools

You can also pass your own custom tools:

```python
from ai_researcher.agent_v1.mcp_integration import get_all_tools

# Get all tools including MCP
tools = await get_all_tools(
    include_pexlib=True,
    include_arxiv=False
)

# Add your custom tools
tools.append(my_custom_tool)

# Build graph with custom tools
app = await build_graph(tools=tools)
```

## Available MCP Servers

### Pexlib MCP Server
Located at: `ai_researcher/mcp_servers/pexlib-mcp-server/`

Tools provided:
- File system operations
- Git operations  
- Code analysis tools
- And more...

### Arxiv MCP Server
Located at: `ai_researcher/mcp_servers/arxiv-mcp-server/`

Tools provided:
- Search arxiv papers
- Fetch paper metadata
- Download PDFs
- And more...

## Troubleshooting

If MCP tools fail to load, the agent will print a warning but continue with the default tools:

```
⚠ Warning: Failed to load pexlib tools: [error message]
```

This allows the agent to function even if MCP servers are not properly configured.

