# Dataset Tools Documentation

The AI Researcher now includes comprehensive dataset search and download capabilities through the `dataset_tools` module.

## Overview

The dataset tools enable AI agents to:
- Search for datasets using DuckDuckGo or Google
- Download files from URLs using wget or Python urllib
- Extract compressed archives (zip, tar.gz, tar.bz2, etc.)
- List and download datasets from Kaggle

## Installation

### Basic Installation

The core package includes Python-based download capabilities (no external dependencies):

```bash
pip install -e .
```

### Full Dataset Tools

For all features including DuckDuckGo search and Kaggle integration:

```bash
pip install -e ".[datasets]"
```

This installs:
- `duckduckgo-search>=4.0` - For web search capabilities
- `kaggle>=1.5.0` - For Kaggle dataset access

## Available Tools

### 1. search_datasets_duckduckgo

Search for datasets using DuckDuckGo (no API key required).

**Parameters:**
- `query` (str): Search query (e.g., "climate change dataset csv")
- `max_results` (int, optional): Maximum results to return (default: 10)

**Returns:** Search results with titles, URLs, and descriptions

**Example:**
```python
from ai_researcher.ai_researcher_tools import search_datasets_duckduckgo

result = search_datasets_duckduckgo.invoke({
    "query": "iris dataset csv",
    "max_results": 5
})
print(result)
```

### 2. search_datasets_google

Search for datasets using Google Custom Search (requires API credentials).

**Parameters:**
- `query` (str): Search query
- `max_results` (int, optional): Maximum results to return (default: 10)

**Environment Variables Required:**
- `GOOGLE_API_KEY`: Your Google API key
- `GOOGLE_CSE_ID`: Your Custom Search Engine ID

**Returns:** Search results with titles, URLs, and snippets

**Example:**
```python
import os
os.environ["GOOGLE_API_KEY"] = "your-api-key"
os.environ["GOOGLE_CSE_ID"] = "your-cse-id"

from ai_researcher.ai_researcher_tools import search_datasets_google

result = search_datasets_google.invoke({
    "query": "public datasets machine learning",
    "max_results": 10
})
```

### 3. download_file

Download a file using wget (requires wget to be installed).

**Parameters:**
- `repo_root` (str): Root directory for downloads
- `url` (str): URL of the file to download
- `output_path` (str): Relative path where file should be saved
- `timeout_s` (int, optional): Timeout in seconds (default: 300)

**Returns:** Success message with file location and size

**Example:**
```python
from ai_researcher.ai_researcher_tools import download_file

result = download_file.invoke({
    "repo_root": "/path/to/project",
    "url": "https://example.com/dataset.csv",
    "output_path": "data/dataset.csv",
    "timeout_s": 60
})
```

### 4. download_file_python

Download a file using Python's urllib (no external dependencies).

**Parameters:**
- `repo_root` (str): Root directory for downloads
- `url` (str): URL of the file to download
- `output_path` (str): Relative path where file should be saved

**Returns:** Success message with file location and size

**Example:**
```python
from ai_researcher.ai_researcher_tools import download_file_python

result = download_file_python.invoke({
    "repo_root": "/path/to/project",
    "url": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
    "output_path": "datasets/iris.csv"
})
```

### 5. unzip_file

Extract compressed archives (zip, tar.gz, tar.bz2, etc.).

**Parameters:**
- `repo_root` (str): Root directory
- `zip_path` (str): Relative path to the archive file
- `extract_to` (str, optional): Directory to extract to (default: same as archive)

**Supported Formats:**
- `.zip` - ZIP archives
- `.tar.gz`, `.tgz` - Gzipped tar archives
- `.tar.bz2`, `.tbz` - Bzipped tar archives
- `.tar` - Uncompressed tar archives
- `.gz` - Gzipped files

**Returns:** Success message with extracted file listing

**Example:**
```python
from ai_researcher.ai_researcher_tools import unzip_file

result = unzip_file.invoke({
    "repo_root": "/path/to/project",
    "zip_path": "downloads/dataset.zip",
    "extract_to": "datasets/extracted"
})
```

### 6. list_kaggle_datasets

List datasets from Kaggle (requires Kaggle API credentials).

**Parameters:**
- `search_query` (str, optional): Search query to filter datasets
- `max_results` (int, optional): Maximum results (default: 20)

**Setup Required:**
1. Create Kaggle API credentials at https://www.kaggle.com/settings
2. Download `kaggle.json` and place in `~/.kaggle/`
3. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

**Returns:** List of datasets with titles, references, sizes, and download counts

**Example:**
```python
from ai_researcher.ai_researcher_tools import list_kaggle_datasets

result = list_kaggle_datasets.invoke({
    "search_query": "climate",
    "max_results": 10
})
```

