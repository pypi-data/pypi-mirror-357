# MCP Stdio Client Tool Visibility Issue

## Problem
When using stdio transport, MCP clients cache the initial tool list and don't automatically refresh when new tools are added dynamically. This causes errors like:
```
Tool 'vme_compute_Create_an_Instance' not found on any connected server
```

## Root Cause
1. MCP clients call `tools/list` once during initial connection
2. With stdio transport, servers cannot push notifications about new tools
3. Clients maintain a cached tool list that doesn't update
4. Dynamically added tools exist on the server but aren't visible to the client

## Verified Behavior
Testing confirms:
- Tools ARE successfully added to the server via `mcp.add_tool()`
- The server can execute these tools when called
- The issue is purely client-side caching

## Solutions

### 1. Direct Tool Invocation (Recommended)
Tell the LLM to try calling the tool anyway:
```
Even if 'vme_compute_Create_an_Instance' doesn't appear in your tool list,
JUST TRY CALLING IT - it IS available on the server and WILL work!
```

### 2. Refresh Tool List
We've added a `refresh_tool_list()` tool that provides server state and reminds the LLM to refresh.

### 3. Clear Instructions in Discovery Functions
All discovery functions now include:
- Tool count changes (e.g., "increased from 19 to 42 tools")
- Explicit notes about stdio client limitations
- Instructions to try calling tools directly

## Technical Details

### Server Implementation
```python
# Tools are properly added to the server
mcp.add_tool(tool)  # This works!

# Server has the tool
assert "vme_compute_Create_an_Instance" in mcp._tool_manager._tools  # True!
```

### Client Limitation
- Initial connection: Client calls `tools/list` → gets 19 tools
- After activation: Server has 42 tools, but client still sees 19
- No mechanism in stdio transport to notify client of changes

## Workarounds for LLMs

1. **Just Try It**: Instruct LLMs to attempt tool calls even if not listed
2. **Explicit Examples**: Provide exact tool call syntax in responses
3. **State Awareness**: Include server tool counts to show changes occurred

## Future Improvements

Consider:
1. WebSocket transport for real-time updates
2. Client-side polling mechanism
3. Tool versioning/timestamps to detect changes