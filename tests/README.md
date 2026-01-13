# Tests Directory

This directory contains all tests for the AI Researcher project, organized by component and test type.

## Directory Structure

```
tests/
├── unit/                      # Unit tests for individual components
│   ├── test_parsing.py        # JSON parsing utilities (executor & reviewer)
│   └── test_executor_output.py # Executor output handling
│
├── integration/               # Integration tests
│   ├── test_package.py        # Package structure and imports
│   ├── test_mcp_integration.py # MCP integration functionality
│   └── test_async_mcp_tools.py # Async MCP tools
│
├── agent_v1/                  # Agent v1 specific tests
│   └── test_mcp.py            # MCP integration for agent v1
│
├── agent_v2/                  # Agent v2 specific tests
│   └── test_tooling.py        # Agent v2 tooling tests
│
├── agent_v3/                  # Agent v3 (Claude) specific tests
│   ├── test_tools.py          # Tool availability and integration
│   ├── test_tool_binding.py   # LangChain tool binding
│   ├── test_pruning.py        # Message pruning functionality
│   ├── test_ainvoke.py        # Async invocation tests
│   └── test_routing.py        # Routing logic tests
│
└── tools/                     # Tool-specific tests
    ├── test_fs_tools.py       # File system tools (read_file, write_file)
    ├── test_edit_file.py      # Edit file functionality
    ├── test_dir_tools.py      # Directory operations
    ├── test_git_tools.py      # Git tools
    └── test_venv_tools.py     # Virtual environment tools
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test categories

#### Unit tests
```bash
pytest tests/unit/
```

#### Integration tests
```bash
pytest tests/integration/
```

#### Agent-specific tests
```bash
pytest tests/agent_v1/
pytest tests/agent_v2/
pytest tests/agent_v3/
```

#### Tool tests
```bash
pytest tests/tools/
```

### Run a specific test file
```bash
pytest tests/unit/test_parsing.py
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=ai_researcher --cov-report=html
```

## Test Categories

### Unit Tests
Tests for individual functions and components in isolation:
- **Parsing**: JSON parsing for executor and reviewer responses
- **Executor Output**: Structured output handling

### Integration Tests
Tests that verify multiple components work together:
- **Package Structure**: Import tests and package exports
- **MCP Integration**: Model Context Protocol integration
- **Async MCP Tools**: Asynchronous MCP tool functionality

### Agent Tests
Tests specific to each agent version:
- **Agent v1**: Legacy agent with MCP integration
- **Agent v2**: LangGraph-based agent
- **Agent v3**: Production Claude agent with comprehensive tools

### Tool Tests
Tests for individual tools:
- **File System**: Read, write, and file operations
- **Git**: Git commands and operations
- **Directory**: Directory listing and operations
- **Edit File**: File editing functionality
- **Virtual Environment**: Python venv tools

## Writing Tests

### Test File Naming
- Test files should be named `test_<feature>.py`
- Place tests in the appropriate subdirectory based on what they test

### Test Function Naming
- Test functions should be named `test_<description>`
- Use descriptive names that explain what is being tested

### Example Test Structure
```python
"""Tests for feature X."""

import pytest
from ai_researcher.module import function


def test_basic_functionality():
    """Test that basic functionality works."""
    result = function()
    assert result is not None


def test_error_handling():
    """Test that errors are handled correctly."""
    with pytest.raises(ValueError):
        function(invalid_input)


@pytest.mark.skipif(
    not os.getenv("API_KEY"),
    reason="API key required"
)
def test_with_api():
    """Test that requires API credentials."""
    result = function_with_api()
    assert result["success"] is True
```

## Test Requirements

### Required Packages
Tests use pytest and may require:
- `pytest` - Test runner
- `pytest-asyncio` - For async tests
- `pytest-cov` - For coverage reports

Install with:
```bash
pip install pytest pytest-asyncio pytest-cov
```

### Optional Dependencies
Some tests may require API keys:
- `ANTHROPIC_API_KEY` - For Claude model tests
- `OPENAI_API_KEY` - For OpenAI model tests

Set these in your environment to run all tests:
```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- Tests that require API keys are skipped if keys are not available
- Tests use temporary directories for file operations
- Tests clean up after themselves

## Troubleshooting

### Known Issues

Some tests may require updates:
- `tests/agent_v3/test_pruning.py` - May reference old API that has been refactored
- `tests/integration/test_async_mcp_tools.py` - Requires pytest-asyncio plugin

To install pytest-asyncio for async tests:
```bash
pip install pytest-asyncio
```

### Import Errors
If you get import errors, ensure the package is installed:
```bash
pip install -e .
```

### Test Discovery Issues
If pytest doesn't find tests, check:
- Files are named `test_*.py` or `*_test.py`
- Functions are named `test_*`
- The tests directory has `__init__.py` files

### Async Test Issues
For async tests, ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

## Contributing

When adding new tests:
1. Place them in the appropriate subdirectory
2. Follow existing naming conventions
3. Add docstrings explaining what is tested
4. Ensure tests are independent and can run in any order
5. Clean up any temporary files or resources
6. Update this README if adding a new test category

