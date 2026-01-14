# arXiv MCP Integration - Quick Reference

## Claude Desktop Config

Add to: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arxiv-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/ai-researcher/ai_researcher/mcp_servers/arxiv-mcp-server/src/arxiv_server",
        "run",
        "server.py"
      ],
      "env": {
        "DOWNLOAD_PATH": "/ABSOLUTE/PATH/TO/DOWNLOADS/FOLDER"
      }
    }
  }
}
```

## Install uv

```bash
brew install uv
```

## Available Tools

1. **search_arxiv** - Search papers by keywords
2. **get_article_url** - Get paper URL by title
3. **download_article** - Download paper as PDF
4. **load_article_to_context** - Load paper into LLM context
5. **get_details** - Get paper metadata

## Test Configuration

```bash
cd /Users/dan/pex/ai-researcher
python test_arxiv_import.py
```

## Example Usage in Code

```python
from ai_researcher.mcp_integration import get_arxiv_server_config
from ai_researcher.mcp_integration.loader import load_mcp_tools_from_config

# Load tools
config = get_arxiv_server_config()
tools = await load_mcp_tools_from_config(config)

# Use search tool
search_tool = next(t for t in tools if t.name == "search_arxiv")
result = await search_tool.ainvoke({"all_fields": "machine learning"})
```

## Files Changed

- `ai_researcher/mcp_integration/servers.py` - Updated arXiv server config

