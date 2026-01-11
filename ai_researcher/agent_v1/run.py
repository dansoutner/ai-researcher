import os

def main(argv: list[str] | None = None) -> int:
    # Import optional CLI niceties lazily to avoid breaking imports if extras aren't installed.
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        load_dotenv = None

    try:
        from rich import print as rich_print  # type: ignore
    except Exception:
        rich_print = print

    from agent_v1.agent import build_graph

    if load_dotenv:
        load_dotenv()

    goal = os.getenv("GOAL") or input("What should I do?\n> ").strip()

    # repo_root can be blank; agent can call create_project
    repo_root = os.getenv("REPO_ROOT", "")

    app = build_graph()

    while True:
        state = {"goal": goal, "repo_root": repo_root, "messages": [], "done": False}

        for event in app.stream(state, stream_mode="values"):
            msgs = event.get("messages", [])
            if msgs and msgs[-1]["type"] == "assistant":
                rich_print("\n[bold cyan]Assistant:[/bold cyan]" if rich_print is not print else "\nAssistant:")
                rich_print(msgs[-1]["content"])

            if msgs and msgs[-1]["type"] == "tool":
                rich_print("\n[bold yellow]Tool output:[/bold yellow]" if rich_print is not print else "\nTool output:")
                rich_print(msgs[-1]["content"])

            # Update repo_root if it was set during execution
            if event.get("repo_root"):
                repo_root = event["repo_root"]

        # After stream completes, ask for next steps
        next_goal = input("\nWhat should I do next? (or 'quit' to exit)\n> ").strip()
        if next_goal.lower() in ("quit", "exit", "q"):
            break
        goal = next_goal

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
