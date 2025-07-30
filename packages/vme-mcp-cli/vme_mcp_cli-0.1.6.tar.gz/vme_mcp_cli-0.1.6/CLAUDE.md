I have a VME/Morpheus infrastructure management system with a comprehensive OpenAPI specification (279 endpoints). I need to create an MCP server that allows LLMs to manage virtual machines and infrastructure through progressive tool discovery.

OpenAPI 3.0 spec of the VME / Morpheus API - ./hpe-vme-openapi.yaml

Key Requirements:
- Convert OpenAPI spec to MCP tools that LLMs can actually call
- Implement data-driven tool grouping (compute, networking, storage, etc.) 
- Enable progressive discovery: start with `discover_capabilities`, then activate specific tool groups
- Ensure excellent performance (sub-second tool activation)
- Support VM creation workflow: list images → get zones → create instances

Critical Technical Details:
- Must use FastMCP 2.8.1+ (not 2.7.x) to ensure OpenAPI endpoints become Tools, not Resources
- Anthropic's MCP client only supports Tools, ignores Resources/ResourceTemplates
- Need `import_server()` to properly expose tools through MCP protocol layer
- Use route filtering to avoid processing all 279 endpoints at once
- Implement proper MCP content format: `{"content": [{"type": "text", "text": "..."}]}`

Known Issues to Avoid:
- FastMCP 2.7.1 maps GET requests to Resources → LLMs can't see them
- Over-processing full OpenAPI spec causes 30+ second hangs
- Wrong return format causes MCP protocol violations
- Tools may be imported but not exposed to clients

Links supporting development that shoud be investigated:
https://www.jlowin.dev/blog/fastmcp-2-8-tool-transformation News about critical pieces needed for the developement
https://gofastmcp.com/getting-started/quickstart - VERY IMPORTANT
https://gofastmcp.com/patterns/testing
https://gofastmcp.com/clients/transports - we should start by using stdio

Grounding info about FastMCP Core Concept:
https://gofastmcp.com/servers/tools
https://gofastmcp.com/servers/resources
https://gofastmcp.com/servers/prompts
https://gofastmcp.com/servers/context

Should work with 

Expected Outcome:
LLM should be able to call `discover_compute_infrastructure_operations`, see 40+ VM management tools appear, then successfully call tools like `vme_compute_infrastructure_Get_List_of_Virtual_Images` and `vme_compute_infrastructure_Create_an_Instance`.

Please implement this MCP server with proper FastMCP 2.8.1+ integration and verify the complete VM creation workflow works.
