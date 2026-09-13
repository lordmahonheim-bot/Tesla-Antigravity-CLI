#!/usr/bin/env python3
"""trace_writer.py — Phase A/B (WikiSkill / Ouroboros) : écriture atomique d'une trace scellée.

Canonical layout (WikiSkill v3.0) :
    $ROOT/runtime/evidence/traces/<skill>/.staging/   (atomic staging)
    $ROOT/runtime/evidence/traces/<skill>/<sha256>.json (sealed trace)
    $ROOT/.agents/wiki/<domaine>/chain_head.sha256     (hash chain, optional --update-chain)

The root is resolved from --root > $TESLA_ROOT > $HOME/bifrost/tesla. No hardcoded
user paths: the previous hardcoded "/home/lord-mahonheim/bifrost/tesla/.agents/traces"
is removed (portability fix).
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


def resolve_root(arg_root: str) -> Path:
    if arg_root:
        return Path(arg_root).expanduser().resolve()
    env_root = os.environ.get("TESLA_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    return (Path.home() / "bifrost" / "tesla").resolve()


def read_trace(json_filepath: str) -> dict:
    try:
        with open(json_filepath, "rb") as f:
            data = f.read()
        payload = json.loads(data)
    except FileNotFoundError:
        print(f"Erreur : fichier introuvable {json_filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Erreur de lecture ou JSON invalide : {e}", file=sys.stderr)
        sys.exit(1)
    return payload, data


def update_chain_head(wiki_dir: Path, trace_sha256: str) -> None:
    chain_path = wiki_dir / "chain_head.sha256"
    if chain_path.is_file():
        prev = chain_path.read_text(encoding="utf-8").strip()
    else:
        prev = ""
    new_head = hashlib.sha256((prev + trace_sha256).encode("utf-8")).hexdigest()
    chain_path.write_text(new_head + "\n", encoding="utf-8")
    print(f"[Chain] chain_head.sha256 mis à jour : {new_head}")


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Écrit une trace scellée dans le sas d'évidence WikiSkill.")
    parser.add_argument("json_filepath", help="Chemin du fichier trace JSON (déjà scellé par schemas.py --seal).")
    parser.add_argument("--root", default="", help="Racine TESLA (défaut : $TESLA_ROOT puis $HOME/bifrost/tesla).")
    parser.add_argument("--skill", default="", help="Nom du skill (défaut : champ 'skill' de la trace).")
    parser.add_argument("--domain", default="", help="Domaine wiki (défaut : champ 'domaine' de la trace).")
    parser.add_argument("--update-chain", action="store_true", help="Mettre à jour .agents/wiki/<domaine>/chain_head.sha256.")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    payload, raw = read_trace(args.json_filepath)

    skill = args.skill or payload.get("skill") or "unknown"
    domaine = args.domain or payload.get("domaine") or "unknown"

    traces_dir = root / "runtime" / "evidence" / "traces" / skill
    staging_dir = traces_dir / ".staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    file_hash = hashlib.sha256(raw).hexdigest()
    dest_file = traces_dir / f"{file_hash}.json"

    if dest_file.exists():
        print(f"Trace déjà présente (idempotent) : {dest_file}")
        return 0

    fd, temp_path = tempfile.mkstemp(dir=staging_dir, suffix=".json", prefix="trace_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, dest_file)
        print(f"Trace écrite avec succès : {dest_file}")
    except Exception as e:
        print(f"Erreur lors de l'écriture de la trace : {e}", file=sys.stderr)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return 1

    if args.update_chain:
        wiki_dir = root / ".agents" / "wiki" / domaine
        wiki_dir.mkdir(parents=True, exist_ok=True)
        update_chain_head(wiki_dir, file_hash)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
