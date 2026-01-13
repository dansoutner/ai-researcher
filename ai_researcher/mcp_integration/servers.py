"""MCP Server Configuration and Management.

This module provides utilities to configure and manage MCP servers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from mcp import StdioServerParameters


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server.

    Attributes:
        name: Unique identifier for the server
        command: The command to run (e.g., "node", "python")
        args: Arguments for the command
        env: Environment variables (optional)
        cwd: Working directory for the server process (optional)
        description: Human-readable description of the server
    """
    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None
    description: str = ""

    def to_stdio_params(self) -> StdioServerParameters:
        """Convert to StdioServerParameters for MCP client."""
        env = self.env if self.env is not None else os.environ.copy()
        return StdioServerParameters(
            command=self.command,
            args=self.args,
            env=env,  # type: ignore
            cwd=self.cwd
        )


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
        env=env,  # type: ignore
        cwd=cwd
    )


def get_pexlib_server_params(repo_root: Optional[str] = None) -> StdioServerParameters:
    """Get server parameters for the pexlib MCP server.

    The pexlib server provides tools for audio fingerprinting and asset management.

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

    The arxiv server provides tools for searching and retrieving research papers.

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


def get_pexlib_server_config(repo_root: Optional[str] = None) -> MCPServerConfig:
    """Get server configuration for the pexlib MCP server.

    Args:
        repo_root: Root directory of the repository

    Returns:
        MCPServerConfig for the pexlib server
    """
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    else:
        repo_root = Path(repo_root)

    server_path = repo_root / "mcp_servers" / "pexlib-mcp-server" / "dist" / "index.js"

    return MCPServerConfig(
        name="pexlib",
        command="node",
        args=[str(server_path)],
        env=os.environ.copy(),
        description="Audio fingerprinting and asset management tools"
    )


def get_arxiv_server_config(repo_root: Optional[str] = None) -> MCPServerConfig:
    """Get server configuration for the arxiv MCP server.

    Args:
        repo_root: Root directory of the repository

    Returns:
        MCPServerConfig for the arxiv server
    """
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    else:
        repo_root = Path(repo_root)

    server_path = repo_root / "mcp_servers" / "arxiv-mcp-server" / "dist" / "index.js"

    return MCPServerConfig(
        name="arxiv",
        command="node",
        args=[str(server_path)],
        env=os.environ.copy(),
        description="Research paper search and retrieval from arXiv"
    )


def get_all_mcp_servers(repo_root: Optional[str] = None) -> List[MCPServerConfig]:
    """Get all available MCP server configurations.

    Args:
        repo_root: Root directory of the repository

    Returns:
        List of all MCPServerConfig instances
    """
    return [
        get_pexlib_server_config(repo_root),
        get_arxiv_server_config(repo_root),
    ]


def get_server_by_name(name: str, repo_root: Optional[str] = None) -> Optional[MCPServerConfig]:
    """Get a specific MCP server configuration by name.

    Args:
        name: Name of the server (e.g., "pexlib", "arxiv")
        repo_root: Root directory of the repository

    Returns:
        MCPServerConfig if found, None otherwise
    """
    servers = {s.name: s for s in get_all_mcp_servers(repo_root)}
    return servers.get(name)

