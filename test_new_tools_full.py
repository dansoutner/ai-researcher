#!/usr/bin/env python3
"""Test the new run_terminal_command and get_errors tools."""

from pathlib import Path
from ai_researcher.ai_researcher_tools import run_terminal_command, get_errors

# Test directory
repo_root = str(Path(__file__).parent)

print("=" * 60)
print("Testing run_terminal_command tool")
print("=" * 60)

# Test 1: Simple command
print("\n1. Testing simple echo command:")
result = run_terminal_command.invoke({
    "repo_root": repo_root,
    "cmd": "echo 'Hello from terminal command'",
    "is_background": False,
    "timeout_s": 10
})
print(result)

# Test 2: List files
print("\n2. Testing ls command:")
result = run_terminal_command.invoke({
    "repo_root": repo_root,
    "cmd": "ls -la | head -5",
    "is_background": False,
    "timeout_s": 10
})
print(result)

print("\n" + "=" * 60)
print("Testing get_errors tool")
print("=" * 60)

# Create a test file with syntax error
test_file = Path(repo_root) / "test_syntax_error.py"
test_file.write_text("""
# This file has a syntax error
def broken_function():
    return "missing closing quote
""")

print("\n3. Testing get_errors on file with syntax error:")
result = get_errors.invoke({
    "repo_root": repo_root,
    "file_paths": ["test_syntax_error.py"]
})
print(result)

# Create a test file with no errors
test_file_ok = Path(repo_root) / "test_no_error.py"
test_file_ok.write_text("""
# This file has no errors
def working_function():
    return "all good"
""")

print("\n4. Testing get_errors on file with no errors:")
result = get_errors.invoke({
    "repo_root": repo_root,
    "file_paths": ["test_no_error.py"]
})
print(result)

print("\n5. Testing get_errors on non-existent file:")
result = get_errors.invoke({
    "repo_root": repo_root,
    "file_paths": ["does_not_exist.py"]
})
print(result)

# Clean up test files
test_file.unlink()
test_file_ok.unlink()

print("\n" + "=" * 60)
print("✓ All tests completed successfully!")
print("=" * 60)

