#!/usr/bin/env python3
"""Gemini REST client for Terminator: explicit cloud consent, never executes output.

Python 3.10+, standard library only. No browser, repository indexing, shell,
SDK telemetry, local model, or persistent chat history.
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_ROOT = "https://generativelanguage.googleapis.com/v1beta/"
MAX_PROMPT_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MODEL_RE = re.compile(r"(?:models/)?([A-Za-z0-9][A-Za-z0-9._-]{0,127})\Z")


class BridgeError(Exception):
    """User-safe error: never include credentials or raw API bodies."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward an API credential to a redirected host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GeminiClient:
    """Bounded synchronous REST requests; only 429/503 can be retried."""

    def __init__(self, key: str, timeout: int = 30, retries: int = 0):
        if not key or any(ord(c) < 33 or ord(c) > 126 for c in key):
            raise BridgeError("GEMINI_API_KEY absente ou invalide.")
        self.key = key
        self.timeout = timeout
        self.retries = retries
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, path: str, payload: dict | None = None) -> dict:
        """Call the fixed TLS endpoint; sanitize all transport errors."""
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            API_ROOT + path, data=data,
            headers={"x-goog-api-key": self.key, "Content-Type": "application/json"},
        )
        for attempt in range(self.retries + 1):
            try:
                with self.opener.open(request, timeout=self.timeout) as response:
                    body = response.read(MAX_RESPONSE_BYTES + 1)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise BridgeError("Réponse trop volumineuse; rien n'a été sauvegardé.")
                result = json.loads(body)
                if not isinstance(result, dict):
                    raise BridgeError("Format de réponse API invalide.")
                return result
            except urllib.error.HTTPError as exc:
                status = exc.code
                retry_after = exc.headers.get("Retry-After", "") if exc.headers else ""
                exc.close()
                delay = min(2 ** attempt, 8)
                # Do not retry earlier than Google's numeric Retry-After.
                # Long or date-form delays require an explicit later invocation.
                if retry_after:
                    if len(retry_after) > 2 or not retry_after.isdigit() or int(retry_after) > 30:
                        raise BridgeError(f"HTTP {status}: réessayer plus tard.") from None
                    delay = max(delay, int(retry_after))
                if status in (429, 503) and attempt < self.retries:
                    time.sleep(delay)
                    continue
                hints = {
                    400: "requête ou paramètres incompatibles avec ce modèle",
                    401: "authentification refusée",
                    403: "vérifier clé, restrictions, autorisations et région",
                    404: "modèle indisponible; utiliser la commande models",
                    429: "quota dépassé; vérifier les limites et la facturation",
                    503: "service temporairement indisponible",
                }
                raise BridgeError(f"HTTP {status}: {hints.get(status, 'requête refusée')}.") from None
            except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException):
                raise BridgeError("Erreur réseau/TLS, délai dépassé ou JSON invalide; aucune relance automatique.") from None
        raise BridgeError("Requête interrompue.")

    def models(self) -> list[str]:
        """Discover generateContent models, with bounded pagination."""
        names = set()
        token = ""
        for _ in range(20):
            query = urllib.parse.urlencode({"pageSize": 100, "pageToken": token})
            result = self.request("models?" + query)
            entries = result.get("models", [])
            if not isinstance(entries, list):
                raise BridgeError("Liste de modèles invalide.")
            for model in entries:
                if not isinstance(model, dict):
                    raise BridgeError("Métadonnées de modèle invalides.")
                name = model.get("name", "")
                methods = model.get("supportedGenerationMethods") or []
                if not isinstance(methods, list):
                    raise BridgeError("Capacités de modèle invalides.")
                if (isinstance(name, str) and MODEL_RE.fullmatch(name)
                        and "generateContent" in methods):
                    names.add(name)
            token = result.get("nextPageToken", "")
            if not token:
                return sorted(names)
            if not isinstance(token, str) or len(token) > 4096:
                raise BridgeError("Pagination API invalide.")
        raise BridgeError("Pagination API excessive; liste non exhaustive refusée.")

    def generate(self, model: str, prompt: str, max_tokens: int) -> str:
        """Return only a complete text candidate; never invoke model tools."""
        match = MODEL_RE.fullmatch(model)
        if not match:
            raise BridgeError("Modèle invalide; choisir un identifiant retourné par models.")
        result = self.request(f"models/{match.group(1)}:generateContent", {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"candidateCount": 1, "maxOutputTokens": max_tokens},
        })
        try:
            if result.get("promptFeedback", {}).get("blockReason"):
                raise BridgeError("Prompt bloqué par le fournisseur; aucun artefact créé.")
            candidate = result["candidates"][0]
            if candidate.get("finishReason") != "STOP":
                raise BridgeError("Réponse bloquée, tronquée ou incomplète; aucun artefact créé.")
            parts = candidate["content"]["parts"]
            if not isinstance(parts, list) or any(not isinstance(p, dict) for p in parts):
                raise BridgeError("Réponse textuelle invalide.")
            if any("functionCall" in p or "executableCode" in p for p in parts):
                raise BridgeError("Appel d'outil/code exécutable refusé.")
            text = "\n".join(p["text"] for p in parts if "text" in p and not p.get("thought"))
        except (KeyError, IndexError, TypeError, AttributeError):
            raise BridgeError("Réponse vide ou format non pris en charge.") from None
        if not text.strip():
            raise BridgeError("Réponse sans texte; aucun artefact créé.")
        return text


