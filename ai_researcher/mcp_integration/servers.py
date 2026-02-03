"""MCP Server Configuration and Management.

This module provides utilities to configure and manage MCP servers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Literal, Any

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


@dataclass
class MCPHttpServerConfig:
    """Configuration for an HTTP-based MCP server.

    Attributes:
        name: Unique identifier for the server
        url: The HTTP URL of the server
        headers: Optional HTTP headers for authentication
        metadata: Optional metadata about the server
        description: Human-readable description of the server
    """
    name: str
    url: str
    headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    description: str = ""

    @property
    def type(self) -> Literal["http"]:
        """Return the server type."""
        return "http"


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

    server_dir = repo_root / "mcp_servers" / "arxiv-mcp-server" / "src" / "arxiv_server"

    # Set up environment with download path
    env = os.environ.copy()
    if "DOWNLOAD_PATH" not in env:
        # Default to a downloads folder in the user's home directory
        env["DOWNLOAD_PATH"] = str(Path.home() / "Downloads" / "arxiv_papers")

    return create_mcp_server_params(
        command="uv",
        args=[
            "--directory",
            str(server_dir),
            "run",
            "server.py"
        ],
        env=env
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

    server_dir = repo_root / "mcp_servers" / "arxiv-mcp-server" / "src" / "arxiv_server"

    # Set up environment with download path
    env = os.environ.copy()
    if "DOWNLOAD_PATH" not in env:
        # Default to a downloads folder in the user's home directory
        env["DOWNLOAD_PATH"] = str(Path.home() / "Downloads" / "arxiv_papers")

    return MCPServerConfig(
        name="arxiv",
        command="uv",
        args=[
            "--directory",
            str(server_dir),
            "run",
            "server.py"
        ],
        env=env,
        description="Research paper search and retrieval from arXiv"
    )


def get_huggingface_server_config() -> MCPHttpServerConfig:
    """Get server configuration for the HuggingFace MCP server.

    The HuggingFace server provides tools for interacting with HuggingFace models,
    datasets, and spaces via an HTTP-based MCP server.

    Returns:
        MCPHttpServerConfig for the HuggingFace server
    """
    return MCPHttpServerConfig(
        name="huggingface",
        url="https://huggingface.co/mcp?login",
        metadata={
            "registry": {
                "api": {
                    "baseUrl": "https://api.mcp.github.com",
                    "version": "v0.1"
                },
                "mcpServer": {
                    "name": "huggingface/hf-mcp-server",
                    "version": "1.0.0"
                }
            }
        },
        description="HuggingFace model, dataset, and space tools via HTTP MCP server"
    )


def get_all_mcp_servers(repo_root: Optional[str] = None) -> List[MCPServerConfig | MCPHttpServerConfig]:
    """Get all available MCP server configurations.

    Args:
        repo_root: Root directory of the repository

    Returns:
        List of all MCP server configurations (MCPServerConfig and MCPHttpServerConfig instances)
    """
    return [
        get_pexlib_server_config(repo_root),
        get_arxiv_server_config(repo_root),
        get_huggingface_server_config(),
    ]


def get_server_by_name(name: str, repo_root: Optional[str] = None) -> Optional[MCPServerConfig | MCPHttpServerConfig]:
    """Get a specific MCP server configuration by name.

    Args:
        name: Name of the server (e.g., "pexlib", "arxiv", "huggingface")
        repo_root: Root directory of the repository

    Returns:
        MCPServerConfig or MCPHttpServerConfig if found, None otherwise
    """
    servers = {s.name: s for s in get_all_mcp_servers(repo_root)}
    return servers.get(name)

