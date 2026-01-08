from __future__ import annotations
from typing import TypedDict, List, Optional, Dict, Any

class ControlChannel(TypedDict, total=False):
    """Structured control output from the LLM."""
    done: bool
    summary: Optional[str]  # Final summary when done=True

class AgentState(TypedDict, total=False):
    goal: str
    messages: List[Dict[str, Any]]  # LangChain message dicts
    repo_root: str
    last_tool_output: Optional[str]
    done: bool
    pending_tool_calls: List[Dict[str, Any]]
    control: Optional[ControlChannel]  # Structured control from LLM
