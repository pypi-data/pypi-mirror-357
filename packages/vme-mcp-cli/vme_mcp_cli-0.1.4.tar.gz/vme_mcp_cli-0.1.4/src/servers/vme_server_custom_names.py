#!/usr/bin/env python3
"""
VME FastMCP Server with Custom Tool Names
Uses FastMCP's official mcp_names parameter to provide shorter, cleaner tool names
"""

import json
import httpx
import os
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from dotenv import load_dotenv
# from src.shared.api_utils import api_check, detect_platform_type

# Load environment variables from .env file
load_dotenv()

# Load environment variables
VME_API_BASE_URL = os.getenv("VME_API_BASE_URL", "https://vmemgr01.lab.loc/api")
VME_API_TOKEN = os.getenv("VME_API_TOKEN")

if not VME_API_TOKEN:
    raise ValueError("VME_API_TOKEN environment variable is required")

# Load the VME OpenAPI specification
with open("hpe-vme-openapi.yaml", "r") as f:
    openapi_spec = json.load(f)

# Update the server URL in the spec to use the real VME API
openapi_spec["servers"] = [{"url": VME_API_BASE_URL}]

# Create HTTP client for VME API with authentication
client = httpx.AsyncClient(
    base_url=VME_API_BASE_URL,
    headers={
        "Authorization": f"Bearer {VME_API_TOKEN}",
        "Content-Type": "application/json"
    },
    verify=False  # Disable SSL verification for lab environment
)

# Custom tool names mapping (official FastMCP approach)
# Maps operationId from OpenAPI spec to cleaner names
custom_tool_names = {
    # License management
    "vme_license_Get_Current_License": "get_current_license",
    "vme_provisioning_licenses_Get_All_Licenses": "get_running_licenses",
    "vme_license_Install_License": "install_license",
    "vme_license_Uninstall_License": "uninstall_license",
    
    # Instance management
    "vme_compute_infrastructure_Get_All_Instances": "list_instances",
    "vme_compute_infrastructure_Create_an_Instance": "create_instance", 
    "vme_compute_infrastructure_Delete_Instance": "delete_instance",
    "vme_compute_infrastructure_Get_Instance": "get_instance",
    "vme_compute_infrastructure_Update_Instance": "update_instance",
    "vme_compute_infrastructure_Start_Instance": "start_instance",
    "vme_compute_infrastructure_Stop_Instance": "stop_instance",
    "vme_compute_infrastructure_Restart_Instance": "restart_instance",
    
    # Virtual images
    "vme_virtual_images_Get_All_Virtual_Images": "list_images",
    "vme_virtual_images_Get_Virtual_Image": "get_image",
    "vme_virtual_images_Upload_Virtual_Image": "upload_image",
    "vme_virtual_images_Delete_Virtual_Image": "delete_image",
    
    # Service plans
    "vme_service_plans_Get_All_Service_Plans": "list_service_plans",
    "vme_service_plans_Get_Service_Plan": "get_service_plan",
    "vme_service_plans_Create_Service_Plan": "create_service_plan",
    "vme_service_plans_Update_Service_Plan": "update_service_plan",
    "vme_service_plans_Delete_Service_Plan": "delete_service_plan",
    
    # Instance types
    "vme_instance_types_Get_All_Instance_Types": "list_instance_types",
    "vme_instance_types_Get_Instance_Type": "get_instance_type",
    
    # Appliance settings
    "vme_appliance_settings_Get_Appliance_Settings": "get_appliance_settings",
    "vme_appliance_settings_Update_Appliance_Settings": "update_appliance_settings",
    
    # Zones
    "vme_zones_Get_All_Zones": "list_zones",
    "vme_zones_Get_Zone": "get_zone",
    
    # Groups
    "vme_groups_Get_All_Groups": "list_groups",
    "vme_groups_Get_Group": "get_group",
    "vme_groups_Create_Group": "create_group",
    "vme_groups_Update_Group": "update_group",
    "vme_groups_Delete_Group": "delete_group",
    
    # Networks
    "vme_networks_Get_All_Networks": "list_networks",
    "vme_networks_Get_Network": "get_network",
    "vme_networks_Create_Network": "create_network",
    "vme_networks_Update_Network": "update_network",
    "vme_networks_Delete_Network": "delete_network",
    
    # Storage
    "vme_storage_Get_All_Storage_Providers": "list_storage_providers",
    "vme_storage_Get_Storage_Provider": "get_storage_provider",
    
    # Clusters and Hosts (critical for node information)
    "vme_clusters_Get_All_Clusters": "list_clusters",
    "vme_clusters_Get_Cluster": "get_cluster",
    "vme_clusters_Create_Cluster": "create_cluster",
    "vme_clusters_Update_Cluster": "update_cluster",
    "vme_clusters_Delete_Cluster": "delete_cluster",
    "vme_servers_Get_all_hosts": "list_hosts",
    "vme_servers_Get_Host": "get_host",
    "vme_servers_Provision_a_host": "create_host",
    "vme_servers_Update_Host": "update_host",
    "vme_servers_Delete_Host": "delete_host",
    
    # User management
    "vme_user_Get_current_user_information": "whoami",
    
    # Helper tools (keep these descriptive)
    "discover_capabilities": "discover_capabilities",
    "discover_compute_infrastructure": "discover_compute",
    "discover_networking": "discover_networking", 
    "discover_storage": "discover_storage",
    "discover_monitoring": "discover_monitoring",
    "discover_management": "discover_management",
    
    # Resolution helpers
    "resolve_zone_name": "resolve_zone",
    "resolve_image_name": "resolve_image",
    "resolve_service_plan_name": "resolve_service_plan",
    "resolve_instance_type_name": "resolve_instance_type",
    "resolve_group_name": "resolve_group",
    "resolve_network_name": "resolve_network",
}

