# AI Researcher

A collection of autonomous AI agent implementations for research and development tasks.

## Overview

This repository contains multiple agent architectures that demonstrate various approaches to building autonomous AI systems capable of:
- Planning and executing multi-step tasks
- Managing code repositories and running tests
- Interacting with file systems and command-line tools
- Self-correcting through structured feedback loops

## Agent Implementations

### Agent v3 Claude (Recommended)
**Location:** `agent_v3_claude/`

A production-ready LangGraph-based agent with a modular planner-executor-reviewer architecture:
- ✅ **Structured Output**: Executor returns typed success/failure status
- ✅ **Automatic Recovery**: Self-healing on failures without manual intervention
- ✅ **26+ Tools**: File system, Git, pytest, virtual environments, memory persistence
- ✅ **Context Management**: Intelligent message pruning for large outputs
- ✅ **Modular Design**: Clean separation of concerns across 9 modules

**Quick Start:**
```python
from ai_researcher import run_v3

state = run_v3("Run pytest and fix any failing tests", max_iters=10)
print(f"Final status: {state['status']}")
```

Or use the CLI:
```bash
ai-researcher-agent-v3 "Your task here"
```

📖 [Read the full documentation](docs/agent_v3_claude/README.md)

### Agent v2 (LangGraph + Together)
**Location:** `agent_v2/`

LangGraph implementation integrated with Together AI's code interpreter:
```bash
# Run as module
python -m ai_researcher.agent_v2.langgraph_agent --query "Your task here"

# Or use installed script
ai-researcher-agent-v2 --query "Your task here"
```

**Common Options:**
- `--data-dir ./data` - Upload local files to code interpreter
- `--model <model-name>` - Specify Together AI model
- `--max-iterations 15` - Set iteration limit

### Agent v1 (Legacy)
**Location:** `agent_v1/`

Original proof-of-concept implementation.

## Requirements

- **Python:** 3.10+
- **API Keys:**
  - `ANTHROPIC_API_KEY` (for Agent v3 with Claude)
  - `TOGETHER_API_KEY` (for Agent v2)
  - `OPENAI_API_KEY` (optional, for Agent v3 with OpenAI)

## Installation

### Using uv (Recommended)
```bash
brew install uv  # macOS
uv venv
source .venv/bin/activate
uv sync
```

### Using pip
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Project Structure

```
ai-researcher/
├── ai_researcher/             # Main Python package
│   ├── agent_v1/             # Legacy proof-of-concept
│   ├── agent_v2/             # LangGraph + Together AI
│   ├── agent_v3_claude/      # Production-ready (recommended)
│   ├── ai_researcher_tools/  # Reusable tool implementations
│   └── mcp_servers/          # Model Context Protocol servers
│       └── arxiv-mcp-server/ # arXiv paper search and retrieval
├── tests/                     # Test suite
├── examples/                  # Example scripts and demos
├── docs/                      # Documentation
├── experiments/               # Experimental features
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # This file
└── LICENSE                   # MIT License
```

## Tools & Capabilities

The agents have access to a comprehensive toolkit (`ai_researcher_tools/`):

### File System
- Read/write files, list directories, grep search

### Git Operations
- Status, diff, commit, branch management, PR preparation

### Command Execution
- Sandboxed shell commands with allowlist
- pytest runner with timeout controls
- Patch application

### Virtual Environments
- Create and manage Python virtual environments
- Execute commands within isolated environments

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
