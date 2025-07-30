#!/usr/bin/env python3
"""
Examine Existing VMs Script
Analyze existing VMs to understand their configuration and instance types
"""

import os
import sys
import json
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ExistingVMAnalyzer:
    """Analyzer for existing VM configurations"""
    
    def __init__(self):
        self.vme_api_base_url = os.getenv("VME_API_BASE_URL", "https://vmemgr01.lab.loc/api")
        self.vme_api_token = os.getenv("VME_API_TOKEN")
        
        if not self.vme_api_token:
            raise ValueError("VME_API_TOKEN environment variable is required")
        
        # Create HTTP client
        self.http_client = httpx.AsyncClient(
            base_url=self.vme_api_base_url,
            headers={
                "Authorization": f"Bearer {self.vme_api_token}",
                "Content-Type": "application/json"
            },
            verify=False  # Disable SSL verification for lab environment
        )
    
    async def get_existing_vms(self):
        """Get all existing VMs and their configurations"""
        
        print("🔍 Analyzing Existing VM Configurations")
        print("=" * 50)
        
        try:
            response = await self.http_client.get("/api/instances")
            if response.status_code == 200:
                instances_data = response.json()
                instances = instances_data.get('instances', [])
                
                print(f"Found {len(instances)} existing VMs")
                print()
                
                # Analyze each VM
                for i, instance in enumerate(instances[:10]):  # Limit to first 10 for readability
                    print(f"🖥️  VM {i+1}: {instance.get('name', 'Unknown')}")
                    print(f"   ID: {instance.get('id')}")
                    print(f"   Status: {instance.get('status')}")
                    print(f"   Power State: {instance.get('powerState', 'Unknown')}")
                    
                    # Instance type information
                    instance_type = instance.get('instanceType', {})
                    print(f"   Instance Type: {instance_type.get('name', 'Unknown')} (ID: {instance_type.get('id', 'N/A')})")
                    print(f"   Instance Type Code: {instance_type.get('code', 'Unknown')}")
                    
                    # Layout information
                    layout = instance.get('layout', {})
                    print(f"   Layout: {layout.get('name', 'Unknown')} (ID: {layout.get('id', 'N/A')})")
                    print(f"   Layout Code: {layout.get('code', 'Unknown')}")
                    
                    # Plan/Service Plan information
                    plan = instance.get('plan', {})
                    if plan:
                        print(f"   Plan: {plan.get('name', 'Unknown')} (ID: {plan.get('id', 'N/A')})")
                    
                    # Site/Zone information
                    site = instance.get('site', {})
                    print(f"   Site/Zone: {site.get('name', 'Unknown')} (ID: {site.get('id', 'N/A')})")
                    
                    # Group information
                    group = instance.get('group', {})
                    if group:
                        print(f"   Group: {group.get('name', 'Unknown')} (ID: {group.get('id', 'N/A')})")
                    
                    # Resource information
                    memory = instance.get('memory')
                    if memory:
                        print(f"   Memory: {memory} MB")
                    
                    cores = instance.get('cores')
                    if cores:
                        print(f"   CPU Cores: {cores}")
                    
                    print()
                
                # Summarize common patterns
                print("📊 Configuration Summary:")
                instance_type_counts = {}
                layout_counts = {}
                plan_counts = {}
                
                for instance in instances:
                    # Count instance types
                    itype = instance.get('instanceType', {})
                    itype_name = itype.get('name', 'Unknown')
                    instance_type_counts[itype_name] = instance_type_counts.get(itype_name, 0) + 1
                    
                    # Count layouts
                    layout = instance.get('layout', {})
                    layout_name = layout.get('name', 'Unknown')
                    layout_counts[layout_name] = layout_counts.get(layout_name, 0) + 1
                    
                    # Count plans
                    plan = instance.get('plan', {})
                    if plan:
                        plan_name = plan.get('name', 'Unknown')
                        plan_counts[plan_name] = plan_counts.get(plan_name, 0) + 1
                
                print("Most common instance types:")
                for itype, count in sorted(instance_type_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - {itype}: {count} VMs")
                
                print("\nMost common layouts:")
                for layout, count in sorted(layout_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - {layout}: {count} VMs")
                
                print("\nMost common plans:")
                for plan, count in sorted(plan_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - {plan}: {count} VMs")
                
                return instances
                
            else:
                print(f"❌ Failed to get instances: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting instances: {e}")
            return []
    
    async def get_vm_details(self, vm_id: int):
        """Get detailed information about a specific VM"""
        
        print(f"\n🔍 Getting Detailed VM Configuration for ID: {vm_id}")
        print("=" * 50)
        
        try:
            response = await self.http_client.get(f"/api/instances/{vm_id}")
            if response.status_code == 200:
                vm_data = response.json()
                instance = vm_data.get('instance', {})
                
                print("Complete VM Configuration:")
                print(json.dumps(instance, indent=2))
                
                return instance
                
            else:
                print(f"❌ Failed to get VM details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting VM details: {e}")
            return None
    
    async def analyze_successful_configuration(self, instances: List[Dict[str, Any]]):
        """Find a successful VM configuration to use as a template"""
        
        print("\n🎯 Finding Template Configuration from Successful VMs")
        print("=" * 50)
        
        # Find a VM with HPE VM instance type
        hpe_vm_instances = []
        for instance in instances:
            itype = instance.get('instanceType', {})
            if itype.get('name') == 'HPE VM' and itype.get('id') == 3:
                hpe_vm_instances.append(instance)
        
        if hpe_vm_instances:
            template_vm = hpe_vm_instances[0]
            print(f"✅ Found template VM: {template_vm.get('name')} (ID: {template_vm.get('id')})")
            
            # Extract configuration
            config = {
                'instance_type': {
                    'id': template_vm.get('instanceType', {}).get('id'),
                    'name': template_vm.get('instanceType', {}).get('name'),
                    'code': template_vm.get('instanceType', {}).get('code')
                },
                'layout': {
                    'id': template_vm.get('layout', {}).get('id'),
                    'name': template_vm.get('layout', {}).get('name'),
                    'code': template_vm.get('layout', {}).get('code')
                },
                'plan': None,
                'site': {
                    'id': template_vm.get('site', {}).get('id'),
                    'name': template_vm.get('site', {}).get('name')
                },
                'group': {
                    'id': template_vm.get('group', {}).get('id'),
                    'name': template_vm.get('group', {}).get('name')
                } if template_vm.get('group') else None
            }
            
            # Check if it has a plan
            if template_vm.get('plan'):
                config['plan'] = {
                    'id': template_vm.get('plan', {}).get('id'),
                    'name': template_vm.get('plan', {}).get('name')
                }
            
            print("Template Configuration:")
            print(json.dumps(config, indent=2))
            
            return config
        
        print("❌ No HPE VM instances found for template")
        return None
    
    async def run_analysis(self):
        """Run the complete VM analysis"""
        
        print("🔍 VME Existing VM Analysis")
        print("=" * 50)
        
        try:
            # Get all existing VMs
            instances = await self.get_existing_vms()
            if not instances:
                return None
            
            # Find a template configuration
            template_config = await self.analyze_successful_configuration(instances)
            return template_config
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None
        finally:
            await self.http_client.aclose()

async def main():
    """Main analysis function"""
    if not os.getenv('VME_API_BASE_URL') or not os.getenv('VME_API_TOKEN'):
        print("❌ VME credentials not available")
        return None
    
    analyzer = ExistingVMAnalyzer()
    return await analyzer.run_analysis()

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n✅ Analysis completed successfully")
    else:
        print("\n❌ Analysis failed")