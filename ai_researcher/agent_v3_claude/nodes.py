"""Agent role nodes: Planner, Executor, and Reviewer."""

import json
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

from .config import (
    PLANNER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    VALID_VERDICTS,
)
from .state import AgentState
from .tools import run_executor_turn


# =========================
# LLM Provider
# =========================

def require_llm() -> BaseChatModel:
    """Provide your LLM implementation here.

    Examples:
      - OpenAI:
          from langchain_openai import ChatOpenAI
          return ChatOpenAI(model="gpt-4o-mini", temperature=0)
      - Anthropic:
          from langchain_anthropic import ChatAnthropic
          return ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)

    Raises:
        RuntimeError: If not implemented
    """
    raise RuntimeError(
        "Please implement require_llm() with your chosen LLM provider."
    )


# =========================
# Response Parsers
# =========================

def parse_plan_response(content: str) -> list[str]:
    """Parse planner response JSON to extract plan steps.

    Args:
        content: LLM response content (expected JSON)

    Returns:
        List of plan steps

    Raises:
        ValueError: If response format is invalid
    """
    data = json.loads(content)
    plan = data["plan"]

    if not isinstance(plan, list) or not all(isinstance(s, str) for s in plan):
        raise ValueError("Plan must be a list of strings")

    return plan


def parse_reviewer_response(content: str) -> Dict[str, Any]:
    """Parse reviewer response JSON to extract verdict.

    Args:
        content: LLM response content (expected JSON)

    Returns:
        Dict with 'verdict', 'reason', and 'fix_suggestion' keys

    Raises:
        ValueError: If response format is invalid
    """
    data = json.loads(content)
    verdict = data["verdict"]

    if verdict not in VALID_VERDICTS:
        raise ValueError(f"Verdict must be one of {VALID_VERDICTS}")

    return {
        "verdict": verdict,
        "reason": data.get("reason", ""),
        "fix_suggestion": data.get("fix_suggestion", ""),
    }


# =========================
# Role Nodes
# =========================

def planner_node(state: AgentState) -> AgentState:
    """Planner role: Creates or adjusts the execution plan.

    The planner:
    - Reviews the goal and any feedback from the reviewer or executor
    - Generates a concrete, step-by-step plan
    - Returns JSON with the plan

    Args:
        state: Current agent state

    Returns:
        Updated state with new plan
    """
    llm = require_llm()

    # Include reviewer feedback or executor failure context if available
    fix_hint = ""
    if state.get("verdict") and state.get("last_result"):
        fix_hint = f"\nPrevious feedback: {state['last_result']}\n"
    elif state.get("executor_output") and not state["executor_output"]["success"]:
        fix_hint = f"\nPrevious execution failed: {state['executor_output']['output']}\n"

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(
            content=f"GOAL: {state['goal']}{fix_hint}\nCreate/adjust the plan."
        ),
    ]

    ai_message = llm.invoke(messages)

    # Parse plan from JSON response
    try:
        plan = parse_plan_response(ai_message.content)
    except Exception as e:
        # Fallback: treat the entire response as a single-step plan
        plan = [
            f"Parse failure in planner ({e}). "
            f"Executing directly: {ai_message.content}"
        ]

    state["plan"] = plan
    state["step_index"] = 0
    state["messages"].append(ai_message)

    return state


def executor_node(state: AgentState) -> AgentState:
    """Executor role: Executes one step of the plan using tools.

    The executor:
    - Takes the current step from the plan
    - Uses available tools to complete the step
    - Returns a summary of what was done

    Args:
        state: Current agent state

    Returns:
        Updated state with execution results
    """
    llm = require_llm()
    return run_executor_turn(llm, state)


def reviewer_node(state: AgentState) -> AgentState:
    """Reviewer role: Evaluates execution results and decides next action.

    The reviewer:
    - Examines the executor's results
    - Decides whether to continue, retry, replan, or finish
    - Provides feedback for improvements if needed

    Args:
        state: Current agent state

    Returns:
        Updated state with verdict and feedback
    """
    llm = require_llm()

    # Format plan for review
    plan_text = "\n".join([
        f"{i+1}. {step}" for i, step in enumerate(state["plan"])
    ])

    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"GOAL: {state['goal']}\n"
                f"PLAN:\n{plan_text}\n"
                f"CURRENT STEP INDEX: {state['step_index']}\n"
                f"LAST RESULT:\n{state.get('last_result')}\n\n"
                "Decide if the step was successful or if we need to retry/replan."
            )
        ),
    ]

    ai_message = llm.invoke(messages)

    # Parse reviewer decision
    try:
        result = parse_reviewer_response(ai_message.content)
        verdict = result["verdict"]
        reason = result["reason"]
        fix_suggestion = result["fix_suggestion"]
    except Exception as e:
        # Safe fallback on parse errors
        verdict = "retry"
        reason = f"Reviewer JSON parse failed: {e}"
        fix_suggestion = "Check the last output and try again."

    state["verdict"] = verdict
    state["messages"].append(ai_message)
    state["last_result"] = (
        f"{verdict.upper()}: {reason} | {fix_suggestion}"
    )

    return state


def advance_node(state: AgentState) -> AgentState:
    """Update iteration counters and step index based on reviewer verdict.

    This node handles the control flow logic:
    - Increment iteration counter
    - Advance step index on "continue"
    - Reset plan for "replan" to trigger replanning
    - Reset plan for "retry" to allow planner to fix the issue
    - Keep everything on "finish"

    Args:
        state: Current agent state

    Returns:
        Updated state with adjusted counters
    """
    state["iters"] += 1
    verdict = state["verdict"]

    if verdict == "finish":
        return state

    if verdict == "retry":
        # Clear plan and reset index so planner can replan with feedback
        # Don't increment step_index - start fresh
        state["plan"] = []
        state["step_index"] = 0
        return state

    if verdict == "replan":
        # Clear plan to trigger replanning
        state["plan"] = []
        state["step_index"] = 0
        return state

    # Verdict is "continue" - advance to next step
    if state["step_index"] < len(state["plan"]) - 1:
        state["step_index"] += 1
    else:
        # Plan complete but not marked "finish" - replan to verify/extend
        state["plan"] = []
        state["step_index"] = 0

    return state

