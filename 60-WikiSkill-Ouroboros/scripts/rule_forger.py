#!/usr/bin/env python3
"""rule_forger.py - Forge deterministe de propositions .intent.patch (Phase C).

Successeur deterministe de skill_proposer.py (qui SIMULAIT un patch factice).
Seules les regles corroborant des SUCCES repetes sont forgees :
    - outcome == "success" (les echecs restent en memoire wiki, jamais en regle)
    - HITS >= seuil (defaut 3) et score moyen >= seuil (defaut 0.7)
    - aucune source QUARANTINED (AST) dans le pattern
    - skill cible connu et routable (jamais "unknown")
    - aucune proposition ouverte pour le meme (skill, pattern)

Le patch emis respecte le format canonique accepte par intent_formatter.py,
patch_broker.py et git apply :
    ```json {metadonnees} ``` + diff --git (prefixes a/ b/).

La justification est bornee (<= 50 mots) et le corps de regle est borne
(<= 40 lignes ajoutees) : budget semantique anti-hypertrophie.

CLI :
    python3 rule_forger.py --pattern-key "skill::domaine::outcome" [--root DIR]
    python3 rule_forger.py --auto [--root DIR] [--min-hits 3] [--min-score 0.7]
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distiller import aggregate_patterns
from intent_formatter import MAX_JUSTIFICATION_WORDS
from intent_formatter import validate_patch as validate_intent
from patch_broker import validate_patch as validate_broker
from trace_writer import resolve_tesla_root

MAX_ADDED_LINES = 40
MANAGER = "tesla-wiki-manager"


def proposals_dir(root: Path) -> Path:
    path = root / ".agents" / "skills" / MANAGER / "proposals"
    path.mkdir(parents=True, exist_ok=True)
    (path / "accepted").mkdir(exist_ok=True)
    (path / "quarantine").mkdir(exist_ok=True)
    return path


def has_open_proposal(root: Path, skill: str, pattern_id: str) -> bool:
    direct = proposals_dir(root) / f"{skill}__{pattern_id}.intent.patch"
    return direct.exists()


def _wiki_current(root: Path, skill: str) -> tuple[str, str]:
    wiki_path = root / ".agents" / "skills" / skill / "WIKI.md"
    if not wiki_path.exists():
        return "", "genesis"
    content = wiki_path.read_text(encoding="utf-8")
    parent = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    return content, parent


def _latest_excerpt(root: Path, rel_path: str) -> str:
    note = root / ".agents" / rel_path
    if not note.is_file():
        return "evidence unavailable"
    matches = re.findall(r"(?m)^- Extrait: (.+)$", note.read_text(encoding="utf-8"))
    if not matches:
        return "evidence unavailable"
    return matches[-1].strip()[:400]


def build_rule_section(pattern: dict[str, str], stats: dict[str, Any],
                       excerpt: str, when: str) -> list[str]:
    traces = ", ".join(f"`{t[:12]}`" for t in stats["traces"][:5])
    lines = [
        "",
        "## Auto-learned Rules (Ouroboros)",
        "",
        f"### [rule-{pattern['id']}] {pattern['name']} (v1, {when[:10]})",
        "",
        f"- Corroborations: HITS={stats['hits']} | "
        f"mean_score={stats['mean_score']:.2f} | domain=`{pattern['domain']}`.",
        f"- Evidence: `.agents/{pattern['rel_path']}` | traces: {traces}.",
        "- Operational directive (observed, scrubbed, quoted verbatim):",
        f"> {excerpt}",
        "- Provenance: forged deterministically by Ouroboros rule_forger "
        "(no LLM).",
        "",
    ]
    return lines[:MAX_ADDED_LINES]


def build_patch_text(metadata: dict[str, str], rel_wiki: str,
                     old: str, new: str) -> str:
    header = "```json\n" + json.dumps(metadata, indent=2) + "\n```\n\n"
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    if not old:
        added = [f"+{ln}" if ln.endswith("\n") else f"+{ln}\n" for ln in new_lines]
        diff = [
            f"diff --git a/{rel_wiki} b/{rel_wiki}\n",
            "new file mode 100644\n",
            "--- /dev/null\n",
            f"+++ b/{rel_wiki}\n",
            f"@@ -0,0 +1,{len(added)} @@\n",
        ]
        diff += added
        return header + "".join(diff)
    diff = [f"diff --git a/{rel_wiki} b/{rel_wiki}\n"]
    diff += list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"a/{rel_wiki}", tofile=f"b/{rel_wiki}"))
    return header + "".join(diff)


def forge_pattern(pattern_key: str, root: Path,
                  min_hits: int = 3, min_score: float = 0.7) -> dict[str, Any]:
    """Forge (ou ignore avec motif) une proposition pour un pattern."""
    agg = aggregate_patterns(root)
    stats = agg.get(pattern_key)
    if stats is None:
        return {"forged": False, "reason": "pattern inconnu (aucune trace)"}
    pattern = stats["pattern"]
    skill = pattern_key.split("::")[0]
    outcome = pattern_key.split("::")[2] if pattern_key.count("::") == 2 else "unknown"

    ineligible = None
    if outcome != "success":
        ineligible = f"outcome={outcome} (seuls les succes deviennent des regles)"
    elif stats["quarantined"]:
        ineligible = "source QUARANTINED (AST) : forgeage interdit"
    elif skill == "unknown":
        ineligible = "skill cible inconnu : routage impossible"
    elif stats["hits"] < min_hits:
        ineligible = f"HITS={stats['hits']} < {min_hits} (corroboration insuffisante)"
    elif stats["mean_score"] < min_score:
        ineligible = f"mean_score={stats['mean_score']:.2f} < {min_score}"
    elif has_open_proposal(root, skill, pattern["id"]):
        ineligible = "proposition deja ouverte pour ce (skill, pattern)"
    if ineligible is not None:
        return {"forged": False, "reason": ineligible}

    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Anti-duplicat : ne jamais reforger une regle deja gravee dans WIKI.md.
    current, parent_hash = _wiki_current(root, skill)
    if f"[rule-{pattern['id']}]" in current:
        return {"forged": False, "reason": "regle deja gravee dans WIKI.md"}

    rel_wiki = f".agents/skills/{skill}/WIKI.md"
    excerpt = _latest_excerpt(root, pattern["rel_path"])
    section = build_rule_section(pattern, stats, excerpt, when)
    if not current:
        new_content = f"# WIKI — {skill}\n" + "".join(
            ln if ln.endswith("\n") else ln + "\n" for ln in section)
    else:
        base = current if current.endswith("\n") else current + "\n"
        new_content = base + "".join(
            ln if ln.endswith("\n") else ln + "\n" for ln in section)

    justification = (
        f"Auto-learned rule {pattern['id']}: {stats['hits']} corroborated "
        f"successes in {pattern['domain']} "
        f"(mean score {stats['mean_score']:.2f}). Evidence {pattern['rel_path']}."
    )
    assert len(justification.split()) <= MAX_JUSTIFICATION_WORDS  # garde-fou dev
    metadata = {"skill_target": skill, "justification": justification,
                "parent_hash": parent_hash}
    patch_text = build_patch_text(metadata, rel_wiki, current, new_content)

    dest = proposals_dir(root) / f"{skill}__{pattern['id']}.intent.patch"
    dest.write_text(patch_text, encoding="utf-8")

    ok_b, msg_b, _m1 = validate_broker(str(dest))
    ok_i, msg_i, _m2 = validate_intent(str(dest))
    if not (ok_b and ok_i):
        quar = proposals_dir(root) / "quarantine" / dest.name
        dest.replace(quar)
        verdict = {"verdict": "INVALID", "broker": msg_b, "intent": msg_i,
                   "forged_at": when}
        quar.with_suffix("").with_name(dest.stem + ".verdict.json").write_text(
            json.dumps(verdict, indent=2), encoding="utf-8")
        return {"forged": False, "reason": f"patch invalide -> quarantaine: {msg_b} / {msg_i}"}

    return {"forged": True, "proposal": str(dest), "skill": skill,
            "pattern_id": pattern["id"], "justification": justification}


def forge_all_eligible(root: Path, min_hits: int = 3,
                       min_score: float = 0.7) -> list[dict[str, Any]]:
    agg = aggregate_patterns(root)
    results = []
    for key in sorted(agg):
        outcome = forge_pattern(key, root, min_hits, min_score)
        outcome["pattern_key"] = key
        results.append(outcome)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Forge deterministe de regles (Phase C).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pattern-key", help="Cle de pattern skill::domaine::outcome")
    group.add_argument("--auto", action="store_true",
                       help="Forge toutes les regles eligibles")
    parser.add_argument("--root", default=None, help="Racine Tesla")
    parser.add_argument("--min-hits", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.7)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else resolve_tesla_root()

    if args.auto:
        results = forge_all_eligible(root, args.min_hits, args.min_score)
        forged = [r for r in results if r["forged"]]
        for res in results:
            status = "FORGE" if res["forged"] else "SKIP"
            detail = res.get("proposal", res.get("reason"))
            print(f"[Forger] [{status}] {res['pattern_key']} :: {detail}")
        print(f"[Forger] {len(forged)}/{len(results)} proposition(s) forgee(s).")
        return 0

    outcome = forge_pattern(args.pattern_key, root, args.min_hits, args.min_score)
    if outcome["forged"]:
        print(f"[Forger] Proposition forgee : {outcome['proposal']}")
        return 0
    print(f"[Forger] Aucune forge : {outcome['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
