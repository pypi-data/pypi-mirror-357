# VME FastMCP Server - Source Organization

This directory contains the organized source code for the VME FastMCP Server project.

## Directory Structure

```
src/
├── servers/           # MCP Server Implementations
├── clients/           # MCP Client Implementations  
├── shared/            # Shared Utilities & Libraries
└── utils/             # Detection & Analysis Utilities
```

## 🖥️ Servers (`src/servers/`)

### Production Servers
- **`progressive_discovery_server.py`** - Main production server with progressive tool discovery
- **`static_discovery_server.py`** - Static server (workaround for MCP Inspector)

### Adaptive Servers  
- **`vme_server_adaptive_production.py`** - Production adaptive server with client detection
- **`vme_server_adaptive.py`** - Adaptive server with feature filtering

### Specialized Servers
- **`vme_server_filtered.py`** - Filtered server for specific use cases
- **`vme_server_dynamic.py`** - Dynamic server implementation
- **`vme_server.py`** - Basic server implementation

### Examples
- **`my_server.py`** - Hello world example server

## 🔧 Shared Libraries (`src/shared/`)

- **`api_utils.py`** - VME/Morpheus API utilities and platform detection
- **`platform_detector.py`** - Platform detection logic  
- **`route_manager.py`** - Route configuration and management

## 🕵️ Utilities (`src/utils/`)

- **`client_detection.py`** - MCP client detection and capability analysis

## 👥 Clients (`src/clients/`)

*Ready for CLI client and other client implementations*

## Import Paths

When importing from these modules, use the full path:

```python
# Shared utilities
from src.shared.api_utils import detect_platform_type
from src.shared.route_manager import RouteManager

# Client detection
from src.utils.client_detection import detect_client_capabilities

# Server implementations
from src.servers.progressive_discovery_server import ProgressiveDiscoveryServer
```

## Migration Notes

This structure was created to:
1. **Organize by functionality** - clear separation of servers, clients, utilities
2. **Prepare for CLI client** - dedicated `clients/` directory  
3. **Improve maintainability** - related code grouped together
4. **Support testing** - clear import paths for test files