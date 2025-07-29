#!/usr/bin/env python3
"""
Route Manager for Dynamic MCP Server Configuration
Handles loading and converting YAML route configurations to FastMCP RouteMap objects.
"""

import yaml
import os
import logging
from typing import List, Dict, Any, Optional
from fastmcp.server.openapi import RouteMap, MCPType
from src.utils.client_detection import ClientCapabilities, RouteConfig
from src.shared.api_utils import get_platform_features

logger = logging.getLogger(__name__)

class RouteManager:
    """Manages route configurations for different client types"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.test_config_dir = os.path.join(config_dir, "test")
        self.platform_features = {}  # Cache for license features
        
    def get_route_maps(self, client_capabilities: ClientCapabilities, use_test_config: bool = False, 
                      api_base_url: str = None, api_token: str = None) -> List[RouteMap]:
        """
        Get route maps based on client capabilities and license features
        
        Args:
            client_capabilities: Detected client capabilities
            use_test_config: Whether to use test configurations instead of production
            api_base_url: API base URL for feature detection (optional)
            api_token: API token for feature detection (optional)
            
        Returns:
            List of RouteMap objects for FastMCP, filtered by license features
        """
        
        # Get license features for filtering (if not using test config)
        if not use_test_config and api_base_url and api_token:
            self.platform_features = get_platform_features(api_base_url, api_token)
            logger.info(f"🔧 Loaded {len(self.platform_features)} platform features for filtering")
        
        config_file = self._get_config_file(client_capabilities.route_config, use_test_config)
        
        if not os.path.exists(config_file):
            logger.warning(f"Config file {config_file} not found, using fallback")
            return self._get_fallback_routes(client_capabilities.route_config)
        
        try:
            route_maps = self._load_route_config(config_file)
            
            # Apply feature filtering (only for production configs)
            if not use_test_config and self.platform_features:
                original_count = len(route_maps)
                route_maps = self._filter_by_features(route_maps)
                filtered_count = original_count - len(route_maps)
                if filtered_count > 0:
                    logger.info(f"🚫 Filtered out {filtered_count} routes due to missing license features")
            
            logger.info(f"✅ Loaded {len(route_maps)} route maps from {config_file}")
            return route_maps
            
        except Exception as e:
            logger.error(f"Failed to load route config {config_file}: {e}")
            return self._get_fallback_routes(client_capabilities.route_config)
    
    def _get_config_file(self, route_config: RouteConfig, use_test_config: bool) -> str:
        """Determine which config file to use"""
        
        base_dir = self.test_config_dir if use_test_config else self.config_dir
        
        if route_config == RouteConfig.TOOLS_ONLY:
            filename = "routes_test_tools_only.yaml" if use_test_config else "routes_tools_only.yaml"
        elif route_config == RouteConfig.HYBRID:
            filename = "routes_test_hybrid.yaml" if use_test_config else "routes_hybrid.yaml"
        elif route_config == RouteConfig.RESOURCES_PREFERRED:
            filename = "routes_test_resources_first.yaml" if use_test_config else "routes_resources_first.yaml"
        else:
            filename = "routes_test_tools_only.yaml" if use_test_config else "routes_tools_only.yaml"
        
        return os.path.join(base_dir, filename)
    
    def _load_route_config(self, config_file: str) -> List[RouteMap]:
        """Load and parse YAML route configuration"""
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        route_maps = []
        
        # Process all route sections
        for section_name, routes in config.items():
            if section_name in ['name', 'description', 'expected_tool_count', 'expected_resource_count']:
                continue
                
            if not isinstance(routes, list):
                continue
            
            for route in routes:
                if not isinstance(route, dict) or 'pattern' not in route:
                    continue
                
                # Determine MCP type
                mcp_type_str = route.get('mcp_type', 'TOOL')
                try:
                    if mcp_type_str == 'EXCLUDE':
                        mcp_type = MCPType.EXCLUDE
                    elif mcp_type_str == 'RESOURCE':
                        mcp_type = MCPType.RESOURCE
                    elif mcp_type_str == 'RESOURCE_TEMPLATE':
                        mcp_type = MCPType.RESOURCE_TEMPLATE
                    else:
                        mcp_type = MCPType.TOOL
                except:
                    mcp_type = MCPType.TOOL
                
                # Handle HTTP methods if specified
                methods = route.get('methods', '*')  # Default to all methods
                
                # Store feature requirements for later filtering
                required_features = route.get('required_features', [])
                
                route_map = RouteMap(
                    pattern=route['pattern'],
                    mcp_type=mcp_type,
                    methods=methods
                )
                
                # Add feature requirements as metadata
                route_map._required_features = required_features
                
                route_maps.append(route_map)
        
        return route_maps
    
    def _filter_by_features(self, route_maps: List[RouteMap]) -> List[RouteMap]:
        """Filter route maps based on available platform features"""
        
        if not self.platform_features:
            return route_maps  # No filtering if no features available
        
        filtered_routes = []
        
        for route_map in route_maps:
            required_features = getattr(route_map, '_required_features', [])
            
            # If no features required, always include
            if not required_features:
                filtered_routes.append(route_map)
                continue
            
            # Check if all required features are available and enabled
            features_satisfied = all(
                self.platform_features.get(feature, False) 
                for feature in required_features
            )
            
            if features_satisfied:
                filtered_routes.append(route_map)
            else:
                missing_features = [
                    feature for feature in required_features 
                    if not self.platform_features.get(feature, False)
                ]
                logger.debug(f"🚫 Excluding route {route_map.pattern} - missing features: {missing_features}")
        
        return filtered_routes
    
    def _get_fallback_routes(self, route_config: RouteConfig) -> List[RouteMap]:
        """Fallback route configuration if YAML loading fails"""
        
        if route_config == RouteConfig.TOOLS_ONLY:
            return [
                RouteMap(pattern=r"^/api/appliance-settings$", mcp_type=MCPType.TOOL),
                RouteMap(pattern=r"^/api/license.*", mcp_type=MCPType.TOOL),
                RouteMap(pattern=r"^/api/whoami$", mcp_type=MCPType.TOOL),
                RouteMap(pattern=r".*", mcp_type=MCPType.EXCLUDE)
            ]
        elif route_config == RouteConfig.HYBRID:
            return [
                RouteMap(pattern=r"^/api/appliance-settings$", mcp_type=MCPType.TOOL),
                RouteMap(pattern=r"^/api/license.*", mcp_type=MCPType.TOOL),
                RouteMap(pattern=r"^/api/instances.*", mcp_type=MCPType.TOOL),
                RouteMap(pattern=r"^/api/zones$", mcp_type=MCPType.RESOURCE),
                RouteMap(pattern=r"^/api/whoami$", mcp_type=MCPType.RESOURCE),
                RouteMap(pattern=r".*", mcp_type=MCPType.EXCLUDE)
            ]
        else:  # RESOURCES_PREFERRED
            return [
                RouteMap(pattern=r"^/api/zones.*", mcp_type=MCPType.RESOURCE),
                RouteMap(pattern=r"^/api/whoami$", mcp_type=MCPType.RESOURCE),
                RouteMap(pattern=r"^/api/appliance-settings$", mcp_type=MCPType.RESOURCE),
                RouteMap(pattern=r"^/api/instances$", mcp_type=MCPType.TOOL),
                RouteMap(pattern=r".*", mcp_type=MCPType.EXCLUDE)
            ]
    
    def get_expected_counts(self, client_capabilities: ClientCapabilities, use_test_config: bool = False) -> Dict[str, int]:
        """Get expected tool/resource counts for validation"""
        
        config_file = self._get_config_file(client_capabilities.route_config, use_test_config)
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return {
                'tools': config.get('expected_tool_count', 0),
                'resources': config.get('expected_resource_count', 0)
            }
        except:
            # Fallback estimates
            if client_capabilities.route_config == RouteConfig.TOOLS_ONLY:
                return {'tools': 5, 'resources': 0}
            elif client_capabilities.route_config == RouteConfig.HYBRID:
                return {'tools': 8, 'resources': 3}
            else:
                return {'tools': 2, 'resources': 7}