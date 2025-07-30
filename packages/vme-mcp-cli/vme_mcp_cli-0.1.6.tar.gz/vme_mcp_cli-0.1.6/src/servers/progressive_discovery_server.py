#!/usr/bin/env python3
"""
Progressive Discovery VME FastMCP Server
Organizes tools into logical groups that LLMs can discover progressively
"""

import json
import yaml
import httpx
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType, OpenAPITool
from fastmcp.utilities.openapi import parse_openapi_to_http_routes, format_description_with_responses, _combine_schemas
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.shared.api_utils import detect_platform_type

# Configure logging - send to stderr only (stdout is for MCP protocol)
logging.basicConfig(
    level=logging.CRITICAL,  # Only critical errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]  # Use stderr, not stdout
)

# Suppress FastMCP and related library logging
logging.getLogger("fastmcp").setLevel(logging.CRITICAL)
logging.getLogger("fastmcp.utilities.openapi").setLevel(logging.CRITICAL)
logging.getLogger("fastmcp.server.openapi").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ProgressiveDiscoveryServer:
    """MCP Server with progressive tool discovery by functional groups"""
    
    def __init__(self):
        # Load environment variables
        self.vme_api_base_url = os.getenv("VME_API_BASE_URL", "https://vmemgr01.lab.loc")
        self.vme_api_token = os.getenv("VME_API_TOKEN")
        
        if not self.vme_api_token:
            raise ValueError(
                "VME_API_TOKEN environment variable is required.\n\n"
                "Configure in your client config file (~/.config/vme-cli/config.yaml):\n"
                "  server:\n"
                "    servers:\n"
                "      your-server:\n"
                "        env:\n"
                "          VME_API_TOKEN: 'your-token-here'\n\n"
                "Or set the environment variable:\n"
                "  export VME_API_TOKEN='your-token-here'"
            )
        
        # Connection status tracking
        self.api_connected = False
        self.connection_error = None
        self.platform_type = "vme"  # Default to vme instead of unknown
        
        # Try to detect platform type (but don't fail if unreachable)
        try:
            self.platform_type = detect_platform_type(self.vme_api_base_url, self.vme_api_token)
            self.api_connected = True
            logger.info(f"🏗️ Detected platform: {self.platform_type}")
        except Exception as e:
            self.connection_error = str(e)
            logger.warning(f"⚠️ Could not connect to VME API: {e}")
            logger.warning(f"⚠️ Server starting in offline mode - tools will return connection errors")
        
        # Load OpenAPI spec and extract overrides
        self.openapi_spec, self.tool_overrides = self._load_openapi_spec()
        
        # Create HTTP client
        self.http_client = self._create_http_client()
        
        # Tool group definitions
        self.tool_groups = self._define_tool_groups()
        
        # Initially only discovery tools are available
        self.active_groups = set()
        
        # Parse OpenAPI and create tool registry
        self.tool_registry = self._parse_openapi_to_tools()
        logger.info(f"📚 Parsed OpenAPI spec into tool registry:")
        for group_name, tools in self.tool_registry.items():
            logger.info(f"   {group_name}: {len(tools)} tools")
        
    def _load_openapi_spec(self) -> tuple[dict, dict]:
        """Load the VME OpenAPI specification with augmentations and extract overrides"""
        try:
            # Load base OpenAPI spec (YAML format)
            with open("hpe-vme-openapi.yaml", "r") as f:
                spec = yaml.safe_load(f)
            
            # Try to load augmentations (optional)
            augmentations = None
            tool_overrides = {}
            augmentation_file = "vme-openapi-augmentations.yaml"
            if os.path.exists(augmentation_file):
                try:
                    with open(augmentation_file, "r") as f:
                        augmentations = yaml.safe_load(f)
                    logger.info(f"✅ Loaded OpenAPI augmentations from {augmentation_file}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not load augmentations: {e}")
            
            # Process augmentations if available
            if augmentations and "paths" in augmentations:
                for path, methods in augmentations["paths"].items():
                    if path in spec.get("paths", {}):
                        for method, augment_data in methods.items():
                            if method in spec["paths"][path]:
                                # Check for tool override
                                if augment_data.get("x-override-tool") and "x-tool-definition" in augment_data:
                                    # Store the override definition
                                    override_key = f"{method.upper()} {path}"
                                    tool_overrides[override_key] = augment_data["x-tool-definition"]
                                    logger.info(f"🔧 Found tool override for {override_key}")
                                    # Don't merge this into the spec - handle it separately
                                    continue
                                
                                # Merge x-augment-description into description
                                if "x-augment-description" in augment_data:
                                    original_desc = spec["paths"][path][method].get("description", "")
                                    augmented_desc = augment_data["x-augment-description"]
                                    # Combine descriptions
                                    spec["paths"][path][method]["description"] = (
                                        original_desc + augmented_desc
                                    ).strip()
                                    logger.debug(f"✅ Augmented {method.upper()} {path}")
                                
                                # Also augment summary if provided
                                if "x-augment-summary" in augment_data:
                                    spec["paths"][path][method]["summary"] = augment_data["x-augment-summary"]
            
            # Update server URL
            spec["servers"] = [{"url": self.vme_api_base_url}]
            return spec, tool_overrides
            
        except FileNotFoundError:
            logger.error("❌ OpenAPI spec file 'hpe-vme-openapi.yaml' not found")
            raise
    
    def _create_http_client(self) -> httpx.AsyncClient:
        """Create HTTP client for VME API"""
        # Create a wrapped client that checks connection status
        class ConnectionAwareClient(httpx.AsyncClient):
            def __init__(self, server_instance, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.server_instance = server_instance
            
            async def request(self, *args, **kwargs):
                # Check if API is connected before making requests
                if not self.server_instance.api_connected:
                    # Provide instructive error message
                    error_msg = f"""VME API Connection Failed

**Issue**: Cannot reach VME API at {self.server_instance.vme_api_base_url}
**Error**: {self.server_instance.connection_error}

**Next Steps**:
1. Run `check_vme_connection_status()` for detailed diagnostics
2. Common fixes:
   - If DNS resolution failed: Check network connectivity
   - If connection refused: Verify server is running
   - If authentication failed: Update API token
3. After fixing, run `check_vme_connection_status()` to retry connection

**Note**: All API tools will fail until connection is restored."""
                    raise httpx.ConnectError(error_msg)
                return await super().request(*args, **kwargs)
        
        return ConnectionAwareClient(
            self,
            base_url=self.vme_api_base_url,
            headers={
                "Authorization": f"Bearer {self.vme_api_token}",
                "Content-Type": "application/json"
            },
            verify=False  # Disable SSL verification for lab environment
        )
    
    def _define_tool_groups(self) -> Dict[str, Dict[str, Any]]:
        """Define logical tool groups for progressive discovery"""
        return {
            "discovery": {
                "name": "Discovery & Capabilities",
                "description": "Tools to discover available capabilities and tool groups",
                "routes": [
                    RouteMap(pattern="^/api/license$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/whoami$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/appliance-settings$", mcp_type=MCPType.TOOL),
                ],
                "always_active": True
            },
            
            "compute": {
                "name": "Compute Infrastructure",
                "description": "Virtual machines, service plans (t-shirt sizes), images, and compute resources",
                "routes": [
                    # VM lifecycle
                    RouteMap(pattern="^/api/instances$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/instances/.*", mcp_type=MCPType.TOOL),
                    
                    # Service Plans (T-shirt sizes: small, medium, large)
                    RouteMap(pattern="^/api/service-plans$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/service-plans/.*", mcp_type=MCPType.TOOL),
                    
                    # Instance Types (for provisioning - platform dependent)
                    RouteMap(pattern="^/api/instance-types$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/instance-types/.*", mcp_type=MCPType.TOOL),
                    
                    # Library Instance Types (Morpheus-specific)
                    RouteMap(pattern="^/api/library/instance-types$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/library/instance-types/.*", mcp_type=MCPType.TOOL),
                    
                    # OS Images (VME uses /api/virtual-images, Morpheus has /api/library/virtual-images)
                    RouteMap(pattern="^/api/virtual-images$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/virtual-images/.*", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/library/virtual-images$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/library/virtual-images/.*", mcp_type=MCPType.TOOL),
                    
                    # Zones and placement
                    RouteMap(pattern="^/api/zones$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/zones/.*", mcp_type=MCPType.TOOL),
                    
                    # Groups for organization
                    RouteMap(pattern="^/api/groups$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/groups/.*", mcp_type=MCPType.TOOL),
                ]
            },
            
            "networking": {
                "name": "Network Infrastructure", 
                "description": "Networks, security groups, load balancers, and connectivity",
                "routes": [
                    # Networks
                    RouteMap(pattern="^/api/networks$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/networks/.*", mcp_type=MCPType.TOOL),
                    
                    # Security groups
                    RouteMap(pattern="^/api/security-groups$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/security-groups/.*", mcp_type=MCPType.TOOL),
                    
                    # Load balancers
                    RouteMap(pattern="^/api/load-balancers$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/load-balancers/.*", mcp_type=MCPType.TOOL),
                    
                    # Network types and pools
                    RouteMap(pattern="^/api/library/network-types$", mcp_type=MCPType.RESOURCE),
                    RouteMap(pattern="^/api/network-pools$", mcp_type=MCPType.RESOURCE),
                ]
            },
            
            "storage": {
                "name": "Storage Infrastructure",
                "description": "Volumes, snapshots, backups, and storage management", 
                "routes": [
                    # Storage volumes
                    RouteMap(pattern="^/api/storage-volumes$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/storage-volumes/.*", mcp_type=MCPType.TOOL),
                    
                    # Snapshots
                    RouteMap(pattern="^/api/snapshots$", mcp_type=MCPType.TOOL), 
                    RouteMap(pattern="^/api/snapshots/.*", mcp_type=MCPType.TOOL),
                    
                    # Backups
                    RouteMap(pattern="^/api/backups$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/backups/.*", mcp_type=MCPType.TOOL),
                    
                    # Storage types
                    RouteMap(pattern="^/api/library/storage-types$", mcp_type=MCPType.RESOURCE),
                ]
            },
            
            "monitoring": {
                "name": "Monitoring & Observability",
                "description": "Health checks, monitoring, logs, and performance metrics",
                "routes": [
                    RouteMap(pattern="^/api/health$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/monitoring$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/monitoring/.*", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/logs$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/stats$", mcp_type=MCPType.TOOL),
                ]
            },
            
            "management": {
                "name": "Platform Management", 
                "description": "Users, accounts, policies, and platform administration",
                "routes": [
                    # Account management
                    RouteMap(pattern="^/api/accounts$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/accounts/.*", mcp_type=MCPType.TOOL),
                    
                    # User management
                    RouteMap(pattern="^/api/users$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/users/.*", mcp_type=MCPType.TOOL),
                    
                    # Policies and roles
                    RouteMap(pattern="^/api/policies$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/roles$", mcp_type=MCPType.TOOL),
                    
                    # Cloud integrations
                    RouteMap(pattern="^/api/clouds$", mcp_type=MCPType.TOOL),
                    RouteMap(pattern="^/api/clouds/.*", mcp_type=MCPType.TOOL),
                ]
            }
        }
    
    def _parse_openapi_to_tools(self) -> Dict[str, List[OpenAPITool]]:
        """Parse OpenAPI spec and create tools organized by group"""
        # Parse routes from OpenAPI spec
        http_routes = parse_openapi_to_http_routes(self.openapi_spec)
        
        # Dictionary to store tools by group
        tools_by_group = {
            group_name: [] for group_name in self.tool_groups.keys()
        }
        
        # Process each route
        for route in http_routes:
            # Determine which group this route belongs to
            group_name = None
            route_type = None
            
            # Check each group's route maps
            for gname, group_config in self.tool_groups.items():
                for route_map in group_config["routes"]:
                    # Check if route matches this route map
                    if self._route_matches(route, route_map):
                        if route_map.mcp_type == MCPType.TOOL:
                            group_name = gname
                            route_type = MCPType.TOOL
                            break
                if group_name:
                    break
            
            # Skip if route doesn't match any group or isn't a tool
            if not group_name or route_type != MCPType.TOOL:
                continue
            
            # Check if this route has an override
            override_key = f"{route.method.upper()} {route.path}"
            if override_key in self.tool_overrides:
                # Create tool from override definition
                tool = self._create_override_tool(route, group_name, self.tool_overrides[override_key])
                if tool:
                    tools_by_group[group_name].append(tool)
                    logger.info(f"🔄 Created override tool for {override_key}")
            else:
                # Create normal OpenAPITool instance
                tool = self._create_openapi_tool(route, group_name)
                if tool:
                    tools_by_group[group_name].append(tool)
        
        return tools_by_group
    
    def _route_matches(self, route, route_map: RouteMap) -> bool:
        """Check if a route matches a route map pattern"""
        import re
        
        # Check pattern match
        if not re.match(route_map.pattern, route.path):
            return False
        
        # Check method match if specified
        if hasattr(route_map, 'methods') and route_map.methods != '*':
            methods = route_map.methods if isinstance(route_map.methods, list) else [route_map.methods]
            if route.method not in methods:
                return False
        
        return True
    
    def _create_openapi_tool(self, route, group_name: str) -> OpenAPITool:
        """Create an OpenAPITool instance from a route"""
        try:
            # Generate tool name
            tool_name = self._generate_tool_name(route, group_name)
            
            # Combine schemas for parameters
            combined_schema = _combine_schemas(route)
            
            # Format description
            base_description = (
                route.description 
                or route.summary 
                or f"Executes {route.method} {route.path}"
            )
            
            enhanced_description = format_description_with_responses(
                base_description=base_description,
                responses=route.responses,
                parameters=route.parameters,
                request_body=route.request_body,
            )
            
            # Get tags from route and group
            route_tags = set(route.tags or [])
            group_tags = set(self.tool_groups[group_name].get("tags", []))
            
            # Create tool
            tool = OpenAPITool(
                client=self.http_client,
                route=route,
                name=tool_name,
                description=enhanced_description,
                parameters=combined_schema,
                tags=route_tags | group_tags | {group_name},
                timeout=None
            )
            
            return tool
            
        except Exception as e:
            logger.warning(f"Failed to create tool for {route.method} {route.path}: {e}")
            return None
    
    def _generate_tool_name(self, route, group_name: str) -> str:
        """Generate a unique tool name from route info - matching FastMCP's approach"""
        import re
        
        # First try operation ID
        if route.operation_id:
            # If there's a double underscore, use the first part
            name = route.operation_id.split("__")[0]
        # Then try summary (this is what FastMCP prefers)
        elif route.summary:
            name = route.summary
        # Fallback to method + path
        else:
            name = f"{route.method}_{route.path}"
        
        # Slugify (same as FastMCP's _slugify function)
        # Replace spaces and common separators with underscores
        name = re.sub(r"[\s\-\.]+", "_", name)
        # Remove non-alphanumeric characters except underscores
        name = re.sub(r"[^a-zA-Z0-9_]", "", name)
        # Remove multiple consecutive underscores
        name = re.sub(r"_+", "_", name)
        # Remove leading/trailing underscores
        name = name.strip("_")
        
        # Truncate to reasonable length
        if len(name) > 40:
            name = name[:40]
        
        # Add group prefix for clarity (matching VME style)
        return f"{self.platform_type}_{group_name}_{name}"
    
    def _create_override_tool(self, route, group_name: str, override_def: dict) -> OpenAPITool:
        """Create a tool from an override definition"""
        try:
            # Use the name from override or generate one
            tool_name = override_def.get("name")
            if not tool_name:
                tool_name = self._generate_tool_name(route, group_name)
            
            # Get description from override
            description = override_def.get("description", f"Override for {route.method} {route.path}")
            
            # Get parameters schema from override
            parameters_schema = override_def.get("parameters", {})
            
            # Get tags from route and group
            route_tags = set(route.tags or [])
            group_tags = set(self.tool_groups[group_name].get("tags", []))
            override_tags = set(override_def.get("tags", []))
            
            # Create a custom OpenAPITool with the override schema
            tool = OpenAPITool(
                client=self.http_client,
                route=route,
                name=tool_name,
                description=description,
                parameters=parameters_schema,
                tags=route_tags | group_tags | override_tags | {group_name, "override"},
                timeout=override_def.get("timeout")
            )
            
            logger.info(f"✅ Created override tool '{tool_name}' for {route.method} {route.path}")
            return tool
            
        except Exception as e:
            logger.error(f"Failed to create override tool for {route.method} {route.path}: {e}")
            return None
    
    def get_active_route_maps(self) -> List[RouteMap]:
        """Get route maps for currently active tool groups"""
        route_maps = []
        
        for group_name, group_config in self.tool_groups.items():
            # Always include discovery tools
            if group_config.get("always_active", False):
                route_maps.extend(group_config["routes"])
            # Include activated groups
            elif group_name in self.active_groups:
                route_maps.extend(group_config["routes"])
        
        # Add exclusion pattern for everything else
        route_maps.append(RouteMap(pattern=".*", mcp_type=MCPType.EXCLUDE))
        
        return route_maps
    
    def activate_tool_group(self, group_name: str) -> bool:
        """Activate a tool group, making its tools available"""
        if group_name not in self.tool_groups:
            return False
            
        if group_name in self.active_groups:
            logger.info(f"Tool group '{group_name}' is already active")
            return True
            
        # Add tools from this group to the MCP server
        tools_to_add = self.tool_registry.get(group_name, [])
        added_count = 0
        
        for tool in tools_to_add:
            try:
                mcp.add_tool(tool)
                added_count += 1
            except Exception as e:
                logger.warning(f"Failed to add tool {tool.name}: {e}")
        
        self.active_groups.add(group_name)
        logger.info(f"🔧 Activated tool group '{group_name}' with {added_count} tools")
        return True
    
    def get_current_tool_count(self) -> int:
        """Get count of currently available tools"""
        # Access the tool manager's tools dictionary
        if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
            return len(mcp._tool_manager._tools)
        return 0
    
    def get_available_groups(self) -> Dict[str, Dict[str, str]]:
        """Get information about available tool groups"""
        return {
            name: {
                "name": config["name"],
                "description": config["description"],
                "active": name in self.active_groups or config.get("always_active", False),
                "tool_count": len(self.tool_registry.get(name, []))
            }
            for name, config in self.tool_groups.items()
        }

# Create server instance
server_instance = ProgressiveDiscoveryServer()

# Create basic FastMCP server without OpenAPI tools
mcp = FastMCP(
    name=f"{server_instance.platform_type.upper()} Progressive Discovery Server"
)

# Activate discovery group by default (contains basic tools like license, whoami, appliance-settings)
if "discovery" in server_instance.tool_registry:
    server_instance.activate_tool_group("discovery")

# Add custom discovery tools
@mcp.tool()
async def discover_capabilities() -> dict:
    """
    Discover available tool groups and platform capabilities.
    Call this first to see what functionality is available.
    """
    groups = server_instance.get_available_groups()
    current_tool_count = server_instance.get_current_tool_count()
    
    return {
        "content": [{
            "type": "text", 
            "text": f"""
# {server_instance.platform_type.upper()} Platform Capabilities

**Connection Status**: {('✅ Connected' if server_instance.api_connected else '❌ DISCONNECTED - Use check_vme_connection_status() for details')}
**Current Tool Count**: {current_tool_count} tools available

## ⚠️ CRITICAL: Progressive Discovery System
This server uses progressive discovery to manage 500+ available tools efficiently.

**HOW IT WORKS:**
1. Initially, only ~19 discovery and utility tools are available
2. You MUST activate tool groups before using their tools
3. Tools that aren't activated DO NOT EXIST in your tool list
4. NEVER attempt to call tools without activating their group first
5. NEVER simulate or pretend to call tools - always use actual tools

**If you see "Tool not found" errors:**
- The tool exists but hasn't been activated yet
- Use the appropriate discover_* function to activate its group
- Wait for confirmation of new tools being added
- Then retry your tool call

## Available Tool Groups:
{chr(10).join([f"- **{info['name']}**: {info['description']} ({('Active' if info['active'] else 'Inactive')}) - {info['tool_count']} tools" for name, info in groups.items()])}

## Getting Started:
1. Use `check_vme_connection_status()` to verify API connectivity
2. Use `discover_compute_infrastructure()` to access VM management tools
3. Use `discover_networking()` to access network management tools  
4. Use `discover_storage()` to access storage management tools
5. Use `discover_monitoring()` to access health and monitoring tools
6. Use `discover_management()` to access platform administration tools

## VM Creation Workflow:
1. **FIRST**: Call this function (`discover_capabilities()`) - ✅ Done!
2. **SECOND**: Call `discover_compute_infrastructure()` to activate VM tools
3. **WAIT**: For confirmation that new tools are available
4. **THEN**: Use `list_available_resources()` to see zones, images, plans
5. Use resolver tools to convert names to IDs
6. Use `vme_compute_Create_an_Instance()` to create VM

⚠️  **CRITICAL**: This is an HPE VM HCI Ceph cluster with KVM virtualization (NOT VMware)!
Read the infrastructure guide first to understand proper instance type selection.

Remember: Tools only exist AFTER you activate their group!
"""
        }]
    }

@mcp.tool()
async def check_vme_connection_status() -> dict:
    """
    Check the connection status to the VME API server.
    Returns current connection state and any error details.
    """
    # Try to reconnect if previously failed
    if not server_instance.api_connected:
        try:
            server_instance.platform_type = detect_platform_type(
                server_instance.vme_api_base_url, 
                server_instance.vme_api_token
            )
            server_instance.api_connected = True
            server_instance.connection_error = None
            logger.info(f"✅ Reconnected to VME API - platform: {server_instance.platform_type}")
        except Exception as e:
            server_instance.connection_error = str(e)
            logger.error(f"❌ Still cannot connect to VME API: {e}")
    
    status_text = f"""
# VME API Connection Status

**API Endpoint**: {server_instance.vme_api_base_url}
**Connection Status**: {'✅ Connected' if server_instance.api_connected else '❌ Disconnected'}
**Platform Type**: {server_instance.platform_type}

"""
    
    if not server_instance.api_connected:
        # Determine troubleshooting steps based on error
        error = server_instance.connection_error or ""
        step1 = "Check network connectivity and DNS resolution" if "DNS resolution failed" in error else "Verify network connectivity"
        step3 = "Update API token in configuration" if "Authentication failed" in error else "Verify API token is valid"
        
        status_text += f"""
## Connection Error:
{server_instance.connection_error}

## Configuration Required:
To fix this, update your client configuration file (~/.config/vme-cli/config.yaml):

```yaml
server:
  servers:
    vmemgr01.lab.loc:
      name: vme
      transport: stdio
      path_or_url: src/servers/progressive_discovery_server.py
      env:
        VME_API_BASE_URL: "https://YOUR-VME-SERVER"  # Update this
        VME_API_TOKEN: "YOUR-API-TOKEN"              # Update this
```

Or set environment variables before running the client:
```bash
export VME_API_BASE_URL="https://YOUR-VME-SERVER"
export VME_API_TOKEN="your-api-token-here"
```

## Troubleshooting Steps:
1. {step1}
2. Confirm the API endpoint is accessible (current: {server_instance.vme_api_base_url})
3. {step3}
4. After fixing configuration, run this tool again to retry the connection

**Note**: All VME API tools will fail until connection is restored.
"""
    else:
        status_text += """
## Available Actions:
- Use `discover_capabilities()` to see available tool groups
- Tool calls should work normally
"""
    
    return {
        "content": [{
            "type": "text",
            "text": status_text
        }]
    }

@mcp.tool()
async def discover_compute_infrastructure() -> dict:
    """
    Activate compute infrastructure tools for VM management.
    Provides access to instances, images, zones, instance types, and groups.
    """
    # Get tool count before activation
    before_count = server_instance.get_current_tool_count()
    
    # Activate the group
    server_instance.activate_tool_group("compute")
    
    # Get tool count after activation
    after_count = server_instance.get_current_tool_count()
    
    return {
        "content": [{
            "type": "text",
            "text": f"""
# Compute Infrastructure Tools Activated

✅ **SUCCESS**: Tool count increased from {before_count} to {after_count} tools
🎯 **STATUS**: VM creation and helper tools are NOW AVAILABLE in your tool list!

You now have access to VM and compute management tools:

## 🏗️ IMPORTANT: Infrastructure Type
This is an **HPE VM HCI Ceph Cluster with KVM virtualization**, NOT VMware!
- Cluster: prod01 (3 nodes: vme01, vme02, vme03)
- Compute Type: MVM (Morpheus VM) - KVM-based
- Storage: Ceph distributed storage

## Virtual Machine Management:
- `vme_compute_Get_All_Instances()` - List all VMs
- `vme_compute_Create_an_Instance()` - Create new VM
- `vme_compute_Get_a_Specific_Instance()` - Get VM details
- `vme_compute_Delete_an_Instance()` - Delete VM

## Resource Discovery (for VM creation):
- `vme_virtual_images_Get_All_Virtual_Images()` - Available OS images (20 images: Ubuntu, CentOS, Rocky, Debian, AlmaLinux)
- `vme_zones_Get_All_Zones()` - Available deployment zones (tc-lab production zone)
- `vme_service_plans_Get_All_Service_Plans()` - Available service plans (25 t-shirt sizes)
- `vme_instance_types_Get_All_Instance_Types_for_Provisioning()` - Platform instance types (13 types)
- `vme_groups_Get_All_Groups()` - Available resource groups

## VM Creation Workflow:
⚠️ **IMPORTANT**: These tools are NOW IN YOUR TOOL LIST - USE THEM DIRECTLY!
Do NOT simulate or describe what would happen - ACTUALLY CALL THE TOOLS!

1. Check available images: `vme_virtual_images_Get_All_Virtual_Images()`
2. Check available zones: `vme_zones_Get_All_Zones()` (use zone ID: 1 for tc-lab)
3. Check service plans: `vme_service_plans_Get_All_Service_Plans()` 
4. Check instance types: `vme_instance_types_Get_All_Instance_Types_for_Provisioning()`
   ⚠️  **CRITICAL**: Avoid VMware instance types - use KVM-compatible types only!
5. Create VM: `vme_compute_Create_an_Instance()`

Remember: ALL THESE TOOLS ARE NOW ACTIVE - USE THEM!

## 🔧 **Helper Tools (MANDATORY - Use these FIRST!)**:
- `list_available_resources()` - See all available resources by name (no IDs)
- `resolve_zone_name("tc-lab")` - Convert zone name to ID
- `resolve_image_name("Ubuntu 22.04")` - Convert image name to ID
- `resolve_service_plan_name("1 CPU, 2GB Memory")` - Get plan ID, code, and name
- `resolve_instance_type_name("Linux VM")` - Convert instance type name to ID + layout
- `resolve_network_name("default")` - Get network ID in correct format (e.g., "network-2")
- `resolve_datastore_name("default")` - Get datastore ID

## 📖 Infrastructure Documentation:
- `get_vme_infrastructure_guide()` - Detailed HCI cluster guide
- This explains the KVM cluster setup, proper instance type selection, and VM creation workflow

## 🎯 **Recommended VM Creation Workflow**:
1. Call `list_available_resources()` to see what's available
2. Use resolver tools to get IDs: `resolve_zone_name("tc-lab")`, etc.
3. Create VM with `vme_compute_Create_an_Instance()`

All compute infrastructure tools and helpers are now available for use.
"""
        }]
    }


@mcp.tool()
async def discover_networking() -> dict:
    """
    Activate networking tools for network infrastructure management.
    Provides access to networks, security groups, and load balancers.
    """
    before_count = server_instance.get_current_tool_count()
    server_instance.activate_tool_group("networking")
    after_count = server_instance.get_current_tool_count()
    
    return {
        "content": [{
            "type": "text",
            "text": f"""
# Network Infrastructure Tools Activated

✅ Tool count increased from {before_count} to {after_count} tools

You now have access to network management tools:

## Network Management:
- `vme_networking_Get_All_Networks()` - List all networks
- `vme_networking_Create_a_Network()` - Create new network
- `vme_networking_Get_a_Specific_Network()` - Get network details

## Security Groups:
- `vme_security_groups_Get_All_Security_Groups()` - List security groups
- `vme_security_groups_Create_a_Security_Group()` - Create security group
- `vme_security_groups_Get_a_Specific_Security_Group()` - Get group details

## Load Balancers:
- `vme_load_balancers_Get_All_Load_Balancers()` - List load balancers
- `vme_load_balancers_Create_a_Load_Balancer()` - Create load balancer
- `vme_load_balancers_Get_a_Specific_Load_Balancer()` - Get LB details

All network infrastructure tools are now available for use.
"""
        }]
    }

@mcp.tool() 
async def discover_storage() -> dict:
    """
    Activate storage tools for storage infrastructure management.
    Provides access to volumes, snapshots, and backup management.
    """
    before_count = server_instance.get_current_tool_count()
    server_instance.activate_tool_group("storage")
    after_count = server_instance.get_current_tool_count()
    
    return {
        "content": [{
            "type": "text",
            "text": f"""
# Storage Tools Activated

✅ Tool count increased from {before_count} to {after_count} tools

You now have access to storage infrastructure management tools:

## Volume Management:
- `vme_storage_volumes_Get_All_Storage_Volumes()` - List all volumes
- `vme_storage_volumes_Create_a_Storage_Volume()` - Create new volume
- `vme_storage_volumes_Get_a_Specific_Storage_Volume()` - Get volume details

## Snapshot Management:
- `vme_snapshots_Get_All_Snapshots()` - List all snapshots
- `vme_snapshots_Create_a_Snapshot()` - Create snapshot
- `vme_snapshots_Get_a_Specific_Snapshot()` - Get snapshot details

## Backup Management:
- `vme_backups_Get_All_Backups()` - List all backups
- `vme_backups_Create_a_Backup()` - Create backup
- `vme_backups_Get_a_Specific_Backup()` - Get backup details

## Storage Resources:
- `vme_library_Get_All_Storage_Types()` - Available storage types

All storage tools are now available for use.
"""
        }]
    }

@mcp.tool()
async def discover_monitoring() -> dict:
    """
    Activate monitoring and observability tools.
    Provides access to health checks, monitoring, and logs.
    """
    before_count = server_instance.get_current_tool_count()
    server_instance.activate_tool_group("monitoring")
    after_count = server_instance.get_current_tool_count()
    
    return {
        "content": [{
            "type": "text",
            "text": f"""
# Monitoring & Observability Tools Activated

✅ Tool count increased from {before_count} to {after_count} tools

You now have access to monitoring and observability tools:

## Health & Status:
- `vme_health_Get_Health_Status()` - Overall system health
- `vme_stats_Get_System_Statistics()` - System performance stats

## Monitoring:
- `vme_monitoring_Get_All_Monitoring_Checks()` - List monitoring checks
- `vme_monitoring_Create_a_Monitoring_Check()` - Create new check

## Logs & Diagnostics:
- `vme_logs_Get_System_Logs()` - Retrieve system logs
- `vme_logs_Search_Logs()` - Search through logs

All monitoring tools are now available for use.
"""
        }]
    }

@mcp.tool()
async def get_vme_infrastructure_guide() -> dict:
    """
    Get detailed VME infrastructure documentation.
    Essential reading for understanding the HCI cluster setup and VM creation process.
    """
    
    try:
        with open("docs/vme-infrastructure-guide.md", "r") as f:
            guide_content = f.read()
        
        return {
            "content": [{
                "type": "text",
                "text": guide_content
            }]
        }
    except FileNotFoundError:
        return {
            "content": [{
                "type": "text",
                "text": """
# VME Infrastructure Guide Not Found

The detailed infrastructure guide is not available. Here's essential information:

## Key Facts:
- **Cluster Type**: HPE VM HCI Ceph Cluster (NOT VMware)
- **Virtualization**: KVM-based (MVM - Morpheus VM)
- **Nodes**: 3 servers (vme01, vme02, vme03)
- **Zone**: tc-lab (ID: 1)

## Critical for VM Creation:
- Use KVM-compatible instance types (avoid VMware types)
- Include layout ID from selected instance type
- Use zone ID: 1 for tc-lab
- Match OS images with compatible instance types
"""
            }]
        }

@mcp.tool()
async def resolve_zone_name(zone_name: str) -> dict:
    """
    Resolve a zone name to its ID for VM creation.
    Helps LLMs avoid dealing with raw IDs by using friendly names.
    """
    try:
        response = await server_instance.http_client.get("/api/zones")
        if response.status_code == 200:
            zones_data = response.json()
            zones = zones_data.get('zones', [])
            
            # Find zone by name (case-insensitive)
            for zone in zones:
                if zone.get('name', '').lower() == zone_name.lower():
                    return {
                        "content": [{"type": "text", "text": f"Zone '{zone_name}' resolved to ID: {zone['id']}"}]
                    }
            
            available_zones = [zone.get('name') for zone in zones if zone.get('active', True)]
            return {
                "content": [{"type": "text", "text": f"Zone '{zone_name}' not found. Available zones: {', '.join(available_zones)}"}]
            }
        else:
            return {
                "content": [{"type": "text", "text": f"Failed to fetch zones: HTTP {response.status_code}"}]
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error resolving zone name: {e}"}]
        }

@mcp.tool()
async def resolve_image_name(image_name: str) -> dict:
    """
    Resolve an OS image name to its ID for VM creation.
    Supports partial matching (e.g., "Ubuntu 22" matches "Ubuntu 22.04 LTS").
    """
    try:
        response = await server_instance.http_client.get("/api/virtual-images")
        if response.status_code == 200:
            images_data = response.json()
            images = images_data.get('virtualImages', [])
            
            # Find exact match first
            for image in images:
                if image.get('name', '').lower() == image_name.lower():
                    return {
                        "content": [{"type": "text", "text": f"Image '{image_name}' resolved to ID: {image['id']}"}]
                    }
            
            # Find partial match
            for image in images:
                if image_name.lower() in image.get('name', '').lower():
                    return {
                        "content": [{"type": "text", "text": f"Image '{image_name}' matched '{image['name']}' → ID: {image['id']}"}]
                    }
            
            available_images = [img.get('name') for img in images if img.get('active', True)][:10]  # Show first 10
            return {
                "content": [{"type": "text", "text": f"Image '{image_name}' not found. Available images: {', '.join(available_images)}..."}]
            }
        else:
            return {
                "content": [{"type": "text", "text": f"Failed to fetch images: HTTP {response.status_code}"}]
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error resolving image name: {e}"}]
        }

@mcp.tool()
async def resolve_service_plan_name(plan_name: str) -> dict:
    """
    Resolve a service plan name to its ID for VM creation.
    Service plans define t-shirt sizes (Small, Medium, Large).
    """
    try:
        response = await server_instance.http_client.get("/api/service-plans")
        if response.status_code == 200:
            plans_data = response.json()
            plans = plans_data.get('servicePlans', [])
            
            # Find exact match first
            for plan in plans:
                if plan.get('name', '').lower() == plan_name.lower():
                    return {
                        "content": [{
                            "type": "text", 
                            "text": f"Service plan '{plan_name}' resolved to:\nID: {plan['id']}\nCode: {plan['code']}\nName: {plan['name']}"
                        }]
                    }
            
            # Find partial match
            for plan in plans:
                if plan_name.lower() in plan.get('name', '').lower():
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Service plan '{plan_name}' matched '{plan['name']}':\nID: {plan['id']}\nCode: {plan['code']}\nName: {plan['name']}"
                        }]
                    }
            
            available_plans = [plan.get('name') for plan in plans if plan.get('active', True)][:10]
            return {
                "content": [{"type": "text", "text": f"Service plan '{plan_name}' not found. Available plans: {', '.join(available_plans)}"}]
            }
        else:
            return {
                "content": [{"type": "text", "text": f"Failed to fetch service plans: HTTP {response.status_code}"}]
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error resolving service plan name: {e}"}]
        }

