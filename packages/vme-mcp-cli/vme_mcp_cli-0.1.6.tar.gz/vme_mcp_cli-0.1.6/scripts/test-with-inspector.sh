#!/bin/bash
# Script to run FastMCP server with MCP Inspector for testing

set -e

echo "Starting MCP Inspector for testing..."
echo "Available servers:"
echo "  1. src/servers/my_server.py - Basic hello world server"  
echo "  2. src/servers/vme_server.py - VME Infrastructure server with 508 auto-generated tools"
echo "  3. src/servers/vme_server_filtered.py - VME Infrastructure server with filtered tools (faster)"
echo "  4. src/servers/progressive_discovery_server.py - Progressive discovery server (main)"
echo "  5. src/servers/static_discovery_server.py - Static discovery server (MCP Inspector)"
echo

# Default to filtered VME server for better performance
SERVER=${1:-src/servers/vme_server_filtered.py}

echo "Starting FastMCP dev environment with MCP Inspector..."
echo "Server: $SERVER"
echo
echo "Note: When Inspector launches:"
echo "  1. Select 'STDIO' from transport dropdown"
echo "  2. Click 'Connect' to start testing"
echo

# Run FastMCP dev command with the specified server
# Use the server file directly, not through fastmcp run
uv run fastmcp dev "$SERVER"