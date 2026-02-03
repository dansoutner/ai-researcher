# AI Researcher

> **Production-ready autonomous AI agents for software development tasks**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An autonomous AI agent system that can plan, execute, and self-correct to accomplish complex software development tasks. Built with LangGraph and Claude, featuring a modular planner-executor-reviewer architecture.

## ✨ Key Features

- 🤖 **Autonomous Execution** - Self-correcting workflow with automatic error recovery
- 🛠️ **26+ Built-in Tools** - File system, Git, pytest, virtual environments, and more
- 🔄 **Planner-Executor-Reviewer** - Proven architecture for reliable task completion
- 🎨 **Colored Logging** - Professional, color-coded output for easy debugging
- 🔌 **MCP Integration** - Extensible via Model Context Protocol servers
- 📦 **Production Ready** - Type-safe, tested, and modular design

## 🚀 Quick Start

### Installation

```bash
# Install with pip
pip install -e .

# Or with uv (recommended)
uv venv && source .venv/bin/activate && uv sync
```

### Set API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Run Your First Agent

**Python API:**
```python
from ai_researcher.agent_v3_claude import run

state = run("Run pytest and fix any failing tests", max_iters=10)
print(f"Status: {state['status']}")
```

**Command Line:**
```bash
ai-researcher-agent-v3 "Create a Flask API with tests"
```

## 📖 Documentation

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Detailed setup and usage
- **[Agent v3 Architecture](docs/ARCHITECTURE.md)** - How the agent works
- **[Available Tools](docs/TOOLS.md)** - Complete tool reference
- **[MCP Integration](docs/MCP_INTEGRATION.md)** - Extending with MCP servers
- **[API Reference](docs/API_REFERENCE.md)** - Python API documentation

## 🏗️ Architecture

```
┌─────────┐
│ Planner │ → Creates step-by-step execution plan
└────┬────┘
     ↓
┌──────────┐
│ Executor │ → Executes steps using tools
└────┬─────┘
     ↓
┌──────────┐
│ Reviewer │ → Evaluates progress, decides next action
└────┬─────┘
     ↓
  continue / retry / replan / finish
```

**Key Design Principles:**
- Structured outputs for reliable parsing
- Automatic replanning on failures
- Context window management for large outputs
- Modular, testable components

## 🛠️ Available Tools

### File System
`read_file`, `write_file`, `list_files`, `grep`, `edit_file`

### Git Operations
`git_status`, `git_diff`, `git_add`, `git_commit`, `git_log`, `git_branch_list`, `git_checkout`

### Testing & Commands
`run_pytest`, `run_cmd`, `run_terminal_command`, `get_errors`

### Virtual Environments
`create_venv`, `run_in_venv`

### Memory (Persistence)
`memory_set`, `memory_get`, `memory_list`, `memory_delete`

[Full tool documentation →](docs/TOOLS.md)

## 📊 Example Use Cases

- 🐛 Debug and fix failing tests
- 📦 Create Python packages with proper structure
- 🔄 Refactor code across multiple files
- 🧪 Generate and run test suites
- 📝 Analyze and document codebases
- 🔍 Search and analyze research papers (via arXiv MCP)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_researcher --cov-report=html

# Run specific test suite
pytest tests/agent_v3/
```

## 📋 Requirements

- **Python:** 3.10 or higher
- **API Keys:** 
  - `ANTHROPIC_API_KEY` (for Claude - recommended)
  - `OPENAI_API_KEY` (alternative LLM provider)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Project Structure

```
ai-researcher/
├── ai_researcher/
│   ├── agent_v3_claude/      # Main agent implementation
│   ├── ai_researcher_tools/  # Reusable tool library
│   └── mcp_integration/      # MCP server integration
├── tests/                     # Comprehensive test suite
└── docs/                      # Documentation
```

---

**Ready to get started?** Check out the [Getting Started Guide](docs/GETTING_STARTED.md) or jump straight to the [API Reference](docs/API_REFERENCE.md).

### Memory & Persistence
- Key-value storage across execution steps
- Repository maps and test result caching

## Documentation

### Architecture & Design
- [Agent v3 Architecture](agent_v3_claude/README.md) - Detailed architecture guide
- [Refactoring Summary](agent_v3_claude/REFACTORING_SUMMARY.md) - Evolution from monolith to modules

### Feature Documentation
- [Quick Reference](QUICK_REFERENCE.md) - Fast lookup for executor structured output
- [Executor Output](EXECUTOR_OUTPUT_SUMMARY.md) - Structured status implementation
- [Routing Logic](ROUTING_FIX_SUMMARY.md) - Workflow routing details
- [Tools Integration](AGENT_V3_TOOLS_INTEGRATION.md) - Tool system overview

### Diagrams
- [Executor Workflow](EXECUTOR_WORKFLOW_DIAGRAM.md) - Visual workflow comparison

## MCP Servers

### arXiv MCP Server
**Location:** `mcp_servers/arxiv-mcp-server/`

Model Context Protocol server for searching and retrieving academic papers from arXiv.org.

📖 [Setup instructions](mcp_servers/arxiv-mcp-server/README.md)

## Testing

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/test_agent_v3_pruning.py
pytest tests/test_git_tools.py
pytest tests/test_python_tools.py
```

## Contributing

This is a research project exploring autonomous agent architectures. Feel free to experiment and extend!

## License

See individual component licenses.
