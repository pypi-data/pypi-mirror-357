#!/usr/bin/env python3
"""
Test script for the GEO MCP server.
This script tests basic functionality without requiring the full MCP client.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from geo_tools import server, BASE_URL, EMAIL, API_KEY


async def test_server():
    """Test the server functionality."""
    print("Testing GEO MCP Server...")
    
    # Test configuration loading
    print(f"Base URL: {BASE_URL}")
    print(f"Email: {EMAIL}")
    print(f"API Key configured: {'Yes' if API_KEY else 'No'}")
    
    # Test tool listing
    try:
        tools = await server.handle_list_tools()
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Error listing tools: {e}")
        return False
    
    # Test a simple search
    try:
        result = await server.handle_call_tool("search_geo_series", {"term": "cancer", "retmax": 2})
        print("Test search successful!")
        print(f"Result type: {type(result)}")
        if result and len(result) > 0:
            print(f"Result content length: {len(result[0].text)}")
    except Exception as e:
        print(f"Error testing search: {e}")
        return False
    
    print("All tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1) 