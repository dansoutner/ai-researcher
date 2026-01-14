# Agent V3 Colored Logging - Visual Examples

## Color Scheme Overview

The new logging system uses distinct colors to make it easy to scan output and distinguish between different types of messages:

```
╔════════════════════════════════════════════════════════════╗
║  LOG LEVEL  │  COLOR   │  PURPOSE                         ║
╠════════════════════════════════════════════════════════════╣
║  DEBUG      │  CYAN    │  Internal system operations      ║
║  TOOL       │  BLUE    │  Tool execution details          ║
║  INFO       │  GREEN   │  State changes & progress        ║
║  USER       │  MAGENTA │  User-facing results/summaries   ║
║  WARNING    │  YELLOW  │  Potential issues                ║
║  ERROR      │  RED     │  Errors and failures             ║
║  CRITICAL   │  RED+BOLD│  Critical errors                 ║
╚════════════════════════════════════════════════════════════╝
```

## Example Output

Below is what you would see when running the agent (colors shown as text):

```
[GREEN] INFO  | Starting agent run with goal: Create a Python package
[CYAN]  DEBUG | Max iterations: 10
[CYAN]  DEBUG | Repo root: /Users/dan/pex/ai-researcher
[CYAN]  DEBUG | Initial state keys: ['goal', 'plan', 'messages', ...]

[GREEN] INFO  | === PLANNER NODE (iteration 0) ===
[CYAN]  DEBUG | First iteration - saving working directory to memory: /Users/dan/pex/ai-researcher

[MAGENTA] USER  | 
[MAGENTA] USER  | ============================================================
[MAGENTA] USER  | PLAN GENERATED
[MAGENTA] USER  | ============================================================
[MAGENTA] USER  | 1. Verify the environment (git status, python version)
[MAGENTA] USER  | 2. Create package structure with __init__.py
[MAGENTA] USER  | 3. Write setup.py with metadata
[MAGENTA] USER  | 4. Create example module with function
[MAGENTA] USER  | 5. Write pytest tests
[MAGENTA] USER  | 6. Run tests to verify everything works
[MAGENTA] USER  | ============================================================

[GREEN] INFO  | === EXECUTOR NODE (iteration 0, step 1/6) ===
[GREEN] INFO  | Executing step: Verify the environment
[CYAN]  DEBUG | Retrieved working directory from memory: /Users/dan/pex/ai-researcher

[BLUE]  TOOL  | Calling tool: git_status
[BLUE]  TOOL  | Tool args: {'repo_root': '/Users/dan/pex/ai-researcher'}
[BLUE]  TOOL  | Tool result length: 234 characters
[BLUE]  TOOL  | Tool result preview: On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean...

[GREEN] INFO  | === REVIEWER NODE (iteration 0) ===
[CYAN]  DEBUG | Executor output: {'success': True, 'output': 'Environment verified successfully'}
[GREEN] INFO  | Reviewer verdict: CONTINUE
[CYAN]  DEBUG | Reason: Step completed successfully, ready for next step
[CYAN]  DEBUG | Fix suggestion: 

[GREEN] INFO  | === EXECUTOR NODE (iteration 0, step 2/6) ===
[GREEN] INFO  | Executing step: Create package structure with __init__.py

[BLUE]  TOOL  | Calling tool: write_file
[BLUE]  TOOL  | Tool args: {'repo_root': '/Users/dan/pex/ai-researcher', 'path': 'mypackage/__init__.py', ...}
[BLUE]  TOOL  | Tool result length: 45 characters
[BLUE]  TOOL  | Tool result preview: Successfully created file: mypackage/__init__.py

[GREEN] INFO  | === REVIEWER NODE (iteration 0) ===
[CYAN]  DEBUG | Executor output: {'success': True, 'output': 'Package structure created'}
[GREEN] INFO  | Reviewer verdict: CONTINUE

... (more iterations) ...

[GREEN] INFO  | === REVIEWER NODE (iteration 5) ===
[CYAN]  DEBUG | Executor output: {'success': True, 'output': 'All 3 tests passed'}
[GREEN] INFO  | Reviewer verdict: FINISH
[CYAN]  DEBUG | Reason: All steps completed successfully and tests pass
```

## Example Error Scenario

When something goes wrong, errors are clearly highlighted:

```
[GREEN] INFO  | === EXECUTOR NODE (iteration 2, step 3/6) ===
[GREEN] INFO  | Executing step: Run pytest on the test file

[BLUE]  TOOL  | Calling tool: run_pytest
[BLUE]  TOOL  | Tool args: {'repo_root': '/Users/dan/pex/ai-researcher', 'args': 'tests/'}
[RED]   ERROR | Tool exception: FileNotFoundError: tests/ directory not found

[GREEN] INFO  | === REVIEWER NODE (iteration 2) ===
[CYAN]  DEBUG | Executor output: {'success': False, 'output': 'ERROR: tests/ directory not found'}
[YELLOW] WARNING| Executor failed, automatically setting verdict to 'retry'

[GREEN] INFO  | === PLANNER NODE (iteration 3) ===
[MAGENTA] USER  | 
[MAGENTA] USER  | ============================================================
[MAGENTA] USER  | PLAN GENERATED (REVISED)
[MAGENTA] USER  | ============================================================
[MAGENTA] USER  | 1. Create tests/ directory first
[MAGENTA] USER  | 2. Write test file in tests/test_example.py
[MAGENTA] USER  | 3. Run pytest to verify tests pass
```

## Benefits at a Glance

1. **🔍 Easy Scanning**: Quickly find what you're looking for
   - Want to see the plan? Look for MAGENTA
   - Debugging tool issues? Look for BLUE
   - Check for errors? Look for RED

2. **🎯 Clear Purpose**: Each color has a specific meaning
   - No confusion about whether a message is for debugging or end users

3. **📊 Better Monitoring**: Track agent progress visually
   - GREEN shows state transitions
   - BLUE shows what tools are being used
   - MAGENTA shows results

4. **🐛 Faster Debugging**: Errors stand out immediately
   - RED errors are impossible to miss
   - YELLOW warnings catch your attention
   - CYAN debug info helps trace execution

## Customization

You can adjust what you see by setting the log level:

```python
import logging
from ai_researcher.agent_v3_claude import setup_logger

# Production: Only show important info
logger = setup_logger("agent", level=logging.INFO)
# Output: INFO (green), USER (magenta), WARNING (yellow), ERROR (red)

# Development: Show everything
logger = setup_logger("agent", level=logging.DEBUG)  
# Output: All levels including DEBUG (cyan) and TOOL (blue)

# Quiet mode: Only warnings and errors
logger = setup_logger("agent", level=logging.WARNING)
# Output: WARNING (yellow), ERROR (red), CRITICAL (bold red)
```

## Integration with Existing Code

All existing functionality remains the same. The only change is behind-the-scenes:
- Old: `print(f"[DEBUG] Starting...")`
- New: `logger.debug("Starting...")`

No changes needed to your scripts that use the agent!

