"""
LangGraph example: agent roles + execution loop (planner -> executor -> reviewer -> (replan|finish))

Roles:
- Planner: decides what to do next (plan steps)
- Executor: runs tools / writes patches / runs tests
- Reviewer: checks results, decides to finish or ask for another iteration

This is a *template*. Plug in your own LLM (OpenAI/Anthropic/etc.) + your own tools.
"""

from __future__ import annotations

import os
import json
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict

# ---- LangChain / LangGraph imports ----
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, END

# Optional: if you want a prebuilt tool node, you can also use:
# from langgraph.prebuilt import ToolNode


# =========================
# Context pruning / tool-output storage
# =========================

@dataclass(frozen=True)
class PruningConfig:
    """Controls how aggressively we prune messages before sending them to the LLM.

    This agent is a template, so we use deterministic truncation rather than
    requiring a separate summarizer LLM.
    """

    # Keep the last N messages verbatim (typically the most relevant context)
    keep_last_messages: int = 20

    # If a ToolMessage content exceeds this, store raw output and replace w/ stub
    tool_max_chars: int = 6000

    # How much of a large tool output to show to the LLM
    tool_head_chars: int = 1200
    tool_tail_chars: int = 800


class ToolOutputStore:
    """Out-of-band storage for raw tool outputs keyed by tool_call_id."""

    def __init__(self) -> None:
        self._store: Dict[str, str] = {}

    def put(self, tool_call_id: str, content: str) -> None:
        if tool_call_id:
            # First write wins; later prunes should not overwrite raw content
            self._store.setdefault(tool_call_id, content)

    def get(self, tool_call_id: str) -> Optional[str]:
        return self._store.get(tool_call_id)

    def __len__(self) -> int:
        return len(self._store)


def _summarize_tool_output(text: str, *, cfg: PruningConfig, tool_call_id: str) -> str:
    if len(text) <= cfg.tool_max_chars:
        return text

    head = text[: cfg.tool_head_chars]
    tail = text[-cfg.tool_tail_chars :] if cfg.tool_tail_chars > 0 else ""

    lines = text.count("\n") + 1 if text else 0
    omitted = len(text) - len(head) - len(tail)

    middle = (
        f"\n... <omitted {omitted} chars, {lines} lines total; "
        f"stored as tool_call_id={tool_call_id}> ...\n"
    )
    return head + middle + tail


def prune_messages_for_llm(
    messages: List[BaseMessage],
    *,
    store: ToolOutputStore,
    cfg: PruningConfig,
) -> List[BaseMessage]:
    """Return a pruned copy of `messages` safe to send to the LLM.

    Strategy:
    - Keep last N messages unchanged.
    - For older ToolMessages, store raw content and replace with a truncated stub.

    This avoids context-window explosion when running tools that output thousands
    of lines (pytest, linters, etc.).
    """

    if not messages:
        return []

    n = cfg.keep_last_messages
    cut = max(0, len(messages) - n) if n >= 0 else 0

    pruned: List[BaseMessage] = []

    for i, m in enumerate(messages):
        if i >= cut:
            pruned.append(m)
            continue

        if isinstance(m, ToolMessage):
            tool_call_id = getattr(m, "tool_call_id", "")
            content = getattr(m, "content", "") or ""

            # Store raw tool output, then replace with a stub (deterministic truncation)
            if tool_call_id and store.get(tool_call_id) is None:
                store.put(tool_call_id, content)

            stub = _summarize_tool_output(content, cfg=cfg, tool_call_id=tool_call_id)
            pruned.append(ToolMessage(content=stub, tool_call_id=tool_call_id))
            continue

        # Non-tool message: keep as-is (these are usually short). If you want to
        # aggressively prune chat history too, you can extend this.
        pruned.append(m)

    return pruned


# =========================
# Tools (import from ai_researcher_tools)
# =========================

