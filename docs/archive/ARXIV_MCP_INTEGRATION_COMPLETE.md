# arXiv MCP Integration - Setup Complete

## Summary

The arXiv MCP server integration has been successfully configured in the ai-researcher project. The configuration has been updated to use the Python-based server with the `uv` package manager.

## Changes Made

### 1. Updated `servers.py`
- **File**: `/Users/dan/pex/ai-researcher/ai_researcher/mcp_integration/servers.py`
- **Changes**:
  - Fixed `get_arxiv_server_params()` to use Python-based server with `uv` command
  - Fixed `get_arxiv_server_config()` to use correct server path and configuration
  - Changed from Node.js server (`node`, `dist/index.js`) to Python server (`uv`, `src/arxiv_server/server.py`)
  - Added automatic `DOWNLOAD_PATH` environment variable configuration

### 2. Server Configuration Details

**Command**: `uv`

**Arguments**:
```bash
--directory
<repo_root>/mcp_servers/arxiv-mcp-server/src/arxiv_server
run
server.py
```

**Environment Variables**:
- `DOWNLOAD_PATH`: Defaults to `~/Downloads/arxiv_papers`

## Testing

Three test scripts have been created:

1. **`test_arxiv_config.py`** - Quick configuration verification (non-async)
2. **`test_arxiv_integration.py`** - Full integration test with tool invocation (async)
3. **`verify_arxiv_config.py`** - Detailed verification and diagnostics

## arXiv MCP Server Tools

The arXiv server provides the following tools:

1. **get_article_url** - Retrieve the URL of an article by title
2. **download_article** - Download an article as a PDF file
3. **load_article_to_context** - Load an article into LLM context
4. **get_details** - Retrieve metadata of an article
5. **search_arxiv** - Search arXiv database with various parameters

## Claude Desktop Configuration

To use the arXiv MCP server in Claude Desktop, add this to your configuration file:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arxiv-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/dan/pex/ai-researcher/ai_researcher/mcp_servers/arxiv-mcp-server/src/arxiv_server",
        "run",
        "server.py"
      ],
      "env": {
        "DOWNLOAD_PATH": "/Users/dan/Downloads/arxiv_papers"
      }
    }
  }
}
```

**Note**: Replace the paths with absolute paths specific to your system.

## Requirements

### System Requirements
- Python 3.13+ (as specified in arxiv-mcp-server's pyproject.toml)
- `uv` package manager

### Installing uv

**macOS** (via Homebrew):
```bash
brew install uv
```

**macOS/Linux** (via curl):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** (via PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Server Dependencies

The arxiv-mcp-server has the following Python dependencies (automatically managed by uv):
- feedparser >= 6.0.11
- httpx >= 0.28.1
- mcp[cli] >= 1.6.0
- pymupdf >= 1.25.5

## Usage in Code

### Basic Usage

```python
from ai_researcher.mcp_integration import get_arxiv_server_config, load_mcp_tools_from_config

# Get server configuration
server_config = get_arxiv_server_config()

# Load tools
tools = await load_mcp_tools_from_config(server_config, verbose=True)

# Use a tool
search_tool = next(t for t in tools if t.name == "search_arxiv")
result = await search_tool.ainvoke({
    "all_fields": "machine learning",
    "start": 0
})
```

### Using with Multiple Servers

```python
from ai_researcher.mcp_integration import get_mcp_tools, get_all_mcp_servers

# Get tools from all available servers (including arxiv)
tools = await get_mcp_tools(get_all_mcp_servers())

# Or get tools from specific servers by name
tools = await get_mcp_tools(['arxiv', 'pexlib'])
```

## Verification

To verify the configuration is working:

```bash
cd /Users/dan/pex/ai-researcher
python test_arxiv_config.py
```

This will:
1. Check that the server configuration is loaded correctly
2. Verify that server files exist
3. Check if `uv` is installed
4. Generate a Claude Desktop configuration snippet

## Next Steps

1. **Install uv** if not already installed
2. **Run test script** to verify configuration
3. **Add to Claude Desktop** using the generated configuration
4. **Test in Claude** by asking it to search arXiv or retrieve papers

## Example Queries for Claude

Once configured in Claude Desktop, you can try:

- "Search arXiv for papers about transformer models"
- "Get the URL for the paper titled 'Attention Is All You Need'"
- "Download the paper about GPT-3"
- "Load the latest paper on quantum computing into context"
- "Get details about papers on reinforcement learning"

## Files Created/Modified

### Modified
- `ai_researcher/mcp_integration/servers.py`

### Created
- `test_arxiv_config.py` - Configuration verification script
- `test_arxiv_integration.py` - Full integration test
- `verify_arxiv_config.py` - Detailed diagnostics
- `ARXIV_MCP_INTEGRATION_COMPLETE.md` - This summary document

## Troubleshooting

### Issue: "uv not found"
**Solution**: Install uv using one of the methods in the Requirements section.

### Issue: "Server directory not found"
**Solution**: Ensure the arxiv-mcp-server submodule is properly initialized:
```bash
git submodule update --init --recursive
```

### Issue: "DOWNLOAD_PATH not writable"
**Solution**: Update the `DOWNLOAD_PATH` in your configuration to a writable directory.

### Issue: "Python version mismatch"
**Solution**: The arxiv-mcp-server requires Python 3.13+. Ensure you have the correct version:
```bash
python3 --version
```

## References

- [arXiv MCP Server GitHub](https://github.com/prashalruchiranga/arxiv-mcp-server)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [uv Package Manager](https://docs.astral.sh/uv/)
- [arXiv API](https://info.arxiv.org/help/api/index.html)

---

**Status**: ✓ Configuration Complete  
**Date**: January 14, 2026  
**Version**: 1.0

