#!/usr/bin/env python3
"""Test script for MCP integration."""

from ai_researcher.mcp_integration import (
    get_mcp_tools,
    get_mcp_tools_by_name,
    get_all_mcp_servers,
    create_mcp_server_params,
    MCPServerConfig,
)

print('✓ All imports successful')

# Test getting server configs
servers = get_all_mcp_servers()
print(f'✓ Found {len(servers)} MCP servers:')
for server in servers:
    print(f'  - {server.name}: {server.description}')

print('\n✓ MCP integration module working correctly!')

