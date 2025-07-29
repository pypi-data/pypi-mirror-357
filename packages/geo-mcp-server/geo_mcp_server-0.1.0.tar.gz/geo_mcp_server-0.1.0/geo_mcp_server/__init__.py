"""
GEO MCP Server - A Model Context Protocol server for accessing GEO data.

This package provides tools to search and download data from the NCBI GEO
(Gene Expression Omnibus) database for gene expression data.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .geo_tools import (
    search_geo_profiles,
    search_geo_datasets,
    search_geo_series,
    search_geo_samples,
    search_geo_platforms,
)

from .geo_downloader import (
    download_geo_data,
    download_geo_batch,
    get_download_status,
    list_downloaded_datasets,
    get_download_stats,
    cleanup_downloads,
)

__all__ = [
    # Search tools
    "search_geo_profiles",
    "search_geo_datasets", 
    "search_geo_series",
    "search_geo_samples",
    "search_geo_platforms",
    # Download tools
    "download_geo_data",
    "download_geo_batch",
    "get_download_status",
    "list_downloaded_datasets",
    "get_download_stats",
    "cleanup_downloads",
] 