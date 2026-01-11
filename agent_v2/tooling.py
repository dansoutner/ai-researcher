"""agent_v2 tooling bridge.

This module lets `agent_v2` call the shared LangChain tools defined at the repo
root in `agent_tools.py`.

The shared tools are LangChain `BaseTool` objects created via the `@tool`
decorator. They expose a `.invoke(dict)` method.

We keep the integration layer small:
- build a registry (name -> tool)
- call the tool safely and stringify results

NOTE: Many tools require a `repo_root` argument. If the caller doesn't pass one,
we default to the current working directory.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

import agent_tools


@dataclass(frozen=True)
class ToolCall:
    """A normalized tool call."""

    name: str
    arguments: Dict[str, Any]


def build_tool_registry() -> Dict[str, Any]:
    """Return a mapping of tool name -> tool instance from `agent_tools`.

    We include only callables that look like LangChain tools (have `.invoke`).
    """

    registry: Dict[str, Any] = {}
    for attr_name in dir(agent_tools):
        if attr_name.startswith("_"):
            continue
        obj = getattr(agent_tools, attr_name)
        if hasattr(obj, "invoke") and callable(getattr(obj, "invoke")):
            # Prefer explicit tool.name when available (LangChain BaseTool)
            tool_name = getattr(obj, "name", attr_name)
            registry[str(tool_name)] = obj
    return registry


def available_tools_markdown(registry: Mapping[str, Any]) -> str:
    """Human-readable tool list for prompt injection (names + docstrings)."""

    lines = ["Available tools (from agent_tools.py):"]
    for name in sorted(registry.keys()):
        tool = registry[name]
        desc = getattr(tool, "description", None) or (getattr(tool, "__doc__", "") or "")
        desc = " ".join(str(desc).strip().split())
        if desc:
            lines.append(f"- {name}: {desc}")
        else:
            lines.append(f"- {name}")
    return "\n".join(lines)


def _ensure_repo_root(arguments: Dict[str, Any], default_repo_root: Optional[str]) -> Dict[str, Any]:
    if "repo_root" in arguments and arguments["repo_root"]:
        return arguments
    repo_root = default_repo_root or os.getcwd()
    return {**arguments, "repo_root": repo_root}


def invoke_tool(
    registry: Mapping[str, Any],
    call: ToolCall,
    *,
    default_repo_root: Optional[str] = None,
) -> str:
    """Invoke a tool by name with arguments.

    Returns a string that is safe to feed back into the LLM as an observation.
    """

    if call.name not in registry:
        available = ", ".join(sorted(registry.keys()))
        return f"TOOL_ERROR: unknown tool '{call.name}'. Available: {available}"

    tool = registry[call.name]
    args = dict(call.arguments or {})

    # Most shared tools require repo_root; auto-fill if missing.
    args = _ensure_repo_root(args, default_repo_root)

    try:
        out = tool.invoke(args)  # LangChain tool API
    except Exception as e:  # pragma: no cover
        return f"TOOL_ERROR: {type(e).__name__}: {e}"

    # Normalize output to string.
    if out is None:
        return "(no output)"
    if isinstance(out, str):
        return out
    try:
        return json.dumps(out, indent=2, default=str)
    except Exception:
        return str(out)

