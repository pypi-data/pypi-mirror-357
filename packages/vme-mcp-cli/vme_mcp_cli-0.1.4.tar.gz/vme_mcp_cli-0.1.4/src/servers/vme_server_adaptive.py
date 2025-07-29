#!/usr/bin/env python3
"""
Adaptive VME FastMCP Server with Client Detection
Automatically detects client type and adapts route filtering accordingly.
"""

import json
import httpx
import os
import logging
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from dotenv import load_dotenv
from src.shared.api_utils import detect_platform_type
from src.utils.client_detection import detect_client_capabilities, ClientCapabilities
from src.shared.route_manager import RouteManager

# Configure logging to stderr to avoid corrupting MCP stdio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global server state
CURRENT_CLIENT_CAPABILITIES = None
CURRENT_ROUTE_MANAGER = None
PLATFORM_TYPE = None

class AdaptiveMCPServer:
    """MCP Server that adapts to client capabilities"""
    
    def __init__(self, use_test_config: bool = False):
        self.use_test_config = use_test_config
        self.route_manager = RouteManager()
        
        # Load environment variables
        self.vme_api_base_url = os.getenv("VME_API_BASE_URL", "https://vmemgr01.lab.loc/api")
        self.vme_api_token = os.getenv("VME_API_TOKEN")
        
        if not self.vme_api_token:
            raise ValueError("VME_API_TOKEN environment variable is required")
        
        # Detect VME platform type
        self.platform_type = detect_platform_type(self.vme_api_base_url, self.vme_api_token)
        logger.info(f"🏗️ Detected platform: {self.platform_type}")
        
        # Load OpenAPI spec
        self.openapi_spec = self._load_openapi_spec()
        
        # Create HTTP client
        self.http_client = self._create_http_client()
        
        # Server will be created during client initialization
        self.mcp_server = None
        self.client_capabilities = None
    
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
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in OpenAPI spec: {e}")
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
    
    def configure_for_client(self, client_info: dict) -> FastMCP:
        """
        Configure MCP server based on client capabilities
        This would be called during MCP initialization handshake
        """
        
        # Detect client capabilities
        self.client_capabilities = detect_client_capabilities(client_info)
        
        logger.info(f"🤖 Client detected: {self.client_capabilities}")
        
        # Get appropriate route maps
        route_maps = self.route_manager.get_route_maps(
            self.client_capabilities, 
            use_test_config=self.use_test_config
        )
        
        expected_counts = self.route_manager.get_expected_counts(
            self.client_capabilities,
            use_test_config=self.use_test_config
        )
        
        logger.info(f"📋 Route configuration: {self.client_capabilities.route_config.value}")
        logger.info(f"🔧 Loaded {len(route_maps)} route patterns")
        logger.info(f"📊 Expected: {expected_counts['tools']} tools, {expected_counts['resources']} resources")
        
        # Create server name based on client and platform
        server_name = f"{self.platform_type.upper()} Server for {self.client_capabilities.client_name}"
        if self.use_test_config:
            server_name += " (Test Mode)"
        
        # Create FastMCP server with dynamic configuration
        self.mcp_server = FastMCP.from_openapi(
            openapi_spec=self.openapi_spec,
            client=self.http_client,
            name=server_name,
            route_maps=route_maps
        )
        
        logger.info(f"✅ Created adaptive server: {server_name}")
        
        return self.mcp_server
    
    def get_server_for_testing(self, client_name: str = "Test Client", client_version: str = "1.0.0") -> FastMCP:
        """
        Create server with specific client identity for testing
        """
        client_info = {"name": client_name, "version": client_version}
        return self.configure_for_client(client_info)

def create_server_for_client(client_info: dict, use_test_config: bool = False) -> FastMCP:
    """
    Factory function to create adaptive server for specific client
    This is the main entry point for client-aware server creation
    """
    
    adaptive_server = AdaptiveMCPServer(use_test_config=use_test_config)
    return adaptive_server.configure_for_client(client_info)

def main():
    """
    Main entry point - creates server with default configuration
    In real MCP usage, client info would come from initialization handshake
    """
    
    logger.info("🚀 Starting Adaptive VME FastMCP Server...")
    
    # For standalone usage, simulate a default client
    # In real MCP, this would come from the initialization handshake
    default_client_info = {
        "name": "Default MCP Client",
        "version": "1.0.0"
    }
    
    try:
        adaptive_server = AdaptiveMCPServer(use_test_config=False)
        mcp_server = adaptive_server.configure_for_client(default_client_info)
        
        logger.info("📡 Starting MCP server with adaptive configuration...")
        mcp_server.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        raise

if __name__ == "__main__":
    main()