# Getting Started with AI Researcher

Get up and running with autonomous AI agents for software development in under 5 minutes.

## Quick Setup

### 1. Install
```bash
# Clone and install
git clone https://github.com/yourusername/ai-researcher.git
cd ai-researcher
pip install -e .
```

### 2. Set API Key
```bash
export ANTHROPIC_API_KEY="your-anthropic-key-here"
```

### 3. Run Your First Agent
```python
from ai_researcher.agent_v3_claude import run

# Python API
state = run("Run pytest and fix any failing tests", max_iters=10)
print(f"Status: {state['status']}")
```

Or use the CLI:
```bash
ai-researcher-agent-v3 "Create a Flask API with tests"
```

## Basic Usage

### Python API
```python
from ai_researcher.agent_v3_claude import run

# Simple task
state = run("Format code with black", max_iters=5)

# Complex task  
state = run("Add authentication to my Flask app and write tests", max_iters=15)

# Check results
print(f"Completed: {state['status'] == 'success'}")
```

### Command Line Interface
```bash
# Quick commands
ai-researcher-agent-v3 "Run pytest"
ai-researcher-agent-v3 "Create a requirements.txt file"
ai-researcher-agent-v3 "Refactor the database module"
```

## Understanding Agent Output

The agent shows color-coded progress:
- 🟢 **Green** - Progress updates
- 🟣 **Magenta** - Plans and results  
- 🔷 **Blue** - Tool execution
- 🟡 **Yellow** - Warnings
- 🔴 **Red** - Errors

Example:
```
INFO  | Starting: Run pytest
USER  | PLAN: 1. Check structure 2. Run tests 3. Fix failures
TOOL  | Running: pytest
INFO  | Status: SUCCESS
```

## Common Tasks

```python
from ai_researcher.agent_v3_claude import run

# Testing
run("Run pytest and fix failures", max_iters=10)

# Code quality  
run("Format code with black and fix linting", max_iters=5)

# Feature development
run("Add user authentication to the API", max_iters=20)

# Documentation
run("Generate README and API docs", max_iters=10)

# Debugging
run("Find and fix the memory leak in the server", max_iters=15)
```

## Quick Troubleshooting

**No API key found?**
```bash
echo $ANTHROPIC_API_KEY  # Should show your key
export ANTHROPIC_API_KEY="your-key-here"
```

**Agent not finding files?**
```bash
pwd  # Check you're in the right directory
cd /path/to/your/project
```

**Need more iterations?**
```python
state = run("complex task", max_iters=20)  # Increase limit
```

## Next Steps

- 📖 [Architecture Guide](agent_v3_claude/ARCHITECTURE.md) - How the agent works
- 🛠️ [Available Tools](agent_v3_claude/README.md) - Full tool reference  
- 🔧 [Advanced Configuration](ADVANCED.md) - Custom settings and integrations
- 🧪 **Try it**: `pytest tests/` to run the test suite

## Need Help?

- 📋 **Issues**: Open an issue on GitHub
- 💬 **Discussions**: Join GitHub Discussions  
- 📚 **Docs**: Browse the [docs/](.) directory

Happy coding! 🚀
