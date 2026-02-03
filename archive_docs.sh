#!/bin/bash

cd /Users/dan/pex/ai-researcher/docs

# Files to archive (technical implementation docs, fix summaries, etc.)
files_to_archive=(
    "AGENT_README_PATH_FIX.md"
    "AGENT_V3_LOGGING_EXAMPLES.md"
    "AGENT_V3_LOGGING_SUMMARY.md"
    "AGENT_V3_LOGGING_UPDATE.md"
    "AGENT_V3_TOOLS_INTEGRATION.md"
    "DATASET_TOOLS.md"
    "DATETIME_PROMPTS_UPDATE.md"
    "EDIT_FILE_IMPLEMENTATION.md"
    "EXECUTOR_OUTPUT_SUMMARY.md"
    "EXECUTOR_TECHNICAL_REFERENCE.md"
    "EXECUTOR_WORKFLOW_DIAGRAM.md"
    "GREP_SEARCH_FILE_FIX.md"
    "GREP_SEARCH_INTEGRATION.md"
    "HUGGINGFACE_MCP_INTEGRATION.md"
    "HUGGINGFACE_MCP_INTEGRATION_CHANGELOG.md"
    "HUGGINGFACE_MCP_INTEGRATION_COMPLETE.md"
    "HUGGINGFACE_MCP_INTEGRATION_SUMMARY.md"
    "HUGGINGFACE_MCP_QUICK_REF.md"
    "LLM_USAGE_LOGGING.md"
    "NETWORK_ACCESS_FIX.md"
    "PIP_INSTALL_NETWORK_QUICK_REF.md"
    "REFACTORING_COMPLETE.md"
    "RG_COMMAND_NOT_FOUND_FIX.md"
    "ROUTING_FIX_SUMMARY.md"
    "TEST_REFACTORING_BEFORE_AFTER.md"
    "TOOL_AUDIT_SUMMARY.md"
    "TOOL_SYNC_COMPLETE.md"
)

# Move files to archive
echo "Moving files to archive..."
for file in "${files_to_archive[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" archive/
        echo "✓ Moved $file"
    else
        echo "✗ File not found: $file"
    fi
done

# Remove empty QUICK_START.md if it exists
if [ -f "QUICK_START.md" ] && [ ! -s "QUICK_START.md" ]; then
    rm "QUICK_START.md"
    echo "✓ Removed empty QUICK_START.md"
fi

echo "Archive operation complete!"
echo "Remaining files in docs/:"
ls -1 *.md 2>/dev/null | sort
