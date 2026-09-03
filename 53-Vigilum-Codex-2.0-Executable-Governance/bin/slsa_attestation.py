#!/usr/bin/env python3
"""Vigilum Codex 2.5.1 — Attestations SLSA : Pivot Cloud CI/CD (Phase 4 du plan V2.5.0, audité).

Contournement déterministe de la limite structurelle du ``transcript.jsonl``
local : en environnement d'intégration continue ÉPHÉMÈRE, le transcript SCD
n'existe pas (pas de cerveau Antigravity local). La preuve d'autorisation
Gate 2 devient alors une ATTESTATION DE PROVENANCE signée par le Plan de
Contrôle (Control Plane), vérifiable par le code — jamais par le récit.

Niveau cible honnête (aucun masquage) : SLSA Provenance v0.2 au format
in-toto Statement v0.1, enveloppe DSSE signée HMAC-SHA256. L'HMAC prouve
l'intégrité et l'origine Control Plane sur cet hôte ; l'atteinte du niveau
SLSA >= 2 (signature de la plateforme de build) exige un runner CI signant
nativement — non-delta assumé et documenté.

Honnêteté cryptographique (C2, V2.6.3 — SPEC LOCK) : un HMAC est une clé
SYMÉTRIQUE — quiconque peut vérifier peut aussi forger. Cette enveloppe est
donc une ATTESTATION LOCALE dont le niveau de confiance est borné par
(a) l'isolation du signataire (la clé ne doit vivre ni dans le workspace
agent ni dans un environnement contrôlable par lui) et (b) la protection
du matériel de clé. Elle n'est PAS une signature indépendante de tiers ;
cette dernière exige une signature asymétrique (courtier Ed25519 — OI-03 —
ou GPG/SSH selon l'invariant A-002). Toute présentation de cette attestation
comme « signature indépendante » serait une violation de P11 (confusion
ATTESTATION ≠ AUTHORIZATION et sur-déclaration du niveau de confiance).

Frontières de confiance (P2 — Producer != Validator) :
  - la clé de signature vit HORS du workspace agent :
    TESLA_CONTROL_PLANE_KEY (env, injectée au runtime) ou --key-file dont
    le chemin réel est REFUSÉ s'il est situé sous la racine du workspace ;
  - la vérification échoue fermé : clé absente => exit 66 (P3 : UNKNOWN !=
    PASS), signature/hachés divergents => exit 1.

Usage :
  generate  --root . --mission <ID> --subject <fichier> [--builder-id <id>]
            [--gate2-evidence <fichier.json|json>] [--materials <commit>]
            [--out <fichier>] [--sign]
  verify    --attestation <fichier> [--root .] [--subject <fichier>]...
            [--key-file <chemin>]

Sorties : 0 PASS | 1 FAIL | 64 USAGE | 66 UNKNOWN (P3).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 64
EXIT_UNKNOWN = 66

STATEMENT_TYPE = "https://in-toto.io/Statement/v0.1"
PREDICATE_TYPE = "https://slsa.dev/provenance/v0.2"
PAYLOAD_TYPE = "application/vnd.in-toto+json"
KEY_ID = "vigilum-control-plane-hmac-2026"
DOCTRINE_VERSION = "2.5.1"


# --------------------------------------------------------------------------- #
# Primitives déterministes                                                      #
# --------------------------------------------------------------------------- #
def canonical_json(data: Any) -> str:
    """Sérialisation canonique (clés triées, séparateurs compacts) —
    compatible JCS pour les sous-ensembles sans nombres exotiques (RFC 8785)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _now_iso() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    if epoch.isdigit():
        moment = datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    else:
        moment = datetime.now(timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def load_control_plane_key(root: Path | None,
                           key_file: str | None) -> tuple[bytes | None, str | None]:
    """Charge la clé Control Plane. Retourne (clé, erreur).

    P2 : un fichier de clé situé sous la racine du workspace est REFUSÉ —
    la racine de confiance ne peut pas vivre dans le territoire de l'agent.
    """
    env_key = os.environ.get("TESLA_CONTROL_PLANE_KEY", "").strip()
    if env_key:
        return env_key.encode("utf-8"), None
    if key_file:
        key_path = Path(key_file).expanduser().resolve()
        if root is not None:
            workspace = root.resolve()
            try:
                key_path.relative_to(workspace)
                return None, ("CLE_DANS_LE_WORKSPACE: la clé Control Plane ne "
                              "peut pas vivre sous la racine agent (P2).")
            except ValueError:
                pass
        if not key_path.is_file():
            return None, f"CLE_INTROUVABLE:{key_path}"
        return key_path.read_bytes().strip(), None
    return None, "CLE_ABSENTE"


# --------------------------------------------------------------------------- #
# Génération                                                                    #
# --------------------------------------------------------------------------- #
def build_statement(root: Path, mission: str, subjects: list[Path],
                    builder_id: str, materials_ref: str | None,
                    gate2_evidence: Any) -> dict[str, Any]:
    subject_entries = []
    for subject in subjects:
        resolved = subject.resolve()
        name = str(resolved.relative_to(root.resolve())) if resolved.is_relative_to(root.resolve()) else str(resolved)
        subject_entries.append({"name": name, "digest": {"sha256": sha256_file(resolved)}})

    materials = []
    if materials_ref:
        materials.append({"uri": f"git+2.53.0:{materials_ref}",
                          "digest": {"sha256": materials_ref}})
    else:
        materials.append({"uri": "git+local:unspecified",
                          "digest": {"sha256": sha256_of_tree_marker(root)}})

    return {
        "_type": STATEMENT_TYPE,
        "subject": subject_entries,
        "predicateType": PREDICATE_TYPE,
        "predicate": {
            "builder": {"id": builder_id},
            "buildType": "https://vigilum-codex.tesla/antigravity-orchestrator/v1",
            "invocation": {
                "configSource": {
                    "uri": f"git+tesla-antigravity-cli:{mission}",
                    "digest": {"sha256": sha256_of_tree_marker(root)},
                    "entryPoint": "Vigilum Codex 2.5.1 — Gate 0..6",
                },
                "parameters": {"mission_id": mission},
                "environment": {"doctrine": "vigilum-codex-2.0",
                                "implementation": DOCTRINE_VERSION},
            },
            "metadata": {
                "buildInvocationID": mission,
                "buildStartedOn": _now_iso(),
                "buildFinishedOn": _now_iso(),
                "completeness": {"parameters": True, "environment": True,
                                 "materials": bool(materials_ref)},
                "reproducible": False,
            },
            "materials": materials,
            "vigilum": {
                "doctrine": "2.0",
                "implementation": DOCTRINE_VERSION,
                "mission_id": mission,
                "gate2_evidence": gate2_evidence,
                "note": ("Preuve Gate 2 en environnement ephemere: attestation "
                         "signee Control Plane (substitut SCD transcript local, "
                         "phase 4 du plan V2.5.0)."),
            },
        },
    }


def sha256_of_tree_marker(root: Path) -> str:
    """Empreinte répérable du workspace (marqueur, non une preuve complète)."""
    marker = root.resolve()
    return hashlib.sha256(str(marker).encode("utf-8")).hexdigest()[:64]


def sign_envelope(statement: dict[str, Any], key: bytes) -> dict[str, Any]:
    payload = canonical_json(statement).encode("utf-8")
    signature = hmac.new(key, payload, hashlib.sha256).digest()
    return {
        "payloadType": PAYLOAD_TYPE,
        "payload": _b64url(payload),
        "signatures": [{"keyid": KEY_ID, "sig": _b64url(signature)}],
    }


# --------------------------------------------------------------------------- #
# Vérification (fail-closed)                                                   #
# --------------------------------------------------------------------------- #
def verify_attestation(envelope: dict[str, Any], key: bytes | None,
                       root: Path | None, subjects: list[Path]) -> tuple[int, dict[str, Any]]:
    verdict: dict[str, Any] = {"tool": "slsa_attestation", "version": DOCTRINE_VERSION}

    if not isinstance(envelope, dict) or envelope.get("payloadType") != PAYLOAD_TYPE:
        verdict.update({"verdict": "FAIL", "reason": "ENVELOPPE_DSSE_INVALIDE"})
        return EXIT_FAIL, verdict
    signatures = envelope.get("signatures")
    if not isinstance(signatures, list) or not signatures:
        verdict.update({"verdict": "FAIL", "reason": "SIGNATURES_ABSENTES"})
        return EXIT_FAIL, verdict

    if key is None:
        # P3 : sans clé, la vérification est INOBSERVABLE — jamais un PASS.
        verdict.update({"verdict": "UNKNOWN",
                        "reason": "CLE_CONTROL_PLANE_ABSENTE (P3: UNKNOWN != PASS)"})
        return EXIT_UNKNOWN, verdict

    payload_b64 = envelope.get("payload", "")
    try:
        payload = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4))
        statement = json.loads(payload.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        verdict.update({"verdict": "FAIL", "reason": f"PAYLOAD_ILLISIBLE:{exc}"})
        return EXIT_FAIL, verdict

    expected = hmac.new(key, payload, hashlib.sha256).digest()
    provided = signatures[0].get("sig", "")
    try:
        provided_bytes = base64.urlsafe_b64decode(provided + "=" * (-len(provided) % 4))
    except ValueError:
        verdict.update({"verdict": "FAIL", "reason": "SIGNATURE_MALFORMEE"})
        return EXIT_FAIL, verdict
    if not hmac.compare_digest(expected, provided_bytes):
        verdict.update({"verdict": "FAIL",
                        "reason": "SIGNATURE_INVALIDE (falsification detectee)"})
        return EXIT_FAIL, verdict

    if statement.get("_type") != STATEMENT_TYPE or \
            statement.get("predicateType") != PREDICATE_TYPE:
        verdict.update({"verdict": "FAIL", "reason": "TYPE_STATEMENT_INVALIDE"})
        return EXIT_FAIL, verdict

    # Couverture des sujets : chaque fichier soumis doit être couvert.
    attested = {entry.get("name"): entry.get("digest", {}).get("sha256")
                for entry in statement.get("subject", []) if isinstance(entry, dict)}
    for subject in subjects:
        resolved = subject.resolve()
        name = str(resolved.relative_to(root.resolve())) if root and resolved.is_relative_to(root.resolve()) else str(resolved)
        if name not in attested:
            verdict.update({"verdict": "FAIL",
                            "reason": f"SUJET_NON_ATTESTE:{name}"})
            return EXIT_FAIL, verdict
        if sha256_file(resolved) != attested[name]:
            verdict.update({"verdict": "FAIL",
                            "reason": f"EMPREINTE_DIVERGENTE:{name}"})
            return EXIT_FAIL, verdict

    predicate = statement.get("predicate", {})
    verdict.update({
        "verdict": "PASS",
        "mission_id": predicate.get("invocation", {}).get("parameters", {}).get("mission_id"),
        "builder": predicate.get("builder", {}).get("id"),
        "subjects": sorted(attested),
        "signed_by": signatures[0].get("keyid"),
    })
    return EXIT_PASS, verdict


# --------------------------------------------------------------------------- #
# CLI                                                                           #
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vigilum Codex 2.5.1 — Attestations SLSA (pivot CI/CD)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Générer une attestation de provenance")
    p_gen.add_argument("--root", default=".", help="racine du workspace")
    p_gen.add_argument("--mission", required=True, help="identifiant de mission")
    p_gen.add_argument("--subject", action="append", required=True,
                       help="fichier couvert par l'attestation (répétable)")
    p_gen.add_argument("--builder-id", default="https://vigilum-codex.tesla/builder/local")
    p_gen.add_argument("--materials", default=None, help="SHA-256 du commit amont")
    p_gen.add_argument("--gate2-evidence", default=None,
                       help="fichier JSON ou JSON inline (preuve Gate 2)")
    p_gen.add_argument("--out", default=None, help="fichier de sortie")
    p_gen.add_argument("--sign", action="store_true",
                       help="signer l'enveloppe DSSE (clé Control Plane)")

    p_ver = sub.add_parser("verify", help="Vérifier une attestation (fail-closed)")
    p_ver.add_argument("--attestation", required=True)
    p_ver.add_argument("--root", default=".")
    p_ver.add_argument("--subject", action="append", default=[],
                       help="fichier à contrôler contre l'attestation")
    p_ver.add_argument("--key-file", default=None,
                       help="clé HMAC Control Plane (hors workspace)")

    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if args.command == "generate":
        subjects = [Path(s).resolve() for s in args.subject]
        for subject in subjects:
            if not subject.is_file():
                print(json.dumps({"error": f"SUJET_INTROUVABLE:{subject}"}),
                      file=sys.stderr)
                return EXIT_USAGE
        gate2_evidence: Any = None
        if args.gate2_evidence:
            candidate = Path(args.gate2_evidence)
            if candidate.is_file():
                gate2_evidence = json.loads(candidate.read_text(encoding="utf-8"))
            else:
                gate2_evidence = json.loads(args.gate2_evidence)
        statement = build_statement(root, args.mission, subjects,
                                    args.builder_id, args.materials, gate2_evidence)
        document: dict[str, Any] = {"statement": statement}
        if args.sign:
            key, error = load_control_plane_key(root, None)
            if key is None:
                print(json.dumps({"error": error}), file=sys.stderr)
                return EXIT_UNKNOWN
            document = sign_envelope(statement, key)
        serialized = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            Path(args.out).write_text(serialized, encoding="utf-8")
            print(json.dumps({"status": "written", "path": args.out,
                              "signed": args.sign}))
        else:
            print(serialized)
        return EXIT_PASS

    # verify
    attestation_path = Path(args.attestation)
    if not attestation_path.is_file():
        print(json.dumps({"error": f"ATTESTATION_INTROUVABLE:{attestation_path}"}),
              file=sys.stderr)
        return EXIT_USAGE
    envelope = json.loads(attestation_path.read_text(encoding="utf-8"))
    subjects = [Path(s).resolve() for s in args.subject]
    for subject in subjects:
        if not subject.is_file():
            print(json.dumps({"error": f"SUJET_INTROUVABLE:{subject}"}),
                  file=sys.stderr)
            return EXIT_USAGE
    key, error = load_control_plane_key(root, args.key_file)
    if error and error != "CLE_ABSENTE":
        print(json.dumps({"error": error}), file=sys.stderr)
        return EXIT_FAIL
    code, verdict = verify_attestation(envelope, key, root, subjects)
    print(json.dumps(verdict, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
