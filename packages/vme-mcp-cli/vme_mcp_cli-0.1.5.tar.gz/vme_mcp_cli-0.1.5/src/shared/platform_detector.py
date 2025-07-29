#!/usr/bin/env python3
"""
Platform Detection for VME vs Morpheus Enterprise
Detects platform type during startup to configure appropriate route filtering.
"""

import httpx
import yaml
import os
import logging
from typing import Dict, List, Tuple
from enum import Enum
from fastmcp.server.openapi import RouteMap, MCPType

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    VME = "vme"
    MORPHEUS = "morpheus"
    UNKNOWN = "unknown"

class PlatformDetector:
    """Detects VME vs Morpheus platform and loads appropriate route configuration"""
    
    def __init__(self, api_base_url: str, api_token: str):
        self.api_base_url = api_base_url
        self.api_token = api_token
        self.client = httpx.Client(
            base_url=api_base_url,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            },
            verify=False  # For lab environments
        )
        
    async def detect_platform(self) -> Tuple[PlatformType, Dict]:
        """
        Detect platform type by checking license endpoint
        Returns: (platform_type, detection_details)
        """
        
        logger.info("🔍 Detecting platform type...")
        
        try:
            # Try to get license information
            response = self.client.get("/api/license")
            
            if response.status_code == 200:
                license_data = response.json()
                return self._analyze_license_data(license_data)
            else:
                logger.warning(f"License endpoint returned {response.status_code}")
                return PlatformType.UNKNOWN, {"error": f"License check failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Platform detection failed: {e}")
            return PlatformType.UNKNOWN, {"error": str(e)}
    
    def _analyze_license_data(self, license_data: Dict) -> Tuple[PlatformType, Dict]:
        """Analyze license data to determine platform type"""
        
        details = {
            "license_data": license_data,
            "indicators": [],
            "confidence": "low"
        }
        
        # Convert to string for easier searching
        license_str = str(license_data).lower()
        
        # Check for VME indicators
        vme_indicators = [
            "vme" in license_str,
            "vm essentials" in license_str, 
            license_data.get("account", {}).get("name", "").lower() == "vme",
            "mvm" in license_str,  # Managed Virtual Machines
            license_data.get("productTier", "").lower() == "core"
        ]
        
        # Check for Morpheus Enterprise indicators
        morpheus_indicators = [
            "morpheus" in license_str and "enterprise" in license_str,
            license_data.get("productTier", "").lower() in ["enterprise", "professional"],
            "workflow" in license_str,
            "multi-cloud" in license_str
        ]
        
        vme_score = sum(vme_indicators)
        morpheus_score = sum(morpheus_indicators)
        
        if vme_score > morpheus_score:
            details["indicators"] = [
                f"VME account name: {license_data.get('account', {}).get('name')}",
                f"Product tier: {license_data.get('productTier')}",
                f"MVM indicators found: {'mvm' in license_str}"
            ]
            details["confidence"] = "high" if vme_score >= 3 else "medium"
            return PlatformType.VME, details
            
        elif morpheus_score > vme_score:
            details["indicators"] = [
                f"Enterprise indicators: {morpheus_score}",
                f"Product tier: {license_data.get('productTier')}"
            ]
            details["confidence"] = "high" if morpheus_score >= 2 else "medium"
            return PlatformType.MORPHEUS, details
            
        else:
            details["indicators"] = ["Unable to determine platform from license data"]
            return PlatformType.UNKNOWN, details
    
    def load_route_config(self, platform_type: PlatformType) -> List[RouteMap]:
        """Load route configuration based on detected platform"""
        
        config_dir = os.path.join(os.path.dirname(__file__), "config")
        
        if platform_type == PlatformType.VME:
            config_file = os.path.join(config_dir, "vme_routes.yaml")
        elif platform_type == PlatformType.MORPHEUS:
            config_file = os.path.join(config_dir, "morpheus_routes.yaml")
        else:
            # Fallback to basic routes if unknown
            logger.warning("Unknown platform, using basic VME routes as fallback")
            config_file = os.path.join(config_dir, "vme_routes.yaml")
        
        return self._parse_route_config(config_file, platform_type)
    
    def _parse_route_config(self, config_file: str, platform_type: PlatformType) -> List[RouteMap]:
        """Parse YAML route configuration into RouteMap objects"""
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            route_maps = []
            
            # Add all allowed route patterns
            for category, routes in config.items():
                if category in ['name', 'description', 'excluded_patterns']:
                    continue
                    
                if isinstance(routes, list):
                    for route in routes:
                        if isinstance(route, dict) and 'pattern' in route:
                            route_maps.append(RouteMap(
                                pattern=route['pattern'],
                                mcp_type=MCPType.TOOL
                            ))
            
            # Add exclusion for everything else
            route_maps.append(RouteMap(
                pattern=r".*",
                mcp_type=MCPType.EXCLUDE
            ))
            
            logger.info(f"✅ Loaded {len(route_maps)-1} route patterns for {platform_type.value}")
            return route_maps
            
        except Exception as e:
            logger.error(f"Failed to load route config {config_file}: {e}")
            # Return basic fallback routes
            return self._get_fallback_routes()
    
    def _get_fallback_routes(self) -> List[RouteMap]:
        """Fallback route configuration if YAML loading fails"""
        return [
            RouteMap(pattern=r"^/api/instances.*", mcp_type=MCPType.TOOL),
            RouteMap(pattern=r"^/api/appliance-settings$", mcp_type=MCPType.TOOL),
            RouteMap(pattern=r"^/api/license.*", mcp_type=MCPType.TOOL),
            RouteMap(pattern=r".*", mcp_type=MCPType.EXCLUDE)
        ]

async def detect_and_configure_platform(api_base_url: str, api_token: str) -> Tuple[PlatformType, List[RouteMap], Dict]:
    """
    Main function to detect platform and return appropriate route configuration
    Returns: (platform_type, route_maps, detection_details)
    """
    
    detector = PlatformDetector(api_base_url, api_token)
    platform_type, details = await detector.detect_platform()
    route_maps = detector.load_route_config(platform_type)
    
    logger.info(f"🎯 Platform detected: {platform_type.value} (confidence: {details.get('confidence', 'unknown')})")
    
    return platform_type, route_maps, details