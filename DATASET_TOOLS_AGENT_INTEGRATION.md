# Dataset Tools Integration - Agent v3 Complete

## Summary

Successfully integrated the dataset tools into **agent_v3_claude** so they are available for use.

## Changes Made

### 1. Updated `ai_researcher/agent_v3_claude/config.py`

Added dataset tools to the **EXECUTOR_SYSTEM_PROMPT** Available Tools list:

```python
**Available Tools:**
- File System: read_file, write_file, edit_file, list_files, grep, create_dir, list_dir, remove_dir, dir_exists, move_path, copy_path
- Git: git_diff, git_status, git_add, git_commit, git_log, git_branch_list, git_checkout, git_remote_list, git_prepare_pr
- Commands: apply_patch, run_pytest, run_cmd, run_terminal_command, get_errors
- Venv: create_venv, run_in_venv
- Memory: memory_set, memory_get, memory_list, memory_delete, memory_append, store_repo_map, store_test_results, clear_memory
- Dataset: search_datasets_duckduckgo, search_datasets_google, download_file, download_file_python, unzip_file, list_kaggle_datasets, download_kaggle_dataset
```

This ensures the agent knows about the dataset tools in its system prompt.

### 2. Updated `ai_researcher/agent_v3_claude/tools.py`

**A. Added imports:**
```python
# Dataset tools
search_datasets_duckduckgo,
search_datasets_google,
download_file,
download_file_python,
unzip_file,
list_kaggle_datasets,
download_kaggle_dataset,
```

**B. Added to TOOLS list:**
```python
TOOLS = [
    # ... existing tools ...
    # Dataset
    search_datasets_duckduckgo,
    search_datasets_google,
    download_file,
    download_file_python,
    unzip_file,
    list_kaggle_datasets,
    download_kaggle_dataset,
]
```

This makes the tools available for the executor to call.

## Agent Compatibility

### ✅ Agent v3 (agent_v3_claude)
- **Fully Integrated**: All 7 dataset tools are now available
- Tools imported from `ai_researcher.ai_researcher_tools`
- Registered in TOOLS list
- Documented in system prompt

### ℹ️ Agent v1 (agent_v1)
- Uses its own tool definitions in `agent_v1/tools.py`
- Does not currently use shared `ai_researcher_tools`
- Would need explicit imports if dataset tools are desired

### ℹ️ Agent v2 (agent_v2)
- Uses dynamic tool registry from `agent_tools` module
- Would need the backwards-compatible shim to access shared tools
- Can be integrated if needed

## Available Dataset Tools in Agent v3

1. **search_datasets_duckduckgo** - Search for datasets using DuckDuckGo
2. **search_datasets_google** - Search for datasets using Google Custom Search
3. **download_file** - Download files using wget
4. **download_file_python** - Download files using Python urllib
5. **unzip_file** - Extract compressed archives
6. **list_kaggle_datasets** - List and search Kaggle datasets
7. **download_kaggle_dataset** - Download datasets from Kaggle

## Usage Example

Agent v3 can now use dataset tools in its execution:

```python
# Agent can now execute commands like:
# 1. Search for datasets
result = search_datasets_duckduckgo.invoke({
    "query": "climate change dataset",
    "max_results": 5
})

# 2. Download datasets
result = download_file_python.invoke({
    "repo_root": ".",
    "url": "https://example.com/data.csv",
    "output_path": "datasets/data.csv"
})

# 3. Extract archives
result = unzip_file.invoke({
    "repo_root": ".",
    "zip_path": "datasets/archive.zip",
    "extract_to": "datasets/extracted"
})
```

## Testing

You can test the integration by running agent v3 with a dataset-related task:

```bash
ai-researcher-agent-v3 "Search for and download the iris dataset"
```

## Next Steps (Optional)

If you want dataset tools in agent_v1 or agent_v2:

### For Agent v1:
Add imports to `ai_researcher/agent_v1/agent.py`:
```python
from ai_researcher.ai_researcher_tools import (
    search_datasets_duckduckgo,
    download_file_python,
    unzip_file,
    # ... other dataset tools
)
```

Then add to TOOLS list in the same file.

### For Agent v2:
Agent v2 uses dynamic tool discovery, so it should automatically pick up tools from `agent_tools` module if a backwards-compatible shim exists at the repo root that re-exports from `ai_researcher_tools`.

## Verification

✅ Dataset tools imported in agent_v3_claude/tools.py  
✅ Dataset tools added to TOOLS list  
✅ Dataset tools documented in config.py system prompt  
✅ No syntax errors  
✅ Backward compatible (no breaking changes)  

## Status: Complete ✅

Agent v3 can now search for and download datasets using all 7 dataset tools!

