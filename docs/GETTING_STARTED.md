# Getting Started with AI Researcher

This guide will help you set up and start using AI Researcher agents for your development tasks.

## Prerequisites

- Python 3.10 or higher
- An Anthropic API key (for Claude) or OpenAI API key
- Git (for version control features)

## Installation

### Option 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/ai-researcher.git
cd ai-researcher

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-researcher.git
cd ai-researcher

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

### Option 3: Install from PyPI (when available)

```bash
pip install ai-researcher
```

## Configuration

### Set Up API Keys

The agent requires an LLM API key. Set it as an environment variable:

**For Claude (recommended):**
```bash
export ANTHROPIC_API_KEY="your-anthropic-key-here"
```

**For OpenAI:**
```bash
export OPENAI_API_KEY="your-openai-key-here"
```

**Make it permanent** (add to your `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`):
```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Configure LLM Provider (Optional)

By default, the agent uses Claude. To use a different model, edit `ai_researcher/agent_v3_claude/nodes.py`:

```python
def require_llm() -> BaseChatModel:
    """Configure your LLM provider."""
    # For Claude (default)
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model="claude-3-5-sonnet-latest",
        temperature=0
    )
    
    # For OpenAI
    # from langchain_openai import ChatOpenAI
    # return ChatOpenAI(model="gpt-4o", temperature=0)
```

## Quick Start Examples

### Example 1: Run Tests and Fix Failures

```python
from ai_researcher.agent_v3_claude import run

state = run(
    goal="Run pytest and fix any failing tests",
    max_iters=10
)

print(f"Final status: {state['status']}")
print(f"Iterations: {state['current_iter']}")
```

### Example 2: Create a Python Package

```python
from ai_researcher.agent_v3_claude import run, print_results

state = run(
    goal="Create a Python package called 'my_utils' with a function to parse dates and comprehensive tests",
    max_iters=15
)

print_results(state)
```

### Example 3: Using the CLI

```bash
# Simple task
ai-researcher-agent-v3 "Run black formatter on all Python files"

# Complex task
ai-researcher-agent-v3 "Analyze test_*.py files, identify untested functions, and add missing tests"
```

### Example 4: Custom Configuration

```python
from ai_researcher.agent_v3_claude import run, PruningConfig

# Configure context window management
pruning_cfg = PruningConfig(
    keep_last_messages=30,      # Keep more recent messages
    tool_max_chars=10000,       # Allow larger tool outputs
    tool_head_chars=2500,       # Show more of output beginning
    tool_tail_chars=1500,       # Show more of output end
)

state = run(
    goal="Refactor the API module to use async/await",
    max_iters=20,
    pruning_cfg=pruning_cfg,
)
```

## Understanding the Output

The agent provides color-coded logs:

- 🟢 **GREEN (INFO)** - Progress and state changes
- 🟣 **MAGENTA (USER)** - Plans and results for you
- 🔷 **BLUE (TOOL)** - Tool execution details
- 🔵 **CYAN (DEBUG)** - System internals
- 🟡 **YELLOW (WARNING)** - Potential issues
- 🔴 **RED (ERROR)** - Errors and failures

Example output:
```
INFO  | Starting agent run with goal: Run pytest
INFO  | === PLANNER NODE (iteration 0) ===
USER  | ============================================================
USER  | PLAN GENERATED
USER  | ============================================================
USER  | 1. Check current directory structure
USER  | 2. Run pytest
USER  | 3. Analyze failures
USER  | ============================================================
TOOL  | Calling tool: run_pytest
TOOL  | Tool result: 5 passed, 2 failed
INFO  | === REVIEWER NODE ===
INFO  | Reviewer verdict: CONTINUE
```

## Working Directory

The agent operates in the directory where you run it. To work on a specific project:

```bash
cd /path/to/your/project
python -c "from ai_researcher.agent_v3_claude import run; run('your goal', max_iters=10)"
```

Or in Python:

```python
import os
os.chdir('/path/to/your/project')
from ai_researcher.agent_v3_claude import run
state = run('your goal', max_iters=10)
```

## Common Patterns

### Pattern 1: Iterative Development

```python
# Start with a simple task
state = run("Create basic Flask app structure", max_iters=5)

# Then expand
state = run("Add authentication to the Flask app", max_iters=10)

# Then test
state = run("Write comprehensive tests for the Flask app", max_iters=10)
```

### Pattern 2: Error Recovery

The agent automatically recovers from errors:

```python
state = run("Refactor code and ensure all tests pass", max_iters=15)

# The agent will:
# 1. Attempt refactoring
# 2. Run tests
# 3. If tests fail, analyze and fix
# 4. Repeat until success or max iterations
```

### Pattern 3: Using Memory for Context

```python
# The agent automatically uses memory for persistence
# You can check what's stored:

state = run("Analyze the codebase and store findings", max_iters=5)

# Later in a new session:
state = run("Using previous analysis, suggest improvements", max_iters=10)
```

## Troubleshooting

### Issue: "No API key found"

**Solution:** Ensure your API key is set as an environment variable:
```bash
echo $ANTHROPIC_API_KEY  # Should show your key
```

### Issue: "Tool execution timeout"

**Solution:** Some commands take longer. The agent has built-in timeouts, but you can increase iteration limits:
```python
state = run(goal="...", max_iters=20)  # Instead of default 10
```

### Issue: "Agent keeps retrying same approach"

**Solution:** This can happen if the goal is unclear. Try:
1. Make the goal more specific
2. Break it into smaller tasks
3. Check if the necessary files/dependencies exist

### Issue: Agent can't find files

**Solution:** Ensure you're in the correct working directory:
```python
import os
print(os.getcwd())  # Check current directory
os.chdir('/path/to/project')  # Change if needed
```

## Next Steps

- 📖 Read the [Architecture Guide](ARCHITECTURE.md) to understand how the agent works
- 🛠️ Explore [Available Tools](TOOLS.md) to see what the agent can do
- 🔌 Learn about [MCP Integration](MCP_INTEGRATION.md) to extend capabilities
- 📚 Check the [API Reference](API_REFERENCE.md) for detailed API documentation
- 🧪 Run the test suite: `pytest tests/`

## Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Join GitHub Discussions
- **Documentation**: Check the [docs/](.) directory

Happy researching! 🚀
