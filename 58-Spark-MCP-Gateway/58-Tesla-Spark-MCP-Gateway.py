#!/usr/bin/env python3
"""
Tesla SPARK MCP Gateway — reference implementation.

Key design decisions:
- Streamable HTTP transport (MCP 2025-03-26). SSE is deprecated.
- Endpoint is exactly /mcp (do NOT expose /mcp/sse).
- DNS-rebinding protection stays ENABLED; the tunnel/proxy host(s) are
  explicitly allowlisted instead of disabling security.
- No fake OAuth/DCR endpoints. Use header auth (`Authorization: Bearer ...`)
  when the client is remote; leave TOKEN empty for local development.
- Bind only to 127.0.0.1. Public exposure is handled by Nginx / named tunnel.

Run directly:
    python mcp_gateway.py

Or with uvicorn:
    uvicorn mcp_gateway:app --host 127.0.0.1 --port 8080
"""

from __future__ import annotations

import os
from typing import Any

import uvicorn
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# --------------------------------------------------------------------------- #
# Configuration (env-driven, no secrets committed)
# --------------------------------------------------------------------------- #
HOST = os.environ.get("TESLA_SPARK_MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("TESLA_SPARK_MCP_PORT", "8080"))
# Optional bearer token. Leave empty for loopback-only development.
TOKEN = os.environ.get("TESLA_SPARK_MCP_TOKEN", "").strip()
# Optional stable externally-facing hostname (e.g. named Cloudflare tunnel).
TUNNEL_HOST = os.environ.get("TESLA_SPARK_TUNNEL_HOST", "").strip()

# --------------------------------------------------------------------------- #
# Transport security: protect DNS rebinding while allowing real hosts
# --------------------------------------------------------------------------- #
allowed_hosts: list[str] = [
    "127.0.0.1",
    "127.0.0.1:*",
    "localhost",
    "localhost:*",
]
allowed_origins: list[str] = [
    "http://127.0.0.1:*",
    "http://localhost:*",
]

if TUNNEL_HOST:
    allowed_hosts += [TUNNEL_HOST, f"{TUNNEL_HOST}:*"]
    allowed_origins.append(f"https://{TUNNEL_HOST}")

security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=allowed_hosts,
    allowed_origins=allowed_origins,
)

# --------------------------------------------------------------------------- #
# MCP server definition
# --------------------------------------------------------------------------- #
mcp = MCPServer(
    "Tesla SPARK Gateway",
    instructions=(
        "Tesla SPARK local gateway. Currently exposes a single read-only "
        "probe tool used to validate the MCP link."
    ),
)


@mcp.tool(name="tesla_status", description="Returns the gateway operational status. Use as a connectivity proof of life.")
async def tesla_status() -> dict[str, Any]:
    """Read-only proof-of-life tool for the Tesla SPARK gateway."""
    return {
        "ok": True,
        "status": "Gateway opérationnelle",
        "service": "Tesla SPARK MCP",
        "mode": "tesla_status",
        "tier": "readonly",
        "transport": "streamable-http",
    }


# --------------------------------------------------------------------------- #
# Optional bearer auth middleware
# --------------------------------------------------------------------------- #

import httpx
import base64

GITHUB_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
GITHUB_REPO = "lordmahonheim-bot/Tesla-Antigravity-CLI"

@mcp.tool(name="github_read_file", description="Read a file from the connected GitHub repository (Tesla-Antigravity-CLI).")
async def github_read_file(path: str) -> dict[str, Any]:
    """Reads the content of a file from the repository."""
    if not GITHUB_TOKEN:
        return {"error": "GITHUB_PERSONAL_ACCESS_TOKEN not configured."}
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 404:
            return {"error": f"File not found: {path}"}
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("type") == "file" and "content" in data:
            content = base64.b64decode(data["content"]).decode('utf-8')
            return {"path": path, "content": content}
        elif isinstance(data, list):
            return {"error": f"Path is a directory, not a file: {path}"}
        return {"error": "Unable to decode file content."}

@mcp.tool(name="github_list_directory", description="List the contents of a directory in the connected GitHub repository.")
async def github_list_directory(path: str = "") -> dict[str, Any]:
    """Lists files and folders in a specific directory of the repository."""
    if not GITHUB_TOKEN:
        return {"error": "GITHUB_PERSONAL_ACCESS_TOKEN not configured."}
        
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 404:
            return {"error": f"Directory not found: {path}"}
        resp.raise_for_status()
        data = resp.json()
        
        if isinstance(data, list):
            items = [{"name": item["name"], "type": item["type"], "path": item["path"]} for item in data]
            return {"path": path or "/", "items": items}
        return {"error": f"Path is a file, not a directory: {path}"}


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Reject requests without the configured bearer token.

    When TOKEN is empty, the middleware is a no-op (local development).
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if TOKEN:
            auth = request.headers.get("authorization", "")
            expected = f"Bearer {TOKEN}"
            if auth != expected:
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)


# The Starlette ASGI app served by uvicorn. Mounted at the SDK's default
# /mcp path. Do not mount this inside a parent app under another /mcp prefix or
# the endpoint becomes /mcp/mcp.
app = BearerAuthMiddleware(mcp.streamable_http_app(transport_security=security))

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