@mcp.tool()
async def resolve_instance_type_name(type_name: str) -> dict:
    """
    Resolve an instance type name to its ID and layout for VM creation.
    Automatically selects KVM-compatible types and includes layout information.
    """
    try:
        response = await server_instance.http_client.get("/api/instance-types")
        if response.status_code == 200:
            types_data = response.json()
            instance_types = types_data.get('instanceTypes', [])
            
            # Filter for KVM-compatible types (avoid VMware)
            kvm_types = []
            for itype in instance_types:
                name = itype.get('name', '').lower()
                code = itype.get('code', '').lower()
                if 'vmware' not in name and 'vmware' not in code:
                    kvm_types.append(itype)
            
            # Find exact match in KVM types
            for itype in kvm_types:
                if itype.get('name', '').lower() == type_name.lower():
                    # Get layout information
                    layouts = itype.get('instanceTypeLayouts', []) or itype.get('layouts', [])
                    layout_info = f" (includes {len(layouts)} layouts)" if layouts else " (no layouts)"
                    layout_id = layouts[0]['id'] if layouts else None
                    
                    result_text = f"Instance type '{type_name}' resolved to ID: {itype['id']}{layout_info}"
                    if layout_id:
                        result_text += f"\nLayout ID: {layout_id}"
                    
                    return {
                        "content": [{"type": "text", "text": result_text}]
                    }
            
            # Find partial match in KVM types
            for itype in kvm_types:
                if type_name.lower() in itype.get('name', '').lower():
                    layouts = itype.get('instanceTypeLayouts', []) or itype.get('layouts', [])
                    layout_info = f" (includes {len(layouts)} layouts)" if layouts else " (no layouts)"
                    layout_id = layouts[0]['id'] if layouts else None
                    
                    result_text = f"Instance type '{type_name}' matched '{itype['name']}' → ID: {itype['id']}{layout_info}"
                    if layout_id:
                        result_text += f"\nLayout ID: {layout_id}"
                    
                    return {
                        "content": [{"type": "text", "text": result_text}]
                    }
            
            available_types = [t.get('name') for t in kvm_types if t.get('active', True)][:10]
            return {
                "content": [{"type": "text", "text": f"Instance type '{type_name}' not found in KVM-compatible types. Available: {', '.join(available_types)}"}]
            }
        else:
            return {
                "content": [{"type": "text", "text": f"Failed to fetch instance types: HTTP {response.status_code}"}]
            }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error resolving instance type name: {e}"}]
        }