### 7. download_kaggle_dataset

Download a dataset from Kaggle.

**Parameters:**
- `repo_root` (str): Root directory for downloads
- `dataset_ref` (str): Kaggle dataset reference (format: "username/dataset-name")
- `extract_path` (str, optional): Extraction directory (default: "datasets")

**Returns:** Success message with downloaded file listing

**Example:**
```python
from ai_researcher.ai_researcher_tools import download_kaggle_dataset

result = download_kaggle_dataset.invoke({
    "repo_root": "/path/to/project",
    "dataset_ref": "uciml/iris",
    "extract_path": "datasets/iris"
})
```

## Security Features

The dataset tools integrate with the existing sandbox security system:

1. **Sandboxed Execution**: All download and extraction commands run in a sandboxed environment
2. **Path Validation**: All file paths are validated to prevent directory traversal attacks
3. **Network Control**: Network access is explicitly enabled only for download operations
4. **Command Allowlisting**: Only safe commands (wget, curl, tar, unzip, etc.) are permitted
5. **User Confirmation**: Suspicious patterns trigger user confirmation prompts

## Common Workflows

### Workflow 1: Search and Download a Dataset

```python
from ai_researcher.ai_researcher_tools import (
    search_datasets_duckduckgo,
    download_file_python,
    unzip_file
)

# 1. Search for datasets
search_result = search_datasets_duckduckgo.invoke({
    "query": "iris dataset csv",
    "max_results": 5
})

# 2. Download the dataset (pick URL from search results)
download_result = download_file_python.invoke({
    "repo_root": ".",
    "url": "https://example.com/iris.zip",
    "output_path": "data/iris.zip"
})

# 3. Extract the archive
extract_result = unzip_file.invoke({
    "repo_root": ".",
    "zip_path": "data/iris.zip",
    "extract_to": "data/iris"
})
```

### Workflow 2: Download from Kaggle

```python
from ai_researcher.ai_researcher_tools import (
    list_kaggle_datasets,
    download_kaggle_dataset
)

# 1. List available datasets
datasets = list_kaggle_datasets.invoke({
    "search_query": "housing prices",
    "max_results": 10
})

# 2. Download a specific dataset
download_result = download_kaggle_dataset.invoke({
    "repo_root": ".",
    "dataset_ref": "harlfoxem/housesalesprediction",
    "extract_path": "datasets/housing"
})
```

### Workflow 3: Direct Download with wget

```python
from ai_researcher.ai_researcher_tools import download_file

# Download large file with timeout
result = download_file.invoke({
    "repo_root": ".",
    "url": "https://example.com/large-dataset.tar.gz",
    "output_path": "data/large-dataset.tar.gz",
    "timeout_s": 600  # 10 minutes
})
```

## Integration with AI Agents

All dataset tools are LangChain-compatible `@tool` functions that can be used directly with agents:

```python
from ai_researcher.ai_researcher_tools import (
    search_datasets_duckduckgo,
    download_file_python,
    unzip_file
)

# Available in agent toolkits
tools = [
    search_datasets_duckduckgo,
    download_file_python,
    unzip_file,
]

# Use with LangGraph or other agent frameworks
```

## Troubleshooting

### DuckDuckGo Search Not Working

If you get an import error:
```bash
pip install duckduckgo-search
```

### Kaggle Credentials Not Found

1. Sign up at https://www.kaggle.com
2. Go to Account settings → API → Create New API Token
3. This downloads `kaggle.json`
4. Move to `~/.kaggle/kaggle.json` and set permissions:
```bash
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### wget Not Found

On macOS:
```bash
brew install wget
```

On Ubuntu/Debian:
```bash
sudo apt-get install wget
```

Or use `download_file_python` instead, which doesn't require wget.

### Network Access Blocked

The sandbox allows network access only for dataset download operations. If you see network blocking errors, ensure you're using the dataset tools (which have `allow_network=True` set internally).

## File Size Limits

- Default timeout: 300 seconds (5 minutes)
- Maximum timeout: 300 seconds (enforced by sandbox)
- For larger files, consider:
  - Using `download_file` (wget) which is more robust than urllib
  - Increasing the `timeout_s` parameter
  - Downloading in chunks or using resumable downloads

## Supported Platforms

- **macOS**: Full support
- **Linux**: Full support  
- **Windows**: Python-based tools work; wget/curl require WSL or installation

## Future Enhancements

Potential additions to the dataset tools:
- HuggingFace datasets integration
- AWS S3 dataset downloads
- Google Cloud Storage support
- Torrent downloads for large datasets
- Progress bars for large downloads
- Checksum verification
- Automatic format detection and conversion

