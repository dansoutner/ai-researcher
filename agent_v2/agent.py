#!/usr/bin/env python3
"""
Together Data Science Agent CLI

A ReAct (Reasoning + Acting) based data science agent powered by Together AI.

Usage:
    python data_science_agent.py --query "Your data science task" [--data-dir ./data]
"""

import os
import re
import json
import textwrap
import base64
import argparse
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple

from together import Together

try:
    from IPython.display import Image, display  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore
    display = None  # type: ignore

from agent_v2.tooling import (
    ToolCall,
    build_tool_registry,
    available_tools_markdown,
    invoke_tool,
)

# =============================================================================
# Configuration
# =============================================================================

REASONING_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
MAX_ITERATIONS = 15
TEMPERATURE = 0.2
SESSION_TIMEOUT = 3600
MAX_OUTPUT_LENGTH = 500
SHOW_IMAGES = True
BOX_WIDTH = 80


# =============================================================================
# Code Execution
# =============================================================================

def run_python(
        code: str,
        code_interpreter,
        session_id: Optional[str] = None,
        files: Optional[List[Dict[str, str]]] = None
) -> Dict:
    """
    Execute Python code using Together Code Interpreter.

    Args:
        code: Python code to execute
        code_interpreter: Together code interpreter client
        session_id: Optional session ID for state persistence
        files: Optional list of files to upload

    Returns:
        Execution result dictionary
    """
    try:
        kwargs = {"code": code, "language": "python"}

        if session_id:
            kwargs["session_id"] = session_id

        if files:
            kwargs["files"] = files

        response = code_interpreter.run(**kwargs)

        result = {
            "session_id": response.data.session_id,
            "status": response.data.status,
            "outputs": []
        }

        for output in response.data.outputs:
            result["outputs"].append({"type": output.type, "data": output.data})

        if response.data.errors:
            result["errors"] = response.data.errors

        return result
    except Exception as e:
        return {"status": "error", "error_message": str(e), "session_id": None}


# =============================================================================
# File Management
# =============================================================================

def collect_files(directory: str) -> List[Dict[str, str]]:
    """
    Collect all files from a directory for upload to code interpreter.

    Args:
        directory: Directory path to scan

    Returns:
        List of file dictionaries with name, encoding, and content
    """
    files = []
    path = Path(directory)

    if not path.exists():
        print(f"Directory '{directory}' does not exist, skipping file collection")
        return files

    for file_path in path.rglob("*"):
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
            try:
                if file_path.suffix.lower() in ['.csv', '.txt', '.json', '.py']:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    files.append({
                        "name": str(file_path.relative_to(directory)),
                        "encoding": "string",
                        "content": content
                    })
                elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                    print(f"Excel file detected: {file_path.name} - will be handled by pandas")
            except (UnicodeDecodeError, PermissionError) as e:
                print(f"Could not read file {file_path}: {e}")

    return files


# =============================================================================
# Output Processing
# =============================================================================

def display_image(b64_image: str):
    """Display base64 encoded image (best-effort).

    In pure CLI environments, IPython may not be installed; in that case, we
    just print a placeholder message.
    """
    if Image is None or display is None:
        print("[Image generated but cannot be displayed (IPython not available)]")
        return

    try:
        decoded_image = base64.b64decode(b64_image)
        display(Image(data=decoded_image))
    except Exception:
        print("[Image generated but cannot be displayed in CLI mode]")


def get_execution_summary(execution_result: Dict) -> str:
    """Create a summary of execution result for the model's history."""
    if not execution_result:
        return "Execution failed - no result returned"

    status = execution_result.get("status", "unknown")
    summary_parts = [f"Execution status: {status}"]

    stdout_outputs = []
    display_outputs = []
    other_outputs = []

    if "outputs" in execution_result:
        for output in execution_result["outputs"]:
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

    if "errors" in execution_result and execution_result["errors"]:
        summary_parts.append("Errors:")
        summary_parts.extend(execution_result["errors"])

    if not stdout_outputs and not display_outputs and not other_outputs and status == "success":
        summary_parts.append("Code executed successfully (no explicit output generated)")

    return "\n".join(summary_parts)


