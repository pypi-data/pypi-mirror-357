"""
FastMCP Manager for multiple MCP server connections
Supports both stdio and HTTP transports
"""

import asyncio
import logging
import httpx
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from fastmcp import Client
    from mcp.types import Implementation
except ImportError:
    raise ImportError("FastMCP not installed. Run: pip install fastmcp")

from ..config.settings import MCPServerConfig

logger = logging.getLogger(__name__)

# Suppress FastMCP logging to reduce noise
logging.getLogger("fastmcp").setLevel(logging.ERROR)
logging.getLogger("fastmcp.utilities.openapi").setLevel(logging.ERROR)

class VMETool:
    """Simple tool representation"""
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any], server_name: str = ""):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.server_name = server_name

class VMEResource:
    """Simple resource representation"""
    def __init__(self, name: str, description: str, uri: str, server_name: str = ""):
        self.name = name
        self.description = description
        self.uri = uri
        self.server_name = server_name

class MCPServerConnection:
    """Individual MCP server connection"""
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.client: Optional[Client] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.tools: List[VMETool] = []
        self.resources: List[VMEResource] = []
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            if self.config.transport == "stdio":
                return await self._connect_stdio()
            elif self.config.transport == "http":
                return await self._connect_http()
            else:
                logger.error(f"Unsupported transport: {self.config.transport}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to server {self.config.name}: {e}")
            return False
    
    async def _connect_stdio(self) -> bool:
        """Connect via stdio transport"""
        script_path = Path(self.config.path_or_url).resolve()
        
        if not script_path.exists():
            logger.error(f"Server script not found: {script_path}")
            return False
        
        logger.info(f"Connecting to {self.config.name} via stdio: {script_path}")
        
        # Temporarily suppress logging during connection
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            client_info = Implementation(
                name="vme-textual-cli",
                version="1.0.0"
            )
            
            async def suppress_logs(log_params):
                """Suppress server log messages"""
                pass
            
            self.client = Client(
                str(script_path),
                client_info=client_info,
                log_handler=suppress_logs
            )
            
            await asyncio.wait_for(
                self.client.__aenter__(), 
                timeout=self.config.timeout
            )
            
            await self._discover_tools()
            await self._discover_resources()
            self.is_connected = True
            logger.info(f"Connected to {self.config.name} - {len(self.tools)} tools, {len(self.resources)} resources available")
            return True
            
        finally:
            logging.getLogger().setLevel(original_level)
    
    async def _connect_http(self) -> bool:
        """Connect via HTTP transport"""
        logger.info(f"Connecting to {self.config.name} via HTTP: {self.config.path_or_url}")
        
        self.http_client = httpx.AsyncClient(
            base_url=self.config.path_or_url,
            timeout=self.config.timeout
        )
        
        # Test connection by trying to list tools and resources
        try:
            # Get tools
            response = await self.http_client.post("/mcp/tools/list", json={})
            response.raise_for_status()
            tools_data = response.json()
            await self._process_tools_data(tools_data)
            
            # Get resources  
            try:
                response = await self.http_client.post("/mcp/resources/list", json={})
                response.raise_for_status()
                resources_data = response.json()
                await self._process_resources_data(resources_data)
            except Exception as e:
                logger.debug(f"No resources endpoint or error for {self.config.name}: {e}")
                self.resources = []
            
            self.is_connected = True
            logger.info(f"Connected to {self.config.name} - {len(self.tools)} tools, {len(self.resources)} resources available")
            return True
            
        except Exception as e:
            logger.error(f"HTTP connection failed for {self.config.name}: {e}")
            if self.http_client:
                await self.http_client.aclose()
                self.http_client = None
            return False
    
    async def _discover_tools(self):
        """Discover tools for stdio connection"""
        if not self.client:
            return
        
        try:
            tools_data = await self.client.list_tools()
            await self._process_tools_data(tools_data)
        except Exception as e:
            logger.error(f"Failed to discover tools for {self.config.name}: {e}")
            self.tools = []
    
    async def _discover_resources(self):
        """Discover resources for stdio connection"""
        if not self.client:
            return
        
        try:
            resources_data = await self.client.list_resources()
            await self._process_resources_data(resources_data)
        except Exception as e:
            logger.debug(f"No resources available or error for {self.config.name}: {e}")
            self.resources = []
    
    async def _process_tools_data(self, tools_data):
        """Process tools data from either stdio or HTTP"""
        self.tools = []
        
        # Handle different response formats
        if isinstance(tools_data, dict) and 'tools' in tools_data:
            tools_list = tools_data['tools']
        else:
            tools_list = tools_data
        
        for tool_data in tools_list:
            # Handle both object and dict formats
            if hasattr(tool_data, 'name'):
                name = tool_data.name
                description = tool_data.description or "No description"
                input_schema = getattr(tool_data, 'input_schema', None) or getattr(tool_data, 'inputSchema', {})
            else:
                name = tool_data.get('name', '')
                description = tool_data.get('description', 'No description')
                input_schema = tool_data.get('input_schema', tool_data.get('inputSchema', {}))
            
            tool = VMETool(
                name=name,
                description=description,
                input_schema=input_schema or {},
                server_name=self.config.name
            )
            self.tools.append(tool)
        
        logger.debug(f"Processed {len(self.tools)} tools for {self.config.name}")
    
    async def _process_resources_data(self, resources_data):
        """Process resources data from either stdio or HTTP"""
        self.resources = []
        
        # Handle different response formats
        if isinstance(resources_data, dict) and 'resources' in resources_data:
            resources_list = resources_data['resources']
        else:
            resources_list = resources_data
        
        for resource_data in resources_list:
            # Handle both object and dict formats
            if hasattr(resource_data, 'name'):
                name = resource_data.name
                description = resource_data.description or "No description"
                uri = getattr(resource_data, 'uri', '')
            else:
                name = resource_data.get('name', '')
                description = resource_data.get('description', 'No description')
                uri = resource_data.get('uri', '')
            
            resource = VMEResource(
                name=name,
                description=description,
                uri=uri,
                server_name=self.config.name
            )
            self.resources.append(resource)
        
        logger.debug(f"Processed {len(self.resources)} resources for {self.config.name}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on this server"""
        if not self.is_connected:
            raise Exception(f"Not connected to server {self.config.name}")
        
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise Exception(f"Tool '{tool_name}' not found on server {self.config.name}")
        
        try:
            if self.config.transport == "stdio" and self.client:
                result = await self.client.call_tool(tool_name, arguments)
            elif self.config.transport == "http" and self.http_client:
                response = await self.http_client.post(
                    "/mcp/tools/call",
                    json={"name": tool_name, "arguments": arguments}
                )
                response.raise_for_status()
                result = response.json()
            else:
                raise Exception(f"No valid client for {self.config.transport} transport")
            
            logger.debug(f"Tool {tool_name} result from {self.config.name}: {str(result)[:200]}...")
            return result
            
        except Exception as e:
            logger.error(f"Tool call failed: {tool_name} on {self.config.name} - {e}")
            raise Exception(f"Tool call failed: {e}")
    
    async def disconnect(self):
        """Disconnect from the server"""
        self.is_connected = False
        
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error disconnecting stdio client for {self.config.name}: {e}")
            finally:
                self.client = None
        
        if self.http_client:
            try:
                await self.http_client.aclose()
            except Exception as e:
                logger.warning(f"Error disconnecting HTTP client for {self.config.name}: {e}")
            finally:
                self.http_client = None
        
        self.tools.clear()
        self.resources.clear()

class MCPManager:
    """Manages multiple MCP server connections"""
    
    def __init__(self, server_configs: Dict[str, MCPServerConfig]):
        self.server_configs = server_configs
        self.servers: Dict[str, MCPServerConnection] = {}
        self.all_tools: List[VMETool] = []
        self.all_resources: List[VMEResource] = []
        
    async def connect(self) -> bool:
        """Connect to all configured MCP servers"""
        logger.info(f"Connecting to {len(self.server_configs)} MCP servers...")
        
        connected_count = 0
        for name, config in self.server_configs.items():
            if not config.enabled or not config.auto_connect:
                logger.info(f"Skipping server {name} (disabled or auto_connect=False)")
                continue
            
            server = MCPServerConnection(config)
            self.servers[name] = server
            
            try:
                if await server.connect():
                    connected_count += 1
                    logger.info(f"✅ Connected to {name}")
                else:
                    logger.warning(f"❌ Failed to connect to {name}")
            except Exception as e:
                logger.error(f"❌ Error connecting to {name}: {e}")
        
        # Rebuild aggregated tools list
        self._rebuild_tools_list()
        
        success = connected_count > 0
        if success:
            auto_connect_servers = len([c for c in self.server_configs.values() if c.enabled and c.auto_connect])
            logger.info(f"Connected to {connected_count}/{auto_connect_servers} servers - {len(self.all_tools)} tools, {len(self.all_resources)} resources")
        else:
            logger.error("Failed to connect to any MCP servers")
        
        return success
    
    async def disconnect(self):
        """Disconnect from all MCP servers"""
        logger.info("Disconnecting from all MCP servers...")
        
        for name, server in self.servers.items():
            try:
                await server.disconnect()
                logger.info(f"✅ Disconnected from {name}")
            except Exception as e:
                logger.warning(f"❌ Error disconnecting from {name}: {e}")
        
        self.servers.clear()
        self.all_tools.clear()
        self.all_resources.clear()
    
    def _rebuild_tools_list(self):
        """Rebuild the aggregated tools and resources lists from all connected servers"""
        self.all_tools.clear()
        self.all_resources.clear()
        
        for server in self.servers.values():
            if server.is_connected:
                self.all_tools.extend(server.tools)
                self.all_resources.extend(server.resources)
        
        logger.debug(f"Rebuilt lists: {len(self.all_tools)} tools, {len(self.all_resources)} resources")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the appropriate MCP server"""
        # Find the tool and determine which server it belongs to
        target_tool = None
        target_server = None
        
        for server in self.servers.values():
            if server.is_connected:
                tool = next((t for t in server.tools if t.name == tool_name), None)
                if tool:
                    target_tool = tool
                    target_server = server
                    break
        
        if not target_tool or not target_server:
            raise Exception(f"Tool '{tool_name}' not found on any connected server")
        
        logger.debug(f"Calling tool {tool_name} on server {target_server.config.name}")
        return await target_server.call_tool(tool_name, arguments)
    
    def get_tools(self) -> List[VMETool]:
        """Get list of all available tools from all servers"""
        return self.all_tools.copy()
    
    def get_tool_by_name(self, name: str) -> Optional[VMETool]:
        """Get a specific tool by name from any server"""
        return next((t for t in self.all_tools if t.name == name), None)
    
    def get_tools_by_server(self, server_name: str) -> List[VMETool]:
        """Get tools from a specific server"""
        server = self.servers.get(server_name)
        if server and server.is_connected:
            return server.tools.copy()
        return []
    
    def get_resources(self) -> List[VMEResource]:
        """Get list of all available resources from all servers"""
        return self.all_resources.copy()
    
    def get_resource_by_name(self, name: str) -> Optional[VMEResource]:
        """Get a specific resource by name from any server"""
        return next((r for r in self.all_resources if r.name == name), None)
    
    def get_resources_by_server(self, server_name: str) -> List[VMEResource]:
        """Get resources from a specific server"""
        server = self.servers.get(server_name)
        if server and server.is_connected:
            return server.resources.copy()
        return []
    
    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names"""
        return [name for name, server in self.servers.items() if server.is_connected]
    
    def has_discovery_tools(self) -> bool:
        """Check if any server has discovery tools available"""
        discovery_keywords = ['discover', 'capabilities', 'list']
        return any(
            any(keyword in tool.name.lower() for keyword in discovery_keywords)
            for tool in self.all_tools
        )
    
    async def connect_server(self, server_name: str) -> bool:
        """Manually connect to a specific server"""
        if server_name not in self.server_configs:
            logger.error(f"Server {server_name} not found in configuration")
            return False
        
        config = self.server_configs[server_name]
        if server_name in self.servers:
            # Disconnect existing connection first
            await self.servers[server_name].disconnect()
        
        server = MCPServerConnection(config)
        self.servers[server_name] = server
        
        try:
            success = await server.connect()
            if success:
                self._rebuild_tools_list()
                logger.info(f"✅ Manually connected to {server_name}")
            else:
                logger.warning(f"❌ Failed to manually connect to {server_name}")
            return success
        except Exception as e:
            logger.error(f"❌ Error manually connecting to {server_name}: {e}")
            return False
    
    async def disconnect_server(self, server_name: str) -> bool:
        """Manually disconnect from a specific server"""
        if server_name not in self.servers:
            logger.warning(f"Server {server_name} not connected")
            return False
        
        try:
            await self.servers[server_name].disconnect()
            del self.servers[server_name]
            self._rebuild_tools_list()
            logger.info(f"✅ Manually disconnected from {server_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error manually disconnecting from {server_name}: {e}")
            return False