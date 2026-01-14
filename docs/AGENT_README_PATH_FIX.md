# Agent README Path Fix

## Problem
The agent was sometimes trying to read `agent_readme.md` from the wrong path, combining the working directory with the filename. For example:

```
ERROR | Tool exception: ERROR executing read_file: [Errno 2] No such file or directory: 
'/Users/dan/pex/ai-agent-experiments/experiments/project_sms_spam/agent_readme.md'
```

Instead of using just `"agent_readme.md"` (which is always at repo root), the agent was prepending subdirectory paths like `"experiments/project_sms_spam/agent_readme.md"`.

## Root Cause
The agent's system prompts mentioned that `agent_readme.md` is "in repo root" but didn't explicitly clarify that:
1. The file is ALWAYS at the repo root
2. When calling `read_file`/`write_file`, the path should ALWAYS be just `"agent_readme.md"`
3. NEVER prepend subdirectory paths to it

This led to confusion when the agent was working in subdirectories - it would try to construct paths relative to the current working subdirectory rather than always using the repo root reference.

## Solution
Updated all three system prompts in `ai_researcher/agent_v3_claude/config.py`:

### 1. PLANNER_SYSTEM_PROMPT
Added explicit path rules:
```
**State Management Protocol:**
1. **Check for Existence:** Always check if `agent_readme.md` exists in repo root.
   - **CRITICAL PATH RULE:** When reading/writing `agent_readme.md`, ALWAYS use path `"agent_readme.md"` (just the filename).
   - **NEVER use paths like `"experiments/project_sms_spam/agent_readme.md"`.** The file is at repo root.
```

### 2. EXECUTOR_SYSTEM_PROMPT
Added multiple reminders:
```
**The "Journaling" Rule:**
You have a persistent scratchpad called `agent_readme.md` in repo root.
1. **Read First:** Before executing code, read `agent_readme.md` to refresh your context on file paths and previous errors.
   - **CRITICAL PATH RULE:** When reading/writing `agent_readme.md`, ALWAYS use path `"agent_readme.md"` (just the filename).
   - **NEVER use paths like `"experiments/project_sms_spam/agent_readme.md"` or any subdirectory path.**
   - The file is ALWAYS at the repo root, so the path is ALWAYS just `"agent_readme.md"`.
...
3. **Write Last:** Before returning "success", you MUST append a note to the "Execution Log" section of `agent_readme.md`.
   - Format: `[timestamp] Action: <what you did> | Result: <outcome> | Next: <what needs to happen>`
   - **Remember:** Use path `"agent_readme.md"` when calling write_file or edit_file, NOT any subdirectory path.
```

### 3. REVIEWER_SYSTEM_PROMPT
Added path validation check:
```
**Documentation Audit:**
- **State Check:** Did the Executor update `agent_readme.md`? 
- **Path Validation:** Did the Executor use the correct path `"agent_readme.md"` (not a subdirectory path)?
```

## How It Works
The `safe_path()` function in `ai_researcher_tools/sandbox.py` combines `repo_root` and the relative `path`:
```python
def safe_path(repo_root: str, rel_path: str) -> Path:
    root = Path(repo_root).resolve()
    p = (root / rel_path).resolve()
    if root not in p.parents and p != root:
        raise ValueError("Path escapes repo_root")
    return p
```

When `read_file(repo_root="/Users/dan/pex/ai-agent-experiments", path="agent_readme.md")` is called, it correctly resolves to:
- `/Users/dan/pex/ai-agent-experiments/agent_readme.md` ✅

But if the agent mistakenly passes `path="experiments/project_sms_spam/agent_readme.md"`, it tries:
- `/Users/dan/pex/ai-agent-experiments/experiments/project_sms_spam/agent_readme.md` ❌

## Expected Behavior
After this fix, the agent should:
1. Always use `path="agent_readme.md"` when reading/writing the agent readme file
2. Never prepend working directory paths or subdirectory paths
3. The reviewer should catch any violations of this rule

## Testing
To verify the fix works:
1. Run the agent in a project that creates subdirectories (e.g., `experiments/project_xyz/`)
2. Observe that the agent correctly reads/writes `agent_readme.md` from repo root
3. Check logs to ensure no `FileNotFoundError` for incorrect paths like `experiments/.../agent_readme.md`

## Files Modified
- `ai_researcher/agent_v3_claude/config.py` - Updated all three system prompts with explicit path rules

