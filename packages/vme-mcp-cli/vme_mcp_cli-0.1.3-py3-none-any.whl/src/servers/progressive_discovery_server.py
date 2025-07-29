#!/usr/bin/env python3
"""
Progressive Discovery VME FastMCP Server
Organizes tools into logical groups that LLMs can discover progressively
"""

import json
import httpx
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
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
        
        # Tool group definitions
        self.tool_groups = self._define_tool_groups()
        
        # Initially only discovery tools are available
        self.active_groups = set()
        
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
                    RouteMap(pattern="^/api/service-plans$", mcp_type=MCPType.RESOURCE),
                    RouteMap(pattern="^/api/service-plans/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
                    
                    # Instance Types (for provisioning - platform dependent)
                    RouteMap(pattern="^/api/instance-types$", mcp_type=MCPType.RESOURCE),
                    RouteMap(pattern="^/api/instance-types/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
                    
                    # Library Instance Types (Morpheus-specific)
                    RouteMap(pattern="^/api/library/instance-types$", mcp_type=MCPType.RESOURCE),
                    RouteMap(pattern="^/api/library/instance-types/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
                    
                    # OS Images (VME uses /api/virtual-images, Morpheus has /api/library/virtual-images)
                    RouteMap(pattern="^/api/virtual-images$", mcp_type=MCPType.RESOURCE),
                    RouteMap(pattern="^/api/virtual-images/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
                    RouteMap(pattern="^/api/library/virtual-images$", mcp_type=MCPType.RESOURCE),
                    RouteMap(pattern="^/api/library/virtual-images/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
                    
                    # Zones and placement
                    RouteMap(pattern="^/api/zones$", mcp_type=MCPType.RESOURCE),
                    RouteMap(pattern="^/api/zones/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
                    
                    # Groups for organization
                    RouteMap(pattern="^/api/groups$", mcp_type=MCPType.RESOURCE),
                    RouteMap(pattern="^/api/groups/.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
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
        if group_name in self.tool_groups:
            self.active_groups.add(group_name)
            logger.info(f"🔧 Activated tool group: {group_name}")
            return True
        return False
    
    def get_available_groups(self) -> Dict[str, Dict[str, str]]:
        """Get information about available tool groups"""
        return {
            name: {
                "name": config["name"],
                "description": config["description"],
                "active": name in self.active_groups or config.get("always_active", False),
                "tool_count": len(config["routes"])
            }
            for name, config in self.tool_groups.items()
        }

# Create server instance
server_instance = ProgressiveDiscoveryServer()

# Get route maps - start with only discovery tools (progressive design)
initial_route_maps = server_instance.get_active_route_maps()

# Create FastMCP server
mcp = FastMCP.from_openapi(
    openapi_spec=server_instance.openapi_spec,
    client=server_instance.http_client,
    name=f"{server_instance.platform_type.upper()} Progressive Discovery Server",
    route_maps=initial_route_maps
)

# Add custom discovery tools
@mcp.tool()
async def discover_capabilities() -> dict:
    """
    Discover available tool groups and platform capabilities.
    Call this first to see what functionality is available.
    """
    groups = server_instance.get_available_groups()
    
    return {
        "content": [{
            "type": "text", 
            "text": f"""
# {server_instance.platform_type.upper()} Platform Capabilities

## Available Tool Groups:
{chr(10).join([f"- **{info['name']}**: {info['description']} ({'Active' if info['active'] else 'Inactive'}) - {info['tool_count']} tools" for name, info in groups.items()])}

## Getting Started:
1. Use `discover_compute_infrastructure()` to access VM management tools
2. Use `discover_networking()` to access network management tools  
3. Use `discover_storage()` to access storage management tools
4. Use `discover_monitoring()` to access health and monitoring tools
5. Use `discover_management()` to access platform administration tools

## VM Creation Workflow:
1. Call `get_vme_infrastructure_guide()` to understand the HCI cluster setup
2. Call `discover_compute_infrastructure()` to activate VM management tools
3. Use `vme_virtual_images_Get_All_Virtual_Images()` to see available OS images
4. Use `vme_zones_Get_All_Zones()` to see available zones
5. Use `vme_service_plans_Get_All_Service_Plans()` to see t-shirt sizes
6. Use `vme_instance_types_Get_All_Instance_Types_for_Provisioning()` to see workload types
7. Use `vme_compute_infrastructure_Create_an_Instance()` to create VM

⚠️  **CRITICAL**: This is an HPE VM HCI Ceph cluster with KVM virtualization (NOT VMware)!
Read the infrastructure guide first to understand proper instance type selection.

Each discovery call activates related tools for that functional area.
"""
        }]
    }

@mcp.tool()
async def discover_compute_infrastructure() -> dict:
    """
    Activate compute infrastructure tools for VM management.
    Provides access to instances, images, zones, instance types, and groups.
    """
    server_instance.activate_tool_group("compute")
    
    return {
        "content": [{
            "type": "text",
            "text": """
# Compute Infrastructure Tools Activated

You now have access to VM and compute management tools:

## 🏗️ IMPORTANT: Infrastructure Type
This is an **HPE VM HCI Ceph Cluster with KVM virtualization**, NOT VMware!
- Cluster: prod01 (3 nodes: vme01, vme02, vme03)
- Compute Type: MVM (Morpheus VM) - KVM-based
- Storage: Ceph distributed storage

## Virtual Machine Management:
- `vme_compute_infrastructure_Get_All_Instances()` - List all VMs
- `vme_compute_infrastructure_Create_an_Instance()` - Create new VM
- `vme_compute_infrastructure_Get_a_Specific_Instance()` - Get VM details
- `vme_compute_infrastructure_Delete_an_Instance()` - Delete VM

## Resource Discovery (for VM creation):
- `vme_virtual_images_Get_All_Virtual_Images()` - Available OS images (20 images: Ubuntu, CentOS, Rocky, Debian, AlmaLinux)
- `vme_zones_Get_All_Zones()` - Available deployment zones (tc-lab production zone)
- `vme_service_plans_Get_All_Service_Plans()` - Available service plans (25 t-shirt sizes)
- `vme_instance_types_Get_All_Instance_Types_for_Provisioning()` - Platform instance types (13 types)
- `vme_groups_Get_All_Groups()` - Available resource groups

## VM Creation Workflow:
1. Check available images: `vme_virtual_images_Get_All_Virtual_Images()`
2. Check available zones: `vme_zones_Get_All_Zones()` (use zone ID: 1 for tc-lab)
3. Check service plans: `vme_service_plans_Get_All_Service_Plans()` 
4. Check instance types: `vme_instance_types_Get_All_Instance_Types_for_Provisioning()`
   ⚠️  **CRITICAL**: Avoid VMware instance types - use KVM-compatible types only!
5. Create VM: `vme_compute_infrastructure_Create_an_Instance()`

## 🔧 **Helper Tools (New!)**:
- `list_available_resources()` - See all available resources by name (no IDs)
- `resolve_zone_name("tc-lab")` - Convert zone name to ID
- `resolve_image_name("Ubuntu 22.04")` - Convert image name to ID
- `resolve_service_plan_name("Small")` - Convert service plan name to ID  
- `resolve_instance_type_name("Linux VM")` - Convert instance type name to ID + layout

## 📖 Infrastructure Documentation:
- `get_vme_infrastructure_guide()` - Detailed HCI cluster guide
- This explains the KVM cluster setup, proper instance type selection, and VM creation workflow

## 🎯 **Recommended VM Creation Workflow**:
1. Call `list_available_resources()` to see what's available
2. Use resolver tools to get IDs: `resolve_zone_name("tc-lab")`, etc.
3. Create VM with `vme_compute_infrastructure_Create_an_Instance()`

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
    server_instance.activate_tool_group("networking")
    
    return {
        "content": [{
            "type": "text",
            "text": """
# Networking Tools Activated

You now have access to network infrastructure management tools:

## Network Management:
- `vme_networks_Get_All_Networks()` - List all networks
- `vme_networks_Create_a_Network()` - Create new network
- `vme_networks_Get_a_Specific_Network()` - Get network details

## Security & Access Control:
- `vme_security_groups_Get_All_Security_Groups()` - List security groups
- `vme_security_groups_Create_a_Security_Group()` - Create security group

## Load Balancing:
- `vme_load_balancers_Get_All_Load_Balancers()` - List load balancers
- `vme_load_balancers_Create_a_Load_Balancer()` - Create load balancer

## Network Resources:
- `vme_library_Get_All_Network_Types()` - Available network types
- `vme_network_pools_Get_All_Network_Pools()` - Available IP pools

All networking tools are now available for use.
"""
        }]
    }

@mcp.tool() 
async def discover_storage() -> dict:
    """
    Activate storage tools for storage infrastructure management.
    Provides access to volumes, snapshots, and backup management.
    """
    server_instance.activate_tool_group("storage")
    
    return {
        "content": [{
            "type": "text",
            "text": """
# Storage Tools Activated

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
    server_instance.activate_tool_group("monitoring")
    
    return {
        "content": [{
            "type": "text",
            "text": """
# Monitoring & Observability Tools Activated

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
                        "content": [{"type": "text", "text": f"Service plan '{plan_name}' resolved to ID: {plan['id']}"}]
                    }
            
            # Find partial match
            for plan in plans:
                if plan_name.lower() in plan.get('name', '').lower():
                    return {
                        "content": [{"type": "text", "text": f"Service plan '{plan_name}' matched '{plan['name']}' → ID: {plan['id']}"}]
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
        
        summary = f"""# Available VME Resources (Names Only)

## 🌍 **Zones** ({len(results.get('zones', []))})
{chr(10).join([f"- {zone}" for zone in results.get('zones', ['None available'])])}

## 💿 **OS Images** ({results.get('total_images', len(results.get('images', [])))})
{chr(10).join([f"- {img}" for img in results.get('images', ['None available'])])}
{f"... and {results.get('total_images', 0) - 10} more images" if results.get('total_images', 0) > 10 else ""}

## 📦 **Service Plans** ({len(results.get('service_plans', []))})
{chr(10).join([f"- {plan}" for plan in results.get('service_plans', ['None available'])])}

## 🖥️ **Instance Types** (KVM-compatible: {len(results.get('instance_types', []))})
{chr(10).join([f"- {itype}" for itype in results.get('instance_types', ['None available'])])}

## 🔧 **Usage**
Use the resolver tools to convert names to IDs:
- `resolve_zone_name("tc-lab")`
- `resolve_image_name("Ubuntu 22.04")`  
- `resolve_service_plan_name("Small")`
- `resolve_instance_type_name("Linux VM")`
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
    server_instance.activate_tool_group("management")
    
    return {
        "content": [{
            "type": "text",
            "text": """
# Platform Management Tools Activated

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