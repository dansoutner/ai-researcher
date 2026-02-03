#!/usr/bin/env python3
import os
import shutil
import sys

# Change to docs directory
os.chdir('/Users/dan/pex/ai-researcher/docs')

files_to_archive = [
    'AGENT_README_PATH_FIX.md',
    'AGENT_V3_LOGGING_EXAMPLES.md',
    'AGENT_V3_LOGGING_SUMMARY.md',
    'AGENT_V3_LOGGING_UPDATE.md',
    'AGENT_V3_TOOLS_INTEGRATION.md',
    'DATASET_TOOLS.md',
    'DATETIME_PROMPTS_UPDATE.md',
    'EDIT_FILE_IMPLEMENTATION.md',
    'EXECUTOR_OUTPUT_SUMMARY.md',
    'EXECUTOR_TECHNICAL_REFERENCE.md',
    'EXECUTOR_WORKFLOW_DIAGRAM.md',
    'GREP_SEARCH_FILE_FIX.md',
    'GREP_SEARCH_INTEGRATION.md',
    'HUGGINGFACE_MCP_INTEGRATION.md',
    'HUGGINGFACE_MCP_INTEGRATION_CHANGELOG.md',
    'HUGGINGFACE_MCP_INTEGRATION_COMPLETE.md',
    'HUGGINGFACE_MCP_INTEGRATION_SUMMARY.md',
    'HUGGINGFACE_MCP_QUICK_REF.md',
    'LLM_USAGE_LOGGING.md',
    'NETWORK_ACCESS_FIX.md',
    'PIP_INSTALL_NETWORK_QUICK_REF.md',
    'REFACTORING_COMPLETE.md',
    'RG_COMMAND_NOT_FOUND_FIX.md',
    'ROUTING_FIX_SUMMARY.md',
    'TEST_REFACTORING_BEFORE_AFTER.md',
    'TOOL_AUDIT_SUMMARY.md',
    'TOOL_SYNC_COMPLETE.md'
]

moved_count = 0
errors = []

print("Starting file archiving process...")

for file in files_to_archive:
    try:
        if os.path.exists(file):
            dest_path = os.path.join('archive', file)
            shutil.move(file, dest_path)
            print(f'✓ Moved {file}')
            moved_count += 1
        else:
            print(f'- File not found: {file}')
    except Exception as e:
        errors.append(f'Error moving {file}: {e}')
        print(f'✗ Error moving {file}: {e}')

# Remove empty QUICK_START.md if it exists
try:
    if os.path.exists('QUICK_START.md'):
        file_size = os.path.getsize('QUICK_START.md')
        if file_size == 0:
            os.remove('QUICK_START.md')
            print('✓ Removed empty QUICK_START.md')
        else:
            print(f'- QUICK_START.md is not empty ({file_size} bytes), keeping it')
    else:
        print('- QUICK_START.md not found')
except Exception as e:
    errors.append(f'Error handling QUICK_START.md: {e}')
    print(f'✗ Error handling QUICK_START.md: {e}')

print(f'\nSummary: Moved {moved_count} files to archive')

if errors:
    print(f'Errors encountered: {len(errors)}')
    for error in errors:
        print(f'  {error}')

print('\nRemaining .md files in docs/:')
try:
    md_files = [f for f in sorted(os.listdir('.')) if f.endswith('.md')]
    for file in md_files:
        print(f'  {file}')

    print(f'\nTotal remaining: {len(md_files)} .md files')
except Exception as e:
    print(f'Error listing files: {e}')

print("\nArchiving complete!")
