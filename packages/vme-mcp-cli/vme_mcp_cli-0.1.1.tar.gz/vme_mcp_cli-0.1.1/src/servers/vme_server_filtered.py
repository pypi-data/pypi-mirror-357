#!/usr/bin/env python3
import json
import httpx
import os
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from dotenv import load_dotenv
from src.shared.api_utils import api_check, detect_platform_type

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

# Create MCP server from OpenAPI spec with specific route filtering
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="VME Infrastructure Server (Filtered)",
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
        # Include appliance settings
        RouteMap(
            pattern=r"^/api/appliance-settings$",
            mcp_type=MCPType.TOOL
        ),
        # Include license endpoints
        RouteMap(
            pattern=r"^/api/license.*",
            mcp_type=MCPType.TOOL
        ),
        # Include whoami endpoint (may show platform info)
        RouteMap(
            pattern=r"^/api/whoami$",
            mcp_type=MCPType.TOOL
        ),
        # Exclude everything else
        RouteMap(
            pattern=r".*",
            mcp_type=MCPType.EXCLUDE
        )
    ]
)

if __name__ == "__main__":
    mcp.run()