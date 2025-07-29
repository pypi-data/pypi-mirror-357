# GEO MCP Server

A Model Context Protocol (MCP) server that provides tools to search and download data from the NCBI GEO (Gene Expression Omnibus) database for gene expression data.

## Features

This MCP server provides the following tools:

### Search Tools
- `search_geo_profiles` - Search GEO Profiles database for gene expression profiles
- `search_geo_datasets` - Search GEO DataSets database for gene expression datasets  
- `search_geo_series` - Search GEO Series database for gene expression series
- `search_geo_samples` - Search GEO Samples database for gene expression samples
- `search_geo_platforms` - Search GEO Platforms database for microarray platforms

### Download Tools
- `download_geo_data` - Download GEO data for a specific ID and database type
- `download_geo_batch` - Download multiple GEO datasets in batch
- `get_download_status` - Check if a GEO dataset has been downloaded
- `list_downloaded_datasets` - List all downloaded datasets
- `get_download_stats` - Get overall download statistics and limits
- `cleanup_downloads` - Clean up downloaded files

## Important NCBI E-Utils Concepts

When working with NCBI E-Utils and GEO data, keep these key concepts in mind:

1. **Metadata vs. Full Data**: E-Utils only retrieves metadata stored within the Entrez system. For GEO databases, only metadata is available through E-Utils. To retrieve complete data tables or raw data files, you need to construct FTP URLs and download the data separately.

2. **Unique IDs (UIDs)**: Each Entrez record is identified by a unique integer ID (UID). These UIDs are used for both data input and output. Search history parameters (query_key and WebEnv) can also be used to identify previous search results.

3. **Field Qualifiers**: Your initial search can be refined using field qualifiers which can filter results based on data types, publication date ranges, and much more.

## Setup

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Configure API Access

Create a `config.json` file in the project root:

```json
{
    "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
    "email": "your_email@example.com",
    "api_key": "YOUR_API_KEY",
    "retmax": 20,
    "download_dir": "./downloads",
    "max_file_size_mb": 500,
    "max_total_downloads_mb": 2000,
    "max_concurrent_downloads": 3,
    "download_timeout_seconds": 300,
    "allowed_download_paths": ["./downloads", "/tmp/geo_downloads"]
}
```

**Required:**
- `email`: Your email address (required by NCBI E-utilities for all requests)

**Optional but Recommended:**
- `api_key`: Your NCBI API key (provides higher rate limits - 10 requests/second vs 3 requests/second)

**Optional:**
- `base_url`: Base URL for NCBI E-utilities (defaults to the standard URL)
- `retmax`: Maximum number of search results to return (default: 20)

**Download Configuration:**
- `download_dir`: Directory where downloads will be stored (default: "./downloads")
- `max_file_size_mb`: Maximum size of individual files to download in MB (default: 500)
- `max_total_downloads_mb`: Maximum total size of all downloads in MB (default: 2000)
- `max_concurrent_downloads`: Maximum number of concurrent downloads (default: 3)
- `download_timeout_seconds`: Timeout for download requests in seconds (default: 300)
- `allowed_download_paths`: List of allowed download paths for security (default: ["./downloads", "/tmp/geo_downloads"])

### 3. Get NCBI API Key (Recommended)

1. Go to [NCBI Account Settings](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)
2. Sign in to your NCBI account
3. Generate an API key
4. Add it to your `config.json` file

**Note**: The API key is automatically included in all requests when available, providing higher rate limits and better performance.

## Usage

### Running the MCP Server

```bash
python main.py
```

The server will start and listen for MCP connections via stdio.

### Running the HTTP Server

```bash
python mcp_http_server.py
```

The HTTP server will start on http://localhost:8001 and provide REST API endpoints for all tools.

### Search Tool Parameters

All search tools accept the following parameters:

- `term` (required): Search term for the GEO database
- `retmax` (optional): Maximum number of results to return (default: 20)

### Download Tool Parameters

#### `download_geo_data`
- `geo_id` (required): GEO ID to download (e.g., GSE12345, GSM12345)
- `db_type` (required): Database type: gds, gse, gsm, or gpl
- `output_dir` (optional): Output directory (must be in allowed paths)

#### `download_geo_batch`
- `geo_ids` (required): List of GEO IDs to download
- `db_type` (required): Database type: gds, gse, gsm, or gpl
- `output_dir` (optional): Output directory (must be in allowed paths)

#### `get_download_status`
- `geo_id` (required): GEO ID to check
- `db_type` (required): Database type: gds, gse, gsm, or gpl

#### `list_downloaded_datasets`
- `db_type` (optional): Database type filter: gds, gse, gsm, or gpl

#### `cleanup_downloads`
- `geo_id` (optional): Specific GEO ID to remove
- `db_type` (optional): Database type to remove all datasets from

### Example Tool Calls

```python
# Search for cancer-related gene expression profiles
await search_geo_profiles(term="cancer", retmax=10)

# Search for breast cancer datasets
await search_geo_datasets(term="breast cancer", retmax=5)

# Download a specific GEO series
await download_geo_data(geo_id="GSE12345", db_type="gse")

# Download multiple datasets in batch
await download_geo_batch(geo_ids=["GSE12345", "GSE67890"], db_type="gse")

# Check download status
await get_download_status(geo_id="GSE12345", db_type="gse")

# List all downloaded datasets
await list_downloaded_datasets()

# Get download statistics
await get_download_stats()

# Clean up specific download
await cleanup_downloads(geo_id="GSE12345", db_type="gse")
```

## Download Safety Features

The downloader includes several safety features to prevent abuse and resource exhaustion:

1. **File Size Limits**: Individual files cannot exceed the configured maximum size
2. **Total Size Limits**: Total downloads cannot exceed the configured maximum
3. **Path Validation**: Downloads can only be saved to allowed paths
4. **Concurrent Download Limits**: Limits the number of simultaneous downloads
5. **Timeout Protection**: Downloads timeout after a configured period
6. **Disk Space Checking**: Verifies sufficient disk space before downloading
7. **Automatic Cleanup**: Partial downloads are cleaned up on failure

## Integration with MCP Clients

This server can be integrated with any MCP-compatible client. The tools are automatically discovered and can be called with the appropriate parameters.

## Error Handling

The server includes proper error handling for:
- Invalid API credentials
- Network connectivity issues
- Invalid search parameters
- NCBI API rate limiting
- Download size limits
- Path validation errors
- Disk space issues
- Download timeouts

## Rate Limiting

NCBI E-utilities have rate limits:
- Without API key: 3 requests per second
- With API key: 10 requests per second

The server respects these limits and will return appropriate error messages if exceeded.

## Development

### Project Structure

```
geo_mcp_server/
├── main.py              # MCP server entry point
├── geo_tools.py         # MCP tool definitions
├── geo_downloader.py    # Download functionality
├── geo_profiles.py      # Original implementation (legacy)
├── mcp_http_server.py   # HTTP server for REST API
├── test_downloader.py   # Test script for downloader
├── config.json          # Configuration file
├── pyproject.toml       # Project dependencies
└── README.md            # This file
```

### Testing

Run the downloader test script:

```bash
python test_downloader.py
```

### Adding New Tools

To add new GEO search or download tools:

1. Add the tool function to `geo_tools.py`
2. Use the `@server.tool()` decorator
3. Include proper type hints and docstrings
4. The tool will be automatically available to MCP clients

## License

This project is open source. Please check the LICENSE file for details.
