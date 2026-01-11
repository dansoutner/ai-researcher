"""Test the edit_file tool for surgical file edits."""
import tempfile
from pathlib import Path
import pytest

from ai_researcher.ai_researcher_tools.fs_tools import edit_file, write_file


def test_edit_file_basic_replacement():
    """Test basic string replacement in a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_content = "Hello World\nThis is a test\nHello again"
        write_file.invoke({"repo_root": tmpdir, "path": "test.txt", "content": test_content})

        # Edit the file
        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "test.txt",
            "old_string": "Hello",
            "new_string": "Hi"
        })

        # Verify result message
        assert "Successfully replaced 2 occurrence(s)" in result
        assert "Warning" in result  # Should warn about multiple occurrences

        # Verify file content
        file_path = Path(tmpdir) / "test.txt"
        new_content = file_path.read_text()
        assert new_content == "Hi World\nThis is a test\nHi again"


def test_edit_file_single_replacement():
    """Test single string replacement without warning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_content = "def foo():\n    return 42"
        write_file.invoke({"repo_root": tmpdir, "path": "code.py", "content": test_content})

        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "code.py",
            "old_string": "return 42",
            "new_string": "return 100"
        })

        assert "Successfully replaced 1 occurrence(s)" in result
        assert "Warning" not in result

        file_path = Path(tmpdir) / "code.py"
        new_content = file_path.read_text()
        assert "return 100" in new_content


def test_edit_file_multiline_replacement():
    """Test replacing multiline strings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_content = """def old_function():
    print("old")
    return None

def other():
    pass"""
        write_file.invoke({"repo_root": tmpdir, "path": "multi.py", "content": test_content})

        old_str = """def old_function():
    print("old")
    return None"""

        new_str = """def new_function():
    print("new")
    return True"""

        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "multi.py",
            "old_string": old_str,
            "new_string": new_str
        })

        assert "Successfully replaced 1 occurrence(s)" in result

        file_path = Path(tmpdir) / "multi.py"
        new_content = file_path.read_text()
        assert "new_function" in new_content
        assert "old_function" not in new_content


def test_edit_file_not_found():
    """Test error handling when old_string is not found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_content = "Hello World"
        write_file.invoke({"repo_root": tmpdir, "path": "test.txt", "content": test_content})

        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "test.txt",
            "old_string": "Goodbye",
            "new_string": "Hi"
        })

        assert "Error: old_string not found" in result


def test_edit_file_nonexistent_file():
    """Test error handling for nonexistent file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "nonexistent.txt",
            "old_string": "foo",
            "new_string": "bar"
        })

        assert "Error: File" in result
        assert "does not exist" in result


def test_edit_file_whitespace_sensitive():
    """Test that whitespace must match exactly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_content = "def foo():\n    return 42"
        write_file.invoke({"repo_root": tmpdir, "path": "space.py", "content": test_content})

        # Try with wrong indentation
        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "space.py",
            "old_string": "def foo():\n  return 42",  # 2 spaces instead of 4
            "new_string": "def bar():\n    return 100"
        })

        assert "Error: old_string not found" in result


def test_edit_file_line_count_reporting():
    """Test that line count changes are reported."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_content = "line1\nline2\nline3"
        write_file.invoke({"repo_root": tmpdir, "path": "lines.txt", "content": test_content})

        # Add extra lines
        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "lines.txt",
            "old_string": "line2",
            "new_string": "line2a\nline2b\nline2c"
        })

        assert "lines: 3 → 5, +2" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

