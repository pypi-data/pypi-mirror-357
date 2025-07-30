#!/usr/bin/env python3
"""
Debug VM Creation Script
Helps debug the "You must select an instance type" error by testing different configurations
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

class VMCreationDebugger:
    """Debugger for VM creation issues"""
    
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
    
    async def analyze_instance_types(self):
        """Analyze available instance types to understand KVM vs VMware compatibility"""
        
        print("🔍 Analyzing Available Instance Types")
        print("=" * 50)
        
        try:
            response = await self.http_client.get("/api/instance-types")
            if response.status_code == 200:
                types_data = response.json()
                instance_types = types_data.get('instanceTypes', [])
                
                print(f"Found {len(instance_types)} instance types:")
                print()
                
                kvm_types = []
                vmware_types = []
                other_types = []
                
                for itype in instance_types:
                    name = itype.get('name', 'Unknown')
                    code = itype.get('code', 'Unknown')
                    type_id = itype.get('id')
                    active = itype.get('active', False)
                    
                    # Get layout information
                    layouts = itype.get('instanceTypeLayouts', []) or itype.get('layouts', [])
                    layout_info = []
                    for layout in layouts:
                        layout_info.append({
                            'id': layout.get('id'),
                            'name': layout.get('name', 'Unknown'),
                            'code': layout.get('code', 'Unknown')
                        })
                    
                    instance_info = {
                        'id': type_id,
                        'name': name,
                        'code': code,
                        'active': active,
                        'layouts': layout_info
                    }
                    
                    # Categorize by type
                    name_lower = name.lower()
                    code_lower = code.lower()
                    
                    if 'vmware' in name_lower or 'vmware' in code_lower:
                        vmware_types.append(instance_info)
                    elif any(keyword in name_lower or keyword in code_lower for keyword in ['kvm', 'morpheus', 'linux', 'generic', 'vm']):
                        kvm_types.append(instance_info)
                    else:
                        other_types.append(instance_info)
                
                # Print categorized results
                print("🐧 KVM-Compatible Instance Types:")
                for itype in kvm_types:
                    status = "✅ ACTIVE" if itype['active'] else "❌ INACTIVE"
                    print(f"  • {itype['name']} (ID: {itype['id']}, Code: {itype['code']}) - {status}")
                    for layout in itype['layouts']:
                        print(f"    - Layout: {layout['name']} (ID: {layout['id']}, Code: {layout['code']})")
                    print()
                
                print("🔧 VMware Instance Types (Incompatible):")
                for itype in vmware_types:
                    status = "✅ ACTIVE" if itype['active'] else "❌ INACTIVE"
                    print(f"  • {itype['name']} (ID: {itype['id']}, Code: {itype['code']}) - {status}")
                    for layout in itype['layouts']:
                        print(f"    - Layout: {layout['name']} (ID: {layout['id']}, Code: {layout['code']})")
                    print()
                
                print("❓ Other Instance Types:")
                for itype in other_types:
                    status = "✅ ACTIVE" if itype['active'] else "❌ INACTIVE"
                    print(f"  • {itype['name']} (ID: {itype['id']}, Code: {itype['code']}) - {status}")
                    for layout in itype['layouts']:
                        print(f"    - Layout: {layout['name']} (ID: {layout['id']}, Code: {layout['code']})")
                    print()
                
                return {
                    'kvm_types': kvm_types,
                    'vmware_types': vmware_types,
                    'other_types': other_types
                }
                
            else:
                print(f"❌ Failed to get instance types: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing instance types: {e}")
            return None
    
    async def get_available_resources(self):
        """Get all available resources for VM creation"""
        
        print("\n📦 Getting Available Resources")
        print("=" * 50)
        
        resources = {}
        
        try:
            # Get zones
            zones_response = await self.http_client.get("/api/zones")
            if zones_response.status_code == 200:
                zones_data = zones_response.json()
                resources['zones'] = zones_data.get('zones', [])
                print(f"✓ Found {len(resources['zones'])} zones")
            
            # Get service plans
            plans_response = await self.http_client.get("/api/service-plans")
            if plans_response.status_code == 200:
                plans_data = plans_response.json()
                resources['service_plans'] = plans_data.get('servicePlans', [])
                print(f"✓ Found {len(resources['service_plans'])} service plans")
            
            # Get virtual images
            images_response = await self.http_client.get("/api/virtual-images")
            if images_response.status_code == 200:
                images_data = images_response.json()
                resources['virtual_images'] = images_data.get('virtualImages', [])
                print(f"✓ Found {len(resources['virtual_images'])} virtual images")
            
            # Get groups
            groups_response = await self.http_client.get("/api/groups")
            if groups_response.status_code == 200:
                groups_data = groups_response.json()
                resources['groups'] = groups_data.get('groups', [])
                print(f"✓ Found {len(resources['groups'])} groups")
            
            return resources
            
        except Exception as e:
            print(f"❌ Error getting resources: {e}")
            return {}
    
    async def test_vm_creation_with_different_instance_types(self, resources: Dict[str, Any], instance_types_analysis: Dict[str, Any]):
        """Test VM creation with different instance types to find what works"""
        
        print("\n🧪 Testing VM Creation with Different Instance Types")
        print("=" * 50)
        
        # Get basic resources
        zone = resources['zones'][0] if resources['zones'] else None
        image = None
        service_plan = None
        group = resources['groups'][0] if resources['groups'] else None
        
        # Find a Linux image
        for img in resources.get('virtual_images', []):
            if img.get('active', True):
                img_name = img.get('name', '').lower()
                if any(keyword in img_name for keyword in ['ubuntu', 'centos', 'linux', 'debian', 'rocky', 'alma']):
                    image = img
                    break
        
        # Find a small service plan
        for plan in resources.get('service_plans', []):
            if plan.get('active', True):
                plan_name = plan.get('name', '').lower()
                if 'small' in plan_name or 'test' in plan_name:
                    service_plan = plan
                    break
        
        if not service_plan and resources.get('service_plans'):
            service_plan = resources['service_plans'][0]
        
        if not zone or not image:
            print("❌ Missing required resources (zone or image)")
            return
        
        print(f"Using zone: {zone.get('name')} (ID: {zone.get('id')})")
        print(f"Using image: {image.get('name')} (ID: {image.get('id')})")
        if service_plan:
            print(f"Using service plan: {service_plan.get('name')} (ID: {service_plan.get('id')})")
        if group:
            print(f"Using group: {group.get('name')} (ID: {group.get('id')})")
        print()
        
        # Test with different KVM-compatible instance types
        kvm_types = instance_types_analysis.get('kvm_types', [])
        
        for i, instance_type in enumerate(kvm_types):
            if not instance_type.get('active', False):
                print(f"Skipping inactive instance type: {instance_type['name']}")
                continue
            
            print(f"🔄 Test {i+1}: Trying instance type '{instance_type['name']}' (ID: {instance_type['id']})")
            
            # Get layout (required)
            layout = None
            if instance_type.get('layouts'):
                layout = instance_type['layouts'][0]
                print(f"   Using layout: {layout['name']} (ID: {layout['id']})")
            
            if not layout:
                print("   ❌ No layout available for this instance type")
                continue
            
            # Build VM config
            vm_config = {
                "instance": {
                    "name": f"progress01-test-{i+1}",
                    "description": f"Test VM with {instance_type['name']} instance type",
                    "site": {"id": zone['id']},
                    "instanceType": {"id": instance_type['id']},
                    "layout": {"id": layout['id']}
                },
                "zoneId": zone['id'],
                "config": {
                    "createUser": False,
                    "noAgent": True,
                    "virtualImage": {"id": image['id']}
                }
            }
            
            # Add service plan if available
            if service_plan:
                vm_config["instance"]["plan"] = {"id": service_plan['id']}
            
            # Add group if available
            if group:
                vm_config["instance"]["group"] = {"id": group['id']}
            
            # Remove None values
            def clean_dict(d):
                if isinstance(d, dict):
                    return {k: clean_dict(v) for k, v in d.items() if v is not None}
                return d
            
            vm_config = clean_dict(vm_config)
            
            print(f"   Payload: {json.dumps(vm_config, indent=2)}")
            
            try:
                # Attempt to create the VM
                response = await self.http_client.post("/api/instances", json=vm_config)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    instance = result.get('instance', {})
                    instance_id = instance.get('id')
                    
                    print(f"   ✅ SUCCESS! VM created with ID: {instance_id}")
                    print(f"   Name: {instance.get('name')}")
                    print(f"   Status: {instance.get('status')}")
                    
                    # Clean up - delete the test VM
                    if instance_id:
                        print(f"   🧹 Cleaning up test VM {instance_id}...")
                        delete_response = await self.http_client.delete(f"/api/instances/{instance_id}")
                        if delete_response.status_code in [200, 204, 404]:
                            print(f"   ✓ Test VM deleted successfully")
                        else:
                            print(f"   ⚠️  Failed to delete test VM: {delete_response.status_code}")
                    
                    # We found a working configuration, use it for the actual VM
                    return {
                        'instance_type': instance_type,
                        'layout': layout,
                        'working_config': vm_config
                    }
                    
                else:
                    print(f"   ❌ FAILED: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
            
            print()
        
        print("❌ No working instance type configuration found")
        return None
    
    async def create_progress01_vm(self, working_config: Dict[str, Any]):
        """Create the actual progress01 VM using the working configuration"""
        
        print("\n🚀 Creating progress01 VM with Working Configuration")
        print("=" * 50)
        
        # Update the config for the actual VM
        vm_config = working_config.copy()
        vm_config["instance"]["name"] = "progress01"
        vm_config["instance"]["description"] = "Progress VM created after debugging instance type issue"
        
        print(f"Final VM config: {json.dumps(vm_config, indent=2)}")
        
        try:
            response = await self.http_client.post("/api/instances", json=vm_config)
            
            if response.status_code in [200, 201]:
                result = response.json()
                instance = result.get('instance', {})
                instance_id = instance.get('id')
                
                print(f"✅ SUCCESS! progress01 VM created!")
                print(f"   ID: {instance_id}")
                print(f"   Name: {instance.get('name')}")
                print(f"   Status: {instance.get('status')}")
                print(f"   Power State: {instance.get('powerState', 'Unknown')}")
                
                return result
                
            else:
                print(f"❌ FAILED to create progress01 VM: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ ERROR creating progress01 VM: {e}")
            return None
    
    async def run_debug_workflow(self):
        """Run the complete debug workflow"""
        
        print("🔧 VME VM Creation Debug Workflow")
        print("=" * 60)
        
        try:
            # Step 1: Analyze instance types
            instance_types_analysis = await self.analyze_instance_types()
            if not instance_types_analysis:
                return False
            
            # Step 2: Get available resources
            resources = await self.get_available_resources()
            if not resources:
                return False
            
            # Step 3: Test different instance types
            working_config_result = await self.test_vm_creation_with_different_instance_types(resources, instance_types_analysis)
            if not working_config_result:
                return False
            
            # Step 4: Create the actual progress01 VM
            vm_result = await self.create_progress01_vm(working_config_result['working_config'])
            if not vm_result:
                return False
            
            print("\n🎉 DEBUG WORKFLOW COMPLETED SUCCESSFULLY!")
            print("✓ Identified KVM-compatible instance types")
            print("✓ Found working VM configuration")
            print("✓ Created progress01 VM successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Debug workflow failed: {e}")
            return False
        finally:
            await self.http_client.aclose()

async def main():
    """Main debug function"""
    if not os.getenv('VME_API_BASE_URL') or not os.getenv('VME_API_TOKEN'):
        print("❌ VME credentials not available")
        print("   Set VME_API_BASE_URL and VME_API_TOKEN environment variables")
        return False
    
    debugger = VMCreationDebugger()
    return await debugger.run_debug_workflow()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)