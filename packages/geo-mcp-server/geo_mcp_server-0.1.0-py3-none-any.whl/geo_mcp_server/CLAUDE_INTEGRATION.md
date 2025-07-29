# Claude Desktop Integration Guide

This guide explains how to use the GEO MCP server with Claude Desktop, including all available tools and their usage.

## Configuration

Your Claude Desktop configuration is set up in `claude_desktop_config.json`:

```json
{
    "mcpServers": {
      "geo-mcp": {
        "command": "/Users/matthiasflo/Documents/2025/GEO_MCP/geo_mcp_server/.venv/bin/python",
        "args": ["/Users/matthiasflo/Documents/2025/GEO_MCP/geo_mcp_server/main.py"],
        "env": {
          "PYTHONPATH": "/Users/matthiasflo/Documents/2025/GEO_MCP/geo_mcp_server",
          "PWD": "/Users/matthiasflo/Documents/2025/GEO_MCP/geo_mcp_server",
          "CONFIG_PATH": "/Users/matthiasflo/Documents/2025/GEO_MCP/geo_mcp_server/config.json",
          "DOWNLOAD_DIR": "/Users/matthiasflo/Documents/2025/GEO_MCP/geo_mcp_server/downloads"
        }
      }
    }
}
```

## Available Tools

### Search Tools

#### 1. `search_geo_profiles`
Search GEO Profiles database for gene expression profiles.

**Parameters:**
- `term` (required): Search term for GEO Profiles
- `retmax` (optional): Maximum number of results (default: 20)

**Example:**
```
Search for cancer-related gene expression profiles with a maximum of 10 results
```

#### 2. `search_geo_datasets`
Search GEO DataSets database for gene expression datasets.

**Parameters:**
- `term` (required): Search term for GEO DataSets
- `retmax` (optional): Maximum number of results (default: 20)

**Example:**
```
Search for breast cancer datasets with a maximum of 5 results
```

#### 3. `search_geo_series`
Search GEO Series database for gene expression series.

**Parameters:**
- `term` (required): Search term for GEO Series
- `retmax` (optional): Maximum number of results (default: 20)

**Example:**
```
Search for BRCA1 gene expression series with a maximum of 15 results
```

#### 4. `search_geo_samples`
Search GEO Samples database for gene expression samples.

**Parameters:**
- `term` (required): Search term for GEO Samples
- `retmax` (optional): Maximum number of results (default: 20)

**Example:**
```
Search for cancer samples with a maximum of 10 results
```

#### 5. `search_geo_platforms`
Search GEO Platforms database for microarray platforms.

**Parameters:**
- `term` (required): Search term for GEO Platforms
- `retmax` (optional): Maximum number of results (default: 20)

**Example:**
```
Search for Affymetrix platforms with a maximum of 5 results
```

### Download Tools

#### 6. `download_geo_data`
Download GEO data for a specific ID and database type.

**Parameters:**
- `geo_id` (required): GEO ID to download (e.g., GSE12345, GSM12345)
- `db_type` (required): Database type: gds, gse, gsm, or gpl
- `output_dir` (optional): Output directory (must be in allowed paths)

**Example:**
```
Download the GEO series GSE12345
```

#### 7. `download_geo_batch`
Download multiple GEO datasets in batch.

**Parameters:**
- `geo_ids` (required): List of GEO IDs to download
- `db_type` (required): Database type: gds, gse, gsm, or gpl
- `output_dir` (optional): Output directory (must be in allowed paths)

**Example:**
```
Download multiple GEO series: GSE12345, GSE67890, and GSE11111
```

#### 8. `get_download_status`
Check if a GEO dataset has been downloaded.

**Parameters:**
- `geo_id` (required): GEO ID to check
- `db_type` (required): Database type: gds, gse, gsm, or gpl

**Example:**
```
Check if GSE12345 has been downloaded
```

#### 9. `list_downloaded_datasets`
List all downloaded datasets.

**Parameters:**
- `db_type` (optional): Database type filter: gds, gse, gsm, or gpl

**Example:**
```
List all downloaded GEO series datasets
```

#### 10. `get_download_stats`
Get overall download statistics and limits.

**Parameters:**
- None

**Example:**
```
Get download statistics and current usage
```

#### 11. `cleanup_downloads`
Clean up downloaded files.

**Parameters:**
- `geo_id` (optional): Specific GEO ID to remove
- `db_type` (optional): Database type to remove all datasets from

**Example:**
```
Remove the downloaded dataset GSE12345
```

## Usage Examples

### Complete Workflow Example

1. **Search for datasets:**
   ```
   Search for breast cancer gene expression datasets
   ```

2. **Download a specific dataset:**
   ```
   Download the GEO series GSE12345
   ```

3. **Check download status:**
   ```
   Check if GSE12345 has been downloaded
   ```

4. **List all downloads:**
   ```
   List all downloaded datasets
   ```

5. **Get usage statistics:**
   ```
   Get download statistics
   ```

### Advanced Usage

#### Batch Operations
```
Download multiple GEO series: GSE12345, GSE67890, GSE11111, and GSE22222
```

#### Filtered Searches
```
Search for cancer-related gene expression profiles with a maximum of 5 results
```

#### Cleanup Operations
```
Remove all downloaded GEO series datasets
```

## Safety Features

The downloader includes several safety features:

1. **File Size Limits**: Individual files cannot exceed 500MB (configurable)
2. **Total Size Limits**: Total downloads cannot exceed 2000MB (configurable)
3. **Path Validation**: Downloads can only be saved to allowed paths
4. **Concurrent Download Limits**: Maximum 3 simultaneous downloads
5. **Timeout Protection**: Downloads timeout after 300 seconds
6. **Disk Space Checking**: Verifies sufficient disk space before downloading
7. **Automatic Cleanup**: Partial downloads are cleaned up on failure

## Configuration Limits

Current configuration limits (from `config.json`):
- Maximum file size: 500MB
- Maximum total downloads: 2000MB
- Maximum concurrent downloads: 3
- Download timeout: 300 seconds
- Allowed download paths: `./downloads`, `/tmp/geo_downloads`

## Troubleshooting

### Common Issues

1. **"Config file not found"**: Ensure the CONFIG_PATH environment variable points to the correct config.json file
2. **"Download path not allowed"**: Check that the download directory is in the allowed_download_paths list
3. **"File size limit exceeded"**: The file is too large for the current configuration
4. **"Total download size limit exceeded"**: You've reached the maximum allowed download size

### Reset Downloads

To reset all downloads:
```
Remove all downloaded datasets
```

## Integration Notes

- All tools are automatically available in Claude Desktop
- Tools return JSON responses that Claude can parse and understand
- Download progress and errors are clearly reported
- The server respects NCBI rate limits (3 requests/second without API key, 10 with API key) 