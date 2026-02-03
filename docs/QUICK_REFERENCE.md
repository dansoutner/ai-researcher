# Quick Reference

Fast lookup for common AI Researcher tasks and commands.

## Installation & Setup

```bash
# Install
git clone https://github.com/yourusername/ai-researcher.git
cd ai-researcher && pip install -e .

# Set API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Python API

```python
from ai_researcher.agent_v3_claude import run

# Basic usage
state = run("your task description", max_iters=10)
print(f"Status: {state['status']}")

# Check if successful
success = state['status'] == 'success'
```

## CLI Commands

```bash
# Basic syntax
ai-researcher-agent-v3 "task description"

# Common tasks
ai-researcher-agent-v3 "Run pytest"
ai-researcher-agent-v3 "Format code with black"  
ai-researcher-agent-v3 "Create requirements.txt"
ai-researcher-agent-v3 "Add tests for my functions"
```

## Common Task Examples

### Testing
```python
run("Run pytest and fix any failing tests", max_iters=10)
run("Add missing tests to achieve 80% coverage", max_iters=15)
run("Generate test cases for the user authentication module", max_iters=8)
```

### Code Quality
```python
run("Format all Python files with black", max_iters=5)
run("Fix all linting issues", max_iters=8)
run("Add type hints to public functions", max_iters=10)
run("Add docstrings to all classes and functions", max_iters=12)
```

### Feature Development
```python
run("Add user authentication to the Flask app", max_iters=20)
run("Create a REST API for todo items", max_iters=18)
run("Add database migrations for the new schema", max_iters=10)
```

### Documentation
```python
run("Generate a comprehensive README", max_iters=8)
run("Create API documentation", max_iters=12)
run("Add installation and usage instructions", max_iters=10)
```

### Debugging
```python
run("Fix the memory leak in the server code", max_iters=15)
run("Debug why the tests are failing", max_iters=12)
run("Analyze and fix performance bottlenecks", max_iters=18)
```

## Configuration

### Custom Iterations
```python
# For simple tasks
state = run("format code", max_iters=5)

# For complex tasks  
state = run("refactor entire module", max_iters=25)
```

### Working Directory
```python
import os
os.chdir('/path/to/project')
state = run("your task", max_iters=10)
```

## Output Understanding

- 🟢 **INFO** - Progress updates
- 🟣 **USER** - Plans and results for you
- 🔷 **TOOL** - Tool execution
- 🟡 **WARNING** - Potential issues
- 🔴 **ERROR** - Errors

## Troubleshooting

```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Check working directory
pwd

# Run tests to verify installation
pytest tests/
```

## Status Codes

- `'success'` - Task completed successfully  
- `'failed'` - Task failed after max iterations
- `'running'` - Task still in progress (shouldn't see this in final state)

---

**Need more details?** See [Getting Started](GETTING_STARTED.md) or [Advanced Configuration](ADVANCED.md).

