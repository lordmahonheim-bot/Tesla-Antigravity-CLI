#!/usr/bin/env python3
"""secrets_scrubber.py - Redaction deterministe des secrets (Ouroboros Phase A).

Vigilum Codex 2.0 : schemas.ExecutionTrace exige secrets_scrubbed=True.
Ce module applique un passage de redaction par regex STDLIB-ONLY, sans
aucun appel LLM. Idempotent : un texte deja redige est inchange.

Usage:
    from secrets_scrubber import scrub_text
    clean, count = scrub_text(raw)

CLI:
    python3 secrets_scrubber.py <fichier_entree> [--in-place]
"""
from __future__ import annotations

import re
import sys

# Marqueur canonique de redaction (stable, grep-able).
REDACTED = "***REDACTED***"

# Patterns deterministes. Ordre significatif : du plus specifique au plus
# generique. Chaque pattern est comptabilise separement dans le rapport.
_PATTERNS: list[tuple[str, re.Pattern]] = [
    # Cles d'API / tokens a prefixe connu.
    ("github_token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{10,}\b")),
    ("openai_key", re.compile(r"\bsk-(proj-)?[A-Za-z0-9_-]{10,}\b")),
    ("aws_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("aws_secret", re.compile(
        r"(?i)(aws_secret_access_key['\"\s:=]+)([A-Za-z0-9/+=]{20,})")),
    ("google_key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("pypi_token", re.compile(r"\bpypi-[A-Za-z0-9_-]{10,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    # Blocs de cles privees (PEM / OpenSSH).
    ("pem_block", re.compile(
        r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
        re.DOTALL)),
    ("openssh_key", re.compile(
        r"\b(ssh-(rsa|ed25519)|ecdsa-sha2-nistp\d+)\s+[A-Za-z0-9+/=]{20,}")),
    # Bearer / Basic dans les headers.
    ("bearer", re.compile(r"(?i)(bearer\s+)[A-Za-z0-9\-._~+/=]{10,}")),
    # Mot de passe dans une URL (scheme://user:PASS@host).
    ("url_password", re.compile(r"(?i)(\b[a-z][a-z0-9+.-]*://[^/\s:@]+:)([^/\s@]{3,})(@)")),
    # Assignations generiques (api_key = "...", password: '...', token=...).
    ("kv_secret", re.compile(
        r"(?i)\b(api[_-]?key|apikey|secret|password|passwd|pwd|token|auth[_-]?token|"
        r"client[_-]?secret|private[_-]?key|access[_-]?key)\b(\s*[:=]\s*)([\"']?)([^\"'\s]{4,})([\"']?)")),
    # Fragments .env generiques (CLE_SECRETE=valeur longue).
    ("dotenv_line", re.compile(
        r"(?im)^([A-Z][A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD|PASSWD|PWD)[A-Z0-9_]*=)([^\s]{4,})$")),
]


def scrub_text(text: str) -> tuple[str, int]:
    """Redige les secrets d'un texte.

    Retourne (texte_redige, nombre_de_substitutions). Deterministe et
    idempotent.
    """
    if not text:
        return text, 0
    total = 0
    scrubbed = text
    for _name, pattern in _PATTERNS:
        if _name in ("aws_secret", "bearer"):
            scrubbed, n = pattern.subn(lambda m: m.group(1) + REDACTED, scrubbed)
        elif _name == "url_password":
            scrubbed, n = pattern.subn(
                lambda m: m.group(1) + REDACTED + m.group(3), scrubbed)
        elif _name == "kv_secret":
            scrubbed, n = pattern.subn(
                lambda m: m.group(1) + m.group(2) + m.group(3) + REDACTED + m.group(5),
                scrubbed)
        elif _name == "dotenv_line":
            scrubbed, n = pattern.subn(
                lambda m: m.group(1) + REDACTED, scrubbed)
        else:
            scrubbed, n = pattern.subn(REDACTED, scrubbed)
        total += n
    return scrubbed, total


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3) or (len(argv) == 3 and argv[2] != "--in-place"):
        print(f"Usage: {argv[0]} <fichier_entree> [--in-place]", file=sys.stderr)
        return 2
    path = argv[1]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        print(f"Erreur de lecture {path}: {exc}", file=sys.stderr)
        return 1
    scrubbed, count = scrub_text(content)
    if len(argv) == 3:
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(scrubbed)
        except OSError as exc:
            print(f"Erreur d'ecriture {path}: {exc}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(scrubbed)
    print(f"[Scrubber] {count} substitution(s) dans {path}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
