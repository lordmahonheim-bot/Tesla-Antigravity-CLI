#!/usr/bin/env python3
"""Vigilum Codex 2.1 — Orchestration Gate & Anti-Usurpation Enforcement (E7).

Deterministic enforcement of Rule N°4 ("AGENTS délègue, il ne réimplémente
pas") and Gate 2 (Mission Contract seal):

1. dag-verify
   Validates structural integrity (mission name, nodes, non-empty agents,
   dependency references, acyclicity) AND checks the cryptographic approval
   seal produced by Lord Mahonheim (``approval_sha256``).

2. receipt-quorum
   Inspects ``runtime/subagents/receipts/`` (and falls back to
   ``runtime/subagents/``) to guarantee that every agent assigned to any
   node in the graph has emitted a physical receipt JSON with status
   SUCCESS/COMPLETED. Includes D-008 runtime attestation and transcript
   correlation.

3. intent-guard
   Pre-commit interceptor: detects staged files declaring a Team-Synergy
   synthesis marker (``team_synergy: true`` / ``x-vigilum-team-synergy: true``)
   or Mission Graph / contract changes, then enforces dag-verify + receipt
   quorum before any commit. Fail-closed: no marker detection without proof.

Exit codes: 0 PASS | 1 BLOCKED | 64 USAGE | 66 UNKNOWN (P3: UNKNOWN != PASS).
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Script-execution shim: allow `python3 core/orchestration/orchestration_gate.py`
# from any CWD while keeping package imports (E4-compliant absolute resolution).
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.orchestration.yaml_mini import YamlMiniError, load_file  # noqa: E402

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_USAGE = 64
EXIT_UNKNOWN = 66

RECEIPT_STATUS_OK = {"SUCCESS", "COMPLETED"}
RECEIPT_PREFIX = "receipt_"
APPROVAL_KEY = "approval"


# --------------------------------------------------------------------------- #
# Canonical serialization & seal (Gate 2)                                      #
# --------------------------------------------------------------------------- #
def canonical_json(payload: dict[str, Any]) -> bytes:
    """RFC-8785-style canonical serialization (sorted keys, minimal separators)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_approval_sha256(graph: dict[str, Any]) -> str:
    """SHA-256 of the graph WITHOUT the approval block (seal covers content only)."""
    payload = {k: v for k, v in graph.items() if k != APPROVAL_KEY}
    return hashlib.sha256(canonical_json(payload)).hexdigest()


