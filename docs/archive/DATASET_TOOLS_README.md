# Dataset Tools - Quick Start Guide

## What's New

The AI Researcher now includes powerful dataset search and download capabilities! You can now:

✅ Search for datasets using DuckDuckGo or Google  
✅ Download files from URLs (wget or Python)  
✅ Extract compressed archives (zip, tar.gz, etc.)  
✅ List and download Kaggle datasets  

## Quick Install

```bash
# Basic installation (includes Python-based downloads)
pip install -e .

# Full installation (includes DuckDuckGo search & Kaggle)
pip install -e ".[datasets]"
```

## Quick Examples

### Search for Datasets

```python
from ai_researcher.ai_researcher_tools import search_datasets_duckduckgo

result = search_datasets_duckduckgo.invoke({
    "query": "iris dataset csv",
    "max_results": 5
})
print(result)
```

### Download a Dataset

```python
from ai_researcher.ai_researcher_tools import download_file_python

result = download_file_python.invoke({
    "repo_root": ".",
    "url": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
    "output_path": "datasets/iris.csv"
})
print(result)
```

### Extract an Archive

```python
from ai_researcher.ai_researcher_tools import unzip_file

result = unzip_file.invoke({
    "repo_root": ".",
    "zip_path": "datasets/archive.zip",
    "extract_to": "datasets/extracted"
})
print(result)
```

## Run the Demo

```bash
python examples/demo_dataset_tools.py
```

This will:
1. Search for iris dataset
2. Download it
3. Show you the contents

## Available Tools

| Tool | Description | Dependencies |
|------|-------------|--------------|
| `search_datasets_duckduckgo` | Search datasets (no API key) | duckduckgo-search |
| `search_datasets_google` | Search datasets (needs API key) | None (uses stdlib) |
| `download_file` | Download with wget | wget command |
| `download_file_python` | Download with Python | None (uses stdlib) |
| `unzip_file` | Extract archives | tar/unzip commands |
| `list_kaggle_datasets` | List Kaggle datasets | kaggle |
| `download_kaggle_dataset` | Download from Kaggle | kaggle |

## Documentation

📖 **Full Documentation**: [docs/DATASET_TOOLS.md](docs/DATASET_TOOLS.md)

## Security

All dataset tools run in a sandboxed environment with:
- Path validation (no directory traversal)
- Command allowlisting (only safe commands)
- Controlled network access (only for downloads)
- User confirmation for suspicious patterns

## Need Help?

See the full documentation or run the demo script for examples!

