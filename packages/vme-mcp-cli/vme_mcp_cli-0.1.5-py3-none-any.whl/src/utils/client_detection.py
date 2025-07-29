#!/usr/bin/env python3
"""
Client Detection and Capability Management for MCP Server
Handles different client types and their specific capabilities/requirements.
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class RouteConfig(Enum):
    TOOLS_ONLY = "tools_only"
    HYBRID = "hybrid" 
    RESOURCES_PREFERRED = "resources_preferred"

@dataclass
class ClientCapabilities:
    """Represents what a specific MCP client supports"""
    client_name: str
    client_version: str
    supports_resources: bool
    supports_tools: bool
    route_config: RouteConfig
    max_tools: int = 1000  # Some clients may have limits
    
    def __str__(self):
        return f"{self.client_name} v{self.client_version} ({self.route_config.value})"

def detect_client_capabilities(client_info: Dict) -> ClientCapabilities:
    """
    Detect client capabilities based on client info from MCP initialize request
    
    Args:
        client_info: Dictionary containing 'name' and 'version' from MCP initialize
        
    Returns:
        ClientCapabilities object with appropriate settings
    """
    
    client_name = client_info.get("name", "Unknown Client")
    client_version = client_info.get("version", "0.0.0")
    
    # Claude Desktop - Tools only (known limitation)
    if "claude" in client_name.lower() and "desktop" in client_name.lower():
        return ClientCapabilities(
            client_name=client_name,
            client_version=client_version,
            supports_resources=False,  # Claude Desktop ignores resources
            supports_tools=True,
            route_config=RouteConfig.TOOLS_ONLY,
            max_tools=100  # Conservative limit for Claude
        )
    
    # MCP Inspector - Full capabilities
    elif "inspector" in client_name.lower():
        return ClientCapabilities(
            client_name=client_name,
            client_version=client_version,
            supports_resources=True,
            supports_tools=True,
            route_config=RouteConfig.HYBRID,
            max_tools=1000
        )
    
    # FastMCP Test Client - Configurable for testing
    elif "fastmcp" in client_name.lower() or "test" in client_name.lower():
        return ClientCapabilities(
            client_name=client_name,
            client_version=client_version,
            supports_resources=True,
            supports_tools=True,
            route_config=RouteConfig.HYBRID,  # Default for testing
            max_tools=1000
        )
    
    # Custom/Unknown clients - Resource-preferred (more semantic)
    else:
        return ClientCapabilities(
            client_name=client_name,
            client_version=client_version,
            supports_resources=True,
            supports_tools=True,
            route_config=RouteConfig.RESOURCES_PREFERRED,
            max_tools=500
        )

# Known client configurations for testing
TEST_CLIENT_CONFIGS = {
    "Claude Desktop": {
        "name": "Claude Desktop",
        "version": "1.0.0",
        "expected_config": RouteConfig.TOOLS_ONLY
    },
    "MCP Inspector": {
        "name": "MCP Inspector", 
        "version": "0.1.0",
        "expected_config": RouteConfig.HYBRID
    },
    "Custom Client": {
        "name": "Custom MCP Client",
        "version": "2.0.0", 
        "expected_config": RouteConfig.RESOURCES_PREFERRED
    },
    "Test Client Tools": {
        "name": "FastMCP Test Client",
        "version": "1.0.0",
        "expected_config": RouteConfig.HYBRID
    }
}