# --------------------------------------------------------------------------- #
# Loading (JSON or YAML subset, stdlib-only)                                   #
# --------------------------------------------------------------------------- #
def load_graph_file(path: Path) -> dict[str, Any]:
    """Load a mission graph (JSON or YAML). Fail-closed on parse errors."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            raw: Any = json.loads(path.read_text(encoding="utf-8"))
        else:
            raw = load_file(str(path))
    except (OSError, json.JSONDecodeError, YamlMiniError) as exc:
        raise GraphError(f"GRAPH_UNPARSEABLE: {exc}") from exc
    if not isinstance(raw, dict):
        raise GraphError("GRAPH_ROOT_NOT_OBJECT")
    return raw


class GraphError(ValueError):
    """Structural or approval failure with a machine-readable reason."""


# --------------------------------------------------------------------------- #
# Gate 2 — Mission Graph validation + approval seal                            #
# --------------------------------------------------------------------------- #
def validate_graph(graph: dict[str, Any]) -> list[str]:
    """Return a list of structural violations (empty list == structurally valid)."""
    problems: list[str] = []

    mission = graph.get("mission")
    if not isinstance(mission, str) or not mission.strip():
        problems.append("GRAPH_MISSION_MISSING")

    nodes = graph.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        problems.append("GRAPH_NODES_MISSING_OR_EMPTY")
        return problems

    seen_ids: set[str] = set()
    node_ids: list[str] = []
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            problems.append(f"NODE_{i}_NOT_OBJECT")
            continue
        nid = node.get("id")
        if not isinstance(nid, str) or not nid.strip():
            problems.append(f"NODE_{i}_ID_MISSING")
            continue
        if nid in seen_ids:
            problems.append(f"NODE_ID_DUPLICATE:{nid}")
        seen_ids.add(nid)
        node_ids.append(nid)

        if not isinstance(node.get("role"), str) or not node["role"].strip():
            problems.append(f"NODE_{nid}_ROLE_MISSING")
        agents = node.get("agents")
        if not isinstance(agents, list) or not agents or not all(isinstance(a, str) and a.strip() for a in agents):
            problems.append(f"NODE_{nid}_AGENTS_MISSING")
        depends = node.get("depends_on", [])
        if not isinstance(depends, list):
            problems.append(f"NODE_{nid}_DEPENDS_ON_NOT_LIST")
        elif not all(isinstance(d, str) for d in depends):
            problems.append(f"NODE_{nid}_DEPENDS_ON_NOT_STRING_LIST")

    # Dependency references must resolve to declared nodes
    for node in nodes:
        if not isinstance(node, dict):
            continue
        nid = node.get("id")
        for dep in node.get("depends_on", []) or []:
            if isinstance(dep, str) and dep not in seen_ids:
                problems.append(f"NODE_{nid}_DEPENDS_ON_UNKNOWN:{dep}")

    # Acyclicity: Kahn's algorithm
    indegree: dict[str, int] = {nid: 0 for nid in node_ids}
    adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        nid = node.get("id")
        if nid not in adjacency:
            continue
        for dep in node.get("depends_on", []) or []:
            if dep in adjacency:
                adjacency[dep].append(nid)
                indegree[nid] += 1
    queue = [nid for nid in node_ids if indegree[nid] == 0]
    visited = 0
    while queue:
        current = queue.pop(0)
        visited += 1
        for nxt in adjacency[current]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    if visited != len(node_ids):
        problems.append("GRAPH_CYCLE_DETECTED")

    return problems


def verify_approval_seal(graph: dict[str, Any]) -> str | None:
    """Return None when the seal is valid, else a machine-readable reason."""
    approval = graph.get(APPROVAL_KEY)
    if not isinstance(approval, dict):
        return "GRAPH_NOT_APPROVED"
    approved_by = approval.get("approved_by")
    if not isinstance(approved_by, str) or not approved_by.strip():
        return "APPROVAL_AUTHORITY_MISSING"
    if not isinstance(approval.get("approved_at"), str) or not approval["approved_at"].strip():
        return "APPROVAL_DATE_MISSING"
    if not isinstance(approval.get("nonce"), str) or not approval["nonce"].strip():
        return "APPROVAL_NONCE_MISSING"
    declared = approval.get("approval_sha256")
    if not isinstance(declared, str) or not declared:
        return "APPROVAL_SHA256_MISSING"
    computed = compute_approval_sha256(graph)
    if not hmac.compare_digest(declared.lower(), computed.lower()):
        return "APPROVAL_SEAL_MISMATCH"
    return None


def dag_verify(graph_path: Path) -> tuple[int, dict[str, Any]]:
    try:
        graph = load_graph_file(graph_path)
    except GraphError as exc:
        return EXIT_BLOCKED, {"verdict": "BLOCKED", "reason": str(exc), "graph": str(graph_path)}

    problems = validate_graph(graph)
    if problems:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "GRAPH_STRUCTURE_INVALID",
            "violations": problems,
            "graph": str(graph_path),
        }

    seal_reason = verify_approval_seal(graph)
    if seal_reason is not None:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": seal_reason,
            "graph": str(graph_path),
            "note": "Gate 2: no Mission Graph may be executed without Lord Mahonheim's approval seal.",
        }

    return EXIT_PASS, {
        "verdict": "PASS",
        "mission": graph.get("mission"),
        "nodes": len(graph.get("nodes", [])),
        "approved_by": graph[APPROVAL_KEY]["approved_by"],
        "approval_sha256": graph[APPROVAL_KEY]["approval_sha256"],
        "graph": str(graph_path),
    }


# --------------------------------------------------------------------------- #
# Receipt quorum (Anti-Usurpation, Rule N°4)                                   #
# --------------------------------------------------------------------------- #
def load_receipts(receipts_dir: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Return ({agent_id: receipt}, errors). Fail-closed on invalid receipt JSON."""
    receipts: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    if not receipts_dir.is_dir():
        return receipts, ["RECEIPTS_DIR_MISSING"]
    for entry in sorted(receipts_dir.iterdir()):
        if not entry.is_file() or not entry.name.startswith(RECEIPT_PREFIX) or entry.suffix != ".json":
            continue
        try:
            data = json.loads(entry.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"RECEIPT_INVALID_JSON:{entry.name}")
            continue
        if not isinstance(data, dict):
            errors.append(f"RECEIPT_ROOT_NOT_OBJECT:{entry.name}")
            continue
        agent_id = data.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id.strip():
            errors.append(f"RECEIPT_AGENT_ID_MISSING:{entry.name}")
            continue
        receipts[agent_id] = data
    return receipts, errors


