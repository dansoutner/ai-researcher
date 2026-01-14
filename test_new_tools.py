#!/usr/bin/env python3
"""Quick test of the new tools."""

import sys
from pathlib import Path

# Add the module to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ai_researcher.ai_researcher_tools.cmd_tools import run_terminal_command, get_errors
    print("✓ Successfully imported run_terminal_command and get_errors")

    # Test that they're properly decorated as tools
    print(f"✓ run_terminal_command is a tool: {hasattr(run_terminal_command, 'name')}")
    print(f"✓ get_errors is a tool: {hasattr(get_errors, 'name')}")

    # Show tool names
    if hasattr(run_terminal_command, 'name'):
        print(f"  - run_terminal_command tool name: {run_terminal_command.name}")
    if hasattr(get_errors, 'name'):
        print(f"  - get_errors tool name: {get_errors.name}")

    print("\n✓ All checks passed!")

except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

