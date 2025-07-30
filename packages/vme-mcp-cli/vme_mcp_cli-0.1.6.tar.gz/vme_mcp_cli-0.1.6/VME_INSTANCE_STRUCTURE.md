# VME Instance Creation Structure (from Ansible)

## Key Findings

### 1. ID Resolution Pattern
The Ansible uses a `vme_id` filter to convert names to IDs:
```yaml
vme_cloud_id: "{{ 'tc-lab' | vme_id('cloud', vme_api) }}"
vme_group_id: "{{ 'production' | vme_id('group', vme_api) }}"
vme_default_plan_id: "{{ '1 CPU, 4GB Memory' | vme_id('plan', vme_api) }}"
vme_default_image_id: "{{ 'ubuntu-2404' | vme_id('image', vme_api) }}"
```

### 2. Required Instance Structure
```yaml
instance:
  name: "vm-name"
  cloud: "tc-lab"  # String name, not ID
  hostName: "vm-name"
  type: "mvm"      # Morpheus VM type
  instanceType:
    code: "mvm"    # Must match type
  site:
    id: <group_id>  # Integer
  layout:
    id: <layout_id>  # Integer
    code: "mvm-1.0-single"  # Must match layout
  plan:
    id: <plan_id>   # Integer
    code: "kvm-vm-4096"  # Must match plan
    name: "1 CPU, 4GB Memory"  # Must match plan
```

### 3. Config Section
```yaml
config:
  resourcePoolId: "pool-1"  # String!
  poolProviderType: "mvm"
  imageId: <image_id>  # Integer
  kvmHostId: 1  # Which KVM host
  createUser: true
```

### 4. Volumes Structure
```yaml
volumes:
  - id: -1  # Negative ID for new volume
    rootVolume: true
    name: "root"
    size: 40  # GB
    storageType: 1
    datastoreId: <datastore_id>
```

### 5. Network Interfaces
```yaml
networkInterfaces:
  - primaryInterface: true
    ipMode: "static"  # or "dhcp"
    ipAddress: "10.200.11.10"  # Only for static
    network:
      id: "network-<id>"  # String with prefix!
    networkInterfaceTypeId: 10
```

### 6. Important Details
- `zoneId` is at root level, not inside instance
- `layoutSize` is at root level (1 = single node)
- Some IDs are integers, some are strings
- Network IDs have "network-" prefix
- Resource pool ID is a string, not integer
- Volume ID of -1 indicates new volume creation

### 7. Minimal Required Fields
Based on the structure, minimal VM creation needs:
- zoneId (integer)
- instance.name
- instance.site.id
- instance.layout.id (with matching code)
- instance.plan.id (with matching code and name)
- config.imageId
- volumes array with at least root volume
- networkInterfaces array with at least one interface