from ai_researcher_tools import (
    # File system tools
    read_file,
    write_file,
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

TOOLS = [
    # File system
    read_file,
    write_file,
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
TOOL_BY_NAME = {t.name: t for t in TOOLS}


# =========================
# State (shared blackboard)
# =========================

class AgentState(TypedDict):
    # Conversation
    messages: List[BaseMessage]

    # Planning/execution metadata
    goal: str
    plan: List[str]
    step_index: int

    # Review loop
    last_result: Optional[str]
    verdict: Optional[Literal["continue", "finish"]]
    max_iters: int
    iters: int

    # Context control
    tool_output_store: ToolOutputStore
    pruning_cfg: PruningConfig


# =========================
# LLM wiring
# =========================

def require_llm() -> BaseChatModel:
    """
    Provide your own LLM here.

    Examples:
      - OpenAI:
          from langchain_openai import ChatOpenAI
          return ChatOpenAI(model="gpt-4.1-mini", temperature=0)
      - Anthropic:
          from langchain_anthropic import ChatAnthropic
          return ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)

    Keep it as BaseChatModel.
    """
    raise RuntimeError(
        "Please implement require_llm() with your chosen provider."
    )


# =========================
# Role prompts
# =========================

PLANNER_SYS = """You are the PLANNER role in an agent.
Write a short, concrete plan as a numbered list of steps.
Each step should be executable using available tools (shell/file IO) and reasoning.
Return ONLY JSON with this schema:
{
  "plan": ["step 1", "step 2", ...]
}
"""

EXECUTOR_SYS = """You are the EXECUTOR role in an agent.
You will execute exactly ONE plan step at a time.

Available tools:
- File system: read_file, write_file, list_files, grep
- Git: git_diff, git_status, git_add, git_commit, git_log, git_branch_list, git_checkout, git_remote_list, git_prepare_pr
- Commands: apply_patch, run_pytest, run_cmd
- Virtual environments: create_venv, run_in_venv
- Memory: memory_set, memory_get, memory_list, memory_delete, memory_append, store_repo_map, store_test_results, clear_memory

You can:
- call tools to inspect the repo, edit files, run tests, manage git, work with virtual environments
- use memory tools to persist context across steps
- produce a result summary for this step

When you need a tool, respond with a tool call (function name + JSON args).
When done with the step, respond with a normal assistant message summarizing what happened.
"""

REVIEWER_SYS = """You are the REVIEWER role in an agent.
You decide whether the current step was successful and what to do next.

Return ONLY JSON with this schema:
{
  "verdict": "continue" | "retry" | "replan" | "finish",
  "reason": "one short sentence explaining why",
  "fix_suggestion": "if retry/replan, give concrete advice to the executor/planner"
}

Verdict Definitions:
- "continue": The current step was successful. Move to the next step.
- "retry": The current step failed. Do NOT advance. The executor must fix this step.
- "replan": The current plan is failing or impossible. Discard the plan and create a new one.
- "finish": The overall goal (not just the step) is complete.
"""

# =========================
# Helper: tool execution loop for a single executor turn
# =========================

def run_executor_turn(llm: BaseChatModel, state: AgentState) -> AgentState:
    """
    Executor runs *one* plan step. If the LLM asks for tools, we execute them and feed back ToolMessages.
    We keep looping until the LLM returns a normal AIMessage (no tool calls).

    Important: We prune message history (especially tool outputs) before each LLM call
    to avoid context-window explosion.
    """
    step = state["plan"][state["step_index"]]
    # Add a system+instruction framing just for the executor
    local_messages: List[BaseMessage] = [
        SystemMessage(content=EXECUTOR_SYS),
        HumanMessage(content=f"GOAL: {state['goal']}\nCURRENT STEP: {step}"),
    ] + state["messages"]

    while True:
        safe_messages = prune_messages_for_llm(
            local_messages,
            store=state["tool_output_store"],
            cfg=state["pruning_cfg"],
        )
        ai = llm.invoke(safe_messages)

        # In LangChain, tool calls are represented differently depending on provider/version.
        # We'll support the common `ai.tool_calls` attribute if present.
        tool_calls = getattr(ai, "tool_calls", None)
        if tool_calls:
            # Execute each tool call and append ToolMessage(s)
            for call in tool_calls:
                name = call["name"]
                args = call.get("args", {}) or {}
                if isinstance(args, str):
                    args = json.loads(args)

                tool_fn = TOOL_BY_NAME.get(name)
                if not tool_fn:
                    out = f"ERROR: tool '{name}' not found. Available: {list(TOOL_BY_NAME)}"
                else:
                    out = tool_fn.invoke(args)

                local_messages.append(ai)

                tool_call_id = call.get("id", "")
                out_text = str(out)

                # Store raw output out-of-band immediately, then only give the LLM a stub
                if tool_call_id:
                    state["tool_output_store"].put(tool_call_id, out_text)

                stub = _summarize_tool_output(
                    out_text,
                    cfg=state["pruning_cfg"],
                    tool_call_id=tool_call_id,
                )
                local_messages.append(ToolMessage(content=stub, tool_call_id=tool_call_id))
            continue

        # No tool calls => final executor message for this step
        local_messages.append(ai)

        # Persist only the new messages the agent produced.
        state["messages"].append(ai)
        state["last_result"] = ai.content if isinstance(ai, AIMessage) else str(ai)
        return state


# =========================
# Graph nodes (roles)
# =========================

def planner_node(state: AgentState) -> AgentState:
    llm = require_llm()

    # If reviewer provided a fix suggestion, include it.
    fix_hint = ""
    if state.get("messages"):
        # Find the last reviewer JSON if present in messages (optional)
        pass
    if state.get("verdict") == "continue" and state.get("last_result"):
        fix_hint = f"\nReviewer said: {state.get('last_result')}\n"

    msgs = [
        SystemMessage(content=PLANNER_SYS),
        HumanMessage(content=f"GOAL: {state['goal']}{fix_hint}\nCreate/adjust the plan."),
    ]
    ai = llm.invoke(msgs)

    # Expect JSON: {"plan":[...]}
    try:
        data = json.loads(ai.content)
        plan = data["plan"]
        if not isinstance(plan, list) or not all(isinstance(s, str) for s in plan):
            raise ValueError("Plan must be a list of strings.")
    except Exception as e:
        # Fallback: treat whole content as a 1-step plan
        plan = [f"Parse failure in planner ({e}). Do the task directly: {ai.content}"]

    state["plan"] = plan
    state["step_index"] = 0
    state["messages"].append(ai)
    return state


def executor_node(state: AgentState) -> AgentState:
    llm = require_llm()
    return run_executor_turn(llm, state)


def reviewer_node(state: AgentState) -> AgentState:
    llm = require_llm()

    # Provide the overall goal + current artifacts
    plan_txt = "\n".join([f"{i+1}. {s}" for i, s in enumerate(state["plan"])])
    msgs = [
        SystemMessage(content=REVIEWER_SYS),
        HumanMessage(
            content=(
                f"GOAL: {state['goal']}\n"
                f"PLAN:\n{plan_txt}\n"
                f"CURRENT STEP INDEX: {state['step_index']}\n"
                f"LAST_RESULT:\n{state.get('last_result')}\n\n"
                "Decide if the step was successful or if we need to retry/replan."
            )
        ),
    ]
    ai = llm.invoke(msgs)

    try:
        data = json.loads(ai.content)
        verdict = data["verdict"]
        valid_verdicts = {"continue", "finish", "retry", "replan"}
        if verdict not in valid_verdicts:
            raise ValueError(f"verdict must be one of {valid_verdicts}")
        reason = data.get("reason", "")
        fix = data.get("fix_suggestion", "")
    except Exception as e:
        # Default safe fallback
        verdict = "retry"
        reason = f"Reviewer JSON parse failed: {e}"
        fix = "Check the last output and try again."

    state["verdict"] = verdict
    state["messages"].append(ai)
    state["last_result"] = f"{verdict.upper()}: {reason} | {fix}"
    return state


def advance_or_stop(state: AgentState) -> AgentState:
    """
    Update counters and move to next step, retry, or replan.
    """
    state["iters"] += 1

    verdict = state["verdict"]

    if verdict == "finish":
        return state

    if verdict == "retry":
        # Do NOT increment step_index.
        # The routing logic will see step_index < len(plan) and send back to Executor.
        # The executor will see the reviewer's 'fix_suggestion' in the message history.
        return state

    if verdict == "replan":
        # Clear the plan to trigger the planner node logic
        state["plan"] = []
        state["step_index"] = 0
        return state

    # Verdict is "continue" -> Advance to next step
    if state["step_index"] < len(state["plan"]) - 1:
        state["step_index"] += 1
    else:
        # We finished the plan but reviewer didn't say "finish"
        # This implies we need to extend the plan or verify.
        # Reset plan to force Planner to decide what's next.
        state["plan"] = []
        state["step_index"] = 0

    return state

# =========================
# Routing logic (the "loop")
# =========================

def route_after_planner(state: AgentState) -> Literal["executor", END]:
    return "executor" if state["plan"] else END


def route_after_executor(state: AgentState) -> Literal["reviewer"]:
    return "reviewer"


def route_after_reviewer(state: AgentState) -> Literal["planner", "executor", END]:
    # Stop conditions
    if state["verdict"] == "finish":
        return END
    if state["iters"] >= state["max_iters"]:
        return END

    # If we have a valid plan and are within bounds, go to Executor.
    # In a "retry", step_index wasn't incremented, so we go back to Executor. Correct.
    if state["plan"] and state["step_index"] < len(state["plan"]):
        return "executor"

    # If plan is empty (replan) or we ran out of steps, go to Planner. Correct.
    return "planner"


# =========================
# Build the graph
# =========================

def build_graph():
    g = StateGraph(AgentState)

    g.add_node("planner", planner_node)
    g.add_node("executor", executor_node)
    g.add_node("reviewer", reviewer_node)
    g.add_node("advance", advance_or_stop)

    # Entry: planner
    g.set_entry_point("planner")

    # planner -> executor (or end)
    g.add_conditional_edges("planner", route_after_planner)

    # executor -> reviewer
    g.add_edge("executor", "reviewer")

    # reviewer -> advance (update counters / next step bookkeeping)
    g.add_edge("reviewer", "advance")

    # advance -> (planner|executor|end)
    g.add_conditional_edges("advance", route_after_reviewer)

    return g.compile()


# =========================
# Run
# =========================

def run(goal: str, max_iters: int = 12) -> AgentState:
    app = build_graph()
    init: AgentState = {
        "messages": [],
        "goal": goal,
        "plan": [],
        "step_index": 0,
        "last_result": None,
        "verdict": None,
        "max_iters": max_iters,
        "iters": 0,
        "tool_output_store": ToolOutputStore(),
        "pruning_cfg": PruningConfig(),
    }
    final_state: AgentState = app.invoke(init)
    return final_state


if __name__ == "__main__":
    # Example goal:
    # goal = "Create a new python package, add pytest, implement foo(), and make tests pass."
    goal = "Run `pytest` in the repo, fix failing tests, and summarize what changed."
    state = run(goal, max_iters=10)

    print("\n=== FINAL VERDICT ===")
    print(state.get("verdict"))
    print("\n=== FINAL REVIEW ===")
    print(state.get("last_result"))
    print("\n=== MESSAGE TRACE (last 6) ===")
    for m in state["messages"][-6:]:
        role = m.__class__.__name__
        content = getattr(m, "content", "")
        print(f"\n[{role}]\n{content}")
