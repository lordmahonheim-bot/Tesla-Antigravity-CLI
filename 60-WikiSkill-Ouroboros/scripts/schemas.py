#!/usr/bin/env python3
"""schemas.py — Phase A (WikiSkill / Ouroboros) : formater, hacher et sceller une trace.

This module is the deterministic "Phase A" primitive of the WikiSkill loop. It is
the ONLY component allowed to format, hash and seal an execution trace. It is
importable (ExecutionTrace dataclass) and executable (CLI: --seal / --verify).

CLI (stdlib only):
    python3 schemas.py --seal   --input trace.json --out trace.sealed.json
    python3 schemas.py --verify --input trace.sealed.json

Exit codes:
    0 : success (seal written / hash verified)
    1 : validation or I/O failure
"""
import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List


@dataclass
class ExecutionTrace:
    trace_id: str
    skill: str
    domaine: str
    task_id: str
    model: str
    outcome: str
    score: float
    verdict_sources: List[str]
    ast_quarantine_status: str
    steps: List[Dict[str, Any]]
    final_answer: str
    secrets_scrubbed: bool
    sha256: str = field(default="")

    def compute_hash(self) -> str:
        data = asdict(self)
        data.pop("sha256", None)
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    def validate(self) -> bool:
        if not isinstance(self.score, (int, float)) or not (0.0 <= self.score <= 1.0):
            raise ValueError("Le score doit être compris entre 0.0 et 1.0")
        if not self.secrets_scrubbed:
            raise ValueError("Les secrets doivent être nettoyés (secrets_scrubbed=True)")
        if not self.trace_id or not self.task_id:
            raise ValueError("trace_id et task_id sont obligatoires")
        return True

    def to_json(self) -> str:
        self.sha256 = self.compute_hash()
        return json.dumps(asdict(self), indent=2)

    def verify_hash(self) -> bool:
        """Verifie l'integrite cryptographique (recalcule vs stocke)."""
        if not self.sha256:
            return False
        return self.compute_hash() == self.sha256

    @classmethod
    def from_json(cls, json_str: str) -> "ExecutionTrace":
        data = json.loads(json_str)
        instance = cls(**data)
        instance.validate()
        return instance


def load_trace(filepath: str) -> ExecutionTrace:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        trace = ExecutionTrace.from_json(content)
    except json.JSONDecodeError as e:
        print(f"[Phase A] JSON invalide dans {filepath} : {e}", file=sys.stderr)
        sys.exit(1)
    except (TypeError, ValueError) as e:
        print(f"[Phase A] Trace invalide ({filepath}) : {e}", file=sys.stderr)
        sys.exit(1)
    return trace


def cmd_seal(input_path: str, out_path: str) -> None:
    trace = load_trace(input_path)
    sealed = trace.to_json()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(sealed + "\n")
    print(
        "[Phase A] Trace scellée : "
        f"trace_id={trace.trace_id} sha256={trace.sha256} -> {out_path}"
    )


def cmd_verify(input_path: str) -> None:
    trace = load_trace(input_path)
    embedded = trace.sha256
    recomputed = trace.compute_hash()
    if not embedded:
        print(f"[Phase A] VERDICT: NON SCELLÉE — sha256 absent dans {input_path}", file=sys.stderr)
        sys.exit(1)
    if embedded != recomputed:
        print(
            "[Phase A] VERDICT: ALTÉRÉE — "
            f"sha256 embarqué {embedded} != recalculé {recomputed}",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"[Phase A] VERDICT: INTÈGRE — sha256 {embedded} vérifié pour trace_id={trace.trace_id}")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Phase A : formater, hacher, sceller une trace d'exécution WikiSkill.")
    parser.add_argument("--seal", action="store_true", help="Sceller une trace (remplit et fige sha256).")
    parser.add_argument("--verify", action="store_true", help="Vérifier l'intégrité cryptographique d'une trace.")
    parser.add_argument("--input", required=True, help="Chemin du fichier trace JSON en entrée.")
    parser.add_argument("--out", help="Chemin du fichier scellé en sortie (requis avec --seal).")
    args = parser.parse_args(argv)

    if args.seal and args.verify:
        print("[Phase A] Erreur : --seal et --verify sont mutuellement exclusifs.", file=sys.stderr)
        return 1
    if args.seal:
        if not args.out:
            print("[Phase A] Erreur : --out est requis avec --seal.", file=sys.stderr)
            return 1
        cmd_seal(args.input, args.out)
        return 0
    if args.verify:
        cmd_verify(args.input)
        return 0
    print("[Phase A] Erreur : choisir --seal ou --verify.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
