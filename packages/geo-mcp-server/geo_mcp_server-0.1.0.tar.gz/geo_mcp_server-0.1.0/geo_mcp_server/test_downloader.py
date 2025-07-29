#!/usr/bin/env python3
"""Test script for the GEO downloader functionality."""
import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from geo_downloader import (
    download_geo_data,
    get_download_status,
    get_download_stats,
    list_downloaded_datasets,
    cleanup_downloads
)


async def test_downloader():
    """Test the downloader functionality."""
    print("Testing GEO Downloader...")
    
    # Test 1: Get download stats
    print("\n1. Getting download stats...")
    try:
        stats = get_download_stats()
        print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"Error getting stats: {e}")
    
    # Test 2: Check status of a non-existent download
    print("\n2. Checking status of non-existent download...")
    try:
        status = get_download_status("GSE12345", "gse")
        print(json.dumps(status, indent=2))
    except Exception as e:
        print(f"Error checking status: {e}")
    
    # Test 3: List downloaded datasets
    print("\n3. Listing downloaded datasets...")
    try:
        datasets = list_downloaded_datasets()
        print(f"Found {len(datasets)} downloaded datasets")
        if datasets:
            print(json.dumps(datasets[:2], indent=2))  # Show first 2
    except Exception as e:
        print(f"Error listing datasets: {e}")
    
    # Test 4: Try to download a small GEO dataset (this will fail if not found, but tests the function)
    print("\n4. Testing download function (will fail if dataset doesn't exist)...")
    try:
        # Try a small test dataset - this might fail but tests the function
        result = await download_geo_data("GSE12345", "gse")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Download test failed (expected for non-existent dataset): {e}")
    
    print("\nDownloader test completed!")


if __name__ == "__main__":
    asyncio.run(test_downloader()) 