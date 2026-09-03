#!/usr/bin/env python3
"""Vigilum Codex 2.6.1 — Gate R : Evidence Reconciliation (P11 — Assertion != Evidence).

Implémentation exécutable de la Phase 5 du plan V2.6.0, corrigée par l'audit :

  « Affirmer que "N/N tests passent" dans un markdown n'est pas une preuve. »

Corrections d'audit apportées au design du plan :
  1. NON-CIRCULARITÉ (P2) : le registre ``runtime/contracts/mission_truth.json``
     est produit par CET OUTIL déterministe — jamais par l'Orchestrateur. La
     version du plan (« l'Orchestrateur génère l'artefact pré-vol ») aurait
     réintroduit BYPASS-01 sous un autre nom. L'écriture agent de ce registre
     est physiquement bloquée par le hook 09 (zero-middleman, V2.6.1).
  2. SIGNATURE INDÉPENDANTE RÉELLE : la preuve d'exécution (ledger du
     test_runner) doit être couverte par une ATTESTATION signée par le Plan de
     Contrôle (HMAC-SHA256, enveloppe DSSE via ``bin/slasa_attestation.py``).
     La clé vit hors du workspace (env runtime ou fichier refusé sous la
     racine) — le générateur du code ne peut pas signer sa propre preuve.
  3. L'ASSET SLSA EST REQUIS : la Phase 5 du plan V2.6.0 dépend de la
     machinerie HMAC/DSSE de la Phase 4 du plan V2.5.0 — confirmer la
     suppression de cette dernière casserait la Gate R (incohérence interne
     du plan V2.6.0, consignée dans le verdict d'audit).

Cérémonie de clôture (ordre strict) :
  R1. Exécuter les suites : ``python3 bin/test_runner.py --root . --mission <ID>``
      → ledger ``evidence/test_runner_<ID>_<ts>.json`` (verdict PASS).
  R2. Signer le ledger depuis le Plan de Contrôle (clé hors workspace) :
      ``TESLA_CONTROL_PLANE_KEY=<clé> python3 bin/slasa_attestation.py \\
         generate --root . --mission <ID> \\
         --subject evidence/test_runner_<ID>_<ts>.json --sign \\
         --out evidence/gate_r_<ID>.attestation.json``
  R3. Réconcilier : ``python3 bin/gate_r.py reconcile --root . --mission <ID>``
      → vérifie manifeste ↔ ledger ↔ signature, émet
      ``runtime/contracts/mission_truth.json`` (verdict RECONCILED).

Sorties : 0 RECONCILED | 50 TESLA_EXIT_MARBLE (bloqué — P1/P11) |
64 USAGE | 66 UNKNOWN (P3 : clé inobservable, ledger introuvable...).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_PASS = 0
EXIT_MARBLE = 50  # TESLA_EXIT_MARBLE : pré-condition de MARBLE_ELIGIBLE non satisfaite
EXIT_USAGE = 64
EXIT_UNKNOWN = 66  # P3 : inobservable ≠ PASS

DOCTRINE_VERSION = "2.6.1"
MANIFEST_NAME = "test_manifest_v2.1.yaml"
SLSA_TOOL = Path(__file__).resolve().parent / "slsa_attestation.py"
DEFAULT_ATTESTATION_PATTERN = "gate_r_{mission}.attestation.json"
TRUTH_CONTRACT_REL = ("runtime", "contracts", "mission_truth.json")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fail(reason: str, code: int = EXIT_MARBLE) -> tuple[int, dict[str, Any]]:
    return code, {"gate": "R", "name": "Evidence Reconciliation",
                  "implementation": DOCTRINE_VERSION,
                  "verdict": "BLOCKED" if code == EXIT_MARBLE else "UNKNOWN",
                  "reason": reason}


def _load_manifest(root: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Charge le manifeste déclaratif (yaml_mini, comme le test_runner)."""
    path = root / "manifest" / MANIFEST_NAME
    if not path.is_file():
        return None, "MANIFESTE_INTROUVABLE"
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    try:
        from core.orchestration.yaml_mini import load_file
        data = load_file(str(path))
    except Exception as exc:  # P3 : illisible => jamais un PASS implicite
        return None, f"MANIFESTE_ILLISIBLE:{exc}"
    if not isinstance(data, dict):
        return None, "MANIFESTE_MALFORME"
    return data, None


