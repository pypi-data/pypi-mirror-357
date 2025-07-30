# Feature Request: Support for Progressive OpenAPI Tool Discovery

## Description

FastMCP currently lacks the ability to dynamically add OpenAPI-generated tools after the initial `from_openapi()` call. This limitation prevents implementing progressive tool discovery patterns where tools are revealed to LLMs gradually based on their needs.

## Current Behavior

When using `FastMCP.from_openapi()`, all tools are generated at initialization based on the provided `route_maps`:

```python
mcp = FastMCP.from_openapi(
    openapi_spec=spec,
    client=http_client,
    route_maps=initial_route_maps  # Fixed at initialization
)
```

Once created, there's no way to:
- Add new OpenAPI tools based on updated route_maps
- Progressively load tools from different sections of an OpenAPI spec
- Dynamically expand the tool set without recreating the entire FastMCP instance

## Use Case

We're building an MCP server for a large infrastructure management API with 500+ endpoints. Loading all tools at once:
- Overwhelms LLMs with too many options
- Increases token usage in tool listings
- Makes it harder for LLMs to find relevant tools

Our desired workflow:
1. Start with basic discovery tools only
2. LLM calls `discover_compute_infrastructure()` 
3. Compute-related tools (VMs, storage, etc.) become available
4. LLM calls `discover_networking()`
5. Network-related tools become available
6. Tool count grows progressively as needed

## Current Workaround

We're forced to recreate the entire FastMCP instance when tool groups are activated:

```python
def activate_tool_group(self, group_name: str):
    # Update active groups
    self.active_groups.add(group_name)
    
    # Get new route maps including newly activated group
    active_route_maps = self.get_active_route_maps()
    
    # Recreate entire FastMCP instance (not ideal!)
    global mcp
    mcp = FastMCP.from_openapi(
        openapi_spec=self.openapi_spec,
        client=self.http_client,
        route_maps=active_route_maps
    )
    
    # Re-register all custom tools
    self._register_custom_tools(mcp)
```

This approach has several drawbacks:
- Overhead of recreating the entire server instance
- Potential race conditions during recreation
- Need to re-register all custom tools
- Feels like fighting against the framework

## Proposed Solution

Add support for dynamically updating OpenAPI tools, either through:

### Option 1: Add method for updating route_maps
```python
# After initialization
mcp.update_openapi_routes(new_route_maps)
```

### Option 2: Support for incremental OpenAPI loading
```python
# Load additional tools from same OpenAPI spec with different routes
mcp.add_from_openapi(
    openapi_spec=spec,
    client=http_client,
    route_maps=additional_route_maps
)
```

### Option 3: Tool group management
```python
# Define tool groups at initialization
mcp = FastMCP.from_openapi(
    openapi_spec=spec,
    client=http_client,
    tool_groups={
        "compute": compute_route_maps,
        "network": network_route_maps,
        "storage": storage_route_maps
    },
    initial_groups=["discovery"]  # Only these are active initially
)

# Activate groups dynamically
mcp.activate_tool_group("compute")
```

## Benefits

- Enable progressive discovery patterns for large APIs
- Reduce cognitive load on LLMs
- Allow fine-grained control over tool availability
- Support dynamic API exploration workflows

## Additional Context

- We're using FastMCP 2.8.1+
- The API has 500+ endpoints organized into logical groups
- Current static approach shows all tools regardless of relevance
- This pattern would be valuable for any large API integration

## Related Issues

None found specifically addressing dynamic OpenAPI tool loading.

## Would you accept a PR?

If this feature aligns with FastMCP's design philosophy, we'd be happy to contribute an implementation. Please let us know your preferred approach.

---

**Environment:**
- FastMCP version: 2.8.1
- Python version: 3.13
- Use case: Infrastructure management API with 500+ endpoints