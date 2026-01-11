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

    args = parser.parse_args(argv)

    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
    print(f"Loaded .env file at {Path(__file__).parent / '.env'}")

    state = run(goal=args.goal, max_iters=args.max_iters)

    # Keep output simple and CLI-friendly.
    print(state.get("last_result") or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

