#!/usr/bin/env python3
"""bootstrap_runtime.py — initialisateur déterministe et idempotent du socle WikiSkill v3.0.

Remplace le "forge" manuel ad-hoc (mkdir -p à la volée) à l'origine de l'incident
par un outil versionné, reproductible et auditable. Il matérialise physiquement
l'infrastructure Ouroboros manquante :

    $ROOT/runtime/evidence/traces/<skill>/{.staging, quarantine, .locks}
    $ROOT/.agents/wiki/<domaine>/{patterns, broker, archive}
    $ROOT/.agents/wiki/<domaine>/{index.tsv, logs.md, chain_head.sha256, skill-impact.md}

Idempotence : les artefacts déjà présents ne sont jamais écrasés (surtout
chain_head.sha256 et logs.md, qui sont des états dérivés chaînés).
"""
import argparse
import hashlib
import sys
from pathlib import Path

INDEX_HEADERS = ["ID", "PATTERN_NAME", "DOMAIN", "HITS", "RECENCY", "REL_PATH"]

GENESIS_LOG = """# Wiki Log — {domaine}

Journal chronologique des événements de la boucle Ouroboros (domaine `{domaine}`).
Format : `YYYY-MM-DD | ACTEUR | ACTION | RÉFÉRENCE`

(initialisé par bootstrap_runtime.py)
"""

GENESIS_IMPACT = """# Skill Impact — {domaine}

Registre des impacts de la boucle Ouroboros sur les compétences du domaine `{domaine}`.
Chaque entrée doit référencer une trace scellée (sha256) et un patch (.intent.patch) le cas échéant.

(initialisé par bootstrap_runtime.py)
"""


def resolve_root(arg_root: str) -> Path:
    if arg_root:
        return Path(arg_root).expanduser().resolve()
    env_root = sys.argv[0] and __import__("os").environ.get("TESLA_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()
    return (Path.home() / "bifrost" / "tesla").resolve()


def genesis_head(domaine: str) -> str:
    return hashlib.sha256(f"WIKISKILL_GENESIS::{domaine}".encode("utf-8")).hexdigest()


def ensure_traces(root: Path, skill: str) -> None:
    base = root / "runtime" / "evidence" / "traces" / skill
    for sub in (".staging", "quarantine", ".locks"):
        d = base / sub
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [traces] {'SKIP' if (d / '.ok').exists() else 'OK  '} {d}")
        (d / ".ok").touch(exist_ok=True)


def ensure_wiki(root: Path, domaine: str) -> None:
    base = root / ".agents" / "wiki" / domaine
    for sub in ("patterns", "broker", "archive"):
        d = base / sub
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [wiki]   OK    {d}")

    index_path = base / "index.tsv"
    if index_path.exists():
        print(f"  [wiki]   SKIP  {index_path} (existant — non écrasé)")
    else:
        index_path.write_text("\t".join(INDEX_HEADERS) + "\n", encoding="utf-8")
        print(f"  [wiki]   OK    {index_path} (en-têtes obligatoires)")

    logs_path = base / "logs.md"
    if logs_path.exists():
        print(f"  [wiki]   SKIP  {logs_path} (existant — non écrasé)")
    else:
        logs_path.write_text(GENESIS_LOG.format(domaine=domaine), encoding="utf-8")
        print(f"  [wiki]   OK    {logs_path}")

    impact_path = base / "skill-impact.md"
    if impact_path.exists():
        print(f"  [wiki]   SKIP  {impact_path} (existant — non écrasé)")
    else:
        impact_path.write_text(GENESIS_IMPACT.format(domaine=domaine), encoding="utf-8")
        print(f"  [wiki]   OK    {impact_path}")

    chain_path = base / "chain_head.sha256"
    if chain_path.exists():
        print(f"  [wiki]   SKIP  {chain_path} (existant — non écrasé)")
    else:
        chain_path.write_text(genesis_head(domaine) + "\n", encoding="utf-8")
        print(f"  [wiki]   OK    {chain_path} (tête de chaîne genesis)")


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Initialise le socle physique WikiSkill v3.0 (idempotent).")
    parser.add_argument("--root", default="", help="Racine TESLA (défaut : $TESLA_ROOT puis $HOME/bifrost/tesla).")
    parser.add_argument("--skills", default="tesla-web-raider", help="Skills (séparés par des virgules).")
    parser.add_argument("--domains", default="web-osint", help="Domaines wiki (séparés par des virgules, 1:1 avec --skills).")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    skills = [s.strip() for s in args.skills.split(",") if s.strip()]
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]

    if len(skills) != len(domains):
        print("Erreur : --skills et --domains doivent avoir la même cardinalité (mapping 1:1).", file=sys.stderr)
        return 1

    print(f"[Bootstrap] Racine : {root}")
    for skill, domaine in zip(skills, domains):
        print(f"[Bootstrap] skill={skill} -> domaine={domaine}")
        ensure_traces(root, skill)
        ensure_wiki(root, domaine)

    print("[Bootstrap] Terminé. La boucle Ouroboros est physiquement initialisable.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
