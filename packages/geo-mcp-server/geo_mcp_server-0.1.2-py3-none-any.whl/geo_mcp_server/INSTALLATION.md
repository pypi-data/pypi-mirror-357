# Installation Guide

## Quick Start

### 1. Install the Package

```bash
pip install geo-mcp-server
```

### 2. Configure NCBI API Access

Create a configuration file:

```bash
mkdir ~/.geo-mcp
cat > ~/.geo-mcp/config.json << EOF
{
    "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
    "email": "your_email@example.com",
    "api_key": "YOUR_API_KEY"
}
EOF
```

**Required:**
- `email`: Your email address (required by NCBI E-utilities)

**Optional but Recommended:**
- `api_key`: Your NCBI API key (provides higher rate limits)

### 3. Set Environment Variable

```bash
export CONFIG_PATH=~/.geo-mcp/config.json
```

### 4. Test Installation

```bash
# Test MCP stdio server
geo-mcp-server --version

# Test HTTP server
geo-mcp-server --http --port 8001
```

## Claude Desktop Integration

### 1. Add to Claude Desktop Configuration

Add this to your Claude Desktop MCP configuration file:

```json
{
  "mcpServers": {
    "geo": {
      "command": "geo-mcp-server",
      "env": {
        "CONFIG_PATH": "~/.geo-mcp/config.json"
      }
    }
  }
}
```

### 2. Restart Claude Desktop

After adding the configuration, restart Claude Desktop to load the new MCP server.

### 3. Verify Integration

In Claude Desktop, you should now have access to GEO tools:
- `search_geo_profiles`
- `search_geo_datasets`
- `search_geo_series`
- `search_geo_samples`
- `search_geo_platforms`
- `download_geo_data`
- `download_geo_batch`
- And more...

## Development Installation

For development or contributing:

```bash
# Clone the repository
git clone https://github.com/yourusername/geo-mcp-server.git
cd geo-mcp-server

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Troubleshooting

### Common Issues

1. **Config file not found**
   - Ensure `CONFIG_PATH` environment variable is set
   - Check that the config file exists and is readable

2. **NCBI API errors**
   - Verify your email is correct
   - Check your API key if using one
   - Ensure you're not hitting rate limits

3. **Permission errors**
   - Make sure you have write permissions for the download directory
   - Check that the config file is readable

### Getting Help

- Check the [README.md](README.md) for detailed usage information
- Review the [CLAUDE_INTEGRATION.md](CLAUDE_INTEGRATION.md) for Claude-specific setup
- Open an issue on GitHub for bugs or feature requests 