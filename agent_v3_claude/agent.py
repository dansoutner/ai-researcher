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
from langchain_core.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, END

# Optional: if you want a prebuilt tool node, you can also use:
# from langgraph.prebuilt import ToolNode


# =========================
# Tools (example set)
# =========================

@tool
def sh(command: str) -> str:
    """Run a shell command in the current working directory and return stdout+stderr."""
    # WARNING: This runs arbitrary shell commands. Lock this down for production.
    p = subprocess.run(
        command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=os.environ.copy(),
    )
    return p.stdout


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file path, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote {len(content)} bytes to {path}"


@tool
def read_file(path: str) -> str:
    """Read a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


TOOLS = [sh, write_file, read_file]
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

You can:
- call tools to inspect the repo, edit files, run tests
- produce a result summary for this step

When you need a tool, respond with a tool call (function name + JSON args).
When done with the step, respond with a normal assistant message summarizing what happened.
"""

REVIEWER_SYS = """You are the REVIEWER role in an agent.
You decide whether the overall goal is done.

Return ONLY JSON with this schema:
{
  "verdict": "continue" | "finish",
  "reason": "one short sentence",
  "fix_suggestion": "if continue, a concrete instruction for planner/executor; else empty string"
}
"""


# =========================
# Helper: tool execution loop for a single executor turn
# =========================

def run_executor_turn(llm: BaseChatModel, state: AgentState) -> AgentState:
    """
    Executor runs *one* plan step. If the LLM asks for tools, we execute them and feed back ToolMessages.
    We keep looping until the LLM returns a normal AIMessage (no tool calls).
    """
    step = state["plan"][state["step_index"]]
    # Add a system+instruction framing just for the executor
    local_messages: List[BaseMessage] = [
        SystemMessage(content=EXECUTOR_SYS),
        HumanMessage(content=f"GOAL: {state['goal']}\nCURRENT STEP: {step}"),
    ] + state["messages"]

    while True:
        ai = llm.invoke(local_messages)

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
                local_messages.append(ToolMessage(content=str(out), tool_call_id=call["id"]))
            continue

        # No tool calls => final executor message for this step
        local_messages.append(ai)

        # Persist only the new messages the agent produced (ai + any tool messages already appended)
        # For simplicity, we store the entire local_messages tail after the original state messages.
        # Here we just append the last AI message to the global conversation.
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
                f"STEP_INDEX: {state['step_index']}\n"
                f"LAST_RESULT:\n{state.get('last_result')}\n\n"
                "Decide if goal is finished."
            )
        ),
    ]
    ai = llm.invoke(msgs)

    try:
        data = json.loads(ai.content)
        verdict = data["verdict"]
        if verdict not in ("continue", "finish"):
            raise ValueError("verdict must be continue|finish")
        reason = data.get("reason", "")
        fix = data.get("fix_suggestion", "")
    except Exception as e:
        verdict = "continue"
        reason = f"Reviewer JSON parse failed: {e}"
        fix = "Proceed with the next plan step or improve the plan."

    state["verdict"] = verdict
    state["messages"].append(ai)

    # Store reviewer summary into last_result for planner hints, etc.
    state["last_result"] = f"{verdict.upper()}: {reason} | {fix}"
    return state


def advance_or_stop(state: AgentState) -> AgentState:
    """
    Update counters and move to next step when appropriate.
    """
    state["iters"] += 1

    if state["verdict"] == "finish":
        return state

    # continue: advance step if possible, else force replan
    if state["step_index"] < len(state["plan"]) - 1:
        state["step_index"] += 1
    else:
        # ran out of steps => replan
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

    # If we have remaining plan steps, keep executing; otherwise replan.
    if state["plan"] and state["step_index"] < len(state["plan"]):
        return "executor"
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