def _find_ledger(root: Path, mission: str, explicit: str | None) -> tuple[Path | None, str | None]:
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute():
            candidate = root / candidate
        if not candidate.is_file():
            return None, f"LEDGER_INTROUVABLE:{candidate}"
        return candidate, None
    evidence_dir = root / "evidence"
    if not evidence_dir.is_dir():
        return None, "REPERTOIRE_EVIDENCE_INTROUVABLE"
    ledgers = sorted(
        (p for p in evidence_dir.glob(f"test_runner_{mission}_*.json")
         if p.is_file()),
        key=lambda p: p.name)
    if not ledgers:
        return None, f"AUCUN_LEDGER_POUR_LA_MISSION:{mission}"
    return ledgers[-1], None  # le plus récent (horodatage dans le nom)


def _find_attestation(root: Path, mission: str, explicit: str | None) -> tuple[Path | None, str | None]:
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute():
            candidate = root / candidate
        if not candidate.is_file():
            return None, f"ATTESTATION_INTROUVABLE:{candidate}"
        return candidate, None
    candidate = root / "evidence" / DEFAULT_ATTESTATION_PATTERN.format(mission=mission)
    if not candidate.is_file():
        return None, ("ATTESTATION_ABSENTE — signer le ledger depuis le Plan "
                      "de Contrôle (slsa_attestation.py generate --sign)")
    return candidate, None


def _reconcile_counts(manifest: dict[str, Any], ledger: dict[str, Any]) -> str | None:
    """Manifeste déclaratif ↔ ledger d'exécution (arbitrage #5, P11)."""
    if ledger.get("verdict_global") != "PASS":
        return f"LEDGER_VERDICT_NON_PASS:{ledger.get('verdict_global')}"
    ledger_suites = {s.get("name"): s for s in ledger.get("suites", [])
                     if isinstance(s, dict)}
    declared_total = 0
    for entry in manifest.get("suites", []):
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        declared = entry.get("expected_tests")
        if not isinstance(declared, int):
            continue
        declared_total += declared
        suite = ledger_suites.get(name)
        if not isinstance(suite, dict):
            return f"SUITE_NON_EXECUTEE:{name}"
        executed = suite.get("tests_reported")
        if not isinstance(executed, int) or executed < declared:
            return (f"COMPTE_INSUFFISANT:{name} déclaré={declared} "
                    f"exécuté={executed if isinstance(executed, int) else 'ABSENT'}")
        # P3 : un confinement (skip) n'est admis que s'il est EXPLICITEMENT
        # divulgué dans le ledger — jamais un vert silencieux.
        skipped = suite.get("tests_skipped", 0)
        if isinstance(skipped, int) and skipped > 0 and "p3_disclosure" not in suite:
            return f"SKIP_NON_DIVULGUE:{name} ({skipped} tests)"
    declared_manifest_total = manifest.get("total_tests")
    if isinstance(declared_manifest_total, int) and declared_manifest_total != declared_total:
        return (f"MANIFESTE_INCOHERENT:total_tests={declared_manifest_total} "
                f"vs somme des suites={declared_total}")
    return None


def _verify_attestation(root: Path, attestation: Path, ledger: Path,
                        key_file: str | None) -> tuple[int, dict[str, Any]]:
    """Vérifie l'enveloppe DSSE signée Control Plane couvrant le ledger."""
    if not SLSA_TOOL.is_file():
        return _fail(f"OUTIL_SLSA_INTROUVABLE:{SLSA_TOOL}")
    cmd = [sys.executable, str(SLSA_TOOL), "verify",
           "--attestation", str(attestation),
           "--root", str(root),
           "--subject", str(ledger)]
    if key_file:
        cmd += ["--key-file", key_file]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return EXIT_UNKNOWN, {"verdict": "UNKNOWN",
                              "reason": f"VERIFICATION_INEXECUTABLE:{exc}"}
    output = (proc.stdout + proc.stderr).strip()
    verdict: dict[str, Any] = {"exit_code": proc.returncode}
    try:
        verdict.update(json.loads(output.splitlines()[-1]))
    except (IndexError, json.JSONDecodeError):
        verdict["raw"] = output[:400]
    if proc.returncode == EXIT_PASS:
        return EXIT_PASS, verdict
    if proc.returncode == EXIT_UNKNOWN:
        return EXIT_UNKNOWN, {"verdict": "UNKNOWN",
                              "reason": f"P3_VERIFICATION_INOBSERVABLE:{verdict.get('reason')}"}
    return EXIT_MARBLE, {"verdict": "BLOCKED",
                         "reason": f"ATTESTATION_INVALIDE:{verdict.get('reason')}"}


