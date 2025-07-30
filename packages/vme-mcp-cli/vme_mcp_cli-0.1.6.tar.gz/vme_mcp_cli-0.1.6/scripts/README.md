# Scripts

## test-with-inspector.sh

Launch the MCP Inspector to test FastMCP servers interactively.

### Usage

```bash
# Test filtered VME server (default - faster, includes appliance-settings)
./scripts/test-with-inspector.sh

# Test basic hello world server  
./scripts/test-with-inspector.sh src/servers/my_server.py

# Test full VME server (508 tools - slower)
./scripts/test-with-inspector.sh src/servers/vme_server.py

# Test filtered VME server explicitly
./scripts/test-with-inspector.sh src/servers/vme_server_filtered.py

# Test progressive discovery server (main production server)
./scripts/test-with-inspector.sh src/servers/progressive_discovery_server.py

# Test static discovery server (MCP Inspector compatible)
./scripts/test-with-inspector.sh src/servers/static_discovery_server.py
```

### What it does

1. Starts FastMCP development environment with MCP Inspector
2. Opens web UI for interactive testing
3. Allows you to explore and test all auto-generated tools

### Instructions

When the Inspector launches:
1. Select "STDIO" from the transport dropdown
2. Click "Connect" to start testing
3. Explore the available tools in the UI