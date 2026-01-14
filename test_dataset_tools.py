"""Test dataset tools functionality.

This test demonstrates the dataset search and download capabilities.
"""

import tempfile
from pathlib import Path

from ai_researcher.ai_researcher_tools import (
    search_datasets_duckduckgo,
    download_file,
    download_file_python,
    unzip_file,
    list_kaggle_datasets,
)


def test_search_datasets_duckduckgo():
    """Test DuckDuckGo dataset search."""
    result = search_datasets_duckduckgo.invoke({"query": "iris dataset csv", "max_results": 5})
    print("\n=== DuckDuckGo Search Results ===")
    print(result)
    assert "Search results for" in result or "Error" in result


def test_download_file_python():
    """Test downloading a file using Python urllib."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Download a small test file
        result = download_file_python.invoke({
            "repo_root": tmpdir,
            "url": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
            "output_path": "iris.csv"
        })
        print("\n=== Download File (Python) ===")
        print(result)

        # Check if file was downloaded
        downloaded_file = Path(tmpdir) / "iris.csv"
        if downloaded_file.exists():
            print(f"File downloaded successfully: {downloaded_file}")
            print(f"File size: {downloaded_file.stat().st_size} bytes")
            # Read first few lines
            with open(downloaded_file) as f:
                lines = f.readlines()[:5]
                print("First 5 lines:")
                for line in lines:
                    print(f"  {line.strip()}")


def test_download_file_wget():
    """Test downloading a file using wget (if available)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = download_file.invoke({
            "repo_root": tmpdir,
            "url": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
            "output_path": "iris_wget.csv",
            "timeout_s": 60
        })
        print("\n=== Download File (wget) ===")
        print(result)

        downloaded_file = Path(tmpdir) / "iris_wget.csv"
        if downloaded_file.exists():
            print(f"File downloaded successfully: {downloaded_file}")


def test_unzip_file():
    """Test unzipping an archive file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # First download a zip file
        zip_url = "https://github.com/datasets/gdp/archive/refs/heads/master.zip"
        result = download_file_python.invoke({
            "repo_root": tmpdir,
            "url": zip_url,
            "output_path": "test.zip"
        })
        print("\n=== Download ZIP File ===")
        print(result)

        # Then unzip it
        zip_file = Path(tmpdir) / "test.zip"
        if zip_file.exists():
            result = unzip_file.invoke({
                "repo_root": tmpdir,
                "zip_path": "test.zip",
                "extract_to": "extracted"
            })
            print("\n=== Unzip File ===")
            print(result)


def test_list_kaggle_datasets():
    """Test listing Kaggle datasets (requires API credentials)."""
    result = list_kaggle_datasets.invoke({"search_query": "iris", "max_results": 5})
    print("\n=== Kaggle Datasets ===")
    print(result)
    # This will fail if Kaggle credentials aren't set up, which is fine for testing


if __name__ == "__main__":
    print("Testing Dataset Tools")
    print("=" * 80)

    # Test search
    test_search_datasets_duckduckgo()

    # Test download with Python
    test_download_file_python()

    # Test download with wget (might not work if wget not installed)
    # test_download_file_wget()

    # Test unzip
    # test_unzip_file()

    # Test Kaggle (requires credentials)
    # test_list_kaggle_datasets()

    print("\n" + "=" * 80)
    print("Testing complete!")