@mcp.tool()
async def resolve_network_name(network_name: str = "default") -> dict:
    """
    Resolve a network name to its ID for VM creation.
    Use "default" to get the first available compute network.
    Network IDs are returned in the format required by the API (e.g., "network-2").
    """
    try:
        # First check which zone we're working with
        zone_id = 1  # Default zone, could be parameterized
        response = await server_instance.http_client.get(f"/api/networks?zoneId={zone_id}")
        
        if response.status_code == 200:
            networks_data = response.json()
            networks = networks_data.get('networks', [])
            
            # If "default" requested, find first compute network
            if network_name.lower() == "default":
                for network in networks:
                    net_name = network.get('name', '').lower()
                    if 'compute' in net_name or 'vlan' in net_name:
                        return {
                            "content": [{
                                "type": "text", 
                                "text": f"Default network resolved to '{network['name']}' → ID: network-{network['id']}"
                            }]
                        }
                # Fallback to first available network
                if networks:
                    network = networks[0]
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Default network resolved to '{network['name']}' → ID: network-{network['id']}"
                        }]
                    }
            
            # Find exact match
            for network in networks:
                if network.get('name', '').lower() == network_name.lower():
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Network '{network_name}' resolved to ID: network-{network['id']}"
                        }]
                    }
            
            # Find partial match
            for network in networks:
                if network_name.lower() in network.get('name', '').lower():
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Network '{network_name}' matched '{network['name']}' → ID: network-{network['id']}"
                        }]
                    }
            
            available_networks = [net.get('name') for net in networks]
            return {
                "content": [{
                    "type": "text",
                    "text": f"Network '{network_name}' not found. Available networks: {', '.join(available_networks)}"
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Failed to fetch networks: HTTP {response.status_code}"
                }]
            }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error resolving network name: {e}"
            }]
        }

