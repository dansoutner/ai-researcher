# Test Refactoring Quick Reference

## What Was Done

✅ **All 17 root-level test files refactored to proper pytest format**

### Key Changes:
- ✅ Converted script-style tests to pytest test functions
- ✅ Added pytest markers (@pytest.mark.integration, @pytest.mark.slow, etc.)
- ✅ Replaced manual setup/teardown with pytest fixtures
- ✅ Used pytest.raises() for exception testing
- ✅ Removed print statements and if __name__ == "__main__" blocks
- ✅ Fixed syntax errors and typos
- ✅ Added clean_memory fixture to tests/conftest.py

## Running Tests

### Run all tests in a file
```bash
pytest test_package.py -v
pytest test_arxiv_comprehensive.py -v
pytest test_dataset_tools.py -v
```

### Run specific test function
```bash
pytest test_package.py::test_package_import -v
pytest test_arxiv_comprehensive.py::test_arxiv_imports -v
```

### Run tests by marker
```bash
# Only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Skip tests requiring API keys
pytest -m "not requires_api"

# Only unit tests (non-integration, non-slow)
pytest -m "not integration and not slow"
```

### Run tests from organized directories
```bash
# After moving files (see TEST_REFACTORING_COMPLETE.md)
pytest tests/unit/
pytest tests/integration/
pytest tests/tools/
pytest tests/agent_v3/
```

### Run with coverage
```bash
pytest --cov=ai_researcher --cov-report=html
pytest --cov=ai_researcher --cov-report=term-missing
```

## Test Files Status

### ✅ Refactored Integration Tests
- test_arxiv_comprehensive.py
- test_arxiv_config.py
- test_arxiv_import.py
- test_arxiv_integration.py (async)
- test_mcp_integration.py
- test_package.py

### ✅ Refactored Tool Tests
- test_dataset_tools.py
- test_new_tools.py
- test_new_tools_full.py

### ✅ Refactored Unit Tests
- test_inline_parser.py (duplicate - can be removed)
- test_parse_fix.py
- test_parse_executor_response.py
- test_reviewer_json_parsing.py
- test_simple_reviewer.py

### ✅ Refactored Agent Tests
- test_repo_root_fix.py
- test_working_dir_persistence.py
- test_tools_fix.py

## Available Pytest Markers

Defined in pytest.ini and tests/conftest.py:

- `@pytest.mark.asyncio` - Async test (requires pytest-asyncio)
- `@pytest.mark.slow` - Slow running test (can skip with -m "not slow")
- `@pytest.mark.integration` - Integration test
- `@pytest.mark.requires_api` - Requires API credentials (skip if not available)

## Available Fixtures

Defined in tests/conftest.py:

- `temp_dir` - Temporary directory for tests
- `temp_file` - Temporary file in temp_dir
- `temp_git_repo` - Temporary git repository
- `mock_api_key` - Mocked ANTHROPIC_API_KEY
- `clean_memory` - Clears memory before and after test

## Next Steps

1. **Move test files to proper directories** (see TEST_REFACTORING_COMPLETE.md)
2. **Run full test suite:** `pytest tests/`
3. **Set up CI/CD** with pytest commands
4. **Add more fixtures** as needed for common test scenarios
5. **Add pytest-xdist** for parallel test execution: `pip install pytest-xdist`
6. **Add pytest-cov** for coverage reports: `pip install pytest-cov`

## Example Test Structure

```python
"""Module docstring describing what is tested."""

import pytest

from ai_researcher.module import function_to_test


@pytest.mark.integration
def test_function_with_fixture(temp_dir):
    """Test function using fixture."""
    result = function_to_test(str(temp_dir))
    assert result is not None


@pytest.mark.slow
@pytest.mark.requires_api
def test_function_requiring_api():
    """Test that requires external API."""
    result = function_to_test()
    assert result["status"] == "success"


def test_function_exception():
    """Test that function raises expected exception."""
    with pytest.raises(ValueError, match="Expected error"):
        function_to_test(invalid_input)
```

## Common Pytest Commands

```bash
# Verbose output
pytest -v

# Very verbose output (shows print statements)
pytest -vv -s

# Stop at first failure
pytest -x

# Run last failed tests
pytest --lf

# Show local variables in traceback
pytest -l

# Parallel execution (requires pytest-xdist)
pytest -n auto

# Generate HTML coverage report
pytest --cov=ai_researcher --cov-report=html

# Run tests matching pattern
pytest -k "test_parse"

# Show available fixtures
pytest --fixtures

# Show available markers
pytest --markers
```

## Troubleshooting

### Import errors
- Make sure ai_researcher package is installed: `pip install -e .`
- Check PYTHONPATH includes project root

### Async test errors
- Install pytest-asyncio: `pip install pytest-asyncio`
- Make sure test has `@pytest.mark.asyncio` decorator

### Fixture not found
- Check fixture is defined in conftest.py
- Make sure conftest.py is in same or parent directory

### Tests not discovered
- Make sure file starts with `test_`
- Make sure function starts with `test_`
- Check pytest.ini configuration

