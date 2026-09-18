#!/usr/bin/env python3
"""trace_writer.py - Ecriture atomique des traces d'execution (Ouroboros Phase A).

BUGFIX Ouroboros Auto-Capture : le chemin de destination etait code en dur
(/home/lord-mahonheim/bifrost/tesla/.agents/traces), ce qui rendait toute
automatisation non portable (CI, autres machines, tests). La racine est
desormais resolue dans cet ordre :
    1. TESLA_ROOT (variable d'environnement)
    2. racine git (git rev-parse --show-toplevel depuis ce script)
    3. repertoire de travail courant

Le module expose une API importable (write_trace_bytes / write_trace_file)
tout en conservant l'interface CLI historique :
    python3 trace_writer.py <fichier_json>

Garanties : validation JSON, hachage SHA-256 du contenu, ecriture atomique
via .staging/ + os.replace + fsync (invariant A-003 / O_EXCL spirit).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def resolve_tesla_root() -> Path:
    """Resout la racine Tesla (portable, deterministe)."""
    env_root = os.environ.get("TESLA_ROOT", "").strip()
    if env_root and Path(env_root).is_dir():
        return Path(env_root).resolve()
    try:
        out = subprocess.run(
            ["git", "-C", str(Path(__file__).resolve().parent),
             "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10, check=False)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.cwd().resolve()


def traces_dir(root: Path | None = None) -> Path:
    """Retourne .agents/traces sous la racine donnee (cree si absent)."""
    base = (root or resolve_tesla_root()) / ".agents" / "traces"
    base.mkdir(parents=True, exist_ok=True)
    staging = base / ".staging"
    staging.mkdir(parents=True, exist_ok=True)
    quarantine = base / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)
    return base


def write_trace_bytes(data: bytes, root: Path | None = None) -> Path:
    """Valide et ecrit atomiquement une trace. Retourne le chemin final.

    Le nom de fichier est le SHA-256 du contenu (deduplication naturelle :
    une meme trace ingeree deux fois n'occupe qu'un seul fichier).
    Leve ValueError si le JSON est invalide.
    """
    try:
        json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"JSON invalide : {exc}") from exc

    file_hash = hashlib.sha256(data).hexdigest()
    dest_dir = traces_dir(root)
    dest_file = dest_dir / f"{file_hash}.json"

    fd, temp_path = tempfile.mkstemp(
        dir=str(dest_dir / ".staging"), suffix=".json", prefix="trace_")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, dest_file)
    except BaseException:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
    return dest_file


def write_trace_file(json_filepath: str, root: Path | None = None) -> Path:
    """Lit un fichier JSON et l'ingere comme trace. Retourne le chemin final."""
    with open(json_filepath, "rb") as fh:
        data = fh.read()
    return write_trace_bytes(data, root)


def write_trace(json_filepath: str) -> None:
    """Point d'entree historique (CLI). Conserve pour compatibilite."""
    try:
        dest = write_trace_file(json_filepath)
    except ValueError as exc:
        print(f"Erreur de lecture ou JSON invalide : {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Erreur lors de l'ecriture de la trace : {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Trace ecrite avec succes : {dest}")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <fichier_json>", file=sys.stderr)
        sys.exit(1)
    write_trace(sys.argv[1])
