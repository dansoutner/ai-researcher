from __future__ import annotations

"""Dataset search and download tools.

This module provides tools for searching and downloading datasets from the web.
"""

from pathlib import Path
from typing import Optional
import urllib.request
import urllib.parse
import json

from langchain_core.tools import tool

from .sandbox import run_sandboxed, safe_path


@tool
def search_datasets_duckduckgo(query: str, max_results: int = 10) -> str:
    """Search for datasets using DuckDuckGo search.

    Args:
        query: Search query (e.g., "climate change dataset csv", "kaggle iris dataset")
        max_results: Maximum number of results to return (default: 10)

    Returns:
        Search results with titles, URLs, and snippets
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return "Error: duckduckgo_search library not installed. Run: pip install duckduckgo-search"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"No results found for query: {query}"

        output = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result.get('title', 'No title')}\n"
            output += f"   URL: {result.get('href', 'No URL')}\n"
            output += f"   {result.get('body', 'No description')}\n\n"

        return output
    except Exception as e:
        return f"Error searching DuckDuckGo: {str(e)}"


@tool
def search_datasets_google(query: str, max_results: int = 10) -> str:
    """Search for datasets using Google Custom Search (requires API key).

    Args:
        query: Search query (e.g., "machine learning dataset", "public datasets")
        max_results: Maximum number of results to return (default: 10)

    Returns:
        Search results with titles, URLs, and snippets

    Note:
        This tool requires GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables.
        You can get these from https://console.cloud.google.com/
    """
    import os

    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        return ("Error: GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables required.\n"
                "Set them in your environment or use search_datasets_duckduckgo instead.")

    try:
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": min(max_results, 10)  # Google limits to 10 per request
        }

        url = f"{base_url}?{urllib.parse.urlencode(params)}"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        items = data.get("items", [])
        if not items:
            return f"No results found for query: {query}"

        output = f"Search results for '{query}':\n\n"
        for i, item in enumerate(items, 1):
            output += f"{i}. {item.get('title', 'No title')}\n"
            output += f"   URL: {item.get('link', 'No URL')}\n"
            output += f"   {item.get('snippet', 'No description')}\n\n"

        return output
    except Exception as e:
        return f"Error searching Google: {str(e)}"


@tool
def download_file(repo_root: str, url: str, output_path: str, timeout_s: int = 300) -> str:
    """Download a file from a URL using wget.

    Args:
        repo_root: The root directory where the file will be saved
        url: URL of the file to download
        output_path: Relative path where the file should be saved (within repo_root)
        timeout_s: Download timeout in seconds (default: 300)

    Returns:
        Success message with file location or error message
    """
    try:
        root = Path(repo_root).resolve()
        target_path = safe_path(repo_root, output_path)

        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Use wget command through sandbox
        cmd = f'wget -O "{target_path}" --timeout={timeout_s} "{url}"'
        result = run_sandboxed(cmd, cwd=root, timeout_s=timeout_s + 10, validate=True, allow_network=True)

        if target_path.exists():
            size_mb = target_path.stat().st_size / (1024 * 1024)
            return f"Successfully downloaded to {output_path} ({size_mb:.2f} MB)\n{result}"
        else:
            return f"Download failed:\n{result}"
    except Exception as e:
        return f"Error downloading file: {str(e)}"


@tool
def download_file_python(repo_root: str, url: str, output_path: str) -> str:
    """Download a file from a URL using Python's urllib (no external dependencies).

    Args:
        repo_root: The root directory where the file will be saved
        url: URL of the file to download
        output_path: Relative path where the file should be saved (within repo_root)

    Returns:
        Success message with file location or error message
    """
    try:
        target_path = safe_path(repo_root, output_path)

        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Download with urllib
        urllib.request.urlretrieve(url, target_path)

        if target_path.exists():
            size_mb = target_path.stat().st_size / (1024 * 1024)
            return f"Successfully downloaded to {output_path} ({size_mb:.2f} MB)"
        else:
            return f"Download failed: File not created"
    except Exception as e:
        return f"Error downloading file: {str(e)}"


@tool
def unzip_file(repo_root: str, zip_path: str, extract_to: Optional[str] = None) -> str:
    """Unzip/extract an archive file (zip, tar.gz, tar.bz2, etc.).

    Args:
        repo_root: The root directory
        zip_path: Relative path to the archive file to extract
        extract_to: Optional directory to extract to (default: same directory as archive)

    Returns:
        Success message listing extracted files or error message
    """
    try:
        root = Path(repo_root).resolve()
        archive_path = safe_path(repo_root, zip_path)

        if not archive_path.exists():
            return f"Error: Archive file not found: {zip_path}"

        # Determine extraction directory
        if extract_to:
            extract_dir = safe_path(repo_root, extract_to)
        else:
            extract_dir = archive_path.parent

        extract_dir.mkdir(parents=True, exist_ok=True)

        # Determine archive type and extract
        archive_str = str(archive_path)

        if archive_str.endswith('.zip'):
            cmd = f'unzip -q "{archive_path}" -d "{extract_dir}"'
        elif archive_str.endswith('.tar.gz') or archive_str.endswith('.tgz'):
            cmd = f'tar -xzf "{archive_path}" -C "{extract_dir}"'
        elif archive_str.endswith('.tar.bz2') or archive_str.endswith('.tbz'):
            cmd = f'tar -xjf "{archive_path}" -C "{extract_dir}"'
        elif archive_str.endswith('.tar'):
            cmd = f'tar -xf "{archive_path}" -C "{extract_dir}"'
        elif archive_str.endswith('.gz') and not archive_str.endswith('.tar.gz'):
            cmd = f'gunzip -k "{archive_path}"'
        else:
            return f"Error: Unsupported archive format. Supported: .zip, .tar.gz, .tgz, .tar.bz2, .tbz, .tar, .gz"

        result = run_sandboxed(cmd, cwd=root, timeout_s=300, validate=True)

        # List extracted contents
        if extract_to:
            extract_rel = extract_to
        else:
            extract_rel = str(archive_path.parent.relative_to(root))
            if extract_rel == '.':
                extract_rel = ''

        list_cmd = f'ls -la "{extract_dir}"'
        listing = run_sandboxed(list_cmd, cwd=root, timeout_s=30, validate=True)

        return f"Successfully extracted {zip_path} to {extract_rel or 'current directory'}\n\nExtracted contents:\n{listing}"
    except Exception as e:
        return f"Error extracting archive: {str(e)}"


@tool
def list_kaggle_datasets(search_query: str = "", max_results: int = 20) -> str:
    """List datasets from Kaggle (requires kaggle API credentials).

    Args:
        search_query: Optional search query to filter datasets
        max_results: Maximum number of results to return (default: 20)

    Returns:
        List of Kaggle datasets with titles, URLs, and metadata

    Note:
        This tool requires Kaggle API credentials configured.
        See: https://github.com/Kaggle/kaggle-api#api-credentials
    """
    try:
        from kaggle import api
        api.authenticate()

        datasets = api.dataset_list(search=search_query, page_size=max_results)

        if not datasets:
            return f"No datasets found for query: {search_query}" if search_query else "No datasets found"

        output = f"Kaggle datasets{f' matching \"{search_query}\"' if search_query else ''}:\n\n"
        for i, ds in enumerate(datasets, 1):
            output += f"{i}. {ds.title}\n"
            output += f"   Ref: {ds.ref}\n"
            output += f"   URL: https://www.kaggle.com/datasets/{ds.ref}\n"
            output += f"   Size: {ds.size}\n"
            output += f"   Downloads: {ds.downloadCount}\n"
            output += f"   Updated: {ds.lastUpdated}\n\n"

        return output
    except ImportError:
        return "Error: kaggle library not installed. Run: pip install kaggle"
    except Exception as e:
        return f"Error listing Kaggle datasets: {str(e)}"


@tool
def download_kaggle_dataset(repo_root: str, dataset_ref: str, extract_path: str = "datasets") -> str:
    """Download a dataset from Kaggle.

    Args:
        repo_root: The root directory where the dataset will be saved
        dataset_ref: Kaggle dataset reference (e.g., "username/dataset-name")
        extract_path: Relative path where dataset should be extracted (default: "datasets")

    Returns:
        Success message with dataset location or error message

    Note:
        This tool requires Kaggle API credentials configured.
        See: https://github.com/Kaggle/kaggle-api#api-credentials
    """
    try:
        from kaggle import api
        api.authenticate()

        root = Path(repo_root).resolve()
        target_dir = safe_path(repo_root, extract_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        # Download and extract
        api.dataset_download_files(dataset_ref, path=str(target_dir), unzip=True)

        # List downloaded files
        files = list(target_dir.glob("*"))
        file_list = "\n".join([f"  - {f.name}" for f in files])

        return f"Successfully downloaded Kaggle dataset '{dataset_ref}' to {extract_path}\n\nFiles:\n{file_list}"
    except ImportError:
        return "Error: kaggle library not installed. Run: pip install kaggle"
    except Exception as e:
        return f"Error downloading Kaggle dataset: {str(e)}"

