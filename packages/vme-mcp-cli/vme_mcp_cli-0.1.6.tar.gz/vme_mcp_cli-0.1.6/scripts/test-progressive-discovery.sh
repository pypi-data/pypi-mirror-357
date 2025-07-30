#!/bin/bash

# Test Progressive Discovery VME FastMCP Server
echo "🧪 Testing Progressive Discovery Server..."

# Check if server file exists
if [ ! -f "src/servers/progressive_discovery_server.py" ]; then
    echo "❌ src/servers/progressive_discovery_server.py not found"
    exit 1
fi

# Check dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import fastmcp, httpx, dotenv" 2>/dev/null; then
    echo "❌ Missing dependencies. Install with: uv sync"
    exit 1
fi

# Check environment variables
if [ -z "$VME_API_BASE_URL" ] || [ -z "$VME_API_TOKEN" ]; then
    echo "❌ VME_API_BASE_URL and VME_API_TOKEN environment variables required"
    echo "   Load with: source .env"
    exit 1
fi

echo "✅ Environment ready"

# Test with MCP Inspector
echo "🔍 Testing with MCP Inspector..."
echo ""
echo "Expected workflow:"
echo "1. Server starts with only discovery tools"
echo "2. Call discover_capabilities() to see available groups" 
echo "3. Call discover_compute_infrastructure() to activate VM tools"
echo "4. VM creation tools become available (images, zones, instance types, etc.)"
echo ""

# Use npx to run MCP Inspector if available
if command -v npx &> /dev/null; then
    echo "🚀 Starting MCP Inspector with Progressive Discovery Server..."
    echo "   Server: src/servers/progressive_discovery_server.py"
    echo ""
    exec npx @modelcontextprotocol/inspector python3 src/servers/progressive_discovery_server.py
else
    echo "❌ npx not found. Install Node.js to use MCP Inspector"
    echo ""
    echo "💡 Alternative: Test manually with Python:"
    echo "   python3 src/servers/progressive_discovery_server.py"
    exit 1
fi