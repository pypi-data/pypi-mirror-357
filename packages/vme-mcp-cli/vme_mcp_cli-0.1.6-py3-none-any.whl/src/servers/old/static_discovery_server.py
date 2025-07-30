#!/usr/bin/env python3
"""
Static Discovery VME FastMCP Server 
For testing - includes all compute resources from the start
"""

import json
import httpx
import os
import logging
from typing import Dict, List, Any
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from dotenv import load_dotenv
from src.shared.api_utils import detect_platform_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class StaticDiscoveryServer:
    """MCP Server with all compute resources available from start"""
    
    def __init__(self):
        # Load environment variables
        self.vme_api_base_url = os.getenv("VME_API_BASE_URL", "https://vmemgr01.lab.loc/api")
        self.vme_api_token = os.getenv("VME_API_TOKEN")
        
        if not self.vme_api_token:
            raise ValueError("VME_API_TOKEN environment variable is required")
        
        # Detect platform type
        self.platform_type = detect_platform_type(self.vme_api_base_url, self.vme_api_token)
        logger.info(f"🏗️ Detected platform: {self.platform_type}")
        
        # Load OpenAPI spec
        self.openapi_spec = self._load_openapi_spec()
        
        # Create HTTP client
        self.http_client = self._create_http_client()
        
    def _load_openapi_spec(self) -> dict:
        """Load the VME OpenAPI specification"""
        try:
            with open("hpe-vme-openapi.yaml", "r") as f:
                spec = json.load(f)
            
            # Update server URL
            spec["servers"] = [{"url": self.vme_api_base_url}]
            return spec
            
        except FileNotFoundError:
            logger.error("❌ OpenAPI spec file 'hpe-vme-openapi.yaml' not found")
            raise
    
    def _create_http_client(self) -> httpx.AsyncClient:
        """Create HTTP client for VME API"""
        return httpx.AsyncClient(
            base_url=self.vme_api_base_url,
            headers={
                "Authorization": f"Bearer {self.vme_api_token}",
                "Content-Type": "application/json"
            },
            verify=False  # Disable SSL verification for lab environment
        )
    
    def get_static_route_maps(self) -> List[RouteMap]:
        """Get static route maps with all compute resources available"""
        route_maps = [
            # Discovery tools (always available)
            RouteMap(pattern="^/api/license$", mcp_type=MCPType.TOOL),
            RouteMap(pattern="^/api/whoami$", mcp_type=MCPType.TOOL),
            RouteMap(pattern="^/api/appliance-settings$", mcp_type=MCPType.TOOL),
            
            # VM lifecycle tools
            RouteMap(pattern="^/api/instances$", mcp_type=MCPType.TOOL),
            RouteMap(pattern="^/api/instances/.*", mcp_type=MCPType.TOOL),
            
            # Compute resources (AVAILABLE FROM START)
            RouteMap(pattern="^/api/service-plans$", mcp_type=MCPType.RESOURCE),
            RouteMap(pattern="^/api/service-plans/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
            RouteMap(pattern="^/api/instance-types$", mcp_type=MCPType.RESOURCE),
            RouteMap(pattern="^/api/instance-types/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
            RouteMap(pattern="^/api/library/instance-types$", mcp_type=MCPType.RESOURCE),
            RouteMap(pattern="^/api/library/instance-types/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
            RouteMap(pattern="^/api/virtual-images$", mcp_type=MCPType.RESOURCE),
            RouteMap(pattern="^/api/virtual-images/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
            RouteMap(pattern="^/api/library/virtual-images$", mcp_type=MCPType.RESOURCE),
            RouteMap(pattern="^/api/library/virtual-images/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
            RouteMap(pattern="^/api/zones$", mcp_type=MCPType.RESOURCE),
            RouteMap(pattern="^/api/zones/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
            RouteMap(pattern="^/api/groups$", mcp_type=MCPType.RESOURCE),
            RouteMap(pattern="^/api/groups/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
            
            # Exclude everything else
            RouteMap(pattern=".*", mcp_type=MCPType.EXCLUDE)
        ]
        
        return route_maps

# Create server instance
server_instance = StaticDiscoveryServer()

# Create FastMCP server with ALL compute resources available from start
mcp = FastMCP.from_openapi(
    openapi_spec=server_instance.openapi_spec,
    client=server_instance.http_client,
    name=f"{server_instance.platform_type.upper()} Static Discovery Server",
    route_maps=server_instance.get_static_route_maps()
)

# Add basic discovery tool
@mcp.tool()
async def discover_resources() -> dict:
    """
    Discover all available VME resources for VM creation.
    All compute resources are available immediately.
    """
    
    return {
        "content": [{
            "type": "text", 
            "text": f"""
# {server_instance.platform_type.upper()} Resource Discovery

## ✅ All Compute Resources Available

This server exposes ALL compute resources from startup:

### 🌍 **Available Resources**:
- **Zones**: `vme://^/api/zones$` - Deployment zones
- **OS Images**: `vme://^/api/virtual-images$` - Available OS images  
- **Service Plans**: `vme://^/api/service-plans$` - T-shirt sizes
- **Instance Types**: `vme://^/api/instance-types$` - VM configurations
- **Groups**: `vme://^/api/groups$` - Resource groups

### 🖥️ **VM Management Tools**:
- `vme_compute_infrastructure_Get_All_Instances()` - List VMs
- `vme_compute_infrastructure_Create_an_Instance()` - Create VM
- `vme_virtual_images_Get_All_Virtual_Images()` - List OS images
- `vme_zones_Get_All_Zones()` - List zones
- `vme_service_plans_Get_All_Service_Plans()` - List service plans
- `vme_instance_types_Get_All_Instance_Types_for_Provisioning()` - List instance types

### 🎯 **VM Creation Workflow**:
1. Browse resources in MCP Inspector
2. Use tools to get available options
3. Create VM with `vme_compute_infrastructure_Create_an_Instance()`

**Note**: This is a STATIC version for testing. All resources are visible from startup.
"""
        }]
    }

def main():
    """Main entry point"""
    logger.info("🚀 Starting Static Discovery VME FastMCP Server...")
    
    try:
        logger.info("📡 Server ready with all compute resources available immediately.")
        logger.info("📦 Resources should be visible in MCP Inspector without any activation needed.")
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        raise

if __name__ == "__main__":
    main()