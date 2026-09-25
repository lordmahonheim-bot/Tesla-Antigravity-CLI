import inspect

from mcp.server import MCPServer

print(inspect.getsource(MCPServer.streamable_http_app))