# Create MCP server with custom tool names
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="VME Infrastructure Server (Custom Names)",
    mcp_names=custom_tool_names,  # Official FastMCP parameter for custom names
    route_maps=[
        # Include instance-related endpoints
        RouteMap(
            pattern=r"^/api/instances.*",
            mcp_type=MCPType.TOOL
        ),
        RouteMap(
            pattern=r"^/api/instance-types.*",
            mcp_type=MCPType.TOOL
        ),
        RouteMap(
            pattern=r"^/api/library/instance-types.*",
            mcp_type=MCPType.TOOL
        ),
        # Include virtual images
        RouteMap(
            pattern=r"^/api/virtual-images.*",
            mcp_type=MCPType.TOOL
        ),
        # Include service plans
        RouteMap(
            pattern=r"^/api/service-plans.*",
            mcp_type=MCPType.TOOL
        ),
        # Include appliance settings
        RouteMap(
            pattern=r"^/api/appliance-settings.*",
            mcp_type=MCPType.TOOL
        ),
        # Include license endpoints
        RouteMap(
            pattern=r"^/api/license.*",
            mcp_type=MCPType.TOOL
        ),
        RouteMap(
            pattern=r"^/api/provisioning-licenses.*",
            mcp_type=MCPType.TOOL
        ),
        # Include user info
        RouteMap(
            pattern=r"^/api/whoami$",
            mcp_type=MCPType.TOOL
        ),
        # Include zones
        RouteMap(
            pattern=r"^/api/zones.*",
            mcp_type=MCPType.TOOL
        ),
        # Include groups
        RouteMap(
            pattern=r"^/api/groups.*",
            mcp_type=MCPType.TOOL
        ),
        # Include networks
        RouteMap(
            pattern=r"^/api/networks.*",
            mcp_type=MCPType.TOOL
        ),
        # Include storage
        RouteMap(
            pattern=r"^/api/storage.*",
            mcp_type=MCPType.TOOL
        ),
        # Include clusters (critical for node information)
        RouteMap(
            pattern=r"^/api/clusters.*",
            mcp_type=MCPType.TOOL
        ),
        # Include servers/hosts (critical for host specifications)
        RouteMap(
            pattern=r"^/api/servers.*",
            mcp_type=MCPType.TOOL
        ),
        # Exclude everything else
        RouteMap(
            pattern=r".*",
            mcp_type=MCPType.EXCLUDE
        )
    ]
)

@mcp.tool()
def list_available_resources():
    """Get a summary of all available VME resources and capabilities"""
    return {
        "compute": {
            "instances": "Use list_instances, create_instance, delete_instance",
            "images": "Use list_images, get_image, upload_image", 
            "service_plans": "Use list_service_plans, get_service_plan",
            "instance_types": "Use list_instance_types, get_instance_type"
        },
        "infrastructure": {
            "zones": "Use list_zones, get_zone",
            "groups": "Use list_groups, create_group, delete_group",
            "networks": "Use list_networks, create_network, delete_network"
        },
        "management": {
            "licenses": "Use get_current_license, get_running_licenses",
            "settings": "Use get_appliance_settings, update_appliance_settings",
            "user": "Use whoami"
        },
        "clusters": {
            "cluster_info": "Use list_clusters, get_cluster",
            "cluster_management": "Use create_cluster, update_cluster, delete_cluster",
            "host_info": "Use list_hosts, get_host",
            "host_management": "Use create_host, update_host, delete_host"
        },
        "discovery": {
            "tools": "Use discover_* tools to find available capabilities",
            "resolution": "Use resolve_* tools to convert names to IDs"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting VME FastMCP Server with Custom Tool Names...")
    print(f"📊 Base URL: {VME_API_BASE_URL}")
    print(f"🔧 Custom tool names configured: {len(custom_tool_names)}")
    
    # Test API connectivity
    import asyncio
    
    async def test_connection():
        """Test VME API connectivity"""
        try:
            # Simple connectivity test
            response = await client.get("/appliance-settings")
            if response.status_code == 200:
                print(f"✅ VME API connection successful")
            else:
                print(f"❌ VME API connection failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
    
    asyncio.run(test_connection())
    
    # Start the server
    mcp.run()