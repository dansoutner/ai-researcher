"""Configuration and constants for the agent system."""

from dataclasses import dataclass
from typing import Literal

# =========================
# Verdict types
# =========================

Verdict = Literal["continue", "retry", "replan", "finish"]

VALID_VERDICTS: set[Verdict] = {"continue", "retry", "replan", "finish"}


# =========================
# Pruning configuration
# =========================

@dataclass(frozen=True)
class PruningConfig:
    """Controls how aggressively we prune messages before sending them to the LLM.

    This helps avoid context-window explosion when running tools that output
    thousands of lines (pytest, linters, etc.).
    """

    # Keep the last N messages verbatim (typically the most relevant context)
    keep_last_messages: int = 20

    # If a ToolMessage content exceeds this, store raw output and replace w/ stub
    tool_max_chars: int = 6000

    # How much of a large tool output to show to the LLM
    tool_head_chars: int = 1200
    tool_tail_chars: int = 800


# =========================
# System prompts
# =========================

PLANNER_SYSTEM_PROMPT = """You are the PLANNER role in an agent.
Write a short, concrete plan as a numbered list of steps.
Each step should be executable using available tools (shell/file IO) and reasoning.
Return ONLY JSON with this schema:
{
  "plan": ["step 1", "step 2", ...]
}
"""

EXECUTOR_SYSTEM_PROMPT = """You are the EXECUTOR role in an agent.
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
When done with the step, respond with ONLY JSON following this schema:
{
  "success": true | false,
  "output": "description of what happened"
}

Set "success" to true if the step completed successfully, false if it failed or encountered errors.
The "output" should be a clear summary of what was accomplished or what went wrong.
"""

REVIEWER_SYSTEM_PROMPT = """You are the REVIEWER role in an agent.
You decide whether the current step was successful and what to do next.

Return ONLY JSON with this schema:
{
  "verdict": "continue" | "retry" | "replan" | "finish",
  "reason": "one short sentence explaining why",
  "fix_suggestion": "if retry/replan, give concrete advice to the executor/planner"
}

Verdict Definitions:
- "continue": The current step was successful. Move to the next step.
- "retry": The current step failed. Loop back to planner to create a new plan with your feedback.
- "replan": The current plan is failing or impossible. Discard the plan and create a new one.
- "finish": The overall goal (not just the step) is complete.
"""


# =========================
# Default settings
# =========================

DEFAULT_MAX_ITERATIONS = 12
DEFAULT_TEMPERATURE = 0