def process_execution_result(execution_result: Dict) -> tuple:
    """Extract text outputs and image data from execution result."""
    text_outputs = []
    image_data = []

    if execution_result and "outputs" in execution_result:
        for output in execution_result["outputs"]:
            if output["type"] == "stdout":
                text_outputs.append(output["data"])
            elif output["type"] == "display_data":
                if isinstance(output["data"], dict):
                    if "image/png" in output["data"]:
                        image_data.append(output["data"]["image/png"])
                    if "text/plain" in output["data"]:
                        text_outputs.append(f"[Display Data] {output['data']['text/plain']}")

    combined_text = "\n".join(text_outputs) if text_outputs else ""
    return combined_text, image_data


# =============================================================================
# Pretty Printing
# =============================================================================

def box_text(text: str, title: Optional[str] = None, emoji: Optional[str] = None) -> str:
    """Create boxed text with optional title and emoji."""
    if not text:
        text = "No output"

    words = text.split()
    if len(words) > MAX_OUTPUT_LENGTH:
        words = words[:MAX_OUTPUT_LENGTH]
        words.append("...")
        text = " ".join(words)

    wrapped_lines = []
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

    result = []
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


def print_boxed(text: str, title: Optional[str] = None, emoji: Optional[str] = None):
    """Print text in a box."""
    print(box_text(text, title, emoji))


def print_boxed_execution_result(
        execution_result: Dict,
        title: Optional[str] = None,
        emoji: Optional[str] = None
):
    """Print execution result in a box and display any images."""
    text_output, image_data = process_execution_result(execution_result)

    if image_data:
        if text_output:
            text_output += f"\n\n[Generated {len(image_data)} plot(s)/image(s)]"
        else:
            text_output = f"[Generated {len(image_data)} plot(s)/image(s)]"
    elif not text_output:
        text_output = "No text output"

    print(box_text(text_output, title, emoji))

    if SHOW_IMAGES:
        for i, img_data in enumerate(image_data):
            if len(image_data) > 1:
                print(f"\n--- Plot/Image {i + 1} ---")
            display_image(img_data)


# =============================================================================
# ReAct Agent
# =============================================================================

