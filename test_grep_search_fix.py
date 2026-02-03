#!/usr/bin/env python3
"""Test grep_search tool with both files and directories."""

import tempfile
import os
from pathlib import Path
from ai_researcher.ai_researcher_tools import grep_search


def test_grep_search_on_file():
    """Test that grep_search works on a single file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "agent_readme.md"
        test_file.write_text("# Agent README\n\nThis is a test file.\nIt contains agent information.\n")

        # Search in the file
        result = grep_search.invoke({
            "repo_root": tmpdir,
            "query": "agent",
            "path": "agent_readme.md",
            "case_sensitive": False
        })

        print("Test 1: Search single file (case-insensitive)")
        print(f"Result: {result}")
        assert "(no matches)" not in result
        assert "agent_readme.md" in result
        print("✓ PASSED\n")


def test_grep_search_on_directory():
    """Test that grep_search works on a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        (Path(tmpdir) / "file1.py").write_text("def agent_function():\n    pass\n")
        (Path(tmpdir) / "file2.py").write_text("# No match here\n")

        # Search in the directory
        result = grep_search.invoke({
            "repo_root": tmpdir,
            "query": "agent",
            "path": ".",
            "case_sensitive": False
        })

        print("Test 2: Search directory (case-insensitive)")
        print(f"Result: {result}")
        assert "file1.py" in result
        assert "agent_function" in result
        print("✓ PASSED\n")


def test_grep_search_nonexistent_path():
    """Test error handling for nonexistent path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = grep_search.invoke({
            "repo_root": tmpdir,
            "query": "test",
            "path": "nonexistent.txt"
        })

        print("Test 3: Nonexistent path")
        print(f"Result: {result}")
        assert "does not exist" in result
        print("✓ PASSED\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing grep_search fix for file/directory handling")
    print("=" * 60 + "\n")

    test_grep_search_on_file()
    test_grep_search_on_directory()
    test_grep_search_nonexistent_path()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)

