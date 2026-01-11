"""Demo script showcasing the edit_file tool capabilities."""
import tempfile
from pathlib import Path
from ai_researcher_tools import write_file, edit_file, read_file


def demo_basic_edit():
    """Demo: Basic string replacement."""
    print("=" * 60)
    print("DEMO 1: Basic String Replacement")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a Python file
        code = '''def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    result = a + b
    return result
'''
        write_file.invoke({"repo_root": tmpdir, "path": "math.py", "content": code})
        print("\n📄 Original file:")
        print(code)

        # Edit: rename function
        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "math.py",
            "old_string": "def calculate_sum(a, b):",
            "new_string": "def add(a, b):"
        })
        print(f"\n✏️  Edit result: {result}")

        # Show updated file
        updated = read_file.invoke({"repo_root": tmpdir, "path": "math.py"})
        print("\n📄 Updated file:")
        print(updated)


def demo_multiline_edit():
    """Demo: Replace multiline code block."""
    print("\n" + "=" * 60)
    print("DEMO 2: Multiline Code Block Replacement")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        code = '''class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        print(f"Hello, I'm {self.name}")
    
    def farewell(self):
        print("Goodbye!")
'''
        write_file.invoke({"repo_root": tmpdir, "path": "person.py", "content": code})
        print("\n📄 Original file:")
        print(code)

        # Replace entire method
        old_method = '''    def greet(self):
        print(f"Hello, I'm {self.name}")'''

        new_method = '''    def greet(self, formal=False):
        if formal:
            print(f"Good day, my name is {self.name}")
        else:
            print(f"Hi! I'm {self.name}")'''

        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "person.py",
            "old_string": old_method,
            "new_string": new_method
        })
        print(f"\n✏️  Edit result: {result}")

        updated = read_file.invoke({"repo_root": tmpdir, "path": "person.py"})
        print("\n📄 Updated file:")
        print(updated)


def demo_error_handling():
    """Demo: Error handling for invalid edits."""
    print("\n" + "=" * 60)
    print("DEMO 3: Error Handling")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        code = "def foo():\n    pass"
        write_file.invoke({"repo_root": tmpdir, "path": "test.py", "content": code})

        # Try to replace non-existent string
        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "test.py",
            "old_string": "def bar():",
            "new_string": "def baz():"
        })
        print(f"\n❌ Error (string not found): {result}")

        # Try to edit non-existent file
        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "nonexistent.py",
            "old_string": "foo",
            "new_string": "bar"
        })
        print(f"\n❌ Error (file not found): {result}")


def demo_multiple_occurrences():
    """Demo: Handling multiple occurrences with warning."""
    print("\n" + "=" * 60)
    print("DEMO 4: Multiple Occurrences Warning")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        code = '''print("Hello")
x = 5
print("Hello")
y = 10
print("Hello")
'''
        write_file.invoke({"repo_root": tmpdir, "path": "multi.py", "content": code})
        print("\n📄 Original file:")
        print(code)

        # Replace all occurrences
        result = edit_file.invoke({
            "repo_root": tmpdir,
            "path": "multi.py",
            "old_string": 'print("Hello")',
            "new_string": 'print("Hi there!")'
        })
        print(f"\n✏️  Edit result: {result}")

        updated = read_file.invoke({"repo_root": tmpdir, "path": "multi.py"})
        print("\n📄 Updated file:")
        print(updated)


if __name__ == "__main__":
    print("\n🎯 edit_file Tool Demonstration\n")
    print("This tool provides surgical file edits without rewriting entire files.")
    print("Benefits:")
    print("  • More precise than write_file for large files")
    print("  • Preserves exact formatting and whitespace")
    print("  • Validates edits before applying")
    print("  • Reports line count changes")

    demo_basic_edit()
    demo_multiline_edit()
    demo_error_handling()
    demo_multiple_occurrences()

    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)

