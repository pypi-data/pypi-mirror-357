#!/usr/bin/env python3
import json
import httpx
import os
from fastmcp import FastMCP
from dotenv import load_dotenv

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

# Create MCP server from OpenAPI spec - no filtering for MCP Inspector compatibility
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="VME Infrastructure Server"
)

if __name__ == "__main__":
    mcp.run()