#!/usr/bin/env python3
"""Example demonstrating dataset tools usage.

This script shows how to search for and download datasets using the ai_researcher_tools.
"""

import sys
from pathlib import Path

# Add parent directory to path to import ai_researcher
sys.path.insert(0, str(Path(__file__).parent))

from ai_researcher.ai_researcher_tools import (
    search_datasets_duckduckgo,
    download_file_python,
    list_dir,
)


def main():
    """Main demonstration function."""
    print("=" * 80)
    print("AI Researcher Dataset Tools Demo")
    print("=" * 80)

    # Example 1: Search for datasets
    print("\n[1] Searching for 'iris dataset csv' on DuckDuckGo...")
    print("-" * 80)

    search_result = search_datasets_duckduckgo.invoke({
        "query": "iris dataset csv",
        "max_results": 3
    })
    print(search_result)

    # Example 2: Download a sample dataset using Python urllib
    print("\n[2] Downloading sample iris dataset...")
    print("-" * 80)

    # Create a temporary datasets directory
    datasets_dir = Path("./example_datasets")
    datasets_dir.mkdir(exist_ok=True)

    download_result = download_file_python.invoke({
        "repo_root": str(Path.cwd()),
        "url": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
        "output_path": "example_datasets/iris.csv"
    })
    print(download_result)

    # Example 3: List downloaded files
    print("\n[3] Listing downloaded files...")
    print("-" * 80)

    list_result = list_dir.invoke({
        "repo_root": str(Path.cwd()),
        "path": "example_datasets"
    })
    print(list_result)

    # Example 4: Show sample of downloaded data
    print("\n[4] Showing first few lines of downloaded dataset...")
    print("-" * 80)

    iris_file = datasets_dir / "iris.csv"
    if iris_file.exists():
        with open(iris_file, 'r') as f:
            lines = f.readlines()[:6]  # Header + 5 data rows
            for line in lines:
                print(line.strip())

    print("\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print(f"\nDownloaded files are in: {datasets_dir.absolute()}")
    print("\nYou can now:")
    print("  - Explore the downloaded dataset")
    print("  - Try other dataset sources")
    print("  - Use download_file for wget-based downloads")
    print("  - Use unzip_file to extract compressed datasets")
    print("\nFor more examples, see: docs/DATASET_TOOLS.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

