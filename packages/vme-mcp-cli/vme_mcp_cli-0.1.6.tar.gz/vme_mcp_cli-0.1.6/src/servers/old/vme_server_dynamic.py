#!/usr/bin/env python3
"""
Dynamic VME/Morpheus FastMCP Server
Automatically detects platform type (VME vs Morpheus) and configures route filtering accordingly.
"""

import json
import httpx
import os
import asyncio
import logging
from fastmcp import FastMCP
from dotenv import load_dotenv
from platform_detector import detect_and_configure_platform, PlatformType

# Configure logging to stderr to avoid corrupting MCP stdio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Load environment variables
VME_API_BASE_URL = os.getenv("VME_API_BASE_URL", "https://vmemgr01.lab.loc/api")
VME_API_TOKEN = os.getenv("VME_API_TOKEN")

if not VME_API_TOKEN:
    raise ValueError("VME_API_TOKEN environment variable is required")

async def create_dynamic_server():
    """Create FastMCP server with dynamic platform detection and route filtering"""
    
    logger.info("🚀 Starting Dynamic VME/Morpheus FastMCP Server...")
    
    # Step 1: Detect platform type
    platform_type, route_maps, detection_details = await detect_and_configure_platform(
        VME_API_BASE_URL, VME_API_TOKEN
    )
    
    # Log detection results
    logger.info(f"📊 Platform Detection Results:")
    logger.info(f"   Platform: {platform_type.value}")
    logger.info(f"   Confidence: {detection_details.get('confidence', 'unknown')}")
    logger.info(f"   Route patterns: {len(route_maps)-1}")  # -1 for exclude-all pattern
    
    for indicator in detection_details.get('indicators', []):
        logger.info(f"   • {indicator}")
    
    # Step 2: Load the OpenAPI specification
    try:
        with open("hpe-vme-openapi.yaml", "r") as f:
            openapi_spec = json.load(f)
    except FileNotFoundError:
        logger.error("❌ OpenAPI spec file 'hpe-vme-openapi.yaml' not found")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in OpenAPI spec: {e}")
        raise
    
    # Update the server URL in the spec to use the real API
    openapi_spec["servers"] = [{"url": VME_API_BASE_URL}]
    
    # Step 3: Create HTTP client for API with authentication
    client = httpx.AsyncClient(
        base_url=VME_API_BASE_URL,
        headers={
            "Authorization": f"Bearer {VME_API_TOKEN}",
            "Content-Type": "application/json"
        },
        verify=False  # Disable SSL verification for lab environment
    )
    
    # Step 4: Create MCP server with dynamic route filtering
    server_name = f"{platform_type.value.upper()} Infrastructure Server (Dynamic)"
    
    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name=server_name,
        route_maps=route_maps
    )
    
    logger.info(f"✅ Created {server_name}")
    logger.info(f"🔧 Applied {len(route_maps)-1} route patterns for {platform_type.value}")
    
    return mcp, platform_type, detection_details

def main():
    """Main entry point"""
    
    try:
        # Create the dynamic server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        mcp, platform_type, details = loop.run_until_complete(create_dynamic_server())
        
        # Add platform info to server metadata
        server_info = {
            "platform_type": platform_type.value,
            "detection_details": details,
            "route_filtering": "dynamic"
        }
        
        logger.info(f"🎯 Server configured for {platform_type.value} platform")
        logger.info("📡 Starting MCP server...")
        
        # Run the MCP server
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        raise

if __name__ == "__main__":
    main()