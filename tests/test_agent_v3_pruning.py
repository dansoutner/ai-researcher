from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

import pytest

from langchain_core.messages import AIMessage, ToolMessage

from agent_v3_claude.agent import (
    PruningConfig,
    ToolOutputStore,
    prune_messages_for_llm,
)


def test_prune_tool_messages_stores_raw_and_replaces_with_stub():
    store = ToolOutputStore()
    cfg = PruningConfig(tool_max_chars=200, keep_last_messages=10)

    big = "x" * 5000
    msgs: List[Any] = [ToolMessage(content=big, tool_call_id="call_1")]

    pruned = prune_messages_for_llm(msgs, store=store, cfg=cfg)

    assert len(pruned) == 1
    assert isinstance(pruned[0], ToolMessage)
    assert pruned[0].tool_call_id == "call_1"
    assert len(pruned[0].content) < 400  # stub/truncation

    raw = store.get("call_1")
    assert raw is not None
    assert raw == big


def test_prune_keeps_recent_messages_intact():
    store = ToolOutputStore()
    cfg = PruningConfig(tool_max_chars=50, keep_last_messages=2)

    msgs: List[Any] = [
        AIMessage(content="old"),
        ToolMessage(content="y" * 1000, tool_call_id="call_old"),
        AIMessage(content="new"),
        ToolMessage(content="z" * 10, tool_call_id="call_new"),
    ]

    pruned = prune_messages_for_llm(msgs, store=store, cfg=cfg)

    # last 2 messages should be untouched
    assert pruned[-2].content == "new"
    assert pruned[-1].content == "z" * 10
    # older tool message should be replaced/stored
    assert store.get("call_old") == "y" * 1000
    assert len(pruned[1].content) < 200


def test_multiple_prunes_dont_bloat_stub():
    store = ToolOutputStore()
    cfg = PruningConfig(tool_max_chars=80, keep_last_messages=0)

    big = "line\n" * 1000
    msg = ToolMessage(content=big, tool_call_id="call_1")

    first = prune_messages_for_llm([msg], store=store, cfg=cfg)
    second = prune_messages_for_llm(first, store=store, cfg=cfg)

    assert len(second[0].content) <= len(first[0].content)
    assert store.get("call_1") == big

