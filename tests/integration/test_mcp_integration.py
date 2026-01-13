"""Integration tests for MCP (Model Context Protocol) integration."""

import pytest


def test_mcp_imports():
    """Test that MCP integration module exports expected functions."""
    from ai_researcher.mcp_integration import (
        get_mcp_tools,
        get_mcp_tools_by_name,
        get_all_mcp_servers,
        create_mcp_server_params,
        MCPServerConfig,
    )

    # All imports should succeed
    assert get_mcp_tools is not None
    assert get_mcp_tools_by_name is not None
    assert get_all_mcp_servers is not None
    assert create_mcp_server_params is not None
    assert MCPServerConfig is not None


def test_get_mcp_servers():
    """Test getting MCP server configurations."""
    from ai_researcher.mcp_integration import get_all_mcp_servers

    servers = get_all_mcp_servers()

    # Should return a list of server configs
    assert isinstance(servers, list)

    # Each server should have name and description
    for server in servers:
        assert hasattr(server, 'name')
        assert hasattr(server, 'description')
        assert isinstance(server.name, str)
        assert isinstance(server.description, str)


def test_mcp_server_config_structure():
    """Test MCPServerConfig structure."""
    from ai_researcher.mcp_integration import MCPServerConfig

    # Should be able to access type annotations
    assert hasattr(MCPServerConfig, '__annotations__')

