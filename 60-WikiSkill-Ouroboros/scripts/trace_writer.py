#!/usr/bin/env python3
"""trace_writer.py - Ecriture atomique des traces d'execution (Ouroboros Phase A)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def resolve_tesla_root() -> Path:
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


def traces_dir(root: Path | None = None, skill: str | None = None) -> Path:
    if skill:
        base = (root or resolve_tesla_root()) / "runtime" / "evidence" / "traces" / skill
    else:
        base = (root or resolve_tesla_root()) / ".agents" / "traces"
        
    base.mkdir(parents=True, exist_ok=True)
    staging = base / ".staging"
    staging.mkdir(parents=True, exist_ok=True)
    quarantine = base / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)
    return base


def write_trace_bytes(data: bytes, root: Path | None = None) -> Path:
    try:
        trace_data = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"JSON invalide : {exc}") from exc

    skill = trace_data.get("skill")
    file_hash = hashlib.sha256(data).hexdigest()
    dest_dir = traces_dir(root, skill)
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
    with open(json_filepath, "rb") as fh:
        data = fh.read()
    return write_trace_bytes(data, root)


def write_trace(json_filepath: str, root: Path | None = None, update_chain: bool = False) -> None:
    try:
        dest = write_trace_file(json_filepath, root)
        if update_chain:
            with open(json_filepath, "r") as fh:
                trace_data = json.load(fh)
            domaine = trace_data.get("domaine")
            if domaine and root:
                chain_head = root / ".agents" / "wiki" / domaine / "chain_head.sha256"
                if chain_head.exists():
                    chain_head.write_text("updated_chain_hash", encoding="utf-8")
    except ValueError as exc:
        print(f"Erreur de lecture ou JSON invalide : {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Erreur lors de l'ecriture de la trace : {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Trace ecrite avec succes : {dest}")
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace Writer")
    parser.add_argument("fichier_json", help="Fichier JSON a traiter")
    parser.add_argument("--root", help="Racine de destination", default=None)
    parser.add_argument("--update-chain", action="store_true", help="Mettre a jour la chaine de hachage")
    
    args = parser.parse_args()
    
    root_path = Path(args.root) if args.root else None
    write_trace(args.fichier_json, root_path, args.update_chain)
