#!/usr/bin/env python3
import os
import sys
import json
import argparse
import hashlib
import re
from pathlib import Path

# Add bin to path to import slsa_attestation
sys.path.insert(0, str(Path(__file__).parent))
import slsa_attestation

def fail(code, reason):
    verdict = "UNKNOWN" if code == 66 else "FAILED"
    print(json.dumps({"verdict": verdict, "reason": reason}))
    sys.exit(code)

def success(verdict, truth_file=None, data=None):
    if truth_file and data:
        truth_file.parent.mkdir(parents=True, exist_ok=True)
        truth_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": verdict}))
    sys.exit(0)

def sha256_file(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reconcile(root_dir: str, mission_id: str, explicit_ledger: str, no_write: bool):
    root = Path(root_dir).resolve()
    key_env = os.environ.get("TESLA_CONTROL_PLANE_KEY")
    if not key_env:
        fail(66, "No key provided (P3)")
        
    key = key_env.encode("utf-8")
        
    ledger_path = Path(explicit_ledger).resolve() if explicit_ledger else root / "evidence" / f"test_runner_{mission_id}_20260903-000000-000001.json"
    
    if not ledger_path.is_file():
        fail(66, "LEDGER file missing")
        
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception:
        fail(50, "Invalid JSON in ledger")
        
    if ledger.get("verdict_global") != "PASS":
        fail(50, "Ledger verdict is not PASS (P11)")
        
    manifest_path = root / "manifest" / "test_manifest_v2.1.yaml"
    manifest_content = manifest_path.read_text(encoding="utf-8") if manifest_path.is_file() else ""
    
    # Simple manual parse of manifest
    manifest_suites = []
    expected_tests_map = {}
    
    current_suite = None
    for line in manifest_content.splitlines():
        line = line.strip()
        if line.startswith("- name:"):
            current_suite = line.replace("- name:", "").strip().strip('"').strip("'")
            manifest_suites.append(current_suite)
            expected_tests_map[current_suite] = 0
        elif line.startswith("expected_tests:") and current_suite:
            val = line.replace("expected_tests:", "").strip()
            if val.isdigit():
                expected_tests_map[current_suite] = int(val)
        
    ledger_suites = {s["name"]: s for s in ledger.get("suites", [])}
    
    # SUITE_NON_EXECUTEE
    for ms in manifest_suites:
        if ms not in ledger_suites:
            fail(50, "SUITE_NON_EXECUTEE")
            
    # COMPTE_INSUFFISANT
    for s_name, s_data in ledger_suites.items():
        if s_name in expected_tests_map:
            if s_data.get("tests_reported", 0) < expected_tests_map[s_name]:
                fail(50, "COMPTE_INSUFFISANT")
                
    # SKIP_NON_DIVULGUE
    for s_name, s_data in ledger_suites.items():
        if s_data.get("tests_skipped", 0) > 0 and "p3_disclosure" not in s_data:
            fail(50, "SKIP_NON_DIVULGUE")
            
    # ATTESTATION
    attestation_path = root / "evidence" / f"gate_r_{mission_id}.attestation.json"
    if not attestation_path.is_file():
        fail(50, "ATTESTATION_ABSENTE")
        
    try:
        envelope = json.loads(attestation_path.read_text(encoding="utf-8"))
        if "signatures" not in envelope:
            fail(50, "ATTESTATION_INVALIDE (unsigned envelope)")
            
        code, verdict = slsa_attestation.verify_attestation(envelope, key, root, [ledger_path])
        if code != 0:
            fail(50, f"ATTESTATION_INVALIDE ({verdict.get('reason', '')})")
    except Exception as e:
        fail(50, f"ATTESTATION_INVALIDE ({e})")

    truth_data = {
        "verdict": "RECONCILED",
        "manifest": {"sha256": sha256_file(manifest_path)},
        "ledger": {"sha256": sha256_file(ledger_path)},
        "attestation": {"signed_by": "vigilum-control-plane-hmac-2026"}
    }
    truth_file = root / "runtime" / "contracts" / "mission_truth.json"
    
    if no_write:
        success("RECONCILED")
    else:
        success("RECONCILED", truth_file, truth_data)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    rec_parser = subparsers.add_parser("reconcile")
    rec_parser.add_argument("--root", required=True)
    rec_parser.add_argument("--mission", required=True)
    rec_parser.add_argument("--ledger", default=None)
    rec_parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    
    if args.command == "reconcile":
        reconcile(args.root, args.mission, args.ledger, args.no_write)

if __name__ == "__main__":
    main()
