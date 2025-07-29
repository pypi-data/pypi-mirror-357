import asyncio
import argparse
import os
import sys
import json
import shutil
from pathlib import Path

def setup_environment():
    """Set up the environment for the MCP server."""
    # Set the working directory to the script's directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # Set CONFIG_PATH environment variable if not already set
    if not os.getenv("CONFIG_PATH"):
        config_dir = Path.home() / ".geo-mcp"
        config_path = config_dir / "config.json"
        os.environ["CONFIG_PATH"] = str(config_path)

    # Get the config path
    config_path = Path(os.getenv("CONFIG_PATH", str(Path.home() / ".geo-mcp" / "config.json")))
    
    # If config file doesn't exist, create it from template
    if not config_path.exists():
        template_path = script_dir / "config_template.json"
        if template_path.exists():
            # Create parent directories if they don't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            # Copy template to config location
            shutil.copy2(template_path, config_path)
            print(f"Created default configuration file at: {config_path}", file=sys.stderr)
        else:
            print(f"Config file not found: {config_path}", file=sys.stderr)
            print(f"Template file not found: {template_path}", file=sys.stderr)
            print(f"Current working directory: {os.getcwd()}", file=sys.stderr)
            print(f"Available files in current directory: {list(Path('.').glob('*'))}", file=sys.stderr)
            sys.exit(1)

    # point any child-spawns at the venv python
    venv_bin = os.path.join(os.path.dirname(__file__), ".venv", "bin")
    os.environ["PATH"] = venv_bin + os.pathsep + os.environ.get("PATH", "")

def run_http_server(host: str = "localhost", port: int = 8001):
    """Run the HTTP server."""
    import uvicorn
    
    # Check if we're running as a package or as a script
    try:
        from .mcp_http_server import app
    except ImportError:
        # Running as script, use absolute import
        from mcp_http_server import app
    
    print(f"Starting HTTP server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

async def run_mcp_server():
    """Run the MCP stdio server."""
    import mcp.server.stdio
    
    # Check if we're running as a package or as a script
    try:
        from .geo_tools import server
    except ImportError:
        # Running as script, use absolute import
        from geo_tools import server
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point for the GEO MCP server."""
    parser = argparse.ArgumentParser(
        description="GEO MCP Server - Access GEO data through Model Context Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  geo-mcp-server                    # Run MCP stdio server
  geo-mcp-server --http             # Run HTTP server on localhost:8001
  geo-mcp-server --http --port 8080 # Run HTTP server on port 8080
  geo-mcp-server --http --host 0.0.0.0 --port 8080  # Run HTTP server on all interfaces
        """
    )
    
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run HTTP server instead of MCP stdio server"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for HTTP server (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port for HTTP server (default: 8001)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="geo-mcp-server 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    
    if args.http:
        # Run HTTP server
        run_http_server(args.host, args.port)
    else:
        # Run MCP stdio server
        asyncio.run(run_mcp_server())

if __name__ == "__main__":
    main()
