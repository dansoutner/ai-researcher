import os
from dotenv import load_dotenv
from rich import print

from agent import build_graph

def main():
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
                print("\n[bold cyan]Assistant:[/bold cyan]")
                print(msgs[-1]["content"])

            if msgs and msgs[-1]["type"] == "tool":
                print("\n[bold yellow]Tool output:[/bold yellow]")
                print(msgs[-1]["content"])

            # Update repo_root if it was set during execution
            if event.get("repo_root"):
                repo_root = event["repo_root"]

        # After stream completes, ask for next steps
        next_goal = input("\nWhat should I do next? (or 'quit' to exit)\n> ").strip()
        if next_goal.lower() in ("quit", "exit", "q"):
            break
        goal = next_goal

if __name__ == "__main__":
    main()
