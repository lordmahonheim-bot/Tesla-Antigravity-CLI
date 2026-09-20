"""No network, API key or browser required."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from tools import tesla_ai as ai


class GeminiTests(unittest.TestCase):
    def setUp(self):
        self.client = ai.GeminiClient("test-key-not-a-secret")
        self.client.opener = Mock()

    def response(self, data):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps(data).encode()
        self.client.opener.open.return_value = response
        return response

    def test_key_header_not_url_and_timeout(self):
        self.response({"models": []})
        self.client.models()
        call = self.client.opener.open.call_args
        req = call.args[0]
        self.assertNotIn(self.client.key, req.full_url)
        self.assertEqual(req.get_header("X-goog-api-key"), self.client.key)
        self.assertEqual(call.kwargs["timeout"], 30)

    def test_redirect_rejected(self):
        self.assertIsNone(ai.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.invalid"))

    def test_models_pagination_and_filter(self):
        with patch.object(self.client, "request", side_effect=[
            {"models": [{"name": "models/gemini-test", "supportedGenerationMethods": ["generateContent"]}], "nextPageToken": "a&b"},
            {"models": [{"name": "models/embed", "supportedGenerationMethods": ["embedContent"]}]},
        ]) as request:
            self.assertEqual(self.client.models(), ["models/gemini-test"])
            self.assertIn("pageToken=a%26b", request.call_args.args[0])

    def test_pagination_bound(self):
        with patch.object(self.client, "request", return_value={"nextPageToken": "repeat"}) as request:
            with self.assertRaises(ai.BridgeError):
                self.client.models()
            self.assertEqual(request.call_count, 20)

    def test_complete_response_and_no_tools(self):
        self.response({"candidates": [{"finishReason": "STOP", "content": {"parts": [
            {"text": "private reasoning", "thought": True}, {"text": "review this"}]}}]})
        self.assertEqual(self.client.generate("models/gemini-test", "hello", 128), "review this")
        req = self.client.opener.open.call_args.args[0]
        payload = json.loads(req.data)
        self.assertNotIn("tools", payload)
        self.assertEqual(payload["generationConfig"]["maxOutputTokens"], 128)

    def test_reject_blocked_empty_truncated_tool_and_malformed(self):
        for result in [
            {}, {"promptFeedback": {"blockReason": "SAFETY"}},
            {"candidates": [{"finishReason": "MAX_TOKENS"}]},
            {"candidates": [{"finishReason": "STOP", "content": {"parts": []}}]},
            {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"functionCall": {}}]}}]},
            {"candidates": [{"finishReason": "STOP", "content": {"parts": [42]}}]},
        ]:
            with self.subTest(result=result):
                self.response(result)
                with self.assertRaises(ai.BridgeError):
                    self.client.generate("gemini-test", "hello", 128)

    def test_model_path_injection(self):
        for model in ("../foo", "x?key=y", "https://evil.invalid", "", "a/b"):
            with self.assertRaises(ai.BridgeError):
                self.client.generate(model, "hello", 128)
        self.client.opener.open.assert_not_called()

    def test_bounded_response_and_bad_json(self):
        response = self.response({})
        for body in (b"x" * (ai.MAX_RESPONSE_BYTES + 1), b"not-json", b"[]"):
            response.read.return_value = body
            with self.assertRaises(ai.BridgeError):
                self.client.request("models")
        response.read.assert_called_with(ai.MAX_RESPONSE_BYTES + 1)

    def test_redacted_errors_no_retries_by_default(self):
        for error in (
            HTTPError("https://secret", 403, "test-key-not-a-secret", {}, None),
            URLError("test-key-not-a-secret"),
            TimeoutError("test-key-not-a-secret"),
        ):
            self.client.opener.open.side_effect = error
            with self.assertRaises(ai.BridgeError) as caught:
                self.client.request("models")
            self.assertNotIn(self.client.key, str(caught.exception))

    @patch.object(ai.time, "sleep")
    def test_retry_429_bounded(self, sleep):
        self.client.retries = 2
        self.client.opener.open.side_effect = HTTPError("u", 429, "quota", {"Retry-After": "3"}, None)
        with self.assertRaises(ai.BridgeError):
            self.client.request("models")
        self.assertEqual(self.client.opener.open.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
        sleep.assert_called_with(3)

    @patch.object(ai.time, "sleep")
    def test_long_retry_after_not_ignored(self, sleep):
        self.client.retries = 2
        self.client.opener.open.side_effect = HTTPError("u", 503, "", {"Retry-After": "60"}, None)
        with self.assertRaises(ai.BridgeError):
            self.client.request("models")
        sleep.assert_not_called()
        self.assertEqual(self.client.opener.open.call_count, 1)


class LocalBoundaryTests(unittest.TestCase):
    def test_artifact_private_unique_and_not_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "review"
            first = ai.save_artifact("unsafe code", directory)
            second = ai.save_artifact("other code", directory)
            self.assertNotEqual(first, second)
            self.assertEqual(first.stat().st_mode & 0o777, 0o600)
            self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
            self.assertEqual(first.read_text(), "unsafe code\n")

    def test_symlink_and_public_directory_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(mode=0o755)
            with self.assertRaises(ai.BridgeError):
                ai.save_artifact("code", target)
            link = Path(tmp) / "link"
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaises(OSError):
                ai.save_artifact("code", link)
            self.assertEqual(list(target.iterdir()), [])

    @patch.object(ai, "GeminiClient")
    def test_no_cloud_without_consent(self, client):
        for command in ("models", "generate"):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ai.main([command]), 1)
        client.assert_not_called()

    @patch.object(ai, "GeminiClient")
    def test_doctor_offline(self, client):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(ai.main(["doctor"]), 0)
        self.assertFalse(json.loads(output.getvalue())["network_tested"])
        client.assert_not_called()

    def test_cli_generate(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-not-a-secret"}):
            stdin = io.TextIOWrapper(io.BytesIO(b"non-sensitive prompt"))
            with patch.object(ai.sys, "stdin", stdin), patch.object(ai.GeminiClient, "generate", return_value="review me") as generate:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    code = ai.main(["generate", "--allow-cloud", "--model", "gemini-test", "--output-dir", tmp])
                self.assertEqual(code, 0)
                result = json.loads(output.getvalue())
                self.assertFalse(result["executed"])
                self.assertEqual(Path(result["artifact"]).read_text(), "review me\n")
                generate.assert_called_once_with("gemini-test", "non-sensitive prompt", 2048)

    def test_invalid_input_and_key_leak_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-not-a-secret"}):
            for raw in (b"", b"x" * (ai.MAX_PROMPT_BYTES + 1), b"\xff", b"my key test-key-not-a-secret"):
                with patch.object(ai.sys, "stdin", io.TextIOWrapper(io.BytesIO(raw))), patch.object(ai.GeminiClient, "request") as request:
                    with contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(ai.main(["generate", "--allow-cloud", "--model", "gemini-test", "--output-dir", tmp]), 1)
                    request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