def validate_receipt(receipt: dict[str, Any]) -> str | None:
    """Return None when valid, else a machine-readable reason.

    Invariant D-008 (Vigilum Codex 2.1.2): a receipt is authentic and
    receivable only when it carries the runtime attestation fields —
    invocation_id (runtime-generated), started_at/finished_at (post-Gate-2),
    output_manifest_sha256 (artefacts fingerprint), executor_attestation,
    and a transcript reference.
    """
    if not isinstance(receipt.get("node_id"), str) or not receipt["node_id"].strip():
        return "RECEIPT_NODE_ID_MISSING"
    if not isinstance(receipt.get("mission_id"), str) or not receipt["mission_id"].strip():
        return "RECEIPT_MISSION_ID_MISSING"
    if receipt.get("status") not in RECEIPT_STATUS_OK:
        return f"RECEIPT_STATUS_NOT_SUCCESS:{receipt.get('status')}"
    if not isinstance(receipt.get("output_artifacts"), list):
        return "RECEIPT_OUTPUT_ARTIFACTS_MISSING"
    if not isinstance(receipt.get("submitted_at"), str) or not receipt["submitted_at"].strip():
        return "RECEIPT_SUBMITTED_AT_MISSING"

    # --- Invariant D-008 : attestation runtime (V2.1.2) ------------------- #
    invocation_id = receipt.get("invocation_id")
    if not isinstance(invocation_id, str) or not re.fullmatch(r"inv-[A-Za-z0-9-]{8,64}", invocation_id):
        return "RECEIPT_INVOCATION_ID_INVALID"
    started_at = receipt.get("started_at")
    finished_at = receipt.get("finished_at")
    if not isinstance(started_at, str) or not started_at.strip():
        return "RECEIPT_STARTED_AT_MISSING"
    if not isinstance(finished_at, str) or not finished_at.strip():
        return "RECEIPT_FINISHED_AT_MISSING"
    if finished_at < started_at:
        return "RECEIPT_TIMELINE_INVALID"
    output_manifest = receipt.get("output_manifest_sha256")
    if not isinstance(output_manifest, str) or not re.fullmatch(r"(sha256:)?[a-fA-F0-9]{64}", output_manifest):
        return "RECEIPT_OUTPUT_MANIFEST_SHA256_INVALID"
    attestation = receipt.get("executor_attestation")
    if not isinstance(attestation, str) or not attestation.strip().endswith("_signed"):
        return "RECEIPT_EXECUTOR_ATTESTATION_MISSING"
    if not isinstance(receipt.get("transcript_ref"), str) or not receipt["transcript_ref"].strip():
        return "RECEIPT_TRANSCRIPT_REF_MISSING"
    if "exit_code" in receipt and (not isinstance(receipt["exit_code"], int) or receipt["exit_code"] != 0):
        return "RECEIPT_EXIT_CODE_NONZERO"
    if "tool_invocations_count" in receipt and (
            not isinstance(receipt["tool_invocations_count"], int) or receipt["tool_invocations_count"] <= 0):
        return "RECEIPT_NO_TOOL_INVOCATIONS"
    return None


