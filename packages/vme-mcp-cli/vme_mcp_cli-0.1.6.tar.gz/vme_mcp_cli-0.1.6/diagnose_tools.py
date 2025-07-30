#!/usr/bin/env python3
"""
Diagnose tool naming and availability
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.servers.progressive_discovery_server import server_instance, mcp


def diagnose():
    """Diagnose tool issues"""
    print("="*60)
    print("TOOL DIAGNOSTIC")
    print("="*60)
    
    # Check initial state
    print("\n1. Initial State:")
    initial_tools = list(mcp._tool_manager._tools.keys()) if hasattr(mcp, '_tool_manager') else []
    print(f"   Total tools: {len(initial_tools)}")
    
    # Activate compute
    print("\n2. Activating compute group...")
    server_instance.activate_tool_group("compute")
    
    # Get all tools
    all_tools = list(mcp._tool_manager._tools.keys()) if hasattr(mcp, '_tool_manager') else []
    print(f"   Total tools after activation: {len(all_tools)}")
    
    # Look for instance creation tools
    print("\n3. Instance/VM Creation Tools:")
    create_patterns = ['create', 'instance', 'vm']
    relevant_tools = []
    
    for tool_name in all_tools:
        tool_lower = tool_name.lower()
        if any(pattern in tool_lower for pattern in create_patterns):
            relevant_tools.append(tool_name)
    
    for tool in sorted(relevant_tools):
        print(f"   - {tool}")
        # Check if it's the create instance tool
        if 'create' in tool.lower() and 'instance' in tool.lower():
            print(f"     ^^^ This should be the VM creation tool")
    
    # Check exact matches
    print("\n4. Checking exact tool names:")
    expected_names = [
        "vme_compute_Create_an_Instance",
        "vme_compute_infrastructure_Create_an_Instance",
        "Create_an_Instance",
        "vme_compute_post_api_instances"
    ]
    
    for name in expected_names:
        exists = name in all_tools
        print(f"   {name}: {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
    
    # Show what's advertised vs reality
    print("\n5. Advertised vs Actual:")
    print("   Advertised in discover_compute_infrastructure():")
    print("   - vme_compute_Create_an_Instance()")
    
    actual_create_tools = [t for t in all_tools if 'create' in t.lower() and 'instance' in t.lower()]
    print(f"\n   Actual tools with 'create' and 'instance':")
    for tool in actual_create_tools:
        print(f"   - {tool}")
    
    # Debug tool registry
    print("\n6. Tool Registry Analysis:")
    print(f"   Groups in registry: {list(server_instance.tool_registry.keys())}")
    if 'compute' in server_instance.tool_registry:
        compute_tools = server_instance.tool_registry['compute']
        print(f"   Compute group has {len(compute_tools)} tools")
        for tool in compute_tools[:5]:  # First 5
            if hasattr(tool, 'name'):
                print(f"   - {tool.name}")


if __name__ == "__main__":
    diagnose()