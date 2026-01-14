"""CLI entrypoint for agent_v3_claude.

This wraps `agent_v3_claude.agent.run()` behind a small argparse interface so it
can be exposed via a `pyproject.toml` script entry.

Note: `agent_v3_claude.agent.require_llm()` is still a template and will raise
until you implement an LLM provider.
"""

from __future__ import annotations

import argparse
from dotenv import load_dotenv
from pathlib import Path

from ai_researcher.agent_v3_claude.agent import run
from ai_researcher.agent_v3_claude.logging_utils import get_logger

logger = get_logger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Researcher agent v3 (template)")
    parser.add_argument(
        "--goal",
        "-g",
        required=True,
        help="Goal/instruction for the agent (v3 requires a real LLM implementation)",
    )
    parser.add_argument(
        "--max-iters",
        "-i",
        type=int,
        default=10,
        help="Maximum planner/executor/reviewer iterations",
    )
    parser.add_argument(
        "--repo-root",
        "-r",
        type=str,
        default=None,
        help="Working directory for the agent (defaults to current directory)",
    )

    args = parser.parse_args(argv)

    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
    logger.debug(f"Loaded .env file at {Path(__file__).parent / '.env'}")

    state = run(goal=args.goal, max_iters=args.max_iters, repo_root=args.repo_root)

    # Keep output simple and CLI-friendly.
    logger.user(state.get("last_result") or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

