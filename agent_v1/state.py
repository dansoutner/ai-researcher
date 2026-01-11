from __future__ import annotations
from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ControlChannel(TypedDict, total=False):
    """Structured control output from the LLM."""
    done: bool
    summary: Optional[str]  # Final summary when done=True

class AgentState(TypedDict, total=False):
    goal: str
    repo_root: str
    messages: List[Dict[str, Any]]
    plan: list[dict]  # [{"id":1,"task":"...","status":"todo|doing|done","files":[],"verify":"pytest -q"}]
    current_step_id: int
    last_test_output: str
    last_error: str
    done: bool
    last_tool_output: Optional[str]
    pending_tool_calls: List[Dict[str, Any]]
    control: Optional[ControlChannel]  # Structured control from LLM
