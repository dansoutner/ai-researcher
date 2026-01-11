"""Message pruning utilities to manage context window size."""

from typing import List

from langchain_core.messages import BaseMessage, ToolMessage

from .config import PruningConfig
from .state import ToolOutputStore


def summarize_tool_output(
    text: str,
    *,
    cfg: PruningConfig,
    tool_call_id: str,
) -> str:
    """Truncate large tool outputs while preserving head and tail.

    Args:
        text: The full tool output text
        cfg: Pruning configuration controlling truncation
        tool_call_id: ID for referencing the full stored output

    Returns:
        Either the full text (if small enough) or a truncated version
        with metadata about the omitted content.
    """
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
    """Return a pruned copy of messages safe to send to the LLM.

    Strategy:
    - Keep last N messages unchanged (most relevant context)
    - For older ToolMessages, store raw content and replace with truncated stub

    This prevents context-window explosion when running tools that output
    thousands of lines (pytest, linters, etc.).

    Args:
        messages: Full message history
        store: Storage for raw tool outputs
        cfg: Configuration controlling pruning behavior

    Returns:
        Pruned message list suitable for LLM context window
    """
    if not messages:
        return []

    n = cfg.keep_last_messages
    cutoff_index = max(0, len(messages) - n) if n >= 0 else 0

    pruned: List[BaseMessage] = []

    for i, msg in enumerate(messages):
        # Keep recent messages unchanged
        if i >= cutoff_index:
            pruned.append(msg)
            continue

        # For older tool messages, store and truncate
        if isinstance(msg, ToolMessage):
            tool_call_id = getattr(msg, "tool_call_id", "")
            content = getattr(msg, "content", "") or ""

            # Store raw output (first write wins)
            if tool_call_id and store.get(tool_call_id) is None:
                store.put(tool_call_id, content)

            # Replace with truncated version
            stub = summarize_tool_output(
                content,
                cfg=cfg,
                tool_call_id=tool_call_id,
            )
            pruned.append(ToolMessage(content=stub, tool_call_id=tool_call_id))
            continue

        # Keep other message types as-is (usually short)
        pruned.append(msg)

    return pruned