class ReActDataScienceAgent:
    """ReAct-based Data Science Agent."""

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

    NEW: You also have access to repository tools from agent_tools.py.

    WAIT FOR THE RESULT OF THE ACTION BEFORE PROCEEDING.

    You must strictly adhere to ONE of these formats:

    ## Format 1 - Run Python code (code interpreter)

    Thought: Reflect on what to do next. Analyze results from previous steps.

    Action Input:
    ```python
    <python code to run>
    ```

    ## Format 2 - Call a repository tool (preferred for git/files/tests)

    Thought: Reflect on what to do next. Analyze results from previous steps.

    Tool Input:
    ```json
    {"name": "tool_name", "arguments": {"repo_root": ".", "other": "args"}}
    ```

    Notes:
    - If you omit repo_root, it will default to the current working directory.
    - Tool output will be returned to you as the Observation.

    ## Format 3 - ONLY when you have completely finished the task:

    Thought: Reflect on the complete process and summarize what was accomplished.

    Final Answer:
    [Provide a comprehensive summary of the analysis, key findings, and any recommendations]
    """

    def __init__(
            self,
            client: Together,
            session_id: Optional[str] = None,
            model: str = REASONING_MODEL,
            max_iterations: int = MAX_ITERATIONS,
            repo_root: Optional[str] = None,
    ):
        self.client = client
        self.code_interpreter = client.code_interpreter
        self.session_id = session_id
        self.model = model
        self.max_iterations = max_iterations

        self.repo_root = repo_root or os.getcwd()
        self.tools = build_tool_registry()

        system_prompt = self.SYSTEM_PROMPT.strip() + "\n\n" + available_tools_markdown(self.tools)
        self.history = [{"role": "system", "content": system_prompt}]

    def llm_call(self) -> str:
        """Make a call to the language model."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=TEMPERATURE,
            stream=False
        )
        return response.choices[0].message.content

    def parse_response(self) -> Tuple[str, Optional[str], Optional[ToolCall]]:
        """Parse the LLM response.

        Returns:
            (thought_or_final, python_code_or_none, tool_call_or_none)

        Exactly one of python_code_or_none and tool_call_or_none will be non-None,
        unless this is a final answer.
        """
        response = self.llm_call()

        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[1].strip()
            return final_answer, None, None

        # Tool call path
        if "Thought:" in response and "Tool Input:" in response:
            thought = response.split("Thought:")[1].split("Tool Input:")[0].strip()
            json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON code block found for Tool Input")
            payload = json.loads(json_match.group(1).strip())
            name = payload.get("name")
            arguments = payload.get("arguments", {})
            if not isinstance(name, str) or not name:
                raise ValueError("Tool Input JSON must include non-empty 'name'")
            if not isinstance(arguments, dict):
                raise ValueError("Tool Input JSON 'arguments' must be an object")
            return thought, None, ToolCall(name=name, arguments=arguments)

        # Python action path (existing)
        if "Thought:" in response and "Action Input:" in response:
            thought = response.split("Thought:")[1].split("Action Input:")[0].strip()
            code_match = re.search(r"```(?:python)?\s*(.*?)\s*```", response, re.DOTALL)
            if code_match:
                action_input = code_match.group(1).strip()
            else:
                raise ValueError("No code block found in the response")
            return thought, action_input, None

        thought = "The assistant didn't follow the ReAct format properly."
        action_input = "print('Error: Format not followed by the assistant')"
        return thought, action_input, None

    def run(self, user_input: str) -> str:
        """Execute the main ReAct reasoning and acting loop."""
        self.history.append({"role": "user", "content": user_input})

        current_iteration = 0

        # Keep output ASCII-friendly by default; some terminals can't render emoji.
        print("Starting ReAct Data Science Agent")
        print(f"Task: {user_input}")
        print("=" * 80)

        while current_iteration < self.max_iterations:
            try:
                result, python_code, tool_call = self.parse_response()

                # Final answer
                if python_code is None and tool_call is None:
                    print_boxed(result, "Final Answer")
                    return result

                thought = result
                print_boxed(thought, f"Thought (Iteration {current_iteration + 1})")

                if tool_call is not None:
                    print_boxed(json.dumps({"name": tool_call.name, "arguments": tool_call.arguments}, indent=2), "Tool")
                    tool_output = invoke_tool(self.tools, tool_call, default_repo_root=self.repo_root)

                    # Tools return plain text; treat it as the Observation.
                    print_boxed(tool_output, "Result")

                    add_to_history = (
                        f"Thought: {thought}\n"
                        f"Tool Input:```json\n{json.dumps({'name': tool_call.name, 'arguments': tool_call.arguments})}\n```"
                    )
                    self.history.append({"role": "assistant", "content": add_to_history})
                    self.history.append({"role": "user", "content": f"Observation: {tool_output}"})

                else:
                    # Python code path
                    action_input = python_code or ""
                    print_boxed(action_input, "Action")

                    execution_result = run_python(
                        action_input,
                        self.code_interpreter,
                        self.session_id
                    )

                    if execution_result and "session_id" in execution_result:
                        self.session_id = execution_result["session_id"]

                    print_boxed_execution_result(execution_result, "Result")

                    execution_summary = get_execution_summary(execution_result)

                    add_to_history = f"Thought: {thought}\nAction Input:```python\n{action_input}\n```"
                    self.history.append({"role": "assistant", "content": add_to_history})
                    self.history.append({"role": "user", "content": f"Observation: {execution_summary}"})

                current_iteration += 1
                print("-" * 80)

            except Exception as e:
                print(f"Error in iteration {current_iteration + 1}: {str(e)}")
                self.history.append({
                    "role": "user",
                    "content": f"Error occurred: {str(e)}. Please try a different approach."
                })
                current_iteration += 1

        print(f"Maximum iterations ({self.max_iterations}) reached without completion")
        return "Task incomplete - maximum iterations reached"