@mcp.tool()
async def resolve_datastore_name(datastore_name: str = "default") -> dict:
    """
    Resolve a datastore name to its ID for VM creation.
    Use "default" to get the default Ceph datastore.
    For VME HCI clusters, this typically returns the Ceph distributed storage.
    """
    try:
        response = await server_instance.http_client.get("/api/options/zoneDatastores?zoneId=1")
        
        if response.status_code == 200:
            datastores_data = response.json()
            datastores = datastores_data.get('datastores', [])
            
            # If no datastores in response, try alternate endpoint
            if not datastores:
                # Return known default for VME
                return {
                    "content": [{
                        "type": "text",
                        "text": "Default datastore resolved to ID: 5 (Ceph distributed storage)"
                    }]
                }
            
            # If "default" requested, find Ceph or first available
            if datastore_name.lower() == "default":
                for ds in datastores:
                    ds_name = ds.get('name', '').lower()
                    if 'ceph' in ds_name or 'default' in ds_name:
                        return {
                            "content": [{
                                "type": "text",
                                "text": f"Default datastore resolved to '{ds['name']}' → ID: {ds['id']}"
                            }]
                        }
                # Fallback to first available
                if datastores:
                    ds = datastores[0]
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Default datastore resolved to '{ds['name']}' → ID: {ds['id']}"
                        }]
                    }
            
            # Find exact match
            for ds in datastores:
                if ds.get('name', '').lower() == datastore_name.lower():
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Datastore '{datastore_name}' resolved to ID: {ds['id']}"
                        }]
                    }
            
            # Find partial match
            for ds in datastores:
                if datastore_name.lower() in ds.get('name', '').lower():
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Datastore '{datastore_name}' matched '{ds['name']}' → ID: {ds['id']}"
                        }]
                    }
            
            # Default fallback for VME
            return {
                "content": [{
                    "type": "text",
                    "text": "Using default VME datastore ID: 5 (Ceph distributed storage)"
                }]
            }
            
        else:
            # Return known default for VME even if API fails
            return {
                "content": [{
                    "type": "text",
                    "text": "Using default VME datastore ID: 5 (API unavailable, using known default)"
                }]
            }
    except Exception as e:
        # Return known default for VME on error
        return {
            "content": [{
                "type": "text",
                "text": f"Using default VME datastore ID: 5 (Error: {e})"
            }]
        }

