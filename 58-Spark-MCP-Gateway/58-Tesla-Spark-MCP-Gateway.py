#!/usr/bin/env python3
"""Read-only Tesla SPARK MCP Gateway (official MCP Python SDK 1.x).

Run this file directly. Requires a bearer token by default, even on loopback.
Local development without auth requires TESLA_SPARK_ALLOW_LOCAL_NO_AUTH=1.
Never use that exception with a reverse proxy/tunnel or a uvicorn bind override.
The Gemini bridge is deliberately separate: a remote tool cannot send local
files to Google, spend Gemini quota or execute generated code.
"""
from __future__ import annotations

import base64
import binascii
import hmac
import json
import os
import re
from typing import Any
from urllib.parse import quote

import httpx
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

HOST = os.environ.get("TESLA_SPARK_MCP_HOST", "127.0.0.1").strip()
PORT = int(os.environ.get("TESLA_SPARK_MCP_PORT", "8080"))
TOKEN = os.environ.get("TESLA_SPARK_MCP_TOKEN", "").strip()
TUNNEL_HOST = os.environ.get("TESLA_SPARK_TUNNEL_HOST", "").strip()
LOCAL_NO_AUTH = os.environ.get("TESLA_SPARK_ALLOW_LOCAL_NO_AUTH") == "1"
GITHUB_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
GITHUB_REPO = "lordmahonheim-bot/Tesla-Antigravity-CLI"
MAX_GITHUB_BYTES = 2 * 1024 * 1024


def validate_config() -> None:
    """Fail closed before serving; never expose credentials in diagnostics."""
    if not 1 <= PORT <= 65535:
        raise ValueError("Invalid MCP port.")
    if not TOKEN and not (LOCAL_NO_AUTH and HOST in {"127.0.0.1", "localhost", "::1"} and not TUNNEL_HOST):
        raise ValueError("TESLA_SPARK_MCP_TOKEN required; unauthenticated remote access refused.")
    if TOKEN and (len(TOKEN) < 32 or not TOKEN.isascii() or any(ord(c) < 33 or ord(c) > 126 for c in TOKEN)):
        raise ValueError("MCP token must contain at least 32 printable ASCII characters without spaces.")
    if TUNNEL_HOST and (len(TUNNEL_HOST) > 253 or any(
        not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
        for label in TUNNEL_HOST.split(".")
    )):
        raise ValueError("Tunnel host must be an exact DNS hostname, without scheme, port or wildcard.")


validate_config()
allowed_hosts = ["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*", "[::1]", "[::1]:*"]
allowed_origins = ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"]
if TUNNEL_HOST:
    allowed_hosts += [TUNNEL_HOST, f"{TUNNEL_HOST}:443"]
    allowed_origins.append(f"https://{TUNNEL_HOST}")

security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=allowed_hosts,
    allowed_origins=allowed_origins,
)
mcp = FastMCP(
    "Tesla SPARK Gateway",
    instructions="Read-only status and GitHub tools. No local execution or Gemini generation.",
    host=HOST, port=PORT, transport_security=security,
    stateless_http=True, json_response=True,
)


@mcp.tool(name="tesla_status", description="Read-only gateway connectivity probe; not a MIDGARD hardware audit.")
async def tesla_status() -> dict[str, Any]:
    """Report only this process, never imply remote hardware was verified."""
    return {
        "ok": True, "service": "Tesla SPARK MCP", "tier": "readonly",
        "transport": "streamable-http", "gemini_execution": False,
        "authenticated": bool(TOKEN), "hardware_verified": False,
    }


def github_path(path: str) -> str:
    """Only relative repository paths; prevent query/traversal injection."""
    if len(path) > 1024 or any(ord(c) < 32 or ord(c) == 127 for c in path):
        raise ValueError("Invalid repository path.")
    if path and (path.startswith("/") or "\\" in path or any(p in {"", ".", ".."} for p in path.split("/"))):
        raise ValueError("Invalid repository path.")
    return quote(path, safe="/")


async def github_contents(path: str) -> dict | list:
    """Bound GitHub latency/memory; return sanitized errors and no redirects."""
    try:
        encoded = github_path(path)
    except ValueError:
        return {"error": "Invalid repository path."}
    if not GITHUB_TOKEN:
        return {"error": "GitHub read access not configured."}
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
            async with client.stream("GET", f"https://api.github.com/repos/{GITHUB_REPO}/contents/{encoded}", headers=headers) as response:
                if response.status_code != 200:
                    return {"error": f"GitHub HTTP {response.status_code}; check path, permissions or quota."}
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > MAX_GITHUB_BYTES:
                        return {"error": "GitHub response exceeds 2 MiB."}
        data = json.loads(body)
        if not isinstance(data, (dict, list)):
            return {"error": "Invalid GitHub response."}
        return data
    except (httpx.HTTPError, ValueError):
        return {"error": "GitHub network or response error."}


@mcp.tool(name="github_read_file", description="Read a UTF-8 file from the Tesla-Antigravity-CLI repository; never execute its content.")
async def github_read_file(path: str) -> dict[str, Any]:
    """Handle directory, binary, symlink and oversize responses safely."""
    data = await github_contents(path)
    if isinstance(data, list):
        return {"error": "Path is a directory, not a file."}
    if "error" in data:
        return data
    if data.get("type") != "file" or data.get("encoding") != "base64" or data.get("target"):
        return {"error": "Not a supported inline file (symlink, submodule or oversized file)."}
    try:
        content = base64.b64decode("".join(data["content"].split()), validate=True).decode("utf-8")
    except (KeyError, AttributeError, TypeError, ValueError, binascii.Error):
        return {"error": "File is not valid base64 UTF-8 content."}
    return {"path": path, "content": content}


@mcp.tool(name="github_list_directory", description="List a directory in the connected Tesla GitHub repository.")
async def github_list_directory(path: str = "") -> dict[str, Any]:
    """List metadata only, without downloading file content."""
    data = await github_contents(path)
    if isinstance(data, dict):
        return data if "error" in data else {"error": "Path is a file, not a directory."}
    try:
        items = [{key: item[key] for key in ("name", "type", "path")} for item in data]
    except (KeyError, TypeError):
        return {"error": "Invalid GitHub directory response."}
    return {"path": path or "/", "items": items, "possibly_truncated": len(items) >= 1000}


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Authenticate before MCP dispatch, using constant-time byte comparison."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if TOKEN:
            auth = request.headers.get("authorization", "").encode("utf-8")
            if not hmac.compare_digest(auth, f"Bearer {TOKEN}".encode("ascii")):
                return JSONResponse({"error": "unauthorized"}, status_code=401, headers={"WWW-Authenticate": "Bearer"})
        return await call_next(request)


app = BearerAuthMiddleware(mcp.streamable_http_app())

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
