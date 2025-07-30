# VME Infrastructure Guide for LLMs
## Understanding Your VME Environment

### 🏗️ **Cluster Architecture**
Your VME environment is an **HPE VM 1.2 HCI Ceph Cluster** running on Ubuntu 24.04, **NOT** a VMware environment.

**Key Infrastructure Details:**
- **Cluster Name**: prod01
- **Cluster Type**: HPE VM (Hyper-Converged Infrastructure)
- **Storage**: Ceph distributed storage
- **Virtualization**: KVM-based (morpheus VMs), not VMware
- **Zone**: tc-lab (production zone)

### 🖥️ **Compute Nodes**
The cluster consists of 3 compute nodes:
- **vme01**: Primary HCI host (morpheus-node)
- **vme02**: HCI host (morpheus-node) 
- **vme03**: HCI host (morpheus-node)

**Compute Server Type**: `mvm` (Morpheus VM) - KVM-based virtualization

### 📋 **VM Creation Workflow for This Environment**

#### **Step 1: Resource Discovery**
```
1. discover_compute_infrastructure()
2. Check available images: vme_virtual_images_Get_All_Virtual_Images()
   Available: Ubuntu 20.04/22.04, CentOS Stream 8/9, Rocky 8/9, Debian 11/12, AlmaLinux 8/9
3. Check service plans: vme_service_plans_Get_All_Service_Plans()
   Available: 25 plans for resource sizing
4. Check instance types: vme_instance_types_Get_All_Instance_Types_for_Provisioning()  
   Available: 13 types for workload optimization
5. Check zones: vme_zones_Get_All_Zones()
   Available: tc-lab production zone
```

#### **Step 2: Instance Type Selection for KVM**
❌ **AVOID**: VMware-related instance types (this is NOT a VMware cluster)
✅ **USE**: KVM-compatible instance types for the HCI cluster

**Recommended Instance Types for KVM/MVM:**
- Look for instance types with code containing "morpheus", "kvm", or generic VM types
- Avoid instance types with "vmware" in the name/code

#### **Step 3: Resource Selection Using Names**
Instead of dealing with complex IDs, use the helper tools to resolve names:
```
1. Select zone by name: resolve_zone_name("tc-lab") → gets zone ID
2. Select image by name: resolve_image_name("Ubuntu 22.04 LTS") → gets image ID  
3. Select service plan: resolve_service_plan_name("Small") → gets plan ID
4. Select instance type: resolve_instance_type_name("Linux VM") → gets type + layout IDs
```

#### **Step 4: VM Creation**
Use the MCP tool: `vme_compute_infrastructure_Create_an_Instance()`
```json
{
  "instance": {
    "name": "your-vm-name",
    "description": "VM description", 
    "site": {"id": "ZONE_ID_FROM_HELPER"},
    "instanceType": {"id": "TYPE_ID_FROM_HELPER"},
    "plan": {"id": "PLAN_ID_FROM_HELPER"},
    "layout": {"id": "LAYOUT_ID_FROM_HELPER"}
  },
  "zoneId": "ZONE_ID_FROM_HELPER",
  "config": {
    "createUser": false,
    "noAgent": true,
    "virtualImage": {"id": "IMAGE_ID_FROM_HELPER"}
  }
}
```

### 🔍 **Common Issues & Solutions**

#### **"You must select an instance type" Error**
This usually means:
1. Using VMware instance type on KVM cluster ❌
2. Missing required layout from instance type ❌  
3. Instance type not compatible with selected image ❌

**Solution**: 
1. Use `vme_instance_types_Get_All_Instance_Types_for_Provisioning()` to see available types
2. Use `resolve_instance_type_name("Linux VM")` or similar to get KVM-compatible type
3. Helper automatically includes layout ID from instance type

#### **Image Compatibility**
- **Linux Images**: Work with most KVM instance types
- **Windows Images**: May require specific Windows-compatible instance types
- **Image-Type Matching**: Ensure instance type supports the selected OS

### 🎯 **Successful VM Creation Checklist**
- [ ] Called `discover_compute_infrastructure()` to activate VM tools
- [ ] Used `vme_virtual_images_Get_All_Virtual_Images()` to see available OS images
- [ ] Used helper tools to resolve names to IDs (avoid hardcoded IDs)
- [ ] Selected KVM-compatible instance type (not VMware)
- [ ] Used zone "tc-lab" (resolved to ID by helper)
- [ ] Matched compatible image and instance type
- [ ] Included service plan for resource allocation

### 🔧 **Resource Limits & Quotas**
From license information:
- **Max MVM Sockets**: 6 (currently at limit)
- **Current Usage**: 47 VMs running
- **Storage**: ~1.8TB used of available capacity
- **Memory**: ~222GB allocated

### 💡 **Pro Tips for LLMs**
1. **Always check cluster type first** - this is HCI/KVM, not VMware
2. **Use service plans for sizing** - they define t-shirt sizes (small/medium/large)
3. **Match image OS to instance type capabilities**
4. **Include layout ID** - required for most instance types
5. **Test with small VMs first** - to avoid resource exhaustion

### 📚 **Available MCP Tools for VM Management**
- **Discovery**: `discover_compute_infrastructure()` - Activate VM management tools
- **OS Images**: `vme_virtual_images_Get_All_Virtual_Images()` - List available OS images
- **Zones**: `vme_zones_Get_All_Zones()` - List deployment zones  
- **Service Plans**: `vme_service_plans_Get_All_Service_Plans()` - List t-shirt sizes
- **Instance Types**: `vme_instance_types_Get_All_Instance_Types_for_Provisioning()` - List VM types
- **Create VM**: `vme_compute_infrastructure_Create_an_Instance()` - Create new VM
- **VM Status**: `vme_compute_infrastructure_Get_a_Specific_Instance()` - Check VM details
- **Helper Tools**: `resolve_zone_name()`, `resolve_image_name()`, etc. - Convert names to IDs

This guide helps you understand the actual VME infrastructure so you can make informed decisions about VM creation rather than guessing configurations.