@mcp.tool()
async def list_available_resources() -> dict:
    """
    Get a summary of all available resources with names (no IDs) for easy selection.
    Perfect for LLMs to see what's available without overwhelming detail.
    """
    try:
        results = {}
        
        # Get zones
        zones_response = await server_instance.http_client.get("/api/zones")
        if zones_response.status_code == 200:
            zones_data = zones_response.json()
            zones = zones_data.get('zones', [])
            results['zones'] = [zone.get('name') for zone in zones if zone.get('active', True)]
        
        # Get images (limit to first 10 for readability)
        images_response = await server_instance.http_client.get("/api/virtual-images")
        if images_response.status_code == 200:
            images_data = images_response.json()
            images = images_data.get('virtualImages', [])
            active_images = [img.get('name') for img in images if img.get('active', True)]
            results['images'] = active_images[:10]  # Show first 10 only
            if len(active_images) > 10:
                results['total_images'] = len(active_images)
        
        # Get service plans  
        plans_response = await server_instance.http_client.get("/api/service-plans")
        if plans_response.status_code == 200:
            plans_data = plans_response.json()
            plans = plans_data.get('servicePlans', [])
            results['service_plans'] = [plan.get('name') for plan in plans if plan.get('active', True)]
        
        # Get instance types (KVM-compatible only)
        types_response = await server_instance.http_client.get("/api/instance-types")
        if types_response.status_code == 200:
            types_data = types_response.json()
            instance_types = types_data.get('instanceTypes', [])
            kvm_types = []
            for itype in instance_types:
                name = itype.get('name', '').lower()
                code = itype.get('code', '').lower()
                if 'vmware' not in name and 'vmware' not in code and itype.get('active', True):
                    kvm_types.append(itype.get('name'))
            results['instance_types'] = kvm_types
        
        # Get networks for default zone
        networks_response = await server_instance.http_client.get("/api/networks?zoneId=1")
        if networks_response.status_code == 200:
            networks_data = networks_response.json()
            networks = networks_data.get('networks', [])
            results['networks'] = [net.get('name') for net in networks]
        
        summary = f"""# Available VME Resources (Names Only)

## 🌍 **Zones** ({len(results.get('zones', []))})
{chr(10).join([f"- {zone}" for zone in results.get('zones', ['None available'])])}

## 💿 **OS Images** ({results.get('total_images', len(results.get('images', [])))})
{chr(10).join([f"- {img}" for img in results.get('images', ['None available'])])}
{(f"... and {results.get('total_images', 0) - 10} more images" if results.get('total_images', 0) > 10 else "")}

## 📦 **Service Plans** ({len(results.get('service_plans', []))})
{chr(10).join([f"- {plan}" for plan in results.get('service_plans', ['None available'])])}

## 🖥️ **Instance Types** (KVM-compatible: {len(results.get('instance_types', []))})
{chr(10).join([f"- {itype}" for itype in results.get('instance_types', ['None available'])])}

## 🌐 **Networks** ({len(results.get('networks', []))})
{chr(10).join([f"- {net}" for net in results.get('networks', ['None available'])])}

## 🔧 **Usage**
Use the resolver tools to convert names to IDs:
- `resolve_zone_name("tc-lab")`
- `resolve_image_name("Ubuntu 22.04")`  
- `resolve_service_plan_name("1 CPU, 2GB Memory")`
- `resolve_instance_type_name("Linux VM")`
- `resolve_network_name("Compute VLAN 11")` or `resolve_network_name("default")`
- `resolve_datastore_name("default")`
"""
        
        return {
            "content": [{"type": "text", "text": summary}]
        }
        
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error listing resources: {e}"}]
        }

