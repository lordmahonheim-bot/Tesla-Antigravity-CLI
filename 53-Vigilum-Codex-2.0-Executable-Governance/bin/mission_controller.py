#!/usr/bin/env python3
"""Vigilum Codex 2.1.3 — Mission Closure Controller (Machine d'États à 13 Niveaux).

Deterministic enforcement of the state machine and the MARBLE_ELIGIBILITY
equation. No transition and no sealing rests on declarative IA text: every
predicate is evaluated from on-disk evidence (tests ledger, memory parity,
hygiene, capability probe, receipt quorum, staging gate, contract/DAG).

States (13-level machine):
  DRAFT -> CONTRACTED -> G2_APPROVED -> EXECUTING -> WORK_VALIDATED ->
  EVIDENCE_VALIDATED -> STAGING_VALIDATED -> MARBLE_ELIGIBLE ->
  HUMAN_AUTHORIZED -> PUBLISHING -> PUBLISHED -> POST_PUB_VERIFIED -> SEALED

Predicates (V2.1.2 §5):
  MARBLE_ELIGIBLE = WORK_VALIDATED ∧ MEMORY_PARITY_PASS ∧ HYGIENE_PASS ∧
                    PROBE_VALID ∧ RECEIPTS_CORRELATED ∧ PROFILE_REQUIREMENTS_PASS

  PROBE_VALID = (∀c ∈ Required: status(c)=PASS) ∧
                (∀u ∈ Optional: status(u) ∈ {PASS, UNKNOWN-CONFINED}) ∧
                UNKNOWN_RECORDED_IN_EVIDENCE

Usage
-----
  python3 bin/mission_controller.py --root <dir> --mission <id>
      [--profile internal-only|public-release|memory-assimilation]
      [--registry <MVP-GITHUB>] [--milestone <N>] [--graph <mission_graph>]
      [--receipts <dir>] [--authorized]

  --authorized  : record HUMAN_AUTHORIZED (Biological Gate) in the ledger.

Evidence outputs:
  runtime/marble_eligibility.json   full predicate ledger + verdict
  runtime/state.json                deepest reached state (machine)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bin.memory_parite import DEFAULT_PILLARS, audit_memory, load_pillars  # noqa: E402
from bin.probe_capabilities import OPTIONAL_DEFAULT, REQUIRED_DEFAULT, probe_set  # noqa: E402
from bin.staging_gate import cmd_next_milestone, cmd_verify  # noqa: E402
from bin.workspace_hygiene import run_hygiene  # noqa: E402
from core.orchestration.orchestration_gate import (  # noqa: E402
    EXIT_BLOCKED,
    EXIT_PASS,
    _default_receipts_dir,
    dag_verify,
    load_graph_file,
    receipt_quorum,
)

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_UNKNOWN = 66

STATES = [
    "DRAFT", "CONTRACTED", "G2_APPROVED", "EXECUTING", "WORK_VALIDATED",
    "EVIDENCE_VALIDATED", "STAGING_VALIDATED", "MARBLE_ELIGIBLE",
    "HUMAN_AUTHORIZED", "PUBLISHING", "PUBLISHED", "POST_PUB_VERIFIED", "SEALED",
]


def _latest_runner_ledger(root: Path, mission: str | None) -> dict[str, Any] | None:
    """Latest evidence/test_runner_*.json with verdict_global PASS."""
    evidence_dir = root / "evidence"
    if not evidence_dir.is_dir():
        return None
    ledgers: list[dict[str, Any]] = []
    for path in sorted(evidence_dir.glob("test_runner_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if mission and data.get("mission_id") != mission:
            continue
        ledgers.append(data)
    if not ledgers:
        return None
    return max(ledgers, key=lambda d: d.get("timestamp", ""))


def _contract_present(root: Path, mission: str | None) -> dict[str, Any] | None:
    contract_path = root / "runtime" / "contracts" / "mission_contract.json"
    if not contract_path.is_file():
        return None
    try:
        data = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if mission and data.get("mission_id") != mission:
        return None
    return data


def _resolve_graph(root: Path, graph_override: str | None) -> Path | None:
    if graph_override:
        candidate = Path(graph_override)
        if not candidate.is_absolute():
            candidate = root / candidate
        return candidate.resolve() if candidate.is_file() else None
    registry = root / "runtime" / "orchestration" / "active_mission.json"
    if registry.is_file():
        try:
            data = json.loads(registry.read_text(encoding="utf-8"))
            ref = data.get("mission_graph")
            if isinstance(ref, str) and ref:
                candidate = Path(ref)
                if not candidate.is_absolute():
                    candidate = root / candidate
                if candidate.is_file():
                    return candidate.resolve()
        except (OSError, json.JSONDecodeError):
            return None
    return None


def _probe_valid(root: Path, contract: dict[str, Any] | None = None) -> tuple[bool, dict[str, Any]]:
    """PROBE_VALID (U-006, P3) — V2.1.3 contextualisé au contrat (arbitrage #4).

    Lorsque le contrat de mission déclare ``required_capabilities``, cet
    ensemble devient la référence REQUISE pour le prédicat (le profil et les
    agents requis pilotent la sonde, jamais un défaut codé en dur). Sans
    déclaration : repli sur les capacités requises par défaut.
    """
    required_override = None
    if isinstance(contract, dict):
        caps = contract.get("required_capabilities")
        if isinstance(caps, list) and caps:
            required_override = [str(c) for c in caps]

    probe_file = root / "runtime" / "capability_health.json"
    if probe_file.is_file():
        try:
            evidence = json.loads(probe_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            evidence = None
    else:
        if required_override:
            required_tools = [{"name": name, "cmd": name, "probe": ["--version"]} for name in required_override]
        else:
            required_tools = list(REQUIRED_DEFAULT)
        code, evidence = probe_set(required_tools, list(OPTIONAL_DEFAULT))
        try:
            probe_file.parent.mkdir(parents=True, exist_ok=True)
            probe_file.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            evidence["evidence"] = str(probe_file)
        except OSError:
            pass

    if not isinstance(evidence, dict):
        return False, {"note": "PROBE_EVIDENCE_UNOBSERVABLE (P3)", "status": "UNKNOWN"}

    caps_by_name = {cap.get("capability"): cap.get("status") for cap in evidence.get("capabilities", [])}
    required_names = required_override or list(evidence.get("required", []))

    # Les capacités requises absentes du fichier de preuve sont re-sondées
    # immédiatement (fail-closed : jamais acceptées sans observation).
    missing = [name for name in required_names if name not in caps_by_name]
    if missing:
        extra = [{"name": name, "cmd": name, "probe": ["--version"]} for name in missing]
        _, extra_result = probe_set(extra, [])
        for cap in extra_result.get("capabilities", []):
            caps_by_name[cap.get("capability")] = cap.get("status")

    required_ok = all(caps_by_name.get(name) == "PASS" for name in required_names)
    optional_names = [name for name in caps_by_name if name not in required_names]
    optional_ok = all(caps_by_name[name] in ("PASS", "UNKNOWN-CONFINED") for name in optional_names)
    recorded = bool(evidence.get("evidence") or probe_file.is_file())
    verdict = required_ok and optional_ok and recorded
    return verdict, {
        "required_set": required_names,
        "required_ok": required_ok,
        "optional_ok": optional_ok,
        "recorded_in_evidence": recorded,
        "verdict_global": evidence.get("verdict"),
        "note": "UNKNOWN-CONFINED documenté — jamais un PASS implicite (P3)",
    }


def _profile_requirements(root: Path, profile: str, registry: Path | None,
                          milestone: int | None) -> tuple[bool, dict[str, Any]]:
    """PROFILE_REQUIREMENTS_PASS — conditional on closure_profile (V2.1.2 §5)."""
    if profile == "internal-only":
        return True, {"profile": profile, "staging": "STAGING_NA_CONFIRMED",
                      "note": "Phase 4 N/A (Local Confinement) — documenté, jamais masqué."}
    if profile == "public-release":
        if registry is None or milestone is None:
            return False, {"profile": profile, "reason": "STAGING_NA_CONFIRMED_MISSING",
                           "note": "public-release exige --registry MVP-GITHUB/ et --milestone N+1"}
        code, result = cmd_verify(registry, milestone)
        return code == EXIT_PASS, {"profile": profile, "staging": result.get("verdict"), "result": result}
    if profile == "memory-assimilation":
        pre = (root / "runtime" / "memory_manifest_pre.json").is_file()
        post = (root / "runtime" / "memory_manifest_post.json").is_file()
        return pre and post, {"profile": profile, "pre_manifest": pre, "post_manifest": post}
    return False, {"profile": profile, "reason": "PROFILE_UNKNOWN"}


def _deepest_state(contract: dict | None, dag_ok: bool, work_ok: bool, memory_ok: bool,
                   hygiene_ok: bool, probe_ok: bool, receipts_ok: bool, profile_ok: bool,
                   authorized: bool) -> str:
    if not contract:
        return "DRAFT"
    if not dag_ok:
        return "CONTRACTED"
    if not work_ok:
        return "G2_APPROVED"
    if not (memory_ok and hygiene_ok and probe_ok and receipts_ok):
        return "EXECUTING" if not (memory_ok or hygiene_ok or probe_ok or receipts_ok) else "WORK_VALIDATED"
    if not profile_ok:
        return "EVIDENCE_VALIDATED"
    if not authorized:
        return "MARBLE_ELIGIBLE"
    return "HUMAN_AUTHORIZED"


def evaluate(root: Path, mission: str, profile: str, registry: Path | None,
             milestone: int | None, graph_override: str | None,
             receipts_override: str | None, authorized: bool) -> tuple[int, dict[str, Any]]:
    contract = _contract_present(root, mission)

    graph_path = _resolve_graph(root, graph_override)
    dag_ok = False
    dag_detail: dict[str, Any] = {}
    if graph_path is not None:
        code, dag_detail = dag_verify(graph_path)
        dag_ok = code == EXIT_PASS

    ledger = _latest_runner_ledger(root, mission)
    work_ok = bool(ledger and ledger.get("verdict_global") == "PASS")

    pillars = load_pillars(None, root)
    mem_code, mem_detail = audit_memory(root, pillars, {})
    memory_ok = mem_code == EXIT_PASS

    hyg_code, hyg_detail = run_hygiene(root, prune=False, extra_targets=[])
    hygiene_ok = hyg_code == EXIT_PASS

    probe_ok, probe_detail = _probe_valid(root, contract)

    receipts_ok = False
    receipts_detail: dict[str, Any] = {}
    if graph_path is not None:
        receipts_dir = Path(receipts_override) if receipts_override else _default_receipts_dir(root)
        code, receipts_detail = receipt_quorum(_load_graph(graph_path), receipts_dir, mission_expected=mission)
        receipts_ok = code == EXIT_PASS

    profile_ok, profile_detail = _profile_requirements(root, profile, registry, milestone)

    terms = {
        "WORK_VALIDATED": {"pass": work_ok, "detail": {"ledger": str(ledger.get("evidence_ledger")) if ledger else None}},
        "MEMORY_PARITY_PASS": {"pass": memory_ok, "detail": {"verdict": mem_detail.get("verdict"), "passed": mem_detail.get("pillars_passed"), "total": mem_detail.get("pillars_total")}},
        "HYGIENE_PASS": {"pass": hygiene_ok, "detail": {"verdict": hyg_detail.get("verdict"), "drafts": hyg_detail.get("drafts_count")}},
        "PROBE_VALID": {"pass": probe_ok, "detail": probe_detail},
        "RECEIPTS_CORRELATED": {"pass": receipts_ok, "detail": {"reason": receipts_detail.get("reason"), "missing": receipts_detail.get("missing")}},
        "PROFILE_REQUIREMENTS_PASS": {"pass": profile_ok, "detail": profile_detail},
    }
    marble_eligible = all(term["pass"] for term in terms.values())
    state = _deepest_state(contract, dag_ok, work_ok, memory_ok, hygiene_ok, probe_ok, receipts_ok, profile_ok, authorized)

    result: dict[str, Any] = {
        "controller": "Mission Closure Controller",
        "version": "2.1.3",
        "mission_id": mission,
        "closure_profile": profile,
        "state": state,
        "marble_eligible": marble_eligible,
        "equation_terms": terms,
        "evidence": {
            "contract": bool(contract),
            "dag_approved": dag_ok,
            "mission_graph": str(graph_path) if graph_path else None,
            "dag_detail": dag_detail if dag_detail else None,
        },
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    runtime_dir = root / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "marble_eligibility.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (runtime_dir / "state.json").write_text(
        json.dumps({"mission_id": mission, "state": state, "marble_eligible": marble_eligible,
                    "timestamp": result["timestamp"]}, indent=2) + "\n", encoding="utf-8")

    return (EXIT_PASS if marble_eligible else EXIT_BLOCKED), result


def _load_graph(graph_path: Path) -> dict[str, Any]:
    try:
        return load_graph_file(graph_path)
    except Exception:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Mission Closure Controller (13-level state machine)")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--mission", required=True)
    parser.add_argument("--profile", default="internal-only",
                        choices=["internal-only", "public-release", "memory-assimilation"])
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--milestone", type=int, default=None)
    parser.add_argument("--graph", default=None)
    parser.add_argument("--receipts", default=None)
    parser.add_argument("--authorized", action="store_true",
                        help="Record HUMAN_AUTHORIZED (Biological Gate de Lord Mahonheim)")
    args = parser.parse_args()

    code, result = evaluate(args.root, args.mission, args.profile, args.registry,
                            args.milestone, args.graph, args.receipts, args.authorized)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
