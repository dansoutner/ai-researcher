from __future__ import annotations

import json
import re
from typing import List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool

from .state import AgentState
from .llm import get_llm
from .tools import (
    create_project,
    read_file,
    write_file,
    list_files,
    grep,
    git_diff,
    git_status,
    git_add,
    git_commit,
    git_log,
    git_branch_list,
    git_checkout,
    git_remote_list,
    git_prepare_pr,
    apply_patch,
    run_pytest,
    run_cmd,
)

SYSTEM = """You are a coding agent working in a local repository.

Rules:
- Make a new repo for every new project and always work with repo. The repo locates into ./experiments dir.
- Use tools to inspect/edit files and run commands (pytest, grep, git diff, patch).
- Prefer small, safe, incremental changes.
- After tool outputs, reason about next steps.

IMPORTANT - Control Output:
After your reasoning, you MUST end your response with a JSON control block in this exact format:

```json
{"done": false}
```

OR when the goal is fully achieved:

```json
{"done": true, "summary": "Brief summary of what was accomplished and how to verify."}
```

Always include this JSON block at the end of every response.
"""

TOOLS = [
    create_project,
    read_file,
    write_file,
    list_files,
    grep,
    # git
    git_status,
    git_diff,
    git_add,
    git_commit,
    git_log,
    git_branch_list,
    git_checkout,
    git_remote_list,
    git_prepare_pr,
    # patch/test/cmd
    apply_patch,
    run_pytest,
    run_cmd,
]

# Regex to extract JSON control block from response
CONTROL_JSON_PATTERN = re.compile(r'```json\s*(\{[^`]*"done"\s*:\s*(?:true|false)[^`]*\})\s*```', re.IGNORECASE | re.DOTALL)
CONTROL_JSON_FALLBACK = re.compile(r'(\{"done"\s*:\s*(?:true|false)[^}]*\})', re.IGNORECASE)


def _parse_control_json(content: str) -> dict:
    """Extract and parse the JSON control block from LLM response."""
    # Handle list content (from some models)
    if isinstance(content, list):
        content = " ".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )

    content = str(content)

    # Try fenced JSON block first
    match = CONTROL_JSON_PATTERN.search(content)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Fallback: bare JSON object
    match = CONTROL_JSON_FALLBACK.search(content)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Default: not done
    return {"done": False}


def _ensure_messages(state: AgentState) -> AgentState:
    if "messages" not in state:
        state["messages"] = []
    return state

def _check_done(state: AgentState) -> AgentState:
    """Check done status from structured control JSON."""
    control = state.get("control", {})
    state["done"] = control.get("done", False)

    # Log summary if done
    if state["done"] and control.get("summary"):
        print(f"\n✅ Agent completed: {control['summary']}\n")

    return state


def _route(state: AgentState) -> str:
    if state.get("pending_tool_calls"):
        return "tools"
    if state.get("done"):
        return END
    return "llm"

async def build_graph(
    tools: Optional[List[BaseTool]] = None,
    include_mcp_pexlib: bool = False,
    include_mcp_arxiv: bool = False,
    verbose: bool = False
):
    """Build the agent graph with optional MCP tools.

    Args:
        tools: Optional list of tools to use. If None, uses DEFAULT_TOOLS.
        include_mcp_pexlib: Whether to include pexlib MCP tools
        include_mcp_arxiv: Whether to include arxiv MCP tools
        verbose: Whether to print debug information about loaded tools

    Returns:
        Compiled LangGraph agent
    """
    # Load tools if not provided
    if tools is None:
        if include_mcp_pexlib or include_mcp_arxiv:
            from ai_researcher.agent_v1.mcp_integration import get_all_tools
            tools = await get_all_tools(
                include_pexlib=include_mcp_pexlib,
                include_arxiv=include_mcp_arxiv,
                verbose=verbose
            )
        else:
            tools = TOOLS

    # Create closures with the tools
    def _llm_node_with_tools(state: AgentState) -> AgentState:
        state = _ensure_messages(state)
        llm = get_llm().bind_tools(tools)

        msgs = [SystemMessage(content=SYSTEM)]
        # repo_root can be empty initially; agent can create_project first
        msgs += [HumanMessage(content=f"Goal:\n{state.get('goal','')}\n\nRepo root: {state.get('repo_root','(none)')}")]

        for m in state["messages"]:
            if m["type"] == "human":
                msgs.append(HumanMessage(content=m["content"]))
            elif m["type"] == "tool":
                msgs.append(ToolMessage(content=m["content"], tool_call_id=m.get("tool_call_id", "tool")))
            else:
                from langchain_core.messages import AIMessage
                # Must include tool_calls to match tool_call_ids in subsequent ToolMessages
                msgs.append(AIMessage(
                    content=m["content"],
                    additional_kwargs=m.get("additional_kwargs", {}),
                    tool_calls=m.get("tool_calls", []),
                ))

        ai = llm.invoke(msgs)

        # Normalize content to string
        content = ai.content
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        content = content or ""

        # Extract tool_calls to store with message (required for tool_call_id matching)
        tool_calls = ai.tool_calls if hasattr(ai, "tool_calls") else []

        state["messages"].append({
            "type": "assistant",
            "content": content,
            "additional_kwargs": getattr(ai, "additional_kwargs", {}) or {},
            "tool_calls": tool_calls,  # Store tool_calls for proper reconstruction
        })

        # Parse structured control from response
        state["control"] = _parse_control_json(content)

        state["pending_tool_calls"] = tool_calls
        return state

    async def _tools_node_with_tools(state: AgentState) -> AgentState:
        state = _ensure_messages(state)
        tool_calls = state.get("pending_tool_calls", [])
        if not tool_calls:
            return state

        tool_map = {t.name: t for t in tools}
        outputs: List[str] = []

        for call in tool_calls:
            name = call["name"]
            args = call.get("args", {}) or {}

            # Sanitize args: remove invalid keys that some LLMs inject
            invalid_keys = [k for k in args if k.startswith("v__") or k.startswith("__")]
            for k in invalid_keys:
                args.pop(k)

            # Handle case where args is a string instead of dict
            if isinstance(args, str):
                args = {"args": args}

            # Many tools require repo_root; but create_project does not.
            if name != "create_project":
                args.setdefault("repo_root", state["repo_root"])

            try:
                tool = tool_map[name]
                # Always use ainvoke in async context
                # LangChain automatically wraps sync functions to work with ainvoke
                result = await tool.ainvoke(args)
            except TypeError as e:
                # Fallback: if still failing, log and return error
                result = f"Tool error: {e}"
            except Exception as e:
                # Catch any other errors
                result = f"Tool error: {e}"

            result_str = str(result)
            outputs.append(result_str)

            # Special: if create_project ran, adopt a new repo root
            if name == "create_project":
                for line in result_str.splitlines():
                    if line.startswith("REPO_ROOT="):
                        state["repo_root"] = line.split("=", 1)[1].strip()
                        break

            state["messages"].append({
                "type": "tool",
                "content": result_str,
                "tool_call_id": call.get("id", "tool"),
            })

        state["last_tool_output"] = "\n\n".join(outputs)
        state["pending_tool_calls"] = []
        return state

    g = StateGraph(AgentState)
    g.add_node("llm", RunnableLambda(_llm_node_with_tools))
    g.add_node("tools", RunnableLambda(_tools_node_with_tools))
    g.add_node("check", RunnableLambda(_check_done))

    g.set_entry_point("llm")
    g.add_edge("llm", "tools")
    g.add_edge("tools", "check")
    g.add_conditional_edges("check", _route, {"llm": "llm", "tools": "tools", END: END})
    return g.compile()