def save_artifact(text: str, directory: Path) -> Path:
    """Write a unique non-executable review file in an owner-only directory.

    A directory FD and O_NOFOLLOW prevent symlink replacement of the final
    directory. Ancestors must belong to a trusted local workspace.
    """
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(directory, flags)
    name = "review-" + os.urandom(12).hex() + ".md"
    try:
        metadata = os.fstat(fd)
        if metadata.st_uid != os.getuid() or metadata.st_mode & 0o077:
            raise BridgeError("Le dossier de sortie doit vous appartenir et être privé (chmod 700).")
        output_fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        try:
            with os.fdopen(output_fd, "w", encoding="utf-8") as output:
                output.write(text + "\n")
        except BaseException:
            os.unlink(name, dir_fd=fd)
            raise
    finally:
        os.close(fd)
    return directory / name


def doctor() -> dict:
    """Read local capabilities, not secrets; never claim this host is MIDGARD."""
    memory = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            if key in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
                memory[key + "_KiB"] = int(value.split()[0])
    except (OSError, ValueError):
        pass
    disks = {}
    for rotational in Path("/sys/block").glob("*/queue/rotational"):
        if rotational.parts[-3].startswith(("loop", "ram")):
            continue
        try:
            disks[rotational.parts[-3]] = rotational.read_text().strip() == "1"
        except OSError:
            pass
    try:
        swappiness = int(Path("/proc/sys/vm/swappiness").read_text())
    except (OSError, ValueError):
        swappiness = None
    return {
        "scope": "machine courante uniquement; diagnostic en lecture seule",
        "python": sys.version.split()[0],
        "tools": {name: bool(shutil.which(name)) for name in
                  ("terminator", "agy", "antigravity", "nvim", "hx", "git", "rtk")},
        "memory": memory,
        "cpu_logical_count": os.cpu_count(),
        "rotational_disks_reported_by_kernel": disks,
        "swappiness": swappiness,
        "gemini_key_present": bool(os.environ.get("GEMINI_API_KEY")),
        "model_configured": bool(os.environ.get("TESLA_GEMINI_MODEL")),
        "network_tested": False,
        "warning": "AGY détecté ne prouve ni sa compatibilité ni une isolation sandbox.",
    }


def main(argv: list[str] | None = None) -> int:
    """CLI boundary: consent before reading a prompt or contacting Google."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Diagnostic local, sans réseau")
    for name in ("models", "generate"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--allow-cloud", action="store_true", help="Autoriser cet appel réseau vers Google")
        cmd.add_argument("--timeout", type=int, choices=range(1, 121), default=30, metavar="1..120")
        cmd.add_argument("--retries", type=int, choices=range(3), default=0, help="Relances 429/503 (défaut: 0)")
        if name == "generate":
            cmd.add_argument("--model", default=os.environ.get("TESLA_GEMINI_MODEL", ""))
            cmd.add_argument("--max-output-tokens", type=int, choices=range(1, 8193), default=2048, metavar="1..8192")
            cmd.add_argument("--output-dir", type=Path, default=Path(".tesla-ai"))
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            print(json.dumps(doctor(), ensure_ascii=False, indent=2))
            return 0
        if not args.allow_cloud:
            raise BridgeError("Envoi cloud interdit sans --allow-cloud; relire et anonymiser le prompt avant envoi.")
        client = GeminiClient(os.environ.get("GEMINI_API_KEY", ""), args.timeout, args.retries)
        if args.command == "models":
            print("\n".join(client.models()))
            return 0
        if not args.model:
            raise BridgeError("Indiquer --model ou TESLA_GEMINI_MODEL après découverte avec models.")
        if sys.stdin.isatty():
            raise BridgeError("Fournir le prompt sur stdin (redirection d'un fichier relu).")
        raw = sys.stdin.buffer.read(MAX_PROMPT_BYTES + 1)
        if not raw.strip() or len(raw) > MAX_PROMPT_BYTES:
            raise BridgeError("Prompt vide ou supérieur à 64 Kio.")
        prompt = raw.decode("utf-8")
        if client.key in prompt:
            raise BridgeError("Le prompt contient la clé API; envoi refusé.")
        # Validate the destination before incurring a cloud request/cost.
        args.output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = args.output_dir.lstat()
        if args.output_dir.is_symlink() or not args.output_dir.is_dir() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise BridgeError("Dossier de sortie non privé ou lien symbolique; envoi refusé.")
        result = client.generate(args.model, prompt, args.max_output_tokens)
        artifact = save_artifact(result, args.output_dir)
        print(json.dumps({"artifact": str(artifact), "executed": False, "review_required": True}, ensure_ascii=True))
        return 0
    except (BridgeError, OSError, UnicodeError) as exc:
        message = str(exc) if isinstance(exc, BridgeError) else "Erreur locale de fichier, permissions ou encodage UTF-8."
        print("Erreur: " + message, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrompu; aucun code exécuté.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