def reconcile(root: Path, mission: str, ledger_explicit: str | None,
              attestation_explicit: str | None, key_file: str | None,
              write_contract: bool = True) -> tuple[int, dict[str, Any]]:
    manifest, error = _load_manifest(root)
    if error:
        return _fail(error)
    ledger, error = _find_ledger(root, mission, ledger_explicit)
    if error:
        return _fail(error, EXIT_UNKNOWN if not ledger_explicit else EXIT_MARBLE)
    attestation, error = _find_attestation(root, mission, attestation_explicit)
    if error:
        return _fail(error)

    try:
        ledger_data = json.loads(ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _fail(f"LEDGER_ILLISIBLE:{exc}")

    # R1 : manifeste ↔ exécution
    problem = _reconcile_counts(manifest, ledger_data)
    if problem:
        return _fail(f"P11_ASSERTION_SANS_EVIDENCE:{problem}")

    # R2 : signature indépendante du Control Plane (P2)
    code, verification = _verify_attestation(root, attestation, ledger, key_file)
    if code != EXIT_PASS:
        return code, {"gate": "R", "name": "Evidence Reconciliation",
                      "implementation": DOCTRINE_VERSION,
                      "verdict": "BLOCKED" if code == EXIT_MARBLE else "UNKNOWN",
                      "reason": verification.get("reason") or "VERIFICATION_ECHOUEE",
                      "detail": verification}

    # R3 : registre de vérité — écrit par l'outil déterministe, jamais l'agent.
    manifest_path = root / "manifest" / MANIFEST_NAME
    truth: dict[str, Any] = {
        "gate": "R",
        "name": "Evidence Reconciliation",
        "doctrine": "2.0",
        "implementation": DOCTRINE_VERSION,
        "mission_id": mission,
        "verdict": "RECONCILED",
        "p11": "ASSERTION != EVIDENCE — corrélé physiquement (manifeste, "
               "ledger, signature Control Plane), pas par récit.",
        "manifest": {"path": str(manifest_path.relative_to(root)),
                     "sha256": _sha256_file(manifest_path)},
        "ledger": {"path": str(ledger.resolve().relative_to(root)),
                   "sha256": _sha256_file(ledger),
                   "verdict_global": ledger_data.get("verdict_global")},
        "attestation": {"path": str(attestation.resolve().relative_to(root)),
                        "signed_by": verification.get("signed_by"),
                        "subjects": verification.get("subjects")},
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if write_contract:
        contract_path = root.joinpath(*TRUTH_CONTRACT_REL)
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(
            json.dumps(truth, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        truth["contract_path"] = str(contract_path.relative_to(root))
    return EXIT_PASS, truth


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vigilum Codex 2.6.1 — Gate R : Evidence Reconciliation (P11)")
    sub = parser.add_subparsers(dest="command", required=True)
    p_rec = sub.add_parser("reconcile", help="Réconcilier manifeste / ledger / signature")
    p_rec.add_argument("--root", default=".")
    p_rec.add_argument("--mission", required=True)
    p_rec.add_argument("--ledger", default=None,
                       help="ledger explicite (défaut : plus récent evidence/test_runner_<mission>_*.json)")
    p_rec.add_argument("--attestation", default=None,
                       help="attestation explicite (défaut : evidence/gate_r_<mission>.attestation.json)")
    p_rec.add_argument("--key-file", default=None,
                       help="clé HMAC Control Plane (hors workspace)")
    p_rec.add_argument("--no-write", action="store_true",
                       help="vérification seule, sans écrire mission_truth.json")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    code, verdict = reconcile(root, args.mission, args.ledger,
                              args.attestation, args.key_file,
                              write_contract=not args.no_write)
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
