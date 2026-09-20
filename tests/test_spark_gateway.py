"""In-process ASGI and mocked GitHub tests; never contacts a remote gateway."""
import base64
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

import httpx

PATH = Path(__file__).resolve().parents[1] / "58-Spark-MCP-Gateway/58-Tesla-Spark-MCP-Gateway.py"
spec = importlib.util.spec_from_file_location("spark_gateway", PATH)
gateway = importlib.util.module_from_spec(spec)
with patch.dict(os.environ, {
    "TESLA_SPARK_MCP_TOKEN": "test-only-token-with-at-least-32-characters",
    "TESLA_SPARK_MCP_HOST": "127.0.0.1", "TESLA_SPARK_MCP_PORT": "8080",
    "TESLA_SPARK_TUNNEL_HOST": "", "TESLA_SPARK_ALLOW_LOCAL_NO_AUTH": "0",
}):
    spec.loader.exec_module(gateway)


class ConfigTests(unittest.TestCase):
    def test_no_token_fail_closed(self):
        with patch.multiple(gateway, TOKEN="", HOST="127.0.0.1", TUNNEL_HOST="", LOCAL_NO_AUTH=False):
            with self.assertRaises(ValueError):
                gateway.validate_config()

    def test_remote_rejects_no_auth_exception(self):
        for host, tunnel in (("0.0.0.0", ""), ("127.0.0.1", "example.com")):
            with patch.multiple(gateway, TOKEN="", HOST=host, TUNNEL_HOST=tunnel, LOCAL_NO_AUTH=True):
                with self.assertRaises(ValueError):
                    gateway.validate_config()

    def test_explicit_loopback_development(self):
        with patch.multiple(gateway, TOKEN="", HOST="127.0.0.1", TUNNEL_HOST="", LOCAL_NO_AUTH=True):
            gateway.validate_config()

    def test_invalid_tunnel_and_short_token(self):
        for value in ("https://example.com", "*.example.com", "host/path", "example.com:443", "-host"):
            with patch.object(gateway, "TUNNEL_HOST", value):
                with self.assertRaises(ValueError):
                    gateway.validate_config()
        with patch.object(gateway, "TOKEN", "short"):
            with self.assertRaises(ValueError):
                gateway.validate_config()

    def test_paths(self):
        for path in ("../private", "/etc/passwd", "a/../b", "a//b", "a\\b", "a\n"):
            with self.assertRaises(ValueError):
                gateway.github_path(path)
        self.assertEqual(gateway.github_path("a?ref=other#file"), "a%3Fref%3Dother%23file")
        self.assertEqual(gateway.github_path(""), "")
        self.assertEqual(gateway.github_path("docs/a b.md"), "docs/a%20b.md")


class HttpTests(unittest.IsolatedAsyncioTestCase):
    async def test_auth_dns_origin_and_protocol(self):
        async with gateway.mcp.session_manager.run(), httpx.AsyncClient(
            transport=httpx.ASGITransport(app=gateway.app), base_url="http://localhost"
        ) as client:
            self.assertEqual((await client.post("/mcp", json={})).status_code, 401)
            self.assertEqual((await client.post("/mcp", headers={"Authorization": "Bearer wrong"}, json={})).status_code, 401)
            headers = {"Authorization": f"Bearer {gateway.TOKEN}", "Accept": "application/json, text/event-stream"}
            payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "offline-test", "version": "1"}}}
            response = await client.post("/mcp", json=payload, headers=headers)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["result"]["serverInfo"]["name"], "Tesla SPARK Gateway")
            self.assertEqual((await client.post("/mcp", json=payload, headers={**headers, "Host": "evil.invalid"})).status_code, 421)
            self.assertEqual((await client.post("/mcp", json=payload, headers={**headers, "Origin": "https://evil.invalid"})).status_code, 403)
            self.assertEqual((await client.get("/mcp/sse", headers=headers)).status_code, 404)
            listed = await client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
            self.assertEqual({t["name"] for t in listed.json()["result"]["tools"]}, {"tesla_status", "github_read_file", "github_list_directory"})
            called = await client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "tesla_status", "arguments": {}}})
            self.assertEqual(called.status_code, 200)
            self.assertFalse(called.json()["result"].get("isError", False))


class GithubTests(unittest.IsolatedAsyncioTestCase):
    async def test_directory_to_read_file_regression(self):
        with patch.object(gateway, "github_contents", AsyncMock(return_value=[])):
            self.assertIn("directory", (await gateway.github_read_file("docs"))["error"])

    async def test_utf8_file_and_binary_rejection(self):
        for raw, valid in (("Bonjour é".encode(), True), (b"\xff", False)):
            data = {"type": "file", "encoding": "base64", "content": base64.b64encode(raw).decode()}
            with patch.object(gateway, "github_contents", AsyncMock(return_value=data)):
                result = await gateway.github_read_file("a.txt")
                self.assertEqual("content" in result, valid)

    async def test_unsupported_files(self):
        for data in ({"type": "symlink"}, {"type": "file", "encoding": "none"},
                     {"type": "file", "encoding": "base64", "content": "bad!"}):
            with patch.object(gateway, "github_contents", AsyncMock(return_value=data)):
                self.assertIn("error", await gateway.github_read_file("file"))

    async def test_directory_and_error_propagation(self):
        data = [{"name": "a", "path": "docs/a", "type": "file", "extra": "ignored"}]
        with patch.object(gateway, "github_contents", AsyncMock(return_value=data)):
            result = await gateway.github_list_directory("docs")
            self.assertNotIn("extra", result["items"][0])
            self.assertFalse(result["possibly_truncated"])
        with patch.object(gateway, "github_contents", AsyncMock(return_value={"error": "sanitized"})):
            self.assertEqual(await gateway.github_read_file("a"), {"error": "sanitized"})

    async def test_http_boundaries(self):
        original_client = httpx.AsyncClient
        for response in (httpx.Response(403, text="private token"),
                         httpx.Response(200, content=b"x" * (gateway.MAX_GITHUB_BYTES + 1)),
                         httpx.Response(200, text="not json"),
                         httpx.Response(302, headers={"Location": "https://evil.invalid"})):
            seen = []

            def handler(request):
                seen.append(request)
                return response

            with patch.object(gateway, "GITHUB_TOKEN", "fake-token"), patch.object(gateway.httpx, "AsyncClient", side_effect=lambda **kwargs: original_client(transport=httpx.MockTransport(handler), **kwargs)):
                result = await gateway.github_contents("docs/a?ref=other")
                self.assertIn("error", result)
                self.assertNotIn("private token", str(result))
                self.assertEqual(len(seen), 1)
                self.assertEqual(seen[0].url.query, b"")


if __name__ == "__main__":
    unittest.main()