@mcp.tool()
async def discover_management() -> dict:
    """
    Activate platform management tools.
    Provides access to accounts, users, policies, and cloud integrations.
    """
    before_count = server_instance.get_current_tool_count()
    server_instance.activate_tool_group("management")
    after_count = server_instance.get_current_tool_count()
    
    return {
        "content": [{
            "type": "text",
            "text": f"""
# Platform Management Tools Activated

✅ Tool count increased from {before_count} to {after_count} tools

You now have access to platform administration tools:

## Account Management:
- `vme_accounts_Get_All_Tenants()` - List all accounts/tenants
- `vme_accounts_Create_a_Tenant()` - Create new tenant
- `vme_accounts_Get_a_Specific_Tenant()` - Get tenant details

## User Management:
- `vme_users_Get_All_Users()` - List all users
- `vme_users_Create_a_User()` - Create new user
- `vme_users_Get_a_Specific_User()` - Get user details

## Access Control:
- `vme_policies_Get_All_Policies()` - List access policies
- `vme_roles_Get_All_Roles()` - List user roles

## Cloud Integration:
- `vme_clouds_Get_All_Cloud_Integrations()` - List cloud connections
- `vme_clouds_Create_a_Cloud_Integration()` - Add cloud integration

All platform management tools are now available for use.
"""
        }]
    }

def main():
    """Main entry point"""
    logger.info("🚀 Starting Progressive Discovery VME FastMCP Server...")
    
    try:
        logger.info("📡 Server ready with discovery tools. Call discover_capabilities() to start.")
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        raise

if __name__ == "__main__":
    main()