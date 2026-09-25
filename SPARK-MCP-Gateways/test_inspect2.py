import inspect

from mcp.server.lowlevel.server import Server

print(inspect.getsource(Server.streamable_http_app))
