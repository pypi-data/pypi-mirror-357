#!/usr/bin/env python3
import httpx

def api_check(api_base_url: str, api_token: str, endpoint: str) -> dict:
    """
    Generic helper function to make API calls and return response data
    Returns: {"success": bool, "data": dict, "status_code": int}
    """
    try:
        client = httpx.Client(
            base_url=api_base_url,
            headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"},
            verify=False
        )
        
        response = client.get(endpoint)
        return {
            "success": response.status_code == 200,
            "data": response.json() if response.status_code == 200 else {},
            "status_code": response.status_code
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "status_code": 0,
            "error": str(e)
        }

def detect_platform_type(api_base_url: str, api_token: str) -> str:
    """
    Enhanced function to detect if this is VME or Morpheus
    Returns: 'vme', 'morpheus', or 'unknown'
    """
    result = api_check(api_base_url, api_token, "/api/license")
    
    if result["success"]:
        license_data = result["data"]
        
        # Extract license info from the nested structure
        license_info = license_data.get("license", {})
        account_name = license_info.get("accountName", "").lower()
        product_tier = license_info.get("productTier", "").lower()
        features = license_info.get("features", {})
        
        # VME detection: accountName="vme" AND productTier="core"
        if account_name == "vme" and product_tier == "core":
            return "vme"
        elif product_tier in ["enterprise", "professional"] or account_name == "morpheus":
            return "morpheus"
        
        # Additional feature-based detection for edge cases
        # VME typically has limited features compared to full Morpheus
        vme_indicators = [
            not features.get("analytics", True),      # VME lacks analytics
            not features.get("approvals", True),     # VME lacks approvals  
            not features.get("automation", True),    # VME lacks automation
            not features.get("monitoring", True),    # VME lacks monitoring
            features.get("mvmClusters", False),      # VME has MVM clusters
        ]
        
        if sum(vme_indicators) >= 3:  # Multiple VME indicators
            return "vme"
    
    return "unknown"

def get_platform_features(api_base_url: str, api_token: str) -> dict:
    """
    Get detailed platform features for route customization
    Returns: Dictionary of feature flags
    """
    result = api_check(api_base_url, api_token, "/api/license")
    
    if result["success"]:
        license_data = result["data"]
        license_info = license_data.get("license", {})
        return license_info.get("features", {})
    
    return {}