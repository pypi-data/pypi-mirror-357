# Progressive Discovery Fix Implementation Plan

## Problem Statement
- Tool count shows static "19 tools" regardless of activated groups
- Progressive discovery doesn't actually load new tools when groups are activated  
- FastMCP loads tools once at startup and never updates

## Background: Deep Dive into FastMCP Implementation

### How `from_openapi()` Works
Based on examination of FastMCP source code:

1. **One-Time Processing** (`/fastmcp/server/openapi.py`):
   - `FastMCP.from_openapi()` creates a `FastMCPOpenAPI` instance
   - In `__init__` (line 726), it parses ALL routes immediately
   - Creates tools/resources based on route_maps (lines 773-780)
   - Registers directly: `self._tool_manager._tools[tool_name] = tool` (line 887)

2. **No Post-Init OpenAPI Loading**:
   - Route processing happens entirely in `__init__`
   - No public method to process additional routes later
   - The `route_maps` are used once and discarded
   - No storage of OpenAPI spec for later processing

### How Regular Tool Registration Works
When NOT using `from_openapi()`:

1. **The `@mcp.tool()` Decorator** (`/fastmcp/server/server.py`):
   ```python
   @mcp.tool()
   def my_tool(x: int) -> str:
       return str(x)
   ```
   - Creates a `Tool` object from the function (lines 786-795)
   - Calls `self.add_tool(tool)` (line 796)

2. **The `add_tool()` Method** (line 660):
   ```python
   def add_tool(self, tool: Tool) -> None:
       """Add a tool to the server."""
       self._tool_manager.add_tool(tool)
       self._cache.clear()
   ```
   - Public method that accepts any `Tool` object
   - Works at runtime - can be called anytime
   - Tool is immediately available to clients

3. **Key Discovery: `OpenAPITool` is Just a `Tool`**:
   - `class OpenAPITool(Tool)` (line 227 in openapi.py)
   - Contains HTTP client, route info, and execution logic
   - Can be created manually and added via `add_tool()`

## Root Cause Analysis
The current implementation:
- Uses `FastMCP.from_openapi()` with initial route maps only
- `activate_tool_group()` only updates internal state
- Never creates or adds new `OpenAPITool` instances
- No mechanism to inform FastMCP about newly activated tools

## Solution: Dynamic Tool Loading via `add_tool()`

Instead of recreating the FastMCP instance, we'll:
1. Parse OpenAPI spec once at startup
2. Create `OpenAPITool` instances for ALL routes (but don't add them yet)
3. Store tools by group in a registry
4. When groups are activated, use `mcp.add_tool()` to add those tools
5. Tools become available immediately without recreation

### Benefits
- ✅ Uses public FastMCP API (`add_tool()`)
- ✅ No server recreation overhead
- ✅ Aligns with FastMCP's design
- ✅ Tools can be added/removed dynamically
- ✅ Clean, maintainable solution

---

## Implementation Sprint: Dynamic Tool Loading

**Branch**: `feature/progressive-discovery-fix`

### High-Level Tasks

#### 1. Setup and Preparation
- [ ] Create new branch: `git checkout -b feature/progressive-discovery-fix`
- [ ] Review current implementation in `progressive_discovery_server.py`
- [ ] Create backup of current working server

#### 2. Extract OpenAPI Processing Logic
- [ ] Study how `FastMCPOpenAPI` processes routes (lines 740-783 in openapi.py)
- [ ] Create method `_parse_openapi_to_tools()` that:
  - [ ] Uses `openapi.parse_openapi_to_http_routes()` to get routes
  - [ ] Processes each route with existing `_define_tool_groups()` route maps
  - [ ] Creates `OpenAPITool` instances for each route
  - [ ] Returns dict mapping group names to lists of tools
- [ ] Import necessary utilities from `fastmcp.utilities.openapi`

#### 3. Refactor Server Initialization
- [ ] Change initial FastMCP creation:
  - [ ] Create basic `FastMCP()` instance (not `from_openapi()`)
  - [ ] Set name and other settings
  - [ ] Do NOT load any OpenAPI tools yet
- [ ] Parse and store all tools:
  - [ ] Call `_parse_openapi_to_tools()` 
  - [ ] Store result in `self.tool_registry` (dict of group -> tool list)
  - [ ] Log tool counts per group

#### 4. Implement Dynamic Tool Loading
- [ ] Update `activate_tool_group()` method:
  - [ ] Check if group exists in `self.tool_registry`
  - [ ] For each tool in the group: call `mcp.add_tool(tool)`
  - [ ] Update `self.active_groups` set
  - [ ] Log number of tools added
- [ ] Add tool counting method:
  - [ ] Create `get_current_tool_count()` using MCP's tool manager
  - [ ] Use for before/after counts in activation

#### 5. Refactor Custom Tools
- [ ] Keep custom tools as-is (using `@mcp.tool()` decorator)
- [ ] Ensure they're registered on the basic FastMCP instance
- [ ] No need to re-register them (they stay registered)

#### 6. Update Discovery Functions
- [ ] Modify all `discover_*` functions to show tool count changes:
  - [ ] `discover_compute_infrastructure()`
  - [ ] `discover_networking()`
  - [ ] `discover_storage()`
  - [ ] `discover_monitoring()` 
  - [ ] `discover_management()`
- [ ] Add before/after tool counts to responses
- [ ] Update `discover_capabilities()` to show current tool count

#### 7. Testing and Validation
- [ ] Test initial state (should show 13 custom tools only)
- [ ] Test activating compute group (count should increase)
- [ ] Test calling an activated OpenAPI tool
- [ ] Test activating multiple groups
- [ ] Verify no regression in existing functionality
- [ ] Test with MCP Inspector

#### 8. Cleanup and Documentation
- [ ] Remove any recreation-related code
- [ ] Add comments explaining the new approach
- [ ] Update docstrings
- [ ] Commit with clear message about the fix

### Implementation Notes

1. **Key Imports Needed**:
   ```python
   from fastmcp.server.openapi import OpenAPITool, RouteMap, MCPType
   from fastmcp.utilities.openapi import parse_openapi_to_http_routes, format_description_with_responses
   from fastmcp.utilities.openapi import _combine_schemas  # For parameter processing
   ```

2. **Tool Creation Pattern**:
   ```python
   tool = OpenAPITool(
       client=self.http_client,
       route=route,
       name=tool_name,
       description=enhanced_description,
       parameters=combined_schema,
       tags=route_tags,
       timeout=self.timeout
   )
   ```

3. **Critical Success Factors**:
   - Tools must be properly named (use existing name generation logic)
   - Route processing must match FastMCPOpenAPI's behavior
   - All route maps must be evaluated correctly
   - Tool registry must be organized by group

### Completion Criteria
- [ ] Tool count starts at 13 (custom tools only)
- [ ] Tool count increases when groups are activated
- [ ] Activated tools are callable and functional
- [ ] No server recreation occurs
- [ ] Performance is improved (no overhead)
- [ ] Code is cleaner and more maintainable