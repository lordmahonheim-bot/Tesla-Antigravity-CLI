from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_linter import (
    MAX_TOKENS,
    REQUIRED_COLUMNS,
)
from index_linter import (
    lint_file as lint_index_file,
)
from intent_formatter import validate_patch as validate_intent
from patch_broker import validate_patch as validate_broker

THRESHOLD = 0.9

def _check_train_val(worktree: Path) -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    indexes = sorted(worktree.glob(".agents/wiki/*/index.tsv"))
    if not indexes:
        results.append(("T1-index-present", True, "aucun index wiki : rien a regresser"))
    for idx in indexes:
        ok, msg = lint_index_file(str(idx))
        results.append((f"T1-index:{idx.parent.name}", ok, msg.splitlines()[-1]))

    wikis = sorted(worktree.glob(".agents/skills/*/WIKI.md"))
    if not wikis:
        results.append(("T2-wiki-present", True, "aucun WIKI.md : rien a regresser"))
    for wiki in wikis:
        try:
            content = wiki.read_text(encoding="utf-8")
        except OSError as exc:
            results.append((f"T2-wiki:{wiki.parent.name}", False, f"illisible: {exc}"))
            continue
        has_title = re.search(r"(?m)^#{1,3}\s+\S+", content) is not None
        non_empty = len(content.strip()) > 0
        ok = has_title and non_empty
        results.append((
            f"T2-wiki:{wiki.parent.name}", ok,
            "structure markdown OK" if ok else "WIKI.md vide ou sans titre",
        ))

    proposals = sorted(worktree.glob("**/proposals/*.intent.patch"))
    proposals += sorted((worktree / ".agents" / "skills").glob(
        "*/proposals/*.intent.patch")) if (worktree / ".agents" / "skills").is_dir() else []
    seen = set()
    uniq = []
    for prop in proposals:
        key = str(prop.resolve()) if prop.exists() else str(prop)
        if key not in seen:
            seen.add(key)
            uniq.append(prop)
    if not uniq:
        results.append(("T3-proposals-present", True, "aucune proposition : rien a valider"))
    for prop in uniq:
        ok_b, msg_b, _meta = validate_broker(str(prop))
        ok_i, msg_i, _meta2 = validate_intent(str(prop))
        ok = ok_b and ok_i
        detail = "format+brodage OK" if ok else f"broker={msg_b} | intent={msg_i}"
        results.append((f"T3-proposal:{prop.name}", ok, detail))

    return results

def _write_temp(suffix: str, content: str) -> str:
    fh = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, prefix="gate_holdout_",
        delete=False, encoding="utf-8")
    with fh:
        fh.write(content)
    return fh.name

def _check_holdout() -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []
    temps: list[str] = []
    try:
        header = "\t".join(REQUIRED_COLUMNS) + "\n"
        big_row = "id-1\tPatternName\tdomain\t99\t2026-01-01T00:00:00Z\tnote.md\n"
        filler = "x" * (MAX_TOKENS * 4 + 1024)
        oversize = _write_temp(".tsv", header + big_row + filler + "\n")
        temps.append(oversize)
        ok, _msg = lint_index_file(oversize)
        results.append(("H1-oversize-rejected", not ok,
                        "rejete (attendu)" if not ok else "ACCEPTE (faute du validateur!)"))

        bad_header = _write_temp(".tsv", "A\tB\tC\n1\t2\t3\n")
        temps.append(bad_header)
        ok, _msg = lint_index_file(bad_header)
        results.append(("H2-badheader-rejected", not ok,
                        "rejete (attendu)" if not ok else "ACCEPTE (faute du validateur!)"))

        evil_patch = _write_temp(".intent.patch", (
            "```json\n"
            '{"skill_target": "tesla-master-code", "justification": "test", '
            '"parent_hash": "00"}\n'
            "```\n"
            "diff --git a/README.md b/README.md\n"
            "--- a/README.md\n"
            "+++ b/README.md\n"
            "@@ -1 +1 @@\n"
            "-x\n+x\n"
        ))
        temps.append(evil_patch)
        ok, _msg, _meta = validate_intent(evil_patch)
        results.append(("H3-offscope-rejected", not ok,
                        "rejete (attendu)" if not ok else "ACCEPTE (faute du validateur!)"))

        long_just = "mot " * 60
        fat_patch = _write_temp(".intent.patch", (
            "```json\n"
            '{"skill_target": "tesla-master-code", '
            f'"justification": "{long_just.strip()}", "parent_hash": "00"}}\n'
            "```\n"
            "diff --git a/.agents/skills/tesla-master-code/WIKI.md "
            "b/.agents/skills/tesla-master-code/WIKI.md\n"
            "--- a/.agents/skills/tesla-master-code/WIKI.md\n"
            "+++ b/.agents/skills/tesla-master-code/WIKI.md\n"
            "@@ -1 +1,2 @@\n"
            " # T\n+# R\n"
        ))
        temps.append(fat_patch)
        ok, _msg, _meta = validate_intent(fat_patch)
        results.append(("H4-fatjust-rejected", not ok,
                        "rejete (attendu)" if not ok else "ACCEPTE (faute du validateur!)"))
    finally:
        for tmp in temps:
            try:
                os.remove(tmp)
            except OSError:
                pass
    return results

def _report(split: str, results: list[tuple[str, bool, str]]) -> float:
    passed = sum(1 for _n, ok, _d in results if ok)
    total = len(results) if results else 1
    score = passed / total
    print(f"[Judge] --- {split} : {passed}/{total} (score={score:.2f}) ---")
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        print(f"[Judge]   [{mark}] {name} :: {detail}")
    return score

def main() -> None:
    parser = argparse.ArgumentParser(description="Double-Split Gating (Juge d'evaluation).")
    parser.add_argument("worktree_path", help="Chemin du worktree a evaluer")
    parser.add_argument("--skill", help="Skill target to check for presence", default=None)
    parser.add_argument("--dataset-dir", help="Dataset directory to check for presence", default=None)
    args = parser.parse_args()

    worktree = Path(os.path.abspath(args.worktree_path))
    print("Demarrage du Gating Judge (Double-Split deterministe v2)...")
    
    if args.skill:
        skill_file = worktree / ".agents" / "skills" / args.skill / "SKILL.md"
        if not skill_file.is_file():
            print(f"[Judge] fail-closed: Worktree is missing SKILL for {args.skill}", file=sys.stderr)
            sys.exit(1)
            
    if args.dataset_dir:
        dataset_path = Path(args.dataset_dir)
        if not dataset_path.is_dir():
            print(f"[Judge] fail-closed: Dataset directory missing {args.dataset_dir}", file=sys.stderr)
            sys.exit(1)

    train_results = _check_train_val(worktree)
    train_score = _report("D_train_val", train_results)
    if train_score < THRESHOLD:
        print(f"[Judge] Echec de la validation sur D_train_val (Score: {train_score:.2f}). "
              "Regression majeure.", file=sys.stderr)
        sys.exit(1)

    holdout_results = _check_holdout()
    holdout_score = _report("D_holdout", holdout_results)
    if holdout_score < THRESHOLD:
        print(f"[Judge] Echec de la validation sur D_holdout (Score: {holdout_score:.2f}). "
              "Overfitting de la regle detecte.", file=sys.stderr)
        sys.exit(1)

    print("[Judge] Toutes les validations sont passees. Le patch est robuste.")
    sys.exit(0)

if __name__ == "__main__":
    main()