# =============================================================================
# Agent Factory Functions
# =============================================================================

def create_agent_with_data(
        client: Together,
        data_dir: Optional[str] = None,
        repo_root: Optional[str] = None,
) -> ReActDataScienceAgent:
    """Create a ReAct agent with optional data file upload."""
    session_id = None

    if data_dir and os.path.exists(data_dir):
        print(f"📁 Collecting files from {data_dir}...")
        files = collect_files(data_dir)

        if files:
            print(f"📤 Found {len(files)} files. Initializing session...")
            init_result = run_python(
                "print('Session initialized with data files')",
                client.code_interpreter,
                None,
                files
            )

            if init_result and "session_id" in init_result:
                session_id = init_result["session_id"]
                print(f"✅ Session initialized with ID: {session_id}")
            else:
                print("⚠️ Failed to get session ID")
        else:
            print("📂 No valid files found in directory")

    return ReActDataScienceAgent(client=client, session_id=session_id, repo_root=repo_root)


def run_data_science_task(
        query: str,
        api_key: str,
        data_dir: Optional[str] = None,
        repo_root: Optional[str] = None,
) -> str:
    """Run a complete data science task."""
    client = Together(api_key=api_key)
    agent = create_agent_with_data(client, data_dir, repo_root=repo_root)
    return agent.run(query)


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Together Data Science Agent - A ReAct-based data science assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "Load the iris dataset and create a scatter plot"
  %(prog)s --query "Perform EDA on data.csv" --data-dir ./data
  %(prog)s --query "Build a classification model" --model meta-llama/Llama-3.3-70B-Instruct-Turbo
        """
    )

    parser.add_argument(
        "--query", "-q",
        type=str,
        required=True,
        help="The data science task to perform"
    )

    parser.add_argument(
        "--data-dir", "-d",
        type=str,
        default=None,
        help="Directory containing data files to upload"
    )

    parser.add_argument(
        "--api-key", "-k",
        type=str,
        default=os.environ.get("TOGETHER_API_KEY"),
        help="Together AI API key (default: TOGETHER_API_KEY env var)"
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        default=REASONING_MODEL,
        help=f"Model to use for reasoning (default: {REASONING_MODEL})"
    )

    parser.add_argument(
        "--max-iterations", "-i",
        type=int,
        default=MAX_ITERATIONS,
        help=f"Maximum number of reasoning iterations (default: {MAX_ITERATIONS})"
    )

    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Disable image display attempts"
    )

    parser.add_argument(
        "--repo-root",
        type=str,
        default=os.getcwd(),
        help="Repository root for repo tools (default: current working directory)"
    )

    args = parser.parse_args()

    if not args.api_key:
        parser.error(
            "API key required. Set TOGETHER_API_KEY environment variable "
            "or use --api-key flag."
        )

    global REASONING_MODEL, MAX_ITERATIONS, SHOW_IMAGES
    REASONING_MODEL = args.model
    MAX_ITERATIONS = args.max_iterations
    SHOW_IMAGES = not args.no_images

    print("=" * 80)
    print("🔬 Together Data Science Agent")
    print("=" * 80)
    print(f"Model: {args.model}")
    print(f"Max iterations: {args.max_iterations}")
    if args.data_dir:
        print(f"Data directory: {args.data_dir}")
    print()

    result = run_data_science_task(
        query=args.query,
        api_key=args.api_key,
        data_dir=args.data_dir,
        repo_root=args.repo_root,
    )

    print("\n" + "=" * 80)
    print("✅ Task completed")
    print("=" * 80)


if __name__ == "__main__":
    main()
