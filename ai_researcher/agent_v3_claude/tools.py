"""Tool registry and execution logic."""

import json
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models.chat_models import BaseChatModel

from ai_researcher.ai_researcher_tools import (
    # File system tools
    read_file,
    write_file,
    edit_file,
    list_files,
    grep,
    # Git tools
    git_diff,
    git_status,
    git_add,
    git_commit,
    git_log,
    git_branch_list,
    git_checkout,
    git_remote_list,
    git_prepare_pr,
    # Command tools
    apply_patch,
    run_pytest,
    run_cmd,
    # Virtual environment tools
    create_venv,
    run_in_venv,
    # Memory tools
    memory_set,
    memory_get,
    memory_list,
    memory_delete,
    memory_append,
    store_repo_map,
    store_test_results,
    clear_memory,
)

from .config import EXECUTOR_SYSTEM_PROMPT
from .pruning import prune_messages_for_llm, summarize_tool_output
from .state import AgentState, ExecutorOutput


# =========================
# Tool Registry
# =========================

TOOLS = [
    # File system
    read_file,
    write_file,
    edit_file,
    list_files,
    grep,
    # Git
    git_diff,
    git_status,
    git_add,
    git_commit,
    git_log,
    git_branch_list,
    git_checkout,
    git_remote_list,
    git_prepare_pr,
    # Commands
    apply_patch,
    run_pytest,
    run_cmd,
    # Virtual environment
    create_venv,
    run_in_venv,
    # Memory
    memory_set,
    memory_get,
    memory_list,
    memory_delete,
    memory_append,
    store_repo_map,
    store_test_results,
    clear_memory,
]

TOOL_BY_NAME = {tool.name: tool for tool in TOOLS}


# =========================
# Response Parsers
# =========================

def parse_executor_response(content: str) -> ExecutorOutput:
    """Parse executor response JSON to extract execution result.

    Args:
        content: LLM response content (expected JSON, may have surrounding text)

    Returns:
        ExecutorOutput with 'success' and 'output' keys

    Raises:
        ValueError: If response format is invalid
    """
    # Handle non-string content (e.g., empty list from LLM with only tool calls)
    if not isinstance(content, str):
        if isinstance(content, list):
            # If it's a list, convert to string or raise if empty
            if not content:
                raise ValueError("Empty content list - executor provided no text response")
            content = str(content)
        else:
            content = str(content)

    # Handle empty or whitespace-only content
    if not content or not content.strip():
        raise ValueError("Empty content - executor provided no response")

    # Try to parse as direct JSON first
    print(f"[DEBUG] Trying to parse executor response as JSON: {content[:500]}")
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from surrounding text
        # Look for JSON object patterns
        import re

        # Find all potential JSON objects in the content
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, content, re.DOTALL)

        data = None
        for match in matches:
            try:
                parsed = json.loads(match)
                # Check if this looks like our executor response format
                if isinstance(parsed, dict) and "success" in parsed and "output" in parsed:
                    data = parsed
                    break
            except json.JSONDecodeError:
                continue

        if data is None:
            raise ValueError(f"Could not find valid JSON in response. Content: {content[:500]}")

    if "success" not in data or not isinstance(data["success"], bool):
        raise ValueError("Response must contain 'success' boolean field")

    if "output" not in data or not isinstance(data["output"], str):
        raise ValueError("Response must contain 'output' string field")

    return ExecutorOutput(
        success=data["success"],
        output=data["output"]
    )


# =========================
# Tool Execution
# =========================

def execute_tool_call(call: Dict[str, Any], repo_root: str) -> str:
    """Execute a single tool call and return the result.

    Args:
        call: Tool call dict with 'name' and 'args' keys
        repo_root: Working directory to inject into tool arguments

    Returns:
        Tool execution result as string
    """
    name = call["name"]
    args = call.get("args", {}) or {}

    # Handle string-encoded args
    if isinstance(args, str):
        args = json.loads(args)

    # Auto-inject repo_root if tool expects it and it's not already provided
    if "repo_root" not in args or not args["repo_root"]:
        args["repo_root"] = repo_root

    # Debug logging for tool calls
    print(f"[DEBUG] Calling tool: {name}")
    print(f"[DEBUG] Tool args: {args}")

    tool_fn = TOOL_BY_NAME.get(name)
    if not tool_fn:
        error_msg = f"ERROR: tool '{name}' not found. Available: {list(TOOL_BY_NAME.keys())}"
        print(f"[DEBUG] Tool error: {error_msg}")
        return error_msg

    try:
        result = tool_fn.invoke(args)
        result_str = str(result)
        print(f"[DEBUG] Tool result length: {len(result_str)} characters")
        print(f"[DEBUG] Tool result preview: {result_str[:200]}{'...' if len(result_str) > 200 else ''}")
        return result_str
    except Exception as e:
        error_msg = f"ERROR executing {name}: {e}"
        print(f"[DEBUG] Tool exception: {error_msg}")
        return error_msg


def run_executor_turn(llm: BaseChatModel, state: AgentState) -> AgentState:
    """Execute one plan step using the LLM and available tools.

    The executor loops until the LLM returns a final message (no tool calls).
    Each loop iteration:
    1. Prunes message history to fit context window
    2. Invokes LLM
    3. Executes any requested tools
    4. Feeds tool results back to LLM

    Args:
        llm: Language model to use for reasoning
        state: Current agent state

    Returns:
        Updated state with executor results
    """
    current_step = state["plan"][state["step_index"]]

    # Build local message context for this executor turn
    local_messages: List[BaseMessage] = [
        SystemMessage(content=EXECUTOR_SYSTEM_PROMPT),
        HumanMessage(
            content=f"GOAL: {state['goal']}\nCURRENT STEP: {current_step}"
        ),
    ] + state["messages"]

    # Bind tools to the LLM for tool calling
    llm_with_tools = llm.bind_tools(TOOLS)

    # Tool execution loop
    while True:
        # Prune messages to avoid context window overflow
        safe_messages = prune_messages_for_llm(
            local_messages,
            store=state["tool_output_store"],
            cfg=state["pruning_cfg"],
        )

        # Get LLM response
        ai_message = llm_with_tools.invoke(safe_messages)

        # Check for tool calls
        tool_calls = getattr(ai_message, "tool_calls", None)
        if not tool_calls:
            # No tool calls - executor is done with this step
            local_messages.append(ai_message)
            state["messages"].append(ai_message)

            # Parse structured executor output
            try:
                executor_output = parse_executor_response(ai_message.content)
            except Exception as e:
                # Fallback if parsing fails - treat as failed execution
                executor_output = ExecutorOutput(
                    success=False,
                    output=f"Executor response parse error: {e}. Raw response: {ai_message.content[:500]}"
                )

            state["executor_output"] = executor_output
            state["last_result"] = executor_output["output"]

            return state

        # Execute all requested tools
        local_messages.append(ai_message)

        for call in tool_calls:
            tool_call_id = call.get("id", "")
            output_text = execute_tool_call(call, state["repo_root"])

            # Store raw output
            if tool_call_id:
                state["tool_output_store"].put(tool_call_id, output_text)

            # Create truncated stub for LLM context
            stub = summarize_tool_output(
                output_text,
                cfg=state["pruning_cfg"],
                tool_call_id=tool_call_id,
            )

            local_messages.append(
                ToolMessage(content=stub, tool_call_id=tool_call_id)
            )

        # Continue loop to get next LLM response

