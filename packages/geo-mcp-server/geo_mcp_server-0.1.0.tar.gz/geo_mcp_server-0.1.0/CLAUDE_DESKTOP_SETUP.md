# Claude Desktop Integration Guide

This guide shows how to integrate the GEO MCP server with Claude Desktop using the installed package.

## Prerequisites

1. **Install the package**:
   ```bash
   pip install geo-mcp-server
   ```

2. **Set up configuration**:
   ```bash
   # Create config directory
   mkdir -p ~/.geo-mcp
   
   # Copy template config
   cp geo_mcp_server/config_template.json ~/.geo-mcp/config.json
   
   # Edit the config file with your NCBI credentials
   nano ~/.geo-mcp/config.json
   ```

3. **Update your config.json** with your NCBI credentials:
   ```json
   {
     "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
     "email": "your_email@example.com",
     "api_key": "YOUR_API_KEY"
   }
   ```

## Claude Desktop Configuration

### Option 1: Simple Configuration (Recommended)

Add this to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "geo-mcp": {
      "command": "geo-mcp-server",
      "env": {
        "CONFIG_PATH": "~/.geo-mcp/config.json"
      }
    }
  }
}
```

### Option 2: Full Configuration with Download Settings

```json
{
  "mcpServers": {
    "geo-mcp": {
      "command": "geo-mcp-server",
      "env": {
        "CONFIG_PATH": "~/.geo-mcp/config.json",
        "DOWNLOAD_DIR": "~/.geo-mcp/downloads"
      }
    }
  }
}
```

### Option 3: Custom Download Directory

```json
{
  "mcpServers": {
    "geo-mcp": {
      "command": "geo-mcp-server",
      "env": {
        "CONFIG_PATH": "~/.geo-mcp/config.json",
        "DOWNLOAD_DIR": "/path/to/your/downloads"
      }
    }
  }
}
```

## Configuration File Locations

### macOS
- **Claude Desktop Config**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **GEO MCP Config**: `~/.geo-mcp/config.json`

### Windows
- **Claude Desktop Config**: `%APPDATA%\Claude\claude_desktop_config.json`
- **GEO MCP Config**: `%USERPROFILE%\.geo-mcp\config.json`

### Linux
- **Claude Desktop Config**: `~/.config/Claude/claude_desktop_config.json`
- **GEO MCP Config**: `~/.geo-mcp/config.json`

## Testing the Integration

1. **Restart Claude Desktop** after updating the configuration

2. **Test the connection** by asking Claude to:
   - List available GEO tools
   - Search for gene expression data
   - Download GEO datasets

3. **Example queries**:
   ```
   "What GEO tools are available?"
   "Search for cancer-related gene expression profiles"
   "Find breast cancer datasets in GEO"
   ```

## Troubleshooting

### Common Issues

1. **"Command not found: geo-mcp-server"**
   - Ensure the package is installed: `pip install geo-mcp-server`
   - Check your PATH: `which geo-mcp-server`

2. **"Config file not found"**
   - Verify the config file exists: `ls ~/.geo-mcp/config.json`
   - Check the CONFIG_PATH environment variable

3. **"NCBI API errors"**
   - Verify your email is correct in the config
   - Check your API key if using one
   - Ensure you're not hitting rate limits

4. **"Permission denied"**
   - Check file permissions: `chmod 644 ~/.geo-mcp/config.json`
   - Ensure download directory is writable

### Debug Mode

To run in debug mode, you can temporarily modify the configuration:

```json
{
  "mcpServers": {
    "geo-mcp": {
      "command": "geo-mcp-server",
      "env": {
        "CONFIG_PATH": "~/.geo-mcp/config.json",
        "DEBUG": "1"
      }
    }
  }
}
```

### Manual Testing

Test the server manually before using with Claude:

```bash
# Test the command
geo-mcp-server --version

# Test MCP protocol
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | geo-mcp-server

# Test HTTP server
geo-mcp-server --http --port 8001 &
curl http://localhost:8001/health
```

## Available Tools

Once integrated, you'll have access to these GEO tools:

- **`search_geo_profiles`** - Search gene expression profiles
- **`search_geo_datasets`** - Search curated datasets
- **`search_geo_series`** - Search gene expression series
- **`search_geo_samples`** - Search individual samples
- **`search_geo_platforms`** - Search microarray platforms
- **`download_geo_data`** - Download specific GEO data
- **`download_geo_batch`** - Download multiple datasets
- **`get_download_status`** - Check download status
- **`list_downloaded_datasets`** - List downloaded data
- **`get_download_stats`** - Get download statistics
- **`cleanup_downloads`** - Clean up downloaded files

## Support

If you encounter issues:

1. Check the [main README](README.md) for detailed documentation
2. Review the [installation guide](INSTALLATION.md)
3. Open an issue on the GitHub repository
4. Check the Claude Desktop logs for error messages 