"""Shared tool implementations.

This package contains the concrete LangChain `@tool` functions used by the
various agent versions.

`agent_tools.py` at the repo root remains as a backwards-compatible shim that
re-exports these tools.
"""

from .venv_tools import create_venv, run_in_venv
from .fs_tools import (
    read_file,
    write_file,
    edit_file,
    list_files,
    grep,
    create_dir,
    list_dir,
    remove_dir,
    dir_exists,
    move_path,
    copy_path,
)
from .git_tools import (
    git_diff,
    git_status,
    git_add,
    git_commit,
    git_log,
    git_branch_list,
    git_checkout,
    git_remote_list,
    git_prepare_pr,
)
from .cmd_tools import apply_patch, run_pytest, run_cmd, run_terminal_command, get_errors
from .memory_tools import (
    memory_set,
    memory_get,
    memory_list,
    memory_delete,
    memory_append,
    store_repo_map,
    store_test_results,
    clear_memory,
)
from .dataset_tools import (
    search_datasets_duckduckgo,
    search_datasets_google,
    download_file,
    download_file_python,
    unzip_file,
    list_kaggle_datasets,
    download_kaggle_dataset,
)

__all__ = [
    # venv
    "create_venv",
    "run_in_venv",
    # fs
    "read_file",
    "write_file",
    "edit_file",
    "list_files",
    "grep",
    "create_dir",
    "list_dir",
    "remove_dir",
    "dir_exists",
    "move_path",
    "copy_path",
    # git
    "git_diff",
    "git_status",
    "git_add",
    "git_commit",
    "git_log",
    "git_branch_list",
    "git_checkout",
    "git_remote_list",
    "git_prepare_pr",
    # cmd/patch/test
    "apply_patch",
    "run_pytest",
    "run_cmd",
    "run_terminal_command",
    "get_errors",
    # memory
    "memory_set",
    "memory_get",
    "memory_list",
    "memory_delete",
    "memory_append",
    "store_repo_map",
    "store_test_results",
    "clear_memory",
    # dataset
    "search_datasets_duckduckgo",
    "search_datasets_google",
    "download_file",
    "download_file_python",
    "unzip_file",
    "list_kaggle_datasets",
    "download_kaggle_dataset",
]

