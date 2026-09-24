import inspect
from mcp.server import MCPServer
print(inspect.signature(MCPServer.sse_app))
