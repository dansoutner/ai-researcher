#!/usr/bin/env python3
"""LangGraph rewrite of the Together ReAct Data Science Agent.

Keeps the same behavior as `agent_v2/agent.py` (boxed CLI, iterative ReAct loop,
Together code interpreter execution + optional data-dir upload), but expresses the
reason/act loop as a LangGraph state machine.

Run:
  python -m agent_v2.langgraph_agent --query "..." --api-key $TOGETHER_API_KEY

Or, if installed via pyproject entrypoint:
  ai-researcher-agent-v2 --query "..."
"""

from __future__ import annotations

import argparse
import base64
import os
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict

from together import Together

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph


# =============================================================================
# Configuration (kept compatible with the original file)
# =============================================================================

REASONING_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
MAX_ITERATIONS = 15
TEMPERATURE = 0.2
MAX_OUTPUT_LENGTH = 500
SHOW_IMAGES = True
BOX_WIDTH = 80


# =============================================================================
# Together helpers (ported from original)
# =============================================================================

def run_python(
    *,
    code: str,
    code_interpreter: Any,
    session_id: Optional[str] = None,
    files: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Execute Python code using Together Code Interpreter."""
    try:
        kwargs: Dict[str, Any] = {"code": code, "language": "python"}
        if session_id:
            kwargs["session_id"] = session_id
        if files:
            kwargs["files"] = files

        response = code_interpreter.run(**kwargs)
        result: Dict[str, Any] = {
            "session_id": response.data.session_id,
            "status": response.data.status,
            "outputs": [],
        }

        for output in response.data.outputs:
            result["outputs"].append({"type": output.type, "data": output.data})

        if response.data.errors:
            result["errors"] = response.data.errors

        return result
    except Exception as e:
        return {"status": "error", "error_message": str(e), "session_id": None}


def collect_files(directory: str) -> List[Dict[str, str]]:
    """Collect files from a directory for upload to Together code interpreter."""
    files: List[Dict[str, str]] = []
    path = Path(directory)

    if not path.exists():
        print(f"Directory '{directory}' does not exist, skipping file collection")
        return files

    for file_path in path.rglob("*"):
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
            try:
                if file_path.suffix.lower() in [".csv", ".txt", ".json", ".py"]:
                    content = file_path.read_text(encoding="utf-8")
                    files.append(
                        {
                            "name": str(file_path.relative_to(directory)),
                            "encoding": "string",
                            "content": content,
                        }
                    )
                elif file_path.suffix.lower() in [".xlsx", ".xls"]:
                    print(f"Excel file detected: {file_path.name} - will be handled by pandas")
            except (UnicodeDecodeError, PermissionError) as e:
                print(f"Could not read file {file_path}: {e}")

    return files


# =============================================================================
# Output processing + printing (ported from original)
# =============================================================================

def _maybe_display_image(b64_image: str) -> None:
    """Best-effort display of base64 images (works in notebooks)."""
    try:
        # Optional dependency: IPython is not guaranteed in CLI environments.
        from IPython.display import Image, display  # type: ignore

        decoded = base64.b64decode(b64_image)
        display(Image(data=decoded))
    except Exception:
        print("[Image generated but cannot be displayed in this environment]")


def get_execution_summary(execution_result: Dict[str, Any]) -> str:
    if not execution_result:
        return "Execution failed - no result returned"

    status = execution_result.get("status", "unknown")
    summary_parts = [f"Execution status: {status}"]

    stdout_outputs: List[str] = []
    display_outputs: List[str] = []
    other_outputs: List[str] = []

    for output in execution_result.get("outputs", []) or []:
        output_type = output.get("type", "unknown")
        output_data = output.get("data", "")

        if output_type == "stdout":
            stdout_outputs.append(output_data)
        elif output_type == "display_data":
            if isinstance(output_data, dict):
                if "image/png" in output_data:
                    display_outputs.append("Generated plot/image")
                if "text/plain" in output_data:
                    display_outputs.append(f"Display: {output_data['text/plain']}")
            else:
                display_outputs.append("Generated display output")
        else:
            other_outputs.append(f"{output_type}: {str(output_data)[:100]}")

    if stdout_outputs:
        summary_parts.append("Text output:")
        summary_parts.extend(stdout_outputs)

    if display_outputs:
        summary_parts.append("Visual outputs:")
        summary_parts.extend(display_outputs)

    if other_outputs:
        summary_parts.append("Other outputs:")
        summary_parts.extend(other_outputs)

    if execution_result.get("errors"):
        summary_parts.append("Errors:")
        summary_parts.extend(execution_result["errors"])

    if not stdout_outputs and not display_outputs and not other_outputs and status == "success":
        summary_parts.append("Code executed successfully (no explicit output generated)")

    return "\n".join(summary_parts)


def process_execution_result(execution_result: Dict[str, Any]) -> Tuple[str, List[str]]:
    text_outputs: List[str] = []
    image_data: List[str] = []

    for output in execution_result.get("outputs", []) or []:
        if output.get("type") == "stdout":
            text_outputs.append(output.get("data", ""))
        elif output.get("type") == "display_data":
            data = output.get("data")
            if isinstance(data, dict):
                if "image/png" in data:
                    image_data.append(data["image/png"])
                if "text/plain" in data:
                    text_outputs.append(f"[Display Data] {data['text/plain']}")

    return ("\n".join(text_outputs) if text_outputs else ""), image_data


def box_text(text: str, title: Optional[str] = None, emoji: Optional[str] = None) -> str:
    if not text:
        text = "No output"

    words = text.split()
    if len(words) > MAX_OUTPUT_LENGTH:
        words = words[:MAX_OUTPUT_LENGTH] + ["..."]
        text = " ".join(words)

    wrapped_lines: List[str] = []
    for line in text.split("\n"):
        if len(line) > BOX_WIDTH:
            wrapped_lines.extend(textwrap.wrap(line, width=BOX_WIDTH))
        else:
            wrapped_lines.append(line)

    if not wrapped_lines:
        wrapped_lines = ["No output"]

    width = max(len(line) for line in wrapped_lines)
    width = max(width, len(title) if title else 0)

    if title and emoji:
        title = f" {emoji} {title} "
    elif title:
        title = f" {title} "
    elif emoji:
        title = f" {emoji} "

    result: List[str] = []
    if title:
        result.append(f"╔{'═' * (width + 2)}╗")
        result.append(f"║ {title}{' ' * (width - len(title) + 2)}║")
        result.append(f"╠{'═' * (width + 2)}╣")
    else:
        result.append(f"╔{'═' * (width + 2)}╗")

    for line in wrapped_lines:
        result.append(f"║ {line}{' ' * (width - len(line))} ║")

    result.append(f"╚{'═' * (width + 2)}╝")
    return "\n".join(result)


def print_boxed(text: str, title: Optional[str] = None, emoji: Optional[str] = None) -> None:
    print(box_text(text, title, emoji))


def print_boxed_execution_result(
    execution_result: Dict[str, Any],
    title: Optional[str] = None,
    emoji: Optional[str] = None,
) -> None:
    text_output, image_data = process_execution_result(execution_result)

    if image_data:
        text_output = (text_output + "\n\n" if text_output else "") + (
            f"[Generated {len(image_data)} plot(s)/image(s)]"
        )
    elif not text_output:
        text_output = "No text output"

    print(box_text(text_output, title, emoji))

    if SHOW_IMAGES:
        for i, img_data in enumerate(image_data):
            if len(image_data) > 1:
                print(f"\n--- Plot/Image {i + 1} ---")
            _maybe_display_image(img_data)


# =============================================================================
# ReAct parsing (kept compatible with old prompting)
# =============================================================================

def parse_react_response(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Parse the model output.

    Returns (thought, action_code, final_answer).
    Exactly one of `action_code` or `final_answer` should be non-None.
    """
    if "Final Answer:" in text:
        final_answer = text.split("Final Answer:", 1)[1].strip()
        # Thought is optional, but keep it for debugging.
        thought = None
        if "Thought:" in text:
            thought = text.split("Thought:", 1)[1].split("Final Answer:", 1)[0].strip()
        return thought, None, final_answer

    if "Thought:" in text and "Action Input:" in text:
        thought = text.split("Thought:", 1)[1].split("Action Input:", 1)[0].strip()
        code_match = re.search(r"```(?:python)?\s*(.*?)\s*```", text, re.DOTALL)
        if not code_match:
            return thought, "print('Error: No python code block found')", None
        return thought, code_match.group(1).strip(), None

    return None, "print('Error: Format not followed by the assistant')", None


# =============================================================================
# LangGraph state machine
# =============================================================================

SYSTEM_PROMPT = """
You are an expert data scientist assistant that follows the ReAct framework (Reasoning + Acting).

CRITICAL RULES:
1. Execute ONLY ONE action at a time - this is non-negotiable
2. Be methodical and deliberate in your approach
3. Always validate data before advanced analysis
4. Never make assumptions about data structure or content
5. Never execute potentially destructive operations without confirmation

IMPORTANT GUIDELINES:
- Be explorative and creative, but cautious
- Try things incrementally and observe the results
- Never randomly guess (e.g., column names) - always examine data first
- If you don't have data files, use "import os; os.listdir()" to see what's available
- When you see "Code executed successfully" or "Generated plot/image", it means your code worked
- Plots and visualizations are automatically displayed to the user
- Build on previous successful steps rather than starting over

WAIT FOR THE RESULT OF THE ACTION BEFORE PROCEEDING.

You must strictly adhere to this format (you have two options):

## Format 1 - For taking an action:

Thought: Reflect on what to do next. Analyze results from previous steps.

Action Input:
```python
<python code to run>
```

## Format 2 - ONLY when you have completely finished the task:

Thought: Reflect on the complete process and summarize what was accomplished.

Final Answer:
[Provide a comprehensive summary of the analysis, key findings, and any recommendations]
""".strip()


class AgentState(TypedDict, total=False):
    client: Together
    model: str
    max_iterations: int

    session_id: Optional[str]
    iteration: int

    messages: List[BaseMessage]

    # parsed step
    thought: Optional[str]
    action_code: Optional[str]
    final_answer: Optional[str]

    # last execution
    last_execution: Optional[Dict[str, Any]]


def _llm_step(state: AgentState) -> AgentState:
    client = state["client"]
    model = state["model"]

    together_messages: List[Dict[str, str]] = []
    for m in state["messages"]:
        role = "user"
        if isinstance(m, SystemMessage):
            role = "system"
        elif isinstance(m, HumanMessage):
            role = "user"
        elif isinstance(m, AIMessage):
            role = "assistant"
        else:
            role = "assistant"

        together_messages.append({"role": role, "content": str(m.content)})

    resp = client.chat.completions.create(
        model=model,
        messages=together_messages,
        temperature=TEMPERATURE,
        stream=False,
    )
    content = resp.choices[0].message.content

    thought, action_code, final_answer = parse_react_response(content)

    # Save the assistant response and parsed fields.
    state["messages"].append(AIMessage(content=content))
    state["thought"] = thought
    state["action_code"] = action_code
    state["final_answer"] = final_answer
    return state


def _act_step(state: AgentState) -> AgentState:
    action_code = state.get("action_code")

    # If model returned a final answer, don't execute anything.
    if state.get("final_answer"):
        return state

    if not action_code:
        state["iteration"] = state.get("iteration", 0) + 1
        state["messages"].append(
            HumanMessage(content="Observation: No action code found to execute.")
        )
        return state

    print_boxed(state.get("thought") or "", f"Thought (Iteration {state.get('iteration', 0) + 1})", "🤔")
    print_boxed(action_code, "Action", "🛠️")

    execution = run_python(
        code=action_code,
        code_interpreter=state["client"].code_interpreter,
        session_id=state.get("session_id"),
    )

    if execution and execution.get("session_id"):
        state["session_id"] = execution.get("session_id")

    state["last_execution"] = execution

    print_boxed_execution_result(execution, "Result", "📊")

    obs = get_execution_summary(execution)
    state["messages"].append(HumanMessage(content=f"Observation: {obs}"))

    state["iteration"] = state.get("iteration", 0) + 1
    print("-" * 80)
    return state


def _should_continue(state: AgentState) -> str:
    if state.get("final_answer"):
        return END
    if state.get("iteration", 0) >= state.get("max_iterations", MAX_ITERATIONS):
        # Force end; the caller will print a warning.
        return END
    return "llm"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("llm", _llm_step)
    graph.add_node("act", _act_step)

    # Start at llm
    graph.set_entry_point("llm")
    graph.add_edge("llm", "act")
    graph.add_conditional_edges("act", _should_continue, {"llm": "llm", END: END})

    return graph.compile()


# =============================================================================
# Public runner (CLI)
# =============================================================================

def create_client(api_key: str) -> Together:
    return Together(api_key=api_key)


def initialize_session_with_data(client: Together, data_dir: Optional[str]) -> Optional[str]:
    if not data_dir or not os.path.exists(data_dir):
        return None

    print(f"📁 Collecting files from {data_dir}...")
    files = collect_files(data_dir)

    if not files:
        print("📂 No valid files found in directory")
        return None

    print(f"📤 Found {len(files)} files. Initializing session...")
    init_result = run_python(
        code="print('Session initialized with data files')",
        code_interpreter=client.code_interpreter,
        session_id=None,
        files=files,
    )

    sid = init_result.get("session_id") if init_result else None
    if sid:
        print(f"✅ Session initialized with ID: {sid}")
    else:
        print("⚠️ Failed to get session ID")
    return sid


def run_task(*, query: str, api_key: str, data_dir: Optional[str], model: str, max_iterations: int) -> str:
    client = create_client(api_key)
    session_id = initialize_session_with_data(client, data_dir)

    app = build_graph()

    state: AgentState = {
        "client": client,
        "model": model,
        "max_iterations": max_iterations,
        "session_id": session_id,
        "iteration": 0,
        "messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)],
    }

    print("🚀 Starting LangGraph Data Science Agent")
    print(f"📝 Task: {query}")
    print("=" * 80)

    final_state = app.invoke(state)

    if final_state.get("final_answer"):
        print_boxed(final_state["final_answer"], "Final Answer", "🎯")
        return final_state["final_answer"]

    if final_state.get("iteration", 0) >= max_iterations:
        msg = "Task incomplete - maximum iterations reached"
        print_boxed(msg, "Final Answer", "🎯")
        return msg

    msg = "Task incomplete"
    print_boxed(msg, "Final Answer", "🎯")
    return msg


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Together Data Science Agent (LangGraph) - ReAct-based data science assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--query", "-q", type=str, required=True, help="The data science task")
    parser.add_argument("--data-dir", "-d", type=str, default=None, help="Directory of data files")
    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        default=os.environ.get("TOGETHER_API_KEY"),
        help="Together API key (default: TOGETHER_API_KEY env var)",
    )
    parser.add_argument("--model", "-m", type=str, default=REASONING_MODEL, help="Reasoning model")
    parser.add_argument(
        "--max-iterations",
        "-i",
        type=int,
        default=MAX_ITERATIONS,
        help="Maximum reasoning iterations",
    )
    parser.add_argument("--no-images", action="store_true", help="Disable image display")

    args = parser.parse_args()

    if not args.api_key:
        parser.error("API key required. Set TOGETHER_API_KEY or use --api-key.")

    global SHOW_IMAGES
    SHOW_IMAGES = not args.no_images

    print("=" * 80)
    print("🔬 Together Data Science Agent (LangGraph)")
    print("=" * 80)
    print(f"Model: {args.model}")
    print(f"Max iterations: {args.max_iterations}")
    if args.data_dir:
        print(f"Data directory: {args.data_dir}")
    print()

    run_task(
        query=args.query,
        api_key=args.api_key,
        data_dir=args.data_dir,
        model=args.model,
        max_iterations=args.max_iterations,
    )

    print("\n" + "=" * 80)
    print("✅ Task completed")
    print("=" * 80)


if __name__ == "__main__":
    main()

