# Advanced Configuration

This guide covers advanced usage patterns, custom configurations, and detailed installation options for AI Researcher.

## Advanced Installation

### Using uv (Recommended for Development)

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

### Using pip with Virtual Environment

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

### Install from PyPI (when available)

```bash
pip install ai-researcher
```

## Advanced Configuration

### Multiple API Providers

Configure different LLM providers by editing `ai_researcher/agent_v3_claude/nodes.py`:

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
    
    # For local models via Ollama
    # from langchain_ollama import ChatOllama
    # return ChatOllama(model="llama3.1:8b")
```

### Environment Variables

Make API keys permanent by adding to your shell profile:

```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.bash_profile
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Custom Pruning Configuration

Control context window management for long-running tasks:

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

## Advanced Usage Patterns

### Pattern 1: Iterative Development

Break complex tasks into phases:

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

### Pattern 3: Context-Aware Sessions

```python
# The agent automatically uses memory for persistence
state = run("Analyze the codebase and store findings", max_iters=5)

# Later in a new session:
state = run("Using previous analysis, suggest improvements", max_iters=10)
```

### Pattern 4: Working Directory Management

```python
import os

# Save current directory
original_dir = os.getcwd()

# Work on specific project
os.chdir('/path/to/project')
state = run("Add logging to all API endpoints", max_iters=10)

# Return to original directory
os.chdir(original_dir)
```

## Detailed Output Understanding

The agent provides detailed color-coded logs:

- 🟢 **GREEN (INFO)** - Progress and state changes
- 🟣 **MAGENTA (USER)** - Plans and results for you
- 🔷 **BLUE (TOOL)** - Tool execution details
- 🔵 **CYAN (DEBUG)** - System internals
- 🟡 **YELLOW (WARNING)** - Potential issues
- 🔴 **RED (ERROR)** - Errors and failures

Example detailed output:
```
INFO  | Starting agent run with goal: Run pytest
INFO  | === PLANNER NODE (iteration 0) ===
USER  | ============================================================
USER  | PLAN GENERATED
USER  | ============================================================
USER  | 1. Check current directory structure
USER  | 2. Run pytest to identify failing tests
USER  | 3. Analyze failures and implement fixes
USER  | 4. Re-run tests to verify fixes
USER  | ============================================================
TOOL  | Calling tool: run_pytest
TOOL  | Tool result: 5 passed, 2 failed
INFO  | === REVIEWER NODE ===
INFO  | Reviewer verdict: CONTINUE
```

## Complex Examples

### Example 1: Full Stack Development

```python
from ai_researcher.agent_v3_claude import run

# Complex multi-step development task
state = run(
    goal="""Create a complete REST API for a todo application with:
    1. SQLAlchemy models for users and todos
    2. Flask-JWT authentication
    3. CRUD endpoints for todos
    4. Comprehensive pytest test suite
    5. Requirements.txt and setup instructions""",
    max_iters=25
)

print(f"Final status: {state['status']}")
print(f"Iterations used: {state['current_iter']}")
```

### Example 2: Code Quality Automation

```python
state = run(
    goal="""Improve code quality by:
    1. Running black formatter on all Python files
    2. Adding type hints where missing
    3. Running mypy and fixing type issues
    4. Adding docstrings to public functions
    5. Ensuring test coverage is above 80%""",
    max_iters=20
)
```

### Example 3: Legacy Code Modernization

```python
state = run(
    goal="""Modernize the legacy codebase:
    1. Identify Python 2 patterns and update to Python 3.10+
    2. Replace deprecated libraries with modern alternatives
    3. Add async/await where beneficial
    4. Update tests to use pytest instead of unittest
    5. Add CI/CD configuration""",
    max_iters=30
)
```

## Troubleshooting Guide

### Performance Issues

**Slow execution:**
- Reduce `max_iters` for simpler tasks
- Use more specific goals
- Check if the working directory contains unnecessary files

**Context window issues:**
- Adjust `PruningConfig` settings
- Break large tasks into smaller ones
- Clear unnecessary files from the working directory

### Common Error Patterns

**Import errors:**
```python
# The agent will typically handle these automatically, but you can help by:
# 1. Ensuring dependencies are in requirements.txt
# 2. Using virtual environments
# 3. Providing clear error context in your goal
```

**File permission errors:**
```bash
# Ensure the agent has write permissions
chmod -R 755 /path/to/project
```

**Network connectivity issues:**
```bash
# For tools requiring internet access
# Ensure your firewall allows Python network connections
```

### Advanced Debugging

**Enable debug logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

state = run("your goal", max_iters=10)
```

**Inspect agent state:**
```python
state = run("your goal", max_iters=10)

print("Memory contents:")
for key, value in state.get('memory', {}).items():
    print(f"  {key}: {value}")

print("Messages:")
for msg in state.get('messages', []):
    print(f"  {msg.type}: {msg.content[:100]}...")
```

## Integration with Other Tools

### Git Integration

The agent has built-in Git tools, but you can enhance integration:

```python
# Automated Git workflow
state = run(
    goal="""Implement feature X with proper Git workflow:
    1. Create feature branch
    2. Implement the feature
    3. Add comprehensive tests
    4. Commit changes with descriptive messages
    5. Run final tests before proposing merge""",
    max_iters=15
)
```

### CI/CD Integration

```python
# Generate CI/CD configurations
state = run(
    goal="""Set up CI/CD pipeline:
    1. Create GitHub Actions workflow
    2. Add pytest, black, and mypy checks
    3. Set up coverage reporting
    4. Add deployment configuration
    5. Document the pipeline in README""",
    max_iters=12
)
```

## Performance Optimization

### Efficient Goal Formulation

**Good goals are:**
- Specific and measurable
- Include success criteria
- Reference existing files when relevant

```python
# Good
state = run("Add input validation to the user_api.py register endpoint and write tests", max_iters=8)

# Less optimal
state = run("Make the API better", max_iters=10)
```

### Resource Management

**Monitor resource usage:**
```python
import psutil
import time

start_time = time.time()
initial_memory = psutil.Process().memory_info().rss

state = run("your goal", max_iters=10)

end_time = time.time()
final_memory = psutil.Process().memory_info().rss

print(f"Execution time: {end_time - start_time:.2f} seconds")
print(f"Memory change: {(final_memory - initial_memory) / 1024 / 1024:.2f} MB")
```

## Extending the Agent

### Custom Tool Integration

The agent is designed to be extended. See the [MCP Integration Guide](MCP_INTEGRATION.md) for adding custom tools.

### Custom Workflows

You can create custom workflows by chaining agent runs:

```python
def custom_development_workflow(feature_description):
    """Custom workflow for feature development."""
    
    # Phase 1: Planning
    planning_state = run(f"Analyze requirements for: {feature_description}", max_iters=5)
    
    # Phase 2: Implementation
    impl_state = run(f"Implement: {feature_description}", max_iters=15)
    
    # Phase 3: Testing
    test_state = run(f"Write comprehensive tests for the implemented feature", max_iters=10)
    
    # Phase 4: Documentation
    docs_state = run(f"Document the new feature in README and add docstrings", max_iters=5)
    
    return {
        'planning': planning_state,
        'implementation': impl_state,
        'testing': test_state,
        'documentation': docs_state
    }

# Usage
results = custom_development_workflow("user authentication with JWT tokens")
```

This advanced guide should help you get the most out of AI Researcher for complex development tasks.