def _transcript_correlation(receipt: dict[str, Any], receipts_dir: Path) -> str | None:
    """Correlate the receipt with the runtime transcript journal (D-008)."""
    ref = receipt.get("transcript_ref")
    if not isinstance(ref, str) or not ref.strip():
        return "RECEIPT_TRANSCRIPT_REF_MISSING"

    ref_path = Path(os.path.expanduser(ref))
    if ref_path.is_absolute():
        return None if ref_path.is_file() else "RECEIPT_TRANSCRIPT_MISSING"

    transcripts_dir = receipts_dir.parent / "transcripts"
    if transcripts_dir.is_dir():
        candidate = transcripts_dir / ref
        return None if candidate.is_file() else "RECEIPT_TRANSCRIPT_MISSING"

    # Fallback to home isolated runtime evidence when local transcripts/ is not used
    mission_id = receipt.get("mission_id", "")
    home_evidence = Path(os.path.expanduser(f"~/.tesla/runtime-evidence/{mission_id}/transcripts"))
    if home_evidence.is_dir():
        candidate = home_evidence / Path(ref).name
        if candidate.is_file():
            return None

    return "RECEIPT_TRANSCRIPT_MISSING"


def receipt_quorum(graph: dict[str, Any], receipts_dir: Path, mission_expected: str | None) -> tuple[int, dict[str, Any]]:
    problems = validate_graph(graph)
    if problems:
        return EXIT_BLOCKED, {"verdict": "BLOCKED", "reason": "GRAPH_STRUCTURE_INVALID", "violations": problems}

    required_agents = sorted({agent for node in graph.get("nodes", []) for agent in node.get("agents", [])})
    receipts, errors = load_receipts(receipts_dir)

    per_agent: dict[str, dict[str, Any]] = {}
    for agent_id in required_agents:
        receipt = receipts.get(agent_id)
        if receipt is None:
            per_agent[agent_id] = {"verdict": "MISSING", "reason": "RECEIPT_FILE_ABSENT"}
            continue
        reason = validate_receipt(receipt)
        if mission_expected and receipt.get("mission_id") != mission_expected:
            reason = "RECEIPT_MISSION_MISMATCH"
        if reason is None:
            reason = _transcript_correlation(receipt, receipts_dir)
        per_agent[agent_id] = {
            "verdict": "PASS" if reason is None else "BLOCKED",
            "reason": reason,
            "node_id": receipt.get("node_id"),
        }

    blocked = [agent for agent, status in per_agent.items() if status["verdict"] != "PASS"]
    if errors:
        blocked.append("__RECEIPT_PARSING__")

    if blocked:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "RECEIPT_QUORUM_MISSING",
            "required_agents": required_agents,
            "receipts_dir": str(receipts_dir),
            "missing": [agent for agent, s in per_agent.items() if s["verdict"] != "PASS"],
            "errors": errors,
        }

    return EXIT_PASS, {
        "verdict": "PASS",
        "mission": graph.get("mission"),
        "agents_receipted": required_agents,
        "receipts_dir": str(receipts_dir),
    }


# --------------------------------------------------------------------------- #
# Intent guard (pre-commit hook 07)                                            #
# --------------------------------------------------------------------------- #
def _resolve_mission_graph(root: Path, explicit: str | None) -> Path | None:
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute():
            candidate = root / candidate
        return candidate.resolve() if candidate.exists() else None
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
    env_ref = _env_mission_graph()
    if env_ref:
        candidate = Path(env_ref)
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.is_file():
            return candidate.resolve()
    return None


def _env_mission_graph() -> str | None:
    import os
    return os.environ.get("TESLA_MISSION_GRAPH") or None


def _target_has_marker(target: Path) -> bool:
    """True when the file declares a Team-Synergy synthesis (explicit marker only)."""
    import re
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return re.search(r"[\"']?(team_synergy|x-vigilum-team-synergy)[\"']?\s*:\s*true",
                     text, flags=re.IGNORECASE) is not None


def _default_receipts_dir(root: Path) -> Path:
    nested = root / "runtime" / "subagents" / "receipts"
    if nested.is_dir():
        return nested
    return root / "runtime" / "subagents"


