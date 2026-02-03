"""Agent role nodes: Planner, Executor, and Reviewer."""

import json
from typing import Dict, Any
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from .config import (
    PLANNER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    VALID_VERDICTS,
    get_current_datetime,
)
from .state import AgentState
from .tools import run_executor_turn
from .logging_utils import get_logger, format_section_header, log_llm_usage

logger = get_logger(__name__)


# =========================
# LLM Provider
# =========================

def require_llm() -> BaseChatModel:
    """Provide your LLM implementation here.

    Choose provider via env:
      LLM_PROVIDER=openai|anthropic
    And set provider keys as usual:
      OPENAI_API_KEY=...
      ANTHROPIC_API_KEY=...

    You can also swap this to any LangChain-compatible chat model.
    """
    provider = os.getenv("LLM_PROVIDER").lower()
    model = os.getenv("LLM_MODEL")  # example default
    temperature = float(os.getenv("LLM_TEMPERATURE", 0))
    if not model:
        raise ValueError("LLM_MODEL is required.")
    if not provider:
        raise ValueError("LLM_PROVIDER is required.")

    if provider == "anthropic":
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        return ChatAnthropic(model=model, temperature=temperature, api_key=ANTHROPIC_API_KEY)
    if provider == "openai":
        return ChatOpenAI(model=model, temperature=temperature)

    raise ValueError(f"Unsupported LLM_PROVIDER={provider!r}")




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
    # Handle non-string content (e.g., empty list from LLM with only tool calls)
    if not isinstance(content, str):
        if isinstance(content, list):
            # If it's a list, convert to string or raise if empty
            if not content:
                raise ValueError("Empty content list - planner provided no text response")
            content = str(content)
        else:
            content = str(content)

    # Handle empty or whitespace-only content
    if not content or not content.strip():
        raise ValueError("Empty content - planner provided no response")

    try:
        data = json.loads(content)
    except json.decoder.JSONDecodeError:
        content = content.replace("```json", "").replace("```", "")
        data = json.loads(content)
    plan = data["plan"]

    if not isinstance(plan, list) or not all(isinstance(s, str) for s in plan):
        raise ValueError("Plan must be a list of strings")

    return plan


def parse_reviewer_response(content: str) -> Dict[str, Any]:
    """Parse reviewer response JSON to extract verdict.

    Args:
        content: LLM response content (expected JSON, may have surrounding text)

    Returns:
        Dict with 'verdict', 'reason', and 'fix_suggestion' keys

    Raises:
        ValueError: If response format is invalid
    """
    # Handle non-string content (e.g., empty list from LLM with only tool calls)
    if not isinstance(content, str):
        if isinstance(content, list):
            # If it's a list, convert to string or raise if empty
            if not content:
                raise ValueError("Empty content list - reviewer provided no text response")
            content = str(content)
        else:
            content = str(content)

    # Handle empty or whitespace-only content
    if not content or not content.strip():
        raise ValueError("Empty content - reviewer provided no response")

    # Try to parse as direct JSON first
    logger.debug(f"Trying to parse reviewer response as JSON: {content[:500]}")
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
                # Check if this looks like our reviewer response format
                if isinstance(parsed, dict) and "verdict" in parsed:
                    data = parsed
                    break
            except json.JSONDecodeError:
                continue

        if data is None:
            raise ValueError(f"Could not find valid JSON in response. Content: {content[:500]}")

    verdict = data.get("verdict")
    if not verdict or verdict not in VALID_VERDICTS:
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
    logger.info(f"=== PLANNER NODE (iteration {state['iters']}) ===")

    # CRITICAL: On first iteration, save working directory to memory
    # This ensures the executor can always recall it, preventing hallucinated paths
    if state['iters'] == 0:
        from ai_researcher.ai_researcher_tools import memory_set
        repo_root = state['repo_root']
        logger.debug(f"First iteration - saving working directory to memory: {repo_root}")
        memory_set.invoke({"repo_root": repo_root, "key": "working_directory", "value": repo_root})

    llm = require_llm()

    # Include reviewer feedback or executor failure context if available
    fix_hint = ""
    if state.get("verdict") and state.get("last_result"):
        fix_hint = f"\nPrevious feedback: {state['last_result']}\n"
    elif state.get("executor_output") and not state["executor_output"]["success"]:
        fix_hint = f"\nPrevious execution failed: {state['executor_output']['output']}\n"

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT.format(current_datetime=get_current_datetime())),
        HumanMessage(
            content=f"GOAL: {state['goal']}{fix_hint}\nCreate/adjust the plan."
        ),
    ]

    ai_message = llm.invoke(messages)
    log_llm_usage(logger, "Planner", messages, ai_message)

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
    state["step_index"] = 0  # Always reset to start of new plan
    state["messages"].append(ai_message)

    # Debug logging to show the plan to user
    logger.info("\n" + "=" * 60)
    logger.info("PLAN GENERATED")
    logger.info("=" * 60)
    for i, step in enumerate(plan, 1):
        logger.info(f"{i}. {step}")
    logger.info("=" * 60 + "\n")

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
    current_step = state["plan"][state["step_index"]] if state["plan"] else "No plan"
    logger.info(f"=== EXECUTOR NODE (iteration {state['iters']}, step {state['step_index'] + 1}/{len(state['plan'])}) ===")
    logger.info(f"Executing step: {current_step}")

    # CRITICAL: Retrieve working directory from memory to prevent hallucinated paths
    from ai_researcher.ai_researcher_tools import memory_get
    try:
        saved_workdir = memory_get.invoke({"repo_root": state["repo_root"], "key": "working_directory"})
        if saved_workdir and saved_workdir != "Key 'working_directory' not found in memory.":
            logger.debug(f"Retrieved working directory from memory: {saved_workdir}")
            # Update state with retrieved working directory to ensure consistency
            state["repo_root"] = saved_workdir
        else:
            logger.debug(f"No working directory in memory, using state value: {state['repo_root']}")
    except Exception as e:
        logger.warning(f"Failed to retrieve working directory from memory: {e}")
        logger.debug(f"Using state value: {state['repo_root']}")

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
    logger.info(f"=== REVIEWER NODE (iteration {state['iters']}) ===")

    # Check if executor failed - if so, automatically set retry verdict
    executor_output = state.get("executor_output")
    logger.debug(f"Executor output: {executor_output}")
    if executor_output and not executor_output["success"]:
        logger.warning(f"Executor failed, automatically setting verdict to 'retry'")
        state["verdict"] = "retry"
        state["last_result"] = f"RETRY: Executor failed - {executor_output['output']}"
        return state

    llm = require_llm()

    # Format plan for review
    plan_text = "\n".join([
        f"{i+1}. {step}" for i, step in enumerate(state["plan"])
    ])

    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT.format(current_datetime=get_current_datetime())),
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
    log_llm_usage(logger, "Reviewer", messages, ai_message)

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

    logger.info(f"Reviewer verdict: {verdict.upper()}")
    logger.debug(f"Reason: {reason}")
    if fix_suggestion:
        logger.debug(f"Fix suggestion: {fix_suggestion}")

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
    if state["plan"] and state["step_index"] < len(state["plan"]) - 1:
        state["step_index"] += 1
    elif state["plan"] and state["step_index"] == len(state["plan"]) - 1:
        # Plan complete with "continue" verdict - treat as goal completion
        state["verdict"] = "finish"
    else:
        # No plan or invalid state - will trigger replanning via routing
        pass

    return state

