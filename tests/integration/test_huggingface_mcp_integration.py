"""
Test HuggingFace MCP Server Integration

This test validates that the HuggingFace MCP server integration
is properly configured and accessible.
"""

import pytest


def test_huggingface_server_config():
    """Test that HuggingFace server config can be retrieved."""
    from ai_researcher.mcp_integration import get_huggingface_server_config

    config = get_huggingface_server_config()

    assert config is not None
    assert config.name == "huggingface"
    assert config.type == "http"
    assert config.url == "https://huggingface.co/mcp?login"
    assert config.description
    assert "HuggingFace" in config.description


def test_huggingface_server_metadata():
    """Test that HuggingFace server has correct metadata."""
    from ai_researcher.mcp_integration import get_huggingface_server_config

    config = get_huggingface_server_config()

    assert config.metadata is not None
    assert "registry" in config.metadata
    assert "api" in config.metadata["registry"]
    assert "mcpServer" in config.metadata["registry"]

    # Check API details
    api = config.metadata["registry"]["api"]
    assert api["baseUrl"] == "https://api.mcp.github.com"
    assert api["version"] == "v0.1"

    # Check server details
    server = config.metadata["registry"]["mcpServer"]
    assert server["name"] == "huggingface/hf-mcp-server"
    assert server["version"] == "1.0.0"


def test_huggingface_in_all_servers():
    """Test that HuggingFace is included in all servers list."""
    from ai_researcher.mcp_integration import get_all_mcp_servers

    all_servers = get_all_mcp_servers()
    server_names = [s.name for s in all_servers]

    assert "huggingface" in server_names
    assert len(server_names) >= 3  # At least pexlib, arxiv, huggingface


def test_get_huggingface_by_name():
    """Test that HuggingFace server can be retrieved by name."""
    from ai_researcher.mcp_integration import get_server_by_name

    hf_server = get_server_by_name("huggingface")

    assert hf_server is not None
    assert hf_server.name == "huggingface"
    assert hf_server.type == "http"


def test_mcp_http_server_config_class():
    """Test MCPHttpServerConfig class."""
    from ai_researcher.mcp_integration import MCPHttpServerConfig

    # Create a test config
    config = MCPHttpServerConfig(
        name="test",
        url="https://example.com/mcp",
        headers={"Authorization": "Bearer token"},
        metadata={"version": "1.0"},
        description="Test server"
    )

    assert config.name == "test"
    assert config.url == "https://example.com/mcp"
    assert config.type == "http"
    assert config.headers["Authorization"] == "Bearer token"
    assert config.metadata["version"] == "1.0"
    assert config.description == "Test server"


@pytest.mark.asyncio
async def test_load_huggingface_tools_placeholder():
    """Test that loading HuggingFace tools shows appropriate warning."""
    from ai_researcher.mcp_integration import get_mcp_tools

    # This should return empty list with warning (HTTP not implemented yet)
    tools = await get_mcp_tools(['huggingface'], verbose=False)

    # Should return empty list until HTTP support is implemented
    assert isinstance(tools, list)
    # Will be empty until HTTP client is implemented
    assert len(tools) == 0


@pytest.mark.asyncio
async def test_mixed_server_types():
    """Test loading tools from mixed STDIO and HTTP servers."""
    from ai_researcher.mcp_integration import get_mcp_tools

    # This should handle both types gracefully
    # May warn about missing servers or HTTP not implemented
    tools = await get_mcp_tools(
        ['pexlib', 'arxiv', 'huggingface'],
        verbose=False
    )

    # Should return a list (may be empty if servers aren't set up)
    assert isinstance(tools, list)


def test_http_server_config_exports():
    """Test that HTTP server functionality is exported."""
    from ai_researcher import mcp_integration

    # Check exports
    assert hasattr(mcp_integration, 'MCPHttpServerConfig')
    assert hasattr(mcp_integration, 'get_huggingface_server_config')
    assert hasattr(mcp_integration, 'load_mcp_tools_from_http_config')


def test_server_type_property():
    """Test that server type property works correctly."""
    from ai_researcher.mcp_integration import (
        get_huggingface_server_config,
        get_server_by_name
    )

    # Get HuggingFace (HTTP)
    hf_config = get_huggingface_server_config()
    assert hf_config.type == "http"

    # Get pexlib (STDIO) - should not have 'type' property or be different
    pexlib = get_server_by_name('pexlib')
    if pexlib:
        # STDIO servers don't have a type property
        assert not hasattr(pexlib, 'url')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