def intent_guard(root: Path, targets: list[Path], graph_override: str | None, receipts_override: str | None) -> tuple[int, dict[str, Any]]:
    triggers = [t for t in targets if _target_has_marker(t)]
    graph_changes = [t for t in targets if "mission_graph" in t.name or "/contracts/" in t.as_posix()]

    if not triggers and not graph_changes:
        return EXIT_PASS, {"verdict": "PASS", "reason": "NO_TEAM_SYNERGY_TRIGGER", "checked": [str(t) for t in targets]}

    graph_path = _resolve_mission_graph(root, graph_override)
    if graph_path is None:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "MISSION_GRAPH_NOT_DECLARED",
            "note": "Gate 2: a Team-Synergy synthesis requires an approved Mission Graph "
                    "(runtime/orchestration/active_mission.json or TESLA_MISSION_GRAPH).",
            "triggers": [str(t) for t in triggers + graph_changes],
        }

    code, dag_result = dag_verify(graph_path)
    if code != EXIT_PASS:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "GATE2_DAG_NOT_APPROVED",
            "dag": dag_result,
            "triggers": [str(t) for t in triggers + graph_changes],
        }

    receipts_dir = Path(receipts_override) if receipts_override else _default_receipts_dir(root)
    code, quorum_result = receipt_quorum(_load_for_quorum(graph_path), receipts_dir, mission_expected=None)
    if code != EXIT_PASS:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "ANTI_USURPATION_RECEIPT_QUORUM_FAILED",
            "note": "Absolute Rule N°4: AGENTS delegates, it does not reimplement. "
                    "Synthesis requires physical subagent receipts.",
            "quorum": quorum_result,
            "triggers": [str(t) for t in triggers + graph_changes],
        }

    return EXIT_PASS, {
        "verdict": "PASS",
        "reason": "TEAM_SYNERGY_SYNTHESIS_AUTHORIZED",
        "mission_graph": str(graph_path),
        "triggers": [str(t) for t in triggers + graph_changes],
    }


def _load_for_quorum(graph_path: Path) -> dict[str, Any]:
    try:
        return load_graph_file(graph_path)
    except GraphError:
        return {}


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vigilum Codex 2.1 Orchestration Gate (Gate 2 + Anti-Usurpation)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_dag = sub.add_parser("dag-verify", help="Validate a sealed Mission Graph (Gate 2)")
    p_dag.add_argument("--graph", type=Path, required=True)
    p_dag.set_defaults(func=_cmd_dag_verify)

    p_quorum = sub.add_parser("receipt-quorum", help="Enforce physical receipt quorum (Rule N°4)")
    p_quorum.add_argument("--graph", type=Path, required=True)
    p_quorum.add_argument("--receipts", type=Path, required=True)
    p_quorum.add_argument("--mission", default=None)
    p_quorum.set_defaults(func=_cmd_receipt_quorum)

    p_guard = sub.add_parser("intent-guard", help="Pre-commit guard: block Team-Synergy synthesis without proofs")
    p_guard.add_argument("--root", type=Path, required=True)
    p_guard.add_argument("--target", type=Path, action="append", default=[])
    p_guard.add_argument("--graph", default=None, help="Mission Graph override (path, absolute or root-relative)")
    p_guard.add_argument("--receipts", default=None, help="Receipts directory override")
    p_guard.set_defaults(func=_cmd_intent_guard)

    args = parser.parse_args(argv)
    return args.func(args)


def _cmd_dag_verify(args: argparse.Namespace) -> int:
    code, result = dag_verify(args.graph)
    _emit(result)
    return code


def _cmd_receipt_quorum(args: argparse.Namespace) -> int:
    try:
        graph = load_graph_file(args.graph)
    except GraphError as exc:
        _emit({"verdict": "BLOCKED", "reason": str(exc), "graph": str(args.graph)})
        return EXIT_BLOCKED
    code, result = receipt_quorum(graph, args.receipts, args.mission)
    _emit(result)
    return code


def _cmd_intent_guard(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    if not args.target:
        _emit({"verdict": "BLOCKED", "reason": "NO_TARGET_FILES", "note": "intent-guard requires --target <file>"})
        return EXIT_USAGE
    code, result = intent_guard(root, [t for t in args.target], args.graph, args.receipts)
    _emit(result)
    return code


def _emit(result: dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    sys.exit(